from flask import Flask, render_template, request
from question_generator import generate_questions
from evaluator import evaluate_answer

app = Flask(__name__, template_folder='../templates')

@app.route('/', methods=['GET', 'POST'])
def index():
    questions = None
    evaluation = None
    error = None
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'generate':
            resume = request.form.get('resume', '')
            job_description = request.form.get('job_description', '')
            result = generate_questions(resume, job_description)
            
            if 'error' in result:
                error = result['error']
            else:
                questions = result
                
        elif action == 'evaluate':
            answer = request.form.get('answer', '')
            evaluation = evaluate_answer(answer)
            if 'score' in evaluation and evaluation['score'] == 'Error':
                error = evaluation['feedback']
            
    return render_template('index.html', questions=questions, evaluation=evaluation, error=error)

if __name__ == '__main__':
    app.run(debug=True)
