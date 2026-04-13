from flask import Flask, render_template

from evaluator import evaluate_answer
from question_generator import generate_questions


app = Flask(__name__)


@app.route("/")
def index():
    sample_questions = generate_questions("", "")
    sample_evaluation = evaluate_answer("", "")
    return render_template(
        "index.html",
        questions=sample_questions,
        evaluation=sample_evaluation,
    )


if __name__ == "__main__":
    app.run(debug=True)
