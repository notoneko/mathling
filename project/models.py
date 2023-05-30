from flask_login import UserMixin
from . import db
from secure_filename import secure_filename
import os


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    is_admin = db.Column(db.Boolean, default=False)
    user_lessons_relationship = db.relationship('UserLessons', backref='user')

    def __repr__(self):
        return f'<User {self.nickname}>'


class Lesson(db.Model):
    __tablename__ = 'lessons'
    id = db.Column(db.Integer, primary_key=True)
    lesson_number = db.Column(db.Integer, unique=True)
    lesson_pdf = db.Column(db.String(100))
    task = db.Column(db.String(500))
    additional_files = db.Column(db.String(500))
    user_homeworks = db.relationship('UserLessons', lazy='dynamic')

    def save_lesson_pdf(self, file):
        if file:
            filename = secure_filename(file.filename)
            directory_name = os.path.join('lessons', str(self.lesson_number), 'lesson_pdf')
            full_directory_name = os.path.join('project', 'static', directory_name)
            if not os.path.exists(full_directory_name):
                os.makedirs(full_directory_name)
            file_path = os.path.join(directory_name, filename)
            file.save(os.path.join(full_directory_name, filename))
            self.lesson_pdf = file_path
        else:
            return 0

    def delete_lesson_pdf(self):
        if self.lesson_pdf:
            full_directory_name = os.path.join('project', 'static', self.lesson_pdf)
            if os.path.exists(full_directory_name):
                os.remove(full_directory_name)
                self.lesson_pdf = None
        else:
            return 0

    def save_task(self, file):
        if file:
            filename = secure_filename(file.filename)
            directory_name = os.path.join('lessons', str(self.lesson_number), 'task')
            full_directory_name = os.path.join('project', 'static', directory_name)
            if not os.path.exists(full_directory_name):
                os.makedirs(full_directory_name)
            file_path = os.path.join(directory_name, filename)
            file.save(os.path.join(full_directory_name, filename))
            self.task = file_path
        else:
            return 0

    def delete_task(self):
        if self.task:
            full_directory_name = os.path.join('project', 'static', self.task)
            if os.path.exists(full_directory_name):
                os.remove(full_directory_name)
                self.task = None
        else:
            return 0

    def save_additional_files(self, files):
        if not files or not any(f for f in files):
            return 0
        directory_name = os.path.join('lessons', str(self.lesson_number), 'additional_files')
        full_directory_name = os.path.join('project', 'static', directory_name)
        if not os.path.exists(full_directory_name):
            os.makedirs(full_directory_name)
        for file in files:
            filename = secure_filename(file.filename)
            file_path = os.path.join(directory_name, filename)
            file.save(os.path.join(full_directory_name, filename))
            if self.additional_files is None or self.additional_files == '':
                self.additional_files = file_path
            else:
                self.additional_files = self.additional_files + ' -|- ' + file_path

    def delete_additional_file(self, file):
        if self.additional_files:
            directory_name = os.path.join('project', 'static')
            existing_filenames = self.additional_files.split(' -|- ')
            full_directory_name = os.path.join(directory_name, file)
            if os.path.exists(full_directory_name):
                os.remove(full_directory_name)
            existing_filenames.remove(file)
            if len(existing_filenames) == 1:
                self.additional_files = existing_filenames[0]
            else:
                self.additional_files = ' -|- '.join(existing_filenames)
        else:
            return 0

    def is_task_done(self, user):
        user_lesson = UserLessons.query.filter_by(user=user, lesson_number=self.lesson_number).first()
        if user_lesson:
            return user_lesson.is_done
        return False

class UserLessons(db.Model):
    __tablename__ = 'user_lessons'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_number = db.Column(db.Integer, db.ForeignKey('lessons.lesson_number'), nullable=False, unique=True)
    link_to_github = db.Column(db.String(256))
    is_done = db.Column(db.Boolean, default=False)

    user_relationship = db.relationship('User', backref='user_lessons')


