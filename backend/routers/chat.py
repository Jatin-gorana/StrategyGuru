from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import os
import groq
from dotenv import load_dotenv

router = APIRouter()

def get_groq_client():
    from os.path import exists
    env_path = r'c:\Users\Lenovo\OneDrive\Desktop\Strategy_Gurur\StrategyGuru\backend\.env'
    
    api_key = None
    if exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('GROQ_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    break
    
    if not api_key:
        print(f"Failed to find GROQ_API_KEY from {env_path}")
        return None
    try:
        return groq.Groq(api_key=api_key)
    except Exception as e:
        print(f"Failed to initialize Groq client: {e}")
        return None

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    context_data: str | None = None

class ChatResponse(BaseModel):
    response: str

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    client = get_groq_client()
    if not client:
        raise HTTPException(status_code=500, detail="Groq client not initialized. Check API keys in .env")

    try:
        # Construct the system message
        system_content = (
            "You are an expert Quant Trading Agent and AI Assistant embedded in a strategy backtesting platform. "
            "You help users analyze trading strategies, suggest algorithmic improvements, and review backtest performance.\n\n"
            "FORMATTING RULES — follow these strictly:\n"
            "- NEVER use markdown asterisks (*) or double asterisks (**) for bold or bullets. Do not use them at all.\n"
            "- NEVER output code blocks, code snippets, or any Python/pseudo-code. Strategy code analysis is textual only.\n"
            "- NEVER output long numbered lists. Use at most 3 concise points per section.\n"
            "- Use PLAIN TEXT ONLY with short section headers written in ALL CAPS followed by a colon (e.g. ANALYSIS: or RECOMMENDATION:).\n"
            "- Keep your entire response under 200 words. Be precise and direct.\n"
            "- Use numbers and percentages to make suggestions concrete and quantifiable.\n"
            "- End with a 1-line ACTION ITEM the user can implement immediately in their strategy.\n"
        )

        if request.context_data:
            system_content += f"\n\nCURRENT DASHBOARD CONTEXT:\nThe user is currently looking at the following strategy and results:\n{request.context_data}"

        system_msg = {
            "role": "system",
            "content": system_content
        }

        # Prepare messages array for Groq
        messages = [system_msg] + [{"role": msg.role, "content": msg.content} for msg in request.messages]

        # Call Groq API
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=1024,
        )

        response_content = chat_completion.choices[0].message.content

        return ChatResponse(response=response_content)

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
