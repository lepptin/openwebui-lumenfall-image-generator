"""
title: Lumenfall Image Generator
author: #
description: Generate images using Lumenfall.ai API (OpenAI-compatible). Supports flux.2-max, flux-realism, gemini-3-pro-image, etc.
version: 1.0
"""

import requests
import json
from typing import Optional, Awaitable, Callable, List
import asyncio
from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        LUMENFALL_API_KEY: str = Field(
            default="", description="Your Lumenfall.ai API key"
        )
        LUMENFALL_API_BASE_URL: str = Field(
            default="https://api.lumenfall.ai/openai/v1",
            description="Lumenfall API base URL",
        )

    def __init__(self):
        self.valves = self.Valves()

    async def generate_image_lumenfall(
        self,
        prompt: str,
        model: str = "flux.2-max",
        size: str = "1024x1024",
        __event_emitter__: Optional[Callable[[dict], Awaitable[None]]] = None,
    ) -> str:
        """
        Generate an image using the Lumenfall.ai API with state-of-the-art AI image generation models.
        This tool uses the OpenAI-compatible endpoint of Lumenfall.

        Args:
            prompt: A detailed natural language prompt describing the image to generate. Should be at least 20-50 words for best results.
            model: The model to use. Options: flux.2-max, flux-realism, flux-anime, flux-3d, gemini-3-pro-image, etc. Default is flux.2-max.
            size: Image size. Options: 1024x1024, 1792x1024, 1024x1792. Default is 1024x1024.

        Returns:
            str: Markdown formatted image link.
        """
        if __event_emitter__:
            await __event_emitter__(
                {
                    "data": {
                        "description": "Generating image with Lumenfall...",
                        "status": "in_progress",
                        "done": False,
                    },
                    "type": "status",
                }
            )

        # API Key check
        if not self.valves.LUMENFALL_API_KEY:
            return "❌ Error: Lumenfall API Key is not set. Please enter your API key in the Tool's Valves section."

        # API URL
        base_url = self.valves.LUMENFALL_API_BASE_URL.rstrip("/")
        url = f"{base_url}/images/generations"

        headers = {
            "Authorization": f"Bearer {self.valves.LUMENFALL_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {"model": model, "prompt": prompt, "n": 1, "size": size}

        try:
            # Send API request asynchronously
            response = await asyncio.to_thread(
                requests.post, url, headers=headers, json=payload, timeout=90
            )
            response.raise_for_status()
            data = response.json()

            if data.get("data") and len(data["data"]) > 0:
                # Get the URL or base64 data
                image_url = data["data"][0].get("url")
                if not image_url:
                    b64 = data["data"][0].get("b64_json")
                    if b64:
                        image_url = f"data:image/png;base64,{b64}"
                    else:
                        return "❌ Error: No image URL or base64 data found in the API response."

                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "data": {
                                "description": "Image successfully created! 🎨",
                                "status": "complete",
                                "done": True,
                            },
                            "type": "status",
                        }
                    )
                # Return in Markdown format
                return f"![Generated Image]({image_url})"

            else:
                return f"❌ Error: Unexpected API response: {data}"

        except requests.exceptions.RequestException as e:
            error_body = e.response.text if e.response else str(e)
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "data": {
                            "description": f"API Error: {error_body}",
                            "status": "complete",
                            "done": True,
                        },
                        "type": "status",
                    }
                )
            return f"❌ Lumenfall API call failed: {error_body}"
        except Exception as e:
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "data": {
                            "description": f"Unexpected error: {str(e)}",
                            "status": "complete",
                            "done": True,
                        },
                        "type": "status",
                    }
                )
            return f"❌ An unexpected error occurred: {str(e)}"
