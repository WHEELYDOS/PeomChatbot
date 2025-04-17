import os
from google import genai
from google.genai import types

def generate(messages, api_key):
    """Generates content using the Gemini model based on a conversation history."""
    if not api_key:
        print("Error: API key not provided.")
        return None

    client = genai.Client(api_key=api_key)
    model = "gemini-2.0-flash"

    contents = []
    for role, text in messages:
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=text)]))

    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
    )

    try:
        response = client.models.generate_content(
            model=model, contents=contents, config=generate_content_config
        )
        if response and response.text:
            return response.text
        else:
            print("Error: No response or empty response from Gemini API.")
            return None

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None
