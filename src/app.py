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
            question = request.form.get('question', '')
            answer = request.form.get('answer', '')
            result = evaluate_answer(question, answer)
            
            if 'error' in result:
                error = result['error']
                # we still want to show the partial fallback evaluation object if it has score/feedback
                if 'score' in result:
                    evaluation = result
            else:
                evaluation = result
            
    return render_template('index.html', questions=questions, evaluation=evaluation, error=error)

if __name__ == '__main__':
    app.run(debug=True)
