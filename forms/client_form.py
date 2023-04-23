from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, BooleanField
from wtforms.validators import DataRequired


class EditClientForm(FlaskForm):
    id_client = IntegerField("id client", validators=[DataRequired()])
    bool_admin = BooleanField("Admin", default=False, validators=[DataRequired()])
    submit = SubmitField("submit")
