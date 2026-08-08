from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from app.models.expense import EXPENSE_CATEGORIES


class ExpenseForm(FlaskForm):
    expense_date = DateField('Date', validators=[DataRequired()])
    category = SelectField(
        'Category',
        choices=EXPENSE_CATEGORIES,
        validators=[DataRequired()],
    )
    description = StringField('Description', validators=[DataRequired(), Length(min=2, max=300)])
    amount = DecimalField('Amount (₹)', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    payment_method = SelectField('Payment Method', choices=[
        ('cash', 'Cash'),
        ('upi', 'UPI'),
        ('bank', 'Bank Transfer'),
        ('card', 'Card'),
    ], validators=[DataRequired()])
    reference = StringField('Reference / Invoice #', validators=[Optional(), Length(max=100)])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Expense')
