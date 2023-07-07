from flask import Flask, render_template, request, redirect, url_for
from threading import Timer

app = Flask(__name__)

# Global variables
questions = [
    {
        'question': 'What is the capital of France?',
        'options': ['London', 'Paris', 'Berlin', 'Rome'],
        'answer': 'Paris'
    },
    {
        'question': 'Which planet is known as the Red Planet?',
        'options': ['Venus', 'Mars', 'Jupiter', 'Saturn'],
        'answer': 'Mars'
    },
    # Add more questions here
]

current_question = 0
timer = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    global current_question, timer

    if request.method == 'POST':
        if 'start' in request.form:
            return redirect(url_for('rules'))

    return render_template('quiz.html')

@app.route('/rules', methods=['GET', 'POST'])
def rules():
    global current_question, timer

    if request.method == 'POST':
        if 'next' in request.form:
            return redirect(url_for('round'))

    return render_template('rules.html')

@app.route('/round', methods=['GET', 'POST'])
def round():
    global current_question, timer

    if request.method == 'POST':
        if 'next' in request.form:
            current_question = 0
            return redirect(url_for('question'))

    return render_template('round.html')

@app.route('/question', methods=['GET', 'POST'])
def question():
    global current_question, timer

    if current_question >= len(questions):
        return render_template('thankyou.html')

    if request.method == 'POST':
        if 'answer' in request.form:
            answer = request.form['answer']
            correct_answer = questions[current_question]['answer']
            if answer == correct_answer:
                message = "CORRECT ANSWER"
            else:
                message = "INCORRECT ANSWER"

            current_question += 1

            if current_question >= len(questions):
                return render_template('thankyou.html')

            return render_template('question.html', question=questions[current_question]['question'], options=questions[current_question]['options'], message=message)

    question_data = questions[current_question]
    options = question_data['options']

    timer = Timer(20.0, timeout)
    timer.start()

    return render_template('question.html', question=question_data['question'], options=options)

def timeout():
    global current_question, timer
    current_question += 1
    return redirect('/question')

@app.route('/reset')
def reset():
    global current_question, timer
    current_question = 0
    if timer is not None and timer.is_alive():
        timer.cancel()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
