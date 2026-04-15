import json
from openai import OpenAI
from prompts import EVALUATION_PROMPT

client = OpenAI()

def evaluate_answer(question: str, answer: str) -> dict:
    """Uses OpenAI to evaluate candidate answers."""
    if not question.strip() or not answer.strip():
        return {"error": "Question and Answer cannot be empty."}

    prompt = EVALUATION_PROMPT.format(question=question, answer=answer)
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={ "type": "json_object" },
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {
            "error": "Failed to parse OpenAI response or API error.",
            "score": "N/A",
            "feedback": str(e),
            "improvement_suggestions": "Please try submitting the answer again."
        }
