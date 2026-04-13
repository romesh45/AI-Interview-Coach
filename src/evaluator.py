import os
import json
from openai import OpenAI
from prompts import EVALUATION_PROMPT

client = OpenAI()

def evaluate_answer(answer: str) -> dict:
    """Uses OpenAI to evaluate candidate answers."""
    prompt = EVALUATION_PROMPT.format(answer=answer)
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_format={ "type": "json_object" },
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return {
            "score": "Error",
            "feedback": "Failed to parse OpenAI response.",
            "improvement_suggestions": "Please try submitting your answer again."
        }
