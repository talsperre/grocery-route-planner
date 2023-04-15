from markupsafe import Markup
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class LocationForm(FlaskForm):
    location = StringField('Location')
    location_submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    search = StringField('Search')
    search_submit = SubmitField('Go')


class ItemForm(FlaskForm):
    item = StringField('Item')
    item_submit = SubmitField('Go')
