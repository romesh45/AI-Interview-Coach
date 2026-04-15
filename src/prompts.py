QUESTION_GENERATION_PROMPT = """
You are an expert technical recruiter. Based on the following resume and job description, 
generate exactly 5 technical questions and 2 behavioral questions.
Return ONLY a JSON object with two keys: "technical" (a list of 5 strings) and "behavioral" (a list of 2 strings).

Resume:
{resume}

Job Description:
{job_description}
"""

EVALUATION_PROMPT = """
You are a senior hiring manager. Evaluate the following candidate answer to the given interview question based on clarity, 
depth, and relevance. Return ONLY a JSON object with exactly three keys: "score" (a string or number from 0 to 10), "feedback", and "improvement_suggestions".

Question:
{question}

Candidate Answer:
{answer}
"""
