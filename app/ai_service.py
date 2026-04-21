import app.crud.messages
from dotenv import load_dotenv
import os
from google import genai
from typing import List
from app.logger import get_logger

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY")) 
#model = genai.GenerativeModel("gemini-1.5-flash") 
logger = get_logger("ai_service")
async def summarize_chat_history(messages: List[str]):
    if not messages:
        logger.warning("No messages found for chat summary")
        return "No conversation history to summarize"
    chat_transcript = "\n".join(messages)

    prompt = (
        "You are a helpful chat assistant. Below is a transcript of the last 100 messages in a chat room "
        "Provide a concise summary in 5-6 bullet points so a newly joined user can quickly catch up on the context. "
        "If the transcript is too short or doesn't have enough context, just provide a 1 or 2 bullet points"
        "Donot include phrases like 'Here's the summary'"
        "Focus only on the key topics discussed.\n\n"
        f"TRANSCRIPT: \n{chat_transcript}"
    )
   # models_to_try = ["gemini-1.5-flash","gemini-1.5-flash-latest","gemini-2.0-flash"]
   

    try:
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        

        if response.text:
            return response.text
        return "I couldn't generate a summary at this time."
    except Exception as e:
        
        logger.error("AI summary generation failed", extra={"error": str(e)})
        return "Sorry, your assistant is currently unavailable. Please try again later"