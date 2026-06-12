from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, TextAreaField, DecimalField, IntegerField,
                     SelectField, BooleanField, SubmitField, FieldList, FormField)
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ProductImageForm(FlaskForm):
    class Meta:
        csrf = False

    image = FileField('Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'])])
    alt_text = StringField('Alt Text', validators=[Optional(), Length(max=300)])
    is_primary = BooleanField('Primary Image')


class ProductVariantForm(FlaskForm):
    class Meta:
        csrf = False

    size = StringField('Size', validators=[DataRequired(), Length(max=20)])
    color = StringField('Color', validators=[DataRequired(), Length(max=50)])
    sku = StringField('SKU', validators=[DataRequired(), Length(max=100)])
    stock_quantity = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)], default=0)
    is_active = BooleanField('Active', default=True)


class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(min=2, max=300)])
    short_description = StringField('Short Description', validators=[Optional(), Length(max=500)])
    description = TextAreaField('Full Description', validators=[Optional()])
    price = DecimalField('Price (₹)', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    compare_at_price = DecimalField('Compare at Price (₹)', validators=[Optional(), NumberRange(min=0)], places=2)
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    brand = StringField('Brand', validators=[Optional(), Length(max=100)])
    gender = SelectField('Gender', choices=[
        ('', 'Select Gender'),
        ('kids', 'Kids (Unisex)'),
        ('girls', 'Girls'),
    ], validators=[Optional()])
    age_group = SelectField('Age Group', choices=[
        ('', 'Select Age Group'),
        ('0-2', '0–2 Years'),
        ('2-4', '2–4 Years'),
        ('4-6', '4–6 Years'),
        ('6-8', '6–8 Years'),
        ('8-12', '8–12 Years'),
    ], validators=[Optional()])
    material = StringField('Material', validators=[Optional(), Length(max=200)])
    care_instructions = TextAreaField('Care Instructions', validators=[Optional()])
    is_active = BooleanField('Active', default=True)
    is_featured = BooleanField('Featured')
    is_trending = BooleanField('Trending')
    submit = SubmitField('Save Product')


class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    parent_id = SelectField('Parent Category', coerce=int, validators=[Optional()])
    image = FileField('Category Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'])])
    is_active = BooleanField('Active', default=True)
    sort_order = IntegerField('Sort Order', default=0, validators=[Optional()])
    submit = SubmitField('Save Category')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_id.choices = [(0, 'None (Top Level)')]
