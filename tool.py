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
            default="", description="Lumenfall.ai API anahtarınız (sk- ile başlar)"
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
                        "description": "Lumenfall ile görsel oluşturuluyor...",
                        "status": "in_progress",
                        "done": False,
                    },
                    "type": "status",
                }
            )

        # API Anahtarı kontrolü
        if not self.valves.LUMENFALL_API_KEY:
            return "❌ Hata: Lumenfall API Key ayarlanmamış. Tool'un Valves kısmından API anahtarını girin."

        # API URL'si
        base_url = self.valves.LUMENFALL_API_BASE_URL.rstrip("/")
        url = f"{base_url}/images/generations"

        headers = {
            "Authorization": f"Bearer {self.valves.LUMENFALL_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {"model": model, "prompt": prompt, "n": 1, "size": size}

        try:
            # Asenkron olarak API isteği gönder
            response = await asyncio.to_thread(
                requests.post, url, headers=headers, json=payload, timeout=90
            )
            response.raise_for_status()
            data = response.json()

            if data.get("data") and len(data["data"]) > 0:
                # URL'yi veya base64 verisini al
                image_url = data["data"][0].get("url")
                if not image_url:
                    b64 = data["data"][0].get("b64_json")
                    if b64:
                        image_url = f"data:image/png;base64,{b64}"
                    else:
                        return "❌ Hata: API yanıtında resim URL'si veya base64 verisi bulunamadı."

                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "data": {
                                "description": "Görsel başarıyla oluşturuldu! 🎨",
                                "status": "complete",
                                "done": True,
                            },
                            "type": "status",
                        }
                    )
                # Markdown formatında döndür
                return f"![Generated Image]({image_url})"

            else:
                return f"❌ Hata: Beklenmeyen API yanıtı: {data}"

        except requests.exceptions.RequestException as e:
            error_body = e.response.text if e.response else str(e)
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "data": {
                            "description": f"API Hatası: {error_body}",
                            "status": "complete",
                            "done": True,
                        },
                        "type": "status",
                    }
                )
            return f"❌ Lumenfall API çağrısı başarısız: {error_body}"
        except Exception as e:
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "data": {
                            "description": f"Beklenmeyen hata: {str(e)}",
                            "status": "complete",
                            "done": True,
                        },
                        "type": "status",
                    }
                )
            return f"❌ Beklenmeyen bir hata oluştu: {str(e)}"
