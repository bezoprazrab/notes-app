


import bcrypt
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash  # для совместимости, но будем использовать bcrypt явно

from config import Config
from models import db, User, Note
from forms import RegistrationForm, LoginForm, NoteForm

from sqlalchemy import text


from flask import abort, flash, redirect, render_template, url_for
from sqlalchemy import text

x=5

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- Хелперы bcrypt ---
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


# --- Маршруты ---

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("base.html", title="Главная")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Пользователь с таким именем уже существует", "danger")
            return render_template("register.html", form=form)

        hashed = hash_password(form.password.data)
        user = User(username=form.username.data, password_hash=hashed)
        db.session.add(user)
        db.session.commit()
        flash("Аккаунт создан. Теперь войдите.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form, title="Регистрация")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and verify_password(form.password.data, user.password_hash):
            login_user(user)
            next_page = request.args.get("next")
            flash("Вы вошли в систему", "success")
            return redirect(next_page or url_for("dashboard"))
        else:
            flash("Неверное имя пользователя или пароль", "danger")
    return render_template("login.html", form=form, title="Вход")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    # Только свои заметки — защита от чужих
    notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.created_at.desc()).all()
    return render_template("dashboard.html", notes=notes, title="Мои заметки")


@app.route("/notes/new", methods=["GET", "POST"])
@login_required
def new_note():
    form = NoteForm()
    if form.validate_on_submit():
        note = Note(
            title=form.title.data.strip(),
            content=form.content.data.strip(),
            user_id=current_user.id
        )
        db.session.add(note)
        db.session.commit()
        flash("Заметка создана", "success")
        return redirect(url_for("dashboard"))
    return render_template("note_form.html", form=form, title="Новая заметка")


@app.route("/notes/<int:note_id>/edit", methods=["GET", "POST"])
@login_required
def edit_note(note_id):
    # Защита от IDOR: заметка должна принадлежать текущему пользователю
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    form = NoteForm(obj=note)
    if form.validate_on_submit():
        # Санитизация: strip() убирает лишние пробелы
        note.title = form.title.data.strip()
        note.content = form.content.data.strip()
        db.session.commit()
        flash("Заметка обновлена", "success")
        return redirect(url_for("dashboard"))
    return render_template("note_form.html", form=form, note=note, title="Редактирование заметки")






# from flask import abort, flash, redirect, render_template, url_for
# from sqlalchemy import text

# @app.route("/notes/<int:note_id>/edit", methods=["GET", "POST"])
# @login_required
# def edit_note(note_id):
#     form = NoteForm()
#     if form.validate_on_submit():
#         title = form.title.data.strip()
#         content = form.content.data.strip()

#         query = f"UPDATE note SET title = '{title}', content = '{content}' WHERE id = {note_id} AND user_id = {current_user.id}"
#         result=db.session.execute(text(query))

#         print(result.rowcount)
        
#         if result.rowcount == 0:
#             flash("Заметка не найдена или не принадлежит вам", "danger")
#             return redirect(url_for("dashboard"))

#         db.session.commit()
#         flash("Заметка обновлена", "success")
#         return redirect(url_for("dashboard"))

    

#     if not form.is_submitted():
#         # Это GET-запрос
#         note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
#         form.title.data = note.title
#         form.content.data = note.content
#     else:
#         # Это POST запрос
#         flash("Исправьте ошибки в форме и попробуйте снова", "danger")

#     return render_template("note_form.html", form=form, title="Редактирование заметки")









@app.route("/notes/<int:note_id>/delete", methods=["POST"])
@login_required
def delete_note(note_id):
    # Защита от IDOR
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    db.session.delete(note)
    db.session.commit()
    flash("Заметка удалена", "info")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # создаст таблицы при первом запуске
    app.run()
