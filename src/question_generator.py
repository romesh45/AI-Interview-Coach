import json
from openai import OpenAI
from prompts import QUESTION_GENERATION_PROMPT

client = OpenAI()

def generate_questions(resume: str, job_description: str) -> dict:
    if not resume.strip() or not job_description.strip():
        return {"error": "Resume and Job Description cannot be empty."}

    prompt = QUESTION_GENERATION_PROMPT.format(
        resume_text=resume,
        job_description=job_description
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-5.4-mini",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}]
        )
        
        raw_output = json.loads(response.choices[0].message.content)
        questions_list = raw_output.get("questions", [])
        
        if not isinstance(questions_list, list):
            raise ValueError("Invalid JSON structure: 'questions' must be a list.")
            
        formatted_questions = {"technical": [], "behavioral": []}
        
        for item in questions_list:
            if not isinstance(item, dict):
                continue
                
            mapped_item = {
                "question": item.get("question", ""),
                "skill": item.get("skill", ""),
                "difficulty": item.get("difficulty", "")
            }
            
            if item.get("type") == "technical":
                formatted_questions["technical"].append(mapped_item)
            elif item.get("type") == "behavioral":
                formatted_questions["behavioral"].append(mapped_item)

        if len(formatted_questions["technical"]) != 5 or len(formatted_questions["behavioral"]) != 2:
            raise ValueError("Model failed to strictly generate 5 technical and 2 behavioral questions.")

        return formatted_questions

    except json.JSONDecodeError:
        return {"error": "Failed to parse API response as JSON."}
    except Exception as e:
        return {"error": f"Failed to generate questions: {str(e)}"}
