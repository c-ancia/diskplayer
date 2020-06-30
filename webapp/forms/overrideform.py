from flask_wtf import FlaskForm
from wtforms import HiddenField

class OverrideForm(FlaskForm):
    override = HiddenField('override')