"""
Realistic demo data used when DEMO_MODE is active.

Provides questions and evaluations that look indistinguishable from
live AI output, so recruiters can explore the full product without
needing an OpenAI API key.
"""

import random

DEMO_QUESTIONS = {
    "technical": [
        {
            "question": (
                "You're designing a REST API for a social media feed that must handle "
                "millions of posts. Walk me through cursor-based vs. offset-based pagination "
                "— what are the trade-offs and which would you choose here?"
            ),
            "skill": "System Design",
            "difficulty": "hard",
        },
        {
            "question": (
                "Explain Python's GIL and how it affects multi-threaded programs. "
                "When would you choose threading vs. multiprocessing vs. asyncio for a "
                "CPU-bound task vs. an I/O-bound task?"
            ),
            "skill": "Python",
            "difficulty": "medium",
        },
        {
            "question": (
                "A SQL query joining four tables on a 10M-row database is taking 8 seconds. "
                "Walk me through your debugging process — what tools would you use, "
                "and what are the most likely causes?"
            ),
            "skill": "Database",
            "difficulty": "hard",
        },
        {
            "question": (
                "What is the difference between authentication and authorization? "
                "Implement JWT-based auth in a Flask API — describe the token flow, "
                "storage, and how you'd handle token expiry securely."
            ),
            "skill": "Security",
            "difficulty": "medium",
        },
        {
            "question": (
                "Describe how Docker containers differ from virtual machines. "
                "How would you containerise a multi-service Flask + PostgreSQL + Redis "
                "application with Docker Compose for local development?"
            ),
            "skill": "DevOps",
            "difficulty": "easy",
        },
    ],
    "behavioral": [
        {
            "question": (
                "Tell me about a time you had to debug a critical production issue under "
                "time pressure. What was your process, what did you communicate to "
                "stakeholders, and what did you change afterwards?"
            ),
            "skill": "Problem Solving",
            "difficulty": "medium",
        },
        {
            "question": (
                "Describe a situation where you disagreed with a technical decision made "
                "by your team or lead. How did you handle the disagreement and what "
                "was the outcome?"
            ),
            "skill": "Collaboration",
            "difficulty": "medium",
        },
    ],
}

# Pool of realistic evaluations — one is sampled per submission
_DEMO_EVAL_POOL = [
    {
        "score": 7.5,
        "feedback": (
            "Strong answer that demonstrates practical experience. You correctly identified "
            "the key trade-offs and gave concrete examples. The explanation was well-structured "
            "and showed genuine understanding rather than textbook recall. "
            "Could push further on edge cases and failure modes."
        ),
        "strengths": [
            "Clearly articulated the core trade-off with real-world reasoning",
            "Used concrete numbers and scenarios rather than vague generalities",
        ],
        "gaps": [
            "Didn't address failure modes or what happens under partial failures",
            "Missing discussion of how this choice affects monitoring and observability",
        ],
        "improvement_suggestions": [
            "Practice explaining the CAP theorem implications for your design choices",
            "Add a sentence on how you'd test this at scale before going to production",
            "Study how large-scale systems (Twitter, Instagram) have solved similar problems",
        ],
    },
    {
        "score": 6.0,
        "feedback": (
            "Acceptable answer that shows foundational knowledge. You got the basics right "
            "but the response lacked depth and specifics. In a real interview, this would "
            "prompt follow-up questions. Interviewers want to see you go beyond the textbook "
            "definition and into actual implementation detail."
        ),
        "strengths": [
            "Correctly identified the key concepts and their relationship",
            "Answer was clear and easy to follow",
        ],
        "gaps": [
            "No concrete examples from past experience or hypothetical projects",
            "Didn't address scalability or production considerations",
        ],
        "improvement_suggestions": [
            "Prepare a specific project example where you applied this concept",
            "Add one 'war story' — a mistake you made and what you learned",
            "Read the relevant system design chapter in 'Designing Data-Intensive Applications'",
        ],
    },
    {
        "score": 8.5,
        "feedback": (
            "Excellent answer. You demonstrated deep understanding, structured your "
            "response logically, and covered edge cases unprompted. The practical "
            "example was relevant and specific. This is the kind of answer that "
            "moves a candidate to the next round — the main missing piece is discussing "
            "how you'd measure success after implementation."
        ),
        "strengths": [
            "Covered both the happy path and failure scenarios proactively",
            "Referenced a real implementation with specific technical details",
            "Communication was precise without unnecessary jargon",
        ],
        "gaps": [
            "Didn't mention how you'd validate or measure the outcome",
            "Could have briefly acknowledged alternative approaches you considered",
        ],
        "improvement_suggestions": [
            "Always close design answers with: 'Here's how I'd measure if this worked'",
            "Mention one alternative you explicitly rejected and why — shows deeper thinking",
            "Practice the STAR format for the delivery: it makes complex answers easier to follow",
        ],
    },
    {
        "score": 5.0,
        "feedback": (
            "The answer touches the right areas but stays too shallow. You listed concepts "
            "without explaining the 'why' behind them. In a technical interview, a surface-level "
            "answer like this will prompt the interviewer to dig deeper — and if you can't go "
            "deeper, that's a red flag. Focus on explaining trade-offs, not just naming things."
        ),
        "strengths": [
            "Identified the correct concepts relevant to the question",
            "Answer stayed on topic without going off on tangents",
        ],
        "gaps": [
            "No trade-off analysis — just listed options without comparing them",
            "No evidence of hands-on experience with this area",
        ],
        "improvement_suggestions": [
            "For every concept you name, add: 'and the trade-off is...'",
            "Build a small project that applies this concept so you have concrete experience",
            "Practice explaining this to a non-technical person — forces you to understand it deeply",
        ],
    },
    {
        "score": 9.0,
        "feedback": (
            "Outstanding answer. You demonstrated mastery by covering not just the what "
            "and how, but the why — including nuanced trade-offs, real constraints, and "
            "how context changes the right answer. Few candidates get to this level of "
            "depth unprompted. Only minor gap: didn't mention team/communication aspects."
        ),
        "strengths": [
            "Showed mastery by covering nuanced trade-offs most candidates miss",
            "Grounded the answer in real constraints rather than ideal scenarios",
            "Structured response made a complex topic easy to follow",
        ],
        "gaps": [
            "Didn't address how you'd bring the team along on this decision",
            "Could mention what you'd document for future maintainers",
        ],
        "improvement_suggestions": [
            "Add a sentence on stakeholder communication — how do you explain this to non-engineers?",
            "Consider what you'd write in the ADR (Architecture Decision Record)",
            "This answer is strong — focus on consistency across all questions now",
        ],
    },
]

DEMO_TRANSCRIPTION = (
    "This is a demo transcription. In live mode with an OpenAI API key, "
    "your voice answer would be transcribed here by Whisper."
)


def get_demo_questions() -> dict:
    """Return the full demo question set."""
    return {
        "technical": list(DEMO_QUESTIONS["technical"]),
        "behavioral": list(DEMO_QUESTIONS["behavioral"]),
    }


def get_demo_evaluation() -> dict:
    """Return a randomly sampled realistic evaluation."""
    return dict(random.choice(_DEMO_EVAL_POOL))
