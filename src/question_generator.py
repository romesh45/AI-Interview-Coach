import os
import json
from openai import OpenAI
from prompts import QUESTION_GENERATION_PROMPT

client = OpenAI()

def generate_questions(resume: str, job_description: str) -> dict:
    """Uses OpenAI to generate technical and behavioral questions."""
    if not resume.strip() or not job_description.strip():
        return {"error": "Resume and Job Description cannot be empty."}
        
    prompt = QUESTION_GENERATION_PROMPT.format(
        resume_text=resume,
        job_description=job_description
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={ "type": "json_object" },
            messages=[{"role": "user", "content": prompt}]
        )
        raw_output = json.loads(response.choices[0].message.content)
        
        # Transform new prompt's array structure to the UI expected dict structure
        formatted_questions = {"technical": [], "behavioral": []}
        for item in raw_output.get("questions", []):
            if item.get("type") == "technical":
                formatted_questions["technical"].append(item.get("question"))
            elif item.get("type") == "behavioral":
                formatted_questions["behavioral"].append(item.get("question"))
                
        return formatted_questions
    except Exception as e:
        return {"error": f"Failed to generate questions: {str(e)}"}
