from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, EmailField, StringField, IntegerField
from wtforms.validators import DataRequired, Length


class CheckPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired(
        message="Input your previous password")])
    submit = SubmitField("Submit")


class ChangePasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired(
        message='Input new password'
    ), Length(min=5, max=20, message="Password length must be between 5 and 20 symbols")])
    repeat_password = PasswordField("Repeat password", validators=[DataRequired(
        message='Repeat your password'
    ), Length(min=5, max=20, message="Password length must be between 5 and 20 symbols")])
    submit = SubmitField('Submit')


class CheckEmail(FlaskForm):
    verification_code = IntegerField('Enter the code that was sent to your new email')


class ChangePhoneNumberForm(FlaskForm):
    pass
