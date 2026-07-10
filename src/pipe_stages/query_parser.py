import os
from google import genai
from google.genai import types
from Types.QueryIntent import QueryIntent


def parsed_intent(query: str) -> QueryIntent:
    """Uses Gemini to parse the structural and semantic constraints out of a user query."""
    # Instantiating the clean modern client
    # It automatically reads GEMINI_API_KEY from environment variables
    client = genai.Client()

    prompt = f"""
    Analyze the following user search query and break down its structural filters, 
    business roles, and underlying target intent.

    User Query: "{query}"
    """

    # We use gemini-2.5-flash as it is lightning fast and perfect for structural parsing tasks
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=QueryIntent,
            temperature=0.0,  # High determinism for extraction tasks
        ),
    )

    # Parse the verified JSON back into our strongly typed Pydantic object
    return QueryIntent.model_validate_json(response.text)