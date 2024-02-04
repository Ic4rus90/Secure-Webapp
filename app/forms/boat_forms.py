from flask_wtf import FlaskForm
from wtforms import RadioField, TextAreaField, StringField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange, URL

"""
Contains forms related to boats
"""


class AddReviewForm(FlaskForm):
    stars = RadioField('Stars', default=3, choices=[(5, '5'), (4, '4'), (3, '3'), (2, '2'), (1, '1')], validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=1, max=1000)])


class AddBoatForm(FlaskForm):
    boat_type = StringField('Boat Type', validators=[DataRequired(), Length(min=1, max=40)])
    make = StringField('Make', validators=[DataRequired(), Length(min=1, max=50)])
    length = IntegerField('Length', validators=[DataRequired(), NumberRange(min=1, max=1000)])
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=1800, max=2023)])
    engine_make = StringField('Engine Make', validators=[DataRequired(), Length(min=1, max=50)])
    engine_hp = IntegerField('Engine HP', validators=[DataRequired(), NumberRange(min=1, max=100000)])
    price = IntegerField('Price', validators=[DataRequired(), NumberRange(min=1, max=1000000000)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=1, max=1000)])
    image_url = StringField('Image URL', validators=[DataRequired(), URL()])

