"""GPT Image Agent tools for AstrBot."""

from __future__ import annotations

import json

from astrbot.api import AstrBotConfig
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star

from .client import GPTImageClient, ImageError


class GPTImagePlugin(Star):
    """Submit an image job and retrieve its final image in chat."""

    def __init__(self, context: Context, config: AstrBotConfig) -> None:
        """Use AstrBot's masked-key plugin setting.

        Args:
            context: AstrBot plugin context.
            config: Plugin configuration.
        """
        super().__init__(context)
        self.config = config

    @filter.llm_tool(name="gpt_image_generate")
    async def gpt_image_generate(self, event: AstrMessageEvent, prompt: str) -> str:
        """Submit one GPT Image 2 generation; save its task ID for retrieval.

        Args:
            prompt(string): Description of the image to generate.

        Returns:
            JSON submission status and task ID, not a completed image.
        """
        try:
            result = await GPTImageClient(self.config.get("api_key", "")).submit(prompt)
        except ImageError as exc:
            result = {"status": "error", "message": str(exc)}
        return json.dumps(result, ensure_ascii=False)

    @filter.llm_tool(name="gpt_image_get_task")
    async def gpt_image_get_task(self, event: AstrMessageEvent, task_id: str) -> str:
        """Query the same GPT Image task ID until final success or failure.

        Args:
            task_id(string): Exact ID from gpt_image_generate.

        Returns:
            JSON status and image URLs only after terminal success.
        """
        try:
            result = await GPTImageClient(self.config.get("api_key", "")).query(task_id)
        except ImageError as exc:
            result = {"status": "error", "message": str(exc), "task_id": task_id}
        return json.dumps(result, ensure_ascii=False)
