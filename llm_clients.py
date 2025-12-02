# llm_clients.py
import os
import requests
import json
from config import OPENROUTER_API_KEY, OPENROUTER_BASE, MISTRAL_API_KEY, MISTRAL_BASE

def call_openrouter(prompt: str, model: str = "gpt-4o-mini", max_tokens: int = 512, timeout: int = 30):
    if not OPENROUTER_API_KEY:
        return None
    url = f"{OPENROUTER_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": model,
        "messages": [{"role":"user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.0
    }
    try:
        r = requests.post(url, headers=headers, json=body, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        if "choices" in data and len(data["choices"])>0:
            text = data["choices"][0].get("message", {}).get("content") or data["choices"][0].get("text")
            return {"success": True, "model": model, "text": text, "meta": data}
        return {"success": True, "model": model, "text": json.dumps(data), "meta": data}
    except Exception as e:
        return {"success": False, "error": str(e)}

def call_generic_http(prompt: str, base_url: str, api_key: str, model: str = None, timeout: int = 30):
    if not api_key or not base_url:
        return None
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type":"application/json"}
    payload = {"prompt": prompt}
    if model:
        payload["model"] = model
    try:
        r = requests.post(base_url, headers=headers, json=payload, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        text = data.get("text") or data.get("output") or data.get("result") or json.dumps(data)
        return {"success": True, "model": model or "generic-http", "text": text, "meta": data}
    except Exception as e:
        return {"success": False, "error": str(e)}

def generate(prompt: str, prefer_openrouter: bool = True, openrouter_model: str = "gpt-4o-mini", fallbacks: bool = True):
    if prefer_openrouter and OPENROUTER_API_KEY:
        res = call_openrouter(prompt, model=openrouter_model)
        if res and res.get("success"):
            return res
    # try Mistral generic
    if MISTRAL_API_KEY and MISTRAL_BASE:
        res = call_generic_http(prompt, base_url=MISTRAL_BASE, api_key=MISTRAL_API_KEY)
        if res and res.get("success"):
            return res
    # fallback stub
    if fallbacks:
        return {"success": True, "model": "stub", "text": f"[LLM-stub] {prompt[:1000]}"}
    return {"success": False, "error": "No LLM available"}
