from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    login = StringField("Login",
                        validators=[DataRequired(), Length(
                            min=5, max=10, message="Incorrect length. Login length must be between 5 and 10 symbols")])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Submit")
