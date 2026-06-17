# 🎨 OpenWebUI Lumenfall Image Generator Tool

[![OpenWebUI](https://img.shields.io/badge/OpenWebUI-Tool-blue)](https://openwebui.com)
[![Lumenfall](https://img.shields.io/badge/Lumenfall-API-orange)](https://lumenfall.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful, plug‑and‑play **Tool** for [OpenWebUI](https://openwebui.com) that enables your LLM (DeepSeek, Llama, GPT, etc.) to generate stunning, high‑quality images using the [Lumenfall.ai](https://lumenfall.ai) API.  

It supports cutting‑edge models like **Flux.2 Max**, **Flux Realism**, **Gemini 3 Pro Image**, and **Stable Diffusion**, all through an OpenAI‑compatible interface. Just chat with your model, and it will generate images automatically!

---

## ✨ Features

- **OpenAI Compatible** – Uses Lumenfall’s `/images/generations` endpoint.
- **Multi‑Model Support** – Choose between `flux.2‑max`, `flux‑realism`, `flux‑anime`, `gemini‑3‑pro‑image`, and more.
- **Native Valves Integration** – API keys are stored securely in the UI (no hardcoding required).
- **Asynchronous & Fast** – Non‑blocking requests with real‑time status updates via `event_emitter`.
- **Customizable Sizes** – Supports standard sizes like `1024x1024`, `1792x1024`, `1024x1792`.
- **Markdown Output** – Returns images as embeddable Markdown links directly in the chat.

---

## 📋 Prerequisites

- **OpenWebUI** (version with Tool/Valves support, e.g., v0.7.0+).
- **Lumenfall.ai Account** – [Sign up here](https://lumenfall.ai) to get your free API key ($1 free credit to start).

---

## 🚀 Installation Guide

Follow these steps to add the tool to your OpenWebUI instance:

### 1. Get the Code
Copy the full Python script from the [`tool.py`](tool.py) file in this repository, or use the script provided in the [Installation Steps](#installation-steps) section below.

### 2. Add the Tool in OpenWebUI
- Navigate to **Workspace** → **Tools** in your OpenWebUI sidebar.
- Click on **"Add Tool"**.
- Give it a name (e.g., "Lumenfall Image Generator").
- Paste the entire Python code into the code editor.
- Click **"Save"**.

### 3. Configure Valves (API Key)
After saving, you'll see the tool in your list. 
- Click the **Gear Icon (⚙️)** next to the tool name to open **Valves**.
- Enter your Lumenfall API Key in the `LUMENFALL_API_KEY` field.
  *(Leave `LUMENFALL_API_BASE_URL` as `https://api.lumenfall.ai/openai/v1` unless you have a custom endpoint).*
- Click **"Save"** again.

### 4. Enable the Tool for your Model
- Go to **Admin Panel** → **Settings** → **Models**.
- Select the model you want to use (e.g., `deepseek-chat`, `gpt-4`, `llama3`).
- Find the **"Tools"** tab/section.
- **Check** the box for **"Lumenfall Image Generator"** to enable it.
- Click **Save**.

---

## 🧪 Usage & Example Prompts

Once enabled, your model will automatically decide when to use the tool based on your prompt. You can also gently guide it.

### Natural Language Trigger (Recommended)
Simply ask the model to generate an image. It will call the tool if it makes sense.

> **User:** *"Generate a photorealistic image of a cozy wooden cabin in a snowy forest at night, with warm yellow lights glowing from the windows. Make it cinematic."*

### Explicit Model Selection
You can specify which AI model to use by mentioning it in the prompt.

> **User:** *"Use Lumenfall with the flux-realism model to create a portrait of a cyberpunk samurai in a rainy neon-lit city street."*

### Direct Tool Call (Force Trigger)
If the model doesn't automatically use the tool, you can explicitly ask it to.

> **User:** *"Call generate_image_lumenfall with the prompt: 'A beautiful sunset over the Bosphorus strait, Istanbul, with seagulls flying. Golden hour, warm colors, highly detailed.' Use flux.2-max."*

### Available Models
You can specify these in the `model` argument:
- `flux.2-max` (Best overall quality, recommended)
- `flux-realism` (Hyper-realistic photos)
- `flux-anime` (Anime/Manga style)
- `flux-3d` (3D rendered scenes)
- `gemini-3-pro-image` (Google's Gemini experimental)
- *Check [Lumenfall Models](https://lumenfall.ai/models) for the latest list.*

---

## 🛠️ Tool Code (Copy & Paste)

If you want to manually create the tool, here is the full code block:

<details>
<summary>Click to expand the full code</summary>

```python
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

</details>

Troubleshooting

    "❌ Hata: Lumenfall API Key ayarlanmamış": You forgot to add your API key in the Valves (Gear icon) of the tool.
    "401 Unauthorized": Your API key is incorrect or expired. Generate a new one in your Lumenfall dashboard.
    "404 Not Found": The LUMENFALL_API_BASE_URL is wrong. Ensure it ends with /openai/v1.
    Model doesn't call the tool: Make sure the tool is enabled in your specific model's settings (Admin > Settings > Models > [Your Model] > Tools).

    Credits: Lumenfall gives you $1 free credit to start. Check your usage in the Lumenfall dashboard.

💬 Contributing
Feel free to open an Issue or a Pull Request if you have suggestions to improve this tool!
📄 License

This project is licensed under the MIT License – feel free to use, modify, and distribute as you like.
🙏 Credits

    OpenWebUI for the amazing platform.
    Lumenfall.ai for the powerful, OpenAI‑compatible image API.
    Special thanks to the OpenWebUI community for the excellent Tool/Valves framework.