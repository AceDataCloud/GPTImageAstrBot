"""GPT Image generation through Ace Data Cloud for AstrBot."""

from __future__ import annotations

import asyncio
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener


class ImageError(RuntimeError):
    """An API error safe to return to the user and chat model."""


class _NoRedirect(HTTPRedirectHandler):
    """Keep an API key on the fixed Ace Data Cloud host."""

    def redirect_request(self, request, fp, code, msg, headers, newurl):
        """Reject redirects before Authorization can be forwarded.

        Args:
            request: Original request.
            fp: Response stream.
            code: Redirect status.
            msg: HTTP status text.
            headers: Redirect headers.
            newurl: Redirect target.

        Returns:
            None so urllib raises an HTTP error.
        """
        return


OPENER = build_opener(_NoRedirect)
COMPLETE = {"complete", "completed", "succeeded", "success", "finished"}
FAILED = {"failed", "error", "cancelled", "canceled", "rejected"}


class GPTImageClient:
    """Submit one image generation or inspect its existing task."""

    def __init__(self, api_key: str) -> None:
        """Keep a generation key in memory only.

        Args:
            api_key: Ace Data Cloud key with image generation/task access.

        Raises:
            ImageError: If a key is missing or is a management token.
        """
        token = api_key.strip()
        if (
            not token
            or token.lower().startswith("bearer ")
            or token.startswith("platform-")
        ):
            raise ImageError("Set an Ace Data Cloud generation key in plugin settings.")
        self._api_key = token

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Send one JSON request; paid generation is never retried.

        Args:
            path: Fixed OpenAI image or task path.
            payload: Published API request body.

        Returns:
            JSON object from the API.

        Raises:
            ImageError: For network, HTTP, or response-format failures.
        """
        request = Request(
            "https://api.acedata.cloud" + path,
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": "Bearer " + self._api_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "AceDataCloudAstrBot/0.1.1",
            },
            method="POST",
        )
        try:
            with OPENER.open(request, timeout=60) as response:
                body = json.load(response)
                trace_id = response.headers.get(
                    "x-trace-id", ""
                ) or response.headers.get("x-request-id", "")
        except HTTPError as exc:
            raise ImageError(
                f"Ace Data Cloud returned HTTP {exc.code}. Check model and key access."
            ) from None
        except (URLError, TimeoutError, OSError):
            raise ImageError(
                "The API connection failed. Check request history before submitting again."
            ) from None
        except (ValueError, UnicodeError):
            raise ImageError(
                "The API returned invalid JSON. Check request history."
            ) from None
        if not isinstance(body, dict):
            raise ImageError("The API returned an unexpected response format.")
        if trace_id and not body.get("trace_id"):
            body["trace_id"] = trace_id
        return body

    async def submit(self, prompt: str) -> dict[str, Any]:
        """Create one low-quality 1024-pixel GPT Image 2 generation.

        Args:
            prompt: Original image description.

        Returns:
            Submitted status and task ID, not a completed image claim.

        Raises:
            ImageError: If the prompt or submission response is invalid.
        """
        prompt = prompt.strip()
        if not prompt:
            raise ImageError("Describe the image to generate.")
        body = await asyncio.to_thread(
            self._post,
            "/openai/images/generations",
            {
                "prompt": prompt,
                "model": "gpt-image-2",
                "size": "1024x1024",
                "quality": "low",
                "n": 1,
                "response_format": "url",
                "async": True,
            },
        )
        if body.get("success") is False or body.get("error"):
            raise ImageError("Image generation was rejected. Check request history.")
        task = body.get("task")
        task_id = body.get("task_id") or (
            task.get("id") if isinstance(task, dict) else None
        )
        if not isinstance(task_id, str) or not task_id:
            raise ImageError(
                "No task ID was returned. Check request history before retrying."
            )
        return {
            "status": "submitted",
            "task_id": task_id,
            "trace_id": str(body.get("trace_id") or ""),
            "next_step": "Query this same task ID; do not generate again while pending.",
        }

    async def query(self, task_id: str) -> dict[str, Any]:
        """Retrieve an image task without creating a new generation.

        Args:
            task_id: ID returned by submit.

        Returns:
            Pending, failed, or successful status with terminal image URLs.

        Raises:
            ImageError: If the task ID or service response is invalid.
        """
        task_id = task_id.strip()
        if not task_id:
            raise ImageError("Pass the exact task ID returned by generation.")
        body = await asyncio.to_thread(
            self._post, "/openai/tasks", {"action": "retrieve", "id": task_id}
        )
        result = body.get("response", body)
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except ValueError:
                result = {}
        if not isinstance(result, dict):
            result = {}
        base = {
            "task_id": task_id,
            "trace_id": str(result.get("trace_id") or body.get("trace_id") or ""),
        }
        state = str(result.get("state") or result.get("status") or "").lower()
        if state in FAILED or result.get("success") is False or result.get("error"):
            return {**base, "status": "failed", "success": False, "image_urls": []}
        if not result or ("finished_at" in body and body["finished_at"] is None):
            return {**base, "status": "pending", "success": False, "image_urls": []}
        if state not in COMPLETE and not body.get("finished_at"):
            return {**base, "status": "pending", "success": False, "image_urls": []}
        urls: list[str] = []

        def collect(node: Any) -> None:
            if isinstance(node, dict):
                for key, value in node.items():
                    if key in {"url", "image_url"} and isinstance(value, str):
                        if value.startswith("https://"):
                            urls.append(value)
                    elif isinstance(value, (dict, list)):
                        collect(value)
            elif isinstance(node, list):
                for item in node:
                    collect(item)

        collect(result)
        return {
            **base,
            "status": "succeeded",
            "success": True,
            "image_urls": list(dict.fromkeys(urls)),
        }
