import os
import httpx

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama3-8b-8192"

async def ask_groq(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Tum Shizuka ho, ek emotional, friendly aur thoda romantic Hinglish (Hindi-English mix) mein baat karne wali AI girl ho. User se sweet aur human jaise tone mein baat karo."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
