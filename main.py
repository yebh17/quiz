#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for, current_app
import threading

app = Flask(__name__, static_url_path='/static')

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
answers = []
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

def start_timer():
    global timer
    timer = threading.Timer(20.0, timeout)
    timer.start()

@app.route('/question', methods=['GET', 'POST'])
def question():
    global current_question, timer

    if current_question >= len(questions):
        if timer:
            timer.cancel()
        return render_template('thankyou.html', total_questions=len(questions), num_correct=calculate_num_correct(), num_incorrect=calculate_num_incorrect(), answers=answers)

    if timer and not timer.is_alive():
        answer_details = {
            'question': questions[current_question]['question'],
            'selected_option': None,
            'correct_option': questions[current_question]['answer'],
            'result': "TIMEOUT",
            'timeout': True
        }
        answers.append(answer_details)  # Store the answer details
        current_question += 1

        if current_question >= len(questions):
            if timer:
                timer.cancel()
            return render_template('thankyou.html', total_questions=len(questions), num_correct=calculate_num_correct(), num_incorrect=calculate_num_incorrect(), answers=answers)

        return render_template('question.html', question=questions[current_question]['question'], options=questions[current_question]['options'])

    if request.method == 'POST':
        if 'answer' in request.form:
            answer = request.form['answer']
            correct_answer = questions[current_question]['answer']
            question_text = questions[current_question]['question']
            answer_details = {
                'question': question_text,
                'selected_option': answer,
                'correct_option': correct_answer
            }

            if answer == correct_answer:
                answer_details['result'] = "CORRECT ANSWER"
            else:
                answer_details['result'] = "INCORRECT ANSWER"

            answers.append(answer_details)  # Store the answer details

            current_question += 1

            if current_question >= len(questions):
                if timer:
                    timer.cancel()
                return render_template('thankyou.html', total_questions=len(questions), num_correct=calculate_num_correct(), num_incorrect=calculate_num_incorrect(), answers=answers)

            return render_template('question.html', question=questions[current_question]['question'], options=questions[current_question]['options'])

    question_data = questions[current_question]
    options = question_data['options']

    if timer and timer.is_alive():
        timer.cancel()

    start_timer()

    return render_template('question.html', question=question_data['question'], options=options)

def timeout():
    with app.app_context():
        global current_question, timer
        current_question += 1

        if current_question <= len(questions):
            question_text = questions[current_question - 1]['question']
            answer_details = {
                'question': question_text,
                'selected_option': 'None',
                'correct_option': questions[current_question - 1]['answer'],
                'result': 'TIMEOUT',
                'timeout': True
            }
            answers.append(answer_details)

        if current_question < len(questions):
            if timer and timer.is_alive():
                timer.cancel()
            start_timer()
        elif current_question == len(questions):
            if timer and timer.is_alive():
                timer.cancel()

def calculate_num_correct():
    num_correct = 0
    for answer in answers:
        if answer['result'] == "CORRECT ANSWER":
            num_correct += 1
    return num_correct

def calculate_num_incorrect():
    num_incorrect = 0
    for answer in answers:
        if answer['result'] == "INCORRECT ANSWER":
            num_incorrect += 1
    return num_incorrect

@app.route('/reset')
def reset():
    global current_question, timer
    current_question = 0
    if timer is not None and timer.is_alive():
        timer.cancel()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='192.168.1.90', port=8080, debug=True)