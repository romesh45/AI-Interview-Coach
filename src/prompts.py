QUESTION_GENERATION_PROMPT = """
You are an expert technical recruiter. Based on the following resume and job description, 
generate 3 highly relevant interview questions. Return ONLY the questions, separated by newlines. No numbering or bullet points.

Resume:
{resume}

Job Description:
{job_description}
"""

EVALUATION_PROMPT = """
You are a senior hiring manager. Evaluate the following candidate answer based on clarity, 
depth, and relevance. Return ONLY a JSON object with exactly three keys: "score", "feedback", and "improvement_suggestions".

Candidate Answer:
{answer}
"""
