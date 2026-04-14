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
        resume=resume,
        job_description=job_description
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={ "type": "json_object" },
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": f"Failed to generate questions: {str(e)}"}
