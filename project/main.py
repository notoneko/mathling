from flask import Blueprint, render_template, send_from_directory, request, abort, send_file
from . import db
from flask_login import login_required, current_user
from .models import Lesson, UserLessons
from werkzeug.utils import secure_filename
import os

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/lessons', methods=['GET', 'POST'])
@login_required
def lessons():
    lessons = Lesson.query.all()
    lesson_cards = []
    for i in range(0, len(lessons), 2):
        row = []
        for j in range(2):
            if i+j < len(lessons):
                lesson = lessons[i+j]
                row.append({
                    'lesson_number': lesson.lesson_number,
                    'lesson_pdf': lesson.lesson_pdf,
                    'task': lesson.task,
                    'is_done': lesson.is_task_done(current_user)
                })
        lesson_cards.append(row)
    return render_template('lessons.html', lesson_cards=lesson_cards)


@main.route('/lessons/<int:lesson_number>/slides')
@login_required
def serve_lesson_pdf(lesson_number):
    lesson = Lesson.query.filter_by(lesson_number=lesson_number).first()
    if lesson and lesson.lesson_pdf:
        directory = os.path.join('static', 'lessons', str(lesson_number), 'lesson_pdf')
        filename = os.path.basename(lesson.lesson_pdf)
        return send_from_directory(directory, filename)
    else:
        return "Lesson not found or PDF file not available"


@main.route('/lessons/<int:lesson_number>/additional_files/<path:file_name>')
@login_required
def download_additional_file(lesson_number, file_name):
    lesson = Lesson.query.filter_by(lesson_number=lesson_number).first()
    if not lesson:
        abort(404)
    file_path = os.path.join('static', file_name)
    return send_file(file_path, as_attachment=True)


@main.route('/lessons/<int:lesson_number>/task', methods=['GET', 'POST'])
@login_required
def render_file_as_template(lesson_number):
    lesson = Lesson.query.filter_by(lesson_number=lesson_number).first()
    if lesson and lesson.task is not None:
        if request.method == 'POST':
            link_to_github = request.form.get('link_to_github')
            if link_to_github:
                user_task = UserLessons.query.filter_by(user_id=current_user.id, lesson_number=lesson.lesson_number).first()
                if user_task:
                    user_task.link_to_github = link_to_github
                else:
                    user_task = UserLessons(user_id=current_user.id, lesson_number=lesson.lesson_number, link_to_github=link_to_github)
                    db.session.add(user_task)
                db.session.commit()
        file_path = os.path.join('project', 'static', lesson.task)
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
        return render_template('task.html', content=file_content, lesson_number=lesson_number, lesson=lesson)
    else:
        return "Lesson not found or task file not available"





