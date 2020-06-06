from flask_wtf import FlaskForm
from wtforms import HiddenField
from wtforms.validators import DataRequired, Regexp

class OverrideForm(FlaskForm):
    override = HiddenField('override')