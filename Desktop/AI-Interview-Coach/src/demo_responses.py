FAKE_QUESTIONS = {
    "technical": [
        {
            "question": "Explain Python's GIL and how it affects multi-threaded programs.",
            "skill": "Python",
            "difficulty": "medium",
        },
        {
            "question": "What is the difference between a REST API and a GraphQL API? When would you choose one over the other?",
            "skill": "APIs",
            "difficulty": "medium",
        },
        {
            "question": "Describe how database indexing works and when you would avoid adding an index.",
            "skill": "Databases",
            "difficulty": "medium",
        },
        {
            "question": "Walk me through how you would design a URL-shortening service like bit.ly at scale.",
            "skill": "System Design",
            "difficulty": "hard",
        },
        {
            "question": "What are Python decorators and how would you implement a retry decorator?",
            "skill": "Python",
            "difficulty": "medium",
        },
    ],
    "behavioral": [
        {
            "question": "Tell me about a time you had to deliver a project under a very tight deadline. How did you prioritize and what was the outcome?",
            "skill": "Time Management",
            "difficulty": "medium",
        },
        {
            "question": "Describe a situation where you disagreed with a technical decision made by your team or manager. How did you handle it?",
            "skill": "Collaboration",
            "difficulty": "medium",
        },
    ],
}


def fake_evaluate(question: str, answer: str) -> dict:
    """Deterministic demo evaluator — score scales with answer length, capped at 8."""
    length = len(answer.strip())

    if length < 30:
        score = 2
        feedback = "The answer is too brief to demonstrate understanding. Aim for at least a few sentences."
        strengths = ["Attempted an answer"]
        gaps = ["No explanation provided", "Missing examples", "Lacks technical depth"]
        suggestions = [
            "Expand your answer with at least 2-3 sentences.",
            "Include a concrete example or use case.",
            "Mention any trade-offs or edge cases.",
        ]
    elif length < 100:
        score = 4
        feedback = "You touched on the topic but the answer needs more depth and supporting examples."
        strengths = ["Basic concept mentioned", "On topic"]
        gaps = ["Lacks specifics", "No examples given"]
        suggestions = [
            "Add a real-world example to illustrate your point.",
            "Explain the 'why' behind your answer.",
            "Cover at least one trade-off or alternative approach.",
        ]
    elif length < 300:
        score = 6
        feedback = "Good answer that covers the key idea. Adding more detail and examples would push this higher."
        strengths = ["Clear explanation", "Covers the core concept"]
        gaps = ["Could include more depth", "Edge cases not mentioned"]
        suggestions = [
            "Describe a specific scenario where you applied this knowledge.",
            "Mention potential pitfalls or common mistakes.",
            "Discuss how this relates to your past experience.",
        ]
    else:
        score = min(8, 5 + len(answer) // 200)
        score = min(score, 8)
        feedback = "Strong, detailed answer demonstrating solid understanding of the topic."
        strengths = ["Comprehensive explanation", "Good use of examples", "Shows practical knowledge"]
        gaps = ["Minor gaps in edge-case coverage"]
        suggestions = [
            "Consider framing your answer using the STAR method for behavioural clarity.",
            "Quantify outcomes where possible (e.g. 'reduced latency by 40%').",
            "Briefly acknowledge alternative approaches to show breadth.",
        ]

    return {
        "score": score,
        "feedback": feedback,
        "strengths": strengths,
        "gaps": gaps,
        "improvement_suggestions": suggestions,
    }
