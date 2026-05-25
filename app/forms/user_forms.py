from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from app.forms.checkout_forms import INDIAN_STATES


class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Update Profile')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters.'),
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match.'),
    ])
    submit = SubmitField('Change Password')


class AddressForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=200)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=20)])
    address_line1 = StringField('Address Line 1', validators=[DataRequired(), Length(max=500)])
    address_line2 = StringField('Address Line 2', validators=[Optional(), Length(max=500)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    state = SelectField('State', choices=INDIAN_STATES, validators=[DataRequired()])
    postal_code = StringField('PIN Code', validators=[DataRequired(), Length(min=6, max=6)])
    is_default = BooleanField('Set as default address')
    submit = SubmitField('Save Address')
