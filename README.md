# AI Interview Coach

A complete, production-grade Flask application utilizing the OpenAI API to conduct mock interviews. It takes a resume and job description to auto-generate deeply tailored interview questions and evaluates user answers in real time with actionable, professional feedback via AI.

## Project Structure
- `src/app.py`: Main Flask application handling UI state and routing.
- `src/question_generator.py`: Generates structured technical and behavioral questions via OpenAI JSON.
- `src/evaluator.py`: Evaluates answers, assigning a score out of 10 with strengths, gaps, and improvements.
- `src/prompts.py`: Houses strict, schema-enforced prompt templates for `gpt-5.4-mini`.
- `templates/index.html`: Clean, responsive UI with loading states and session management.

## Setup Instructions
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure environment:
   Open the `.env` file (or create one) and set your key:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   SECRET_KEY=your_flask_secret_key
   ```
3. Run the application locally:
   ```bash
   flask --app src/app run
   ```
4. Access the web app at `http://127.0.0.1:5000`

## Features Implemented Under Phase 5 (Polish)
- Native rendering of JSON Arrays for Strengths, Gaps, and Improvement Suggestions.
- Strict `gpt-5.4-mini` integration with fallback parsing and validation errors gracefully returning to the UI to prevent panics and unhandled exceptions.
- Embedded colorized CSS badges mapping dynamically generated `skill` and `difficulty` question attributes.
