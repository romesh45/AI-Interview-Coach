from flask import Flask, render_template, request
from question_generator import generate_questions
from evaluator import evaluate_answer

app = Flask(__name__, template_folder='../templates')

@app.route('/', methods=['GET', 'POST'])
def index():
    questions = []
    evaluation = None
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'generate':
            resume = request.form.get('resume', '')
            job_description = request.form.get('job_description', '')
            questions = generate_questions(resume, job_description)
            
        elif action == 'evaluate':
            answer = request.form.get('answer', '')
            evaluation = evaluate_answer(answer)
            
    return render_template('index.html', questions=questions, evaluation=evaluation)

if __name__ == '__main__':
    app.run(debug=True)
