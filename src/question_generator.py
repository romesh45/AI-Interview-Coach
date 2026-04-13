import os
from openai import OpenAI
from prompts import QUESTION_GENERATION_PROMPT

client = OpenAI()

def generate_questions(resume: str, job_description: str) -> list:
    """Uses OpenAI to generate interview questions."""
    prompt = QUESTION_GENERATION_PROMPT.format(
        resume=resume,
        job_description=job_description
    )
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    questions = response.choices[0].message.content.strip().split('\n')
    return [q.strip() for q in questions if q.strip()]
