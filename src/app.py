import os
from flask import Flask, render_template, request, session, redirect, url_for
from question_generator import generate_questions
from evaluator import evaluate_answer

app = Flask(__name__, template_folder='../templates')
app.secret_key = os.environ.get('SECRET_KEY', 'default-secret-key-123')

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    
    # Initialize session state if not present
    if 'questions' not in session:
        session['questions'] = None
    if 'evaluations' not in session:
        session['evaluations'] = {}
        
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'generate':
            resume = request.form.get('resume', '')
            job_description = request.form.get('job_description', '')
            result = generate_questions(resume, job_description)
            
            if 'error' in result:
                error = result['error']
            else:
                session['questions'] = result
                session['evaluations'] = {} # Reset evaluations for new questions
                session.modified = True
                
        elif action == 'evaluate':
            question = request.form.get('question', '')
            answer = request.form.get('answer', '')
            
            result = evaluate_answer(question, answer)
            if 'error' in result:
                error = result['error']
            
            # Save evaluation keyed by question to preserve multiple answers
            evals = session.get('evaluations', {})
            evals[question] = {
                'answer': answer,
                'evaluation': result
            }
            session['evaluations'] = evals
            session.modified = True
            
        elif action == 'reset':
            session.clear()
            return redirect(url_for('index'))
            
    return render_template(
        'index.html',
        questions=session.get('questions'),
        evaluations=session.get('evaluations'),
        error=error
    )

if __name__ == '__main__':
    app.run(debug=True)
