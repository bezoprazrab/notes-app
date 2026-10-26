




from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError


class RegistrationForm(FlaskForm):
    username = StringField("Имя пользователя", validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField("Пароль", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Подтвердите пароль", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Зарегистрироваться")


class LoginForm(FlaskForm):
    username = StringField("Имя пользователя", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Войти")


class NoteForm(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired(), Length(max=120)])
    content = TextAreaField("Содержание", validators=[DataRequired()])
    submit = SubmitField("Сохранить")
