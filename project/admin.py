from flask import Blueprint, render_template, abort, redirect, url_for, request, flash
from functools import wraps
from .models import Lesson, UserLessons
from . import db
from flask_login import current_user

admin = Blueprint('admin', __name__)


def admin_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return view(**kwargs)
    return wrapped_view


@admin.route('/lessons/add')
@admin_required
def add_lesson():
    return render_template('add_lesson.html')


@admin.route('/lessons/add', methods=['POST'])
@admin_required
def add_lesson_post():
    lesson_number = request.form.get('lesson_number')

    lesson = Lesson.query.filter_by(lesson_number=lesson_number).first()

    if lesson:
        return redirect(url_for('admin.edit_lesson_post', lesson_number=lesson_number))

    new_lesson = Lesson(lesson_number=lesson_number)
    if 'lesson_pdf' in request.files:
        lesson_pdf_path = request.files['lesson_pdf']
        new_lesson.save_lesson_pdf(lesson_pdf_path)
    if 'task' in request.files:
        task_path = request.files['task']
        new_lesson.save_task(task_path)
    if 'additional_files' in request.files:
        additional_files = request.files.getlist('additional_files')
        new_lesson.save_additional_files(additional_files)
    db.session.add(new_lesson)
    db.session.commit()

    return render_template('add_lesson.html')


@admin.route('/lessons/edit', methods=['GET', 'POST'])
@admin_required
def get_lesson_by_number():
    lessons = Lesson.query.all()
    return render_template('edit_lesson.html', lessons=lessons)
    return redirect(url_for('admin.edit_lesson_post', lesson_number=lesson_number))


@admin.route('/lessons/edit/<int:lesson_number>', methods=['GET', 'POST'])
@admin_required
def edit_lesson_post(lesson_number):
    lesson = Lesson.query.filter_by(lesson_number=lesson_number).first()
    if request.method == 'POST':
        if 'lesson_pdf' in request.files:
            lesson_pdf_path = request.files['lesson_pdf']
            if lesson_pdf_path:
                lesson.delete_lesson_pdf()
                lesson.save_lesson_pdf(lesson_pdf_path)
        if 'task' in request.files:
            task_path = request.files['task']
            if task_path:
                lesson.delete_task()
                lesson.save_task(task_path)
        if 'additional_files' in request.files:
            additional_files = request.files.getlist('additional_files')
            if additional_files or any(f for f in additional_files):
                lesson.save_additional_files(additional_files)

        if 'delete_additional_files[]' in request.form:
            files_to_delete = request.form.getlist('delete_additional_files[]')
            for file in files_to_delete:
                lesson.delete_additional_file(file)

        db.session.commit()
        return redirect(url_for('main.lessons'))
    return render_template('edit_lesson_bynumber.html', lesson=lesson)


@admin.route('/lessons/check', methods=['POST', 'GET'])
@admin_required
def check_lesson_post():
    lesson_cards = []

    def get_pending_user_lessons():
        return UserLessons.query.filter_by(is_done=False).all()

    pending_user_lessons = get_pending_user_lessons()

    row = []
    for user_lesson in pending_user_lessons:
        row.append({
            'name': user_lesson.user.name,
            'lesson_number': user_lesson.lesson_number,
            'user_lesson_id': user_lesson.id,
            'user_link': user_lesson.link_to_github
        })
        if len(row) == 2:
            lesson_cards.append(row)
            row = []
    if row:
        lesson_cards.append(row)

    return render_template('check_lessons.html', lesson_cards=lesson_cards)


@admin.route('/lessons/mark_done/<int:user_lesson_id>', methods=['POST'])
@admin_required
def mark_user_lesson_done(user_lesson_id):
    user_lesson = UserLessons.query.get(user_lesson_id)
    if user_lesson:
        user_lesson.is_done = True
        db.session.commit()

    return redirect(url_for('admin.check_lesson_post'))
