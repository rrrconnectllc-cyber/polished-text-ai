# ai_core.py (Final version with deferred initialization)
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize client as None initially
client = None

def get_openai_client():
    """Initializes and returns the OpenAI client, ensuring it's a singleton."""
    global client
    if client is None:
        print("Initializing OpenAI client for the first time...")
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        print("✅ OpenAI client initialized.")
    return client

def polish_text(input_text):
    """
    Sends text to the OpenAI API for polishing and returns the result.
    """
    try:
        # Get the initialized client
        openai_client = get_openai_client()

        system_prompt = "You are an expert English editor. Your task is to take the user's text and rewrite it to be more clear, concise, and professional. You must correct all spelling and grammatical errors."

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input_text}
            ],
            temperature=0.7,
            max_tokens=1024
        )

        polished_text = response.choices[0].message.content.strip()
        return polished_text

    except Exception as e:
        print(f"An error occurred with the OpenAI API: {e}")
        return "Sorry, there was an error processing your request."
