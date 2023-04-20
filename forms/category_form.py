from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class CategoryEditForm(FlaskForm):
    id_category = IntegerField("Id category", validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired()])
    submit = SubmitField("Submit")


class CategoryAddForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    submit = SubmitField("Submit")
