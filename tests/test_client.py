"""One image submission and terminal same-ID retrieval."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from client import GPTImageClient, ImageError


class FakeResponse:
    def __init__(self, body: dict) -> None:
        self.body = body
        self.headers = {"x-request-id": "trace-image"}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, *_):
        return json.dumps(self.body).encode()


@pytest.mark.asyncio
async def test_submit_once_returns_task_id():
    calls = []

    def fake_open(request, timeout):
        calls.append((request.full_url, json.loads(request.data)))
        return FakeResponse({"task_id": "image-task", "success": True})

    with patch("client.OPENER.open", side_effect=fake_open):
        result = await GPTImageClient("test-key").submit("A blue sphere")
    assert calls == [
        (
            "https://api.acedata.cloud/openai/images/generations",
            {
                "prompt": "A blue sphere",
                "model": "gpt-image-2",
                "size": "1024x1024",
                "quality": "low",
                "n": 1,
                "response_format": "url",
                "async": True,
            },
        )
    ]
    assert result["status"] == "submitted"
    assert result["task_id"] == "image-task"


@pytest.mark.asyncio
async def test_preview_hidden_then_final_image_returned_for_same_id():
    responses = iter(
        [
            {
                "finished_at": None,
                "response": {
                    "state": "running",
                    "data": [{"url": "https://example.org/preview.png"}],
                },
            },
            {
                "finished_at": "2026-10-11T00:00:00Z",
                "response": {
                    "state": "complete",
                    "success": True,
                    "data": [{"url": "https://example.org/final.png"}],
                },
            },
        ]
    )
    calls = []

    def fake_open(request, timeout):
        calls.append(json.loads(request.data))
        return FakeResponse(next(responses))

    with patch("client.OPENER.open", side_effect=fake_open):
        client = GPTImageClient("test-key")
        pending = await client.query("image-task")
        final = await client.query("image-task")
    assert calls == [{"action": "retrieve", "id": "image-task"}] * 2
    assert pending["status"] == "pending" and pending["image_urls"] == []
    assert final["status"] == "succeeded"
    assert final["image_urls"] == ["https://example.org/final.png"]


@pytest.mark.asyncio
async def test_missing_task_id_does_not_repeat_generation():
    with (
        patch(
            "client.OPENER.open", return_value=FakeResponse({"success": True})
        ) as opening,
        pytest.raises(ImageError),
    ):
        await GPTImageClient("test-key").submit("A blue sphere")
    assert opening.call_count == 1
