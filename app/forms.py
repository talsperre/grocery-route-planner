from markupsafe import Markup
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, Form
from wtforms import BooleanField, FieldList, FormField, SelectField
from wtforms.widgets import CheckboxInput

from wtforms.validators import DataRequired


class LocationForm(FlaskForm):
    location = StringField('Location')
    location_submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    search = StringField('Search')
    search_submit = SubmitField('Go')


class CheckboxForm(Form):
    checkbox = BooleanField(default=True)


class SelectForm(FlaskForm):
    checkboxes = FieldList(FormField(CheckboxForm))
    item_submit = SubmitField('Submit')


class OptimizeForm(FlaskForm):
    optimize_type = SelectField('Optimize Type', choices=[('Lowest Price'), ('Minimum Distance')])
    optimize_submit = SubmitField('Find Routes')

