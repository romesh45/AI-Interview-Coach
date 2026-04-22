import json
from openai import OpenAI
from prompts import ANSWER_EVALUATION_PROMPT

client = OpenAI()

def evaluate_answer(question: str, answer: str) -> dict:
    if not question.strip() or not answer.strip():
        return {"error": "Question and Answer cannot be empty."}

    prompt = ANSWER_EVALUATION_PROMPT.format(question=question, answer=answer)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}]
        )

        parsed_json = json.loads(response.choices[0].message.content)

        if not isinstance(parsed_json, dict):
            raise ValueError("Invalid JSON structure: Output must be an object.")

        evaluation = {
            "score":    parsed_json.get("score", "N/A"),
            "feedback": parsed_json.get("feedback", "No feedback provided."),
            "strengths": (parsed_json.get("strengths")
                          if isinstance(parsed_json.get("strengths"), list) else []),
            "gaps": (parsed_json.get("gaps")
                     if isinstance(parsed_json.get("gaps"), list) else []),
            "improvement_suggestions": (
                parsed_json.get("improvement_suggestions")
                if isinstance(parsed_json.get("improvement_suggestions"), list) else []
            ),
        }
        return evaluation

    except json.JSONDecodeError:
        return {"error": "Failed to parse API response as JSON."}
    except Exception as e:
        return {"error": f"Failed to evaluate answer: {str(e)}"}
