from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, TextAreaField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired


class ItemAddForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    id_category = IntegerField("Id category", validators=[DataRequired()])
    description = TextAreaField("Product description", default='No description')
    cost = IntegerField("Product price", default=0)
    image = FileField("File", validators=[FileAllowed(["png", "jpg", "jpeg"], 'Images only')])
    submit = SubmitField()


class ItemEditForm(FlaskForm):
    id_item = IntegerField("Id item", validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired()])
    id_category = IntegerField("Id category", validators=[DataRequired()])
    path_previous_image = IntegerField('path_previous_image')
    description = TextAreaField("Product description", default='No description')
    cost = IntegerField("Product price", default=0)
    image = FileField("File", validators=[FileAllowed(["png", "jpg", "jpeg"], 'Images only')])
    submit = SubmitField()
