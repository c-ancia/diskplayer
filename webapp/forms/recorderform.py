from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp

class RecorderForm(FlaskForm):
    uri = StringField('Spotify URL', validators=[DataRequired(), Regexp("^((https://open.spotify.com/(album|playlist)/[a-zA-Z0-9]+)|(spotify:(album|playlist):[a-zA-Z0-9]+))$", message="Invalid URL.")])
    save = SubmitField('Record disk')