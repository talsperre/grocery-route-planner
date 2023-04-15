from markupsafe import Markup
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class LocationForm(FlaskForm):
    location = StringField('Location')
    location_submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    text = Markup('<i class="fa-solid fa-shopping-cart"></i>')
    item = StringField('Item')
    item_submit = SubmitField('Go')
