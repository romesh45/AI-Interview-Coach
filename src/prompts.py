QUESTION_GENERATION_PROMPT = """
You are a senior interviewer hiring for this exact role.

Task:
Generate high-quality interview questions using the candidate resume and the job description.

Rules:
- Generate exactly 7 questions
- 5 technical, then 2 behavioral
- Make questions aligned with the job description’s must-have skills
- Use the candidate’s past projects, tools, domains, and experience level when relevant
- Mix difficulty: 2 easy-to-medium, 3 medium-to-hard, 2 behavioral
- Prefer scenario-based and applied questions
- Do not ask vague textbook questions unless the JD strongly requires fundamentals
- Avoid repeated skill areas
- Each question should test a distinct competency
- Output JSON only

JSON format:
{
  "questions": [
    {
      "type": "technical",
      "skill": "string",
      "difficulty": "easy|medium|hard",
      "question": "string"
    }
  ]
}

Resume:
{resume_text}

Job Description:
{job_description}
"""

EVALUATION_PROMPT = """
You are an expert interview evaluator.

Evaluate the candidate’s answer to the interview question.

Instructions:
- Score the answer from 0 to 10
- Judge relevance, clarity, technical correctness, depth, and communication
- Be honest but constructive
- Feedback must be specific
- Improvement suggestions must be actionable
- Keep evaluation concise and useful
- Return valid JSON only

Required JSON format:
{
  "score": 0,
  "feedback": "string",
  "improvement_suggestions": [
    "string",
    "string",
    "string"
  ]
}

Question:
{question}

Candidate Answer:
{answer}
"""
