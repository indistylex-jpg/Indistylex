from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, RadioField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional


INDIAN_STATES = [
    ('', 'Select State'),
    ('AN', 'Andaman and Nicobar Islands'), ('AP', 'Andhra Pradesh'),
    ('AR', 'Arunachal Pradesh'), ('AS', 'Assam'), ('BR', 'Bihar'),
    ('CH', 'Chandigarh'), ('CT', 'Chhattisgarh'), ('DN', 'Dadra and Nagar Haveli'),
    ('DD', 'Daman and Diu'), ('DL', 'Delhi'), ('GA', 'Goa'), ('GJ', 'Gujarat'),
    ('HR', 'Haryana'), ('HP', 'Himachal Pradesh'), ('JK', 'Jammu and Kashmir'),
    ('JH', 'Jharkhand'), ('KA', 'Karnataka'), ('KL', 'Kerala'), ('LA', 'Ladakh'),
    ('LD', 'Lakshadweep'), ('MP', 'Madhya Pradesh'), ('MH', 'Maharashtra'),
    ('MN', 'Manipur'), ('ML', 'Meghalaya'), ('MZ', 'Mizoram'), ('NL', 'Nagaland'),
    ('OR', 'Odisha'), ('PY', 'Puducherry'), ('PB', 'Punjab'), ('RJ', 'Rajasthan'),
    ('SK', 'Sikkim'), ('TN', 'Tamil Nadu'), ('TG', 'Telangana'), ('TR', 'Tripura'),
    ('UP', 'Uttar Pradesh'), ('UT', 'Uttarakhand'), ('WB', 'West Bengal'),
]


class ShippingAddressForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=200)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address_line1 = StringField('Address Line 1', validators=[DataRequired(), Length(max=500)])
    address_line2 = StringField('Address Line 2', validators=[Optional(), Length(max=500)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    state = SelectField('State', choices=INDIAN_STATES, validators=[DataRequired()])
    postal_code = StringField('PIN Code', validators=[DataRequired(), Length(min=6, max=6)])
    notes = TextAreaField('Order Notes', validators=[Optional(), Length(max=500)])
    payment_method = RadioField('Payment Method', choices=[
        ('cod', 'Cash on Delivery'),
        ('online', 'Online Payment (UPI / Card / NetBanking)'),
    ], default='cod', validators=[DataRequired()])
    submit = SubmitField('Place Order')


class GuestCheckoutForm(ShippingAddressForm):
    """Same as shipping form but for guest users."""
    pass


class CouponForm(FlaskForm):
    code = StringField('Coupon Code', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Apply')
