from flask_wtf import FlaskForm
from wtforms import Form, StringField, IntegerField, FloatField, SelectField,SubmitField,PasswordField,DateField
from wtforms.validators import DataRequired, NumberRange,Email,Optional,EqualTo,Length
class Contact(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])

    email = StringField('Email', validators=[DataRequired(), Email()])
    message = StringField('Message', validators=[DataRequired()])
    submit = SubmitField('Submit')


class Login(FlaskForm):
    Email = StringField("Email", validators=[Optional(), Email()])
    phone_number = StringField("Phone Number", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])  # Use PasswordField
    submit = SubmitField("Login")

class Register(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    Email = StringField("Email", validators=[Email(), Optional()])
    phone_number = StringField("Phone Number", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])  # Use PasswordField
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')  # Use EqualTo, not equal_to
    ])
    submit = SubmitField("Register")





class FarmerForm(FlaskForm):
    name=StringField('Name', validators=[DataRequired()])
    Email=StringField("Email",validators=[Optional(),Email()])
    phone=IntegerField('Phone Number', validators=[DataRequired(),NumberRange(min=1000000000, max=9999999999,message="Enter valid phone number")])
    address=StringField('Address', validators=[DataRequired()])
    state=StringField('State', validators=[DataRequired()])
    city=StringField('City', validators=[DataRequired()])
    zip=IntegerField('Zip Code', validators=[DataRequired(),NumberRange(min=100000, max=999999,message="Enter valid zip code")])
    farm_size=FloatField('Farm Size (in acres)', validators=[DataRequired(),NumberRange(min=0.1, message="Enter valid farm size")])
    crop_type=StringField('Crop Type', validators=[DataRequired()])
    soil_type=StringField('Soil Type', validators=[DataRequired()])
    irrigation_methods=StringField('Irrigation Methods', validators=[DataRequired()])
    experience_level=SelectField('Experience Level', choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('expert', 'Expert')], validators=[DataRequired()])
    submit=SubmitField("submit")
    

class orderform(FlaskForm):
    name=StringField('Name', validators=[DataRequired()])
    Email=StringField("Email",validators=[Optional(),Email()])
    phone=IntegerField('Phone Number', validators=[DataRequired(),NumberRange(message="Enter valid phone number")])
    address=StringField('Address', validators=[DataRequired()])
    state=StringField('State', validators=[DataRequired()])
    city=StringField('City', validators=[DataRequired()])
    zip=IntegerField('Zip Code', validators=[DataRequired(),NumberRange(min=100000, max=999999,message="Enter valid zip code")])
    submit=SubmitField("submit")

class rentform(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    Email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    address = StringField('Address', validators=[DataRequired(), Length(max=200)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    state = StringField('State', validators=[DataRequired(), Length(max=100)])
    zip = StringField('ZIP Code', validators=[DataRequired(), Length(max=10)])
    rentdate = DateField('Rental Date', validators=[DataRequired()], format='%Y-%m-%d')
    return_date = DateField('Return Date', validators=[DataRequired()], format='%Y-%m-%d')


class WorkerForm(FlaskForm):
    name=StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    location=StringField('Location', validators=[DataRequired(), Length(max=100)])
    phone=IntegerField('Phone Number', validators=[DataRequired(),NumberRange(message="Enter valid phone number")])
    availability=SelectField('Availability', choices=[('full-time', 'Full-Time'), ('part-time', 'Part-Time')], validators=[DataRequired()])
    budget=FloatField('Expected Salary', validators=[DataRequired(), NumberRange(min=0, message="Enter a valid budget")])
    additional_info=StringField('Additional Information', validators=[Optional(), Length(max=500)])
    skills=SelectField('hire or looking for work', choices=[('Hire', 'Hire'), ('Looking for work', 'Looking for work')], validators=[DataRequired()])
    submit=SubmitField("submit")

# ============================================================
# COLD STORAGE FORMS — paste into your existing forms.py
# ============================================================
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class ColdStorageOwnerForm(FlaskForm):
    owner_name              = StringField('Your Name',           validators=[DataRequired(), Length(max=100)])
    phone                   = StringField('Phone Number',        validators=[DataRequired(), Length(max=15)])
    village                 = StringField('Village',             validators=[DataRequired()])
    district                = StringField('District',            validators=[DataRequired()])
    state                   = StringField('State',               validators=[DataRequired()])
    total_capacity_tons     = FloatField('Total Capacity (Tons)',     validators=[DataRequired(), NumberRange(min=0.1)])
    available_capacity_tons = FloatField('Available Capacity (Tons)', validators=[DataRequired(), NumberRange(min=0.1)])
    temperature_range       = StringField('Temperature Range',   validators=[DataRequired()])
    supported_crops         = StringField('Supported Crops',     validators=[DataRequired()])
    price_per_ton_per_month = FloatField('Price/Ton/Month (₹)',  validators=[DataRequired(), NumberRange(min=1)])
    submit_owner            = SubmitField('List My Storage')


class ColdStorageBookingForm(FlaskForm):
    farmer_name        = StringField('Your Name',          validators=[DataRequired(), Length(max=100)])
    phone              = StringField('Phone Number',       validators=[DataRequired(), Length(max=15)])
    crop_name          = StringField('Crop Name',          validators=[DataRequired()])
    quantity_tons      = FloatField('Quantity (Tons)',     validators=[DataRequired(), NumberRange(min=0.1)])
    preferred_village  = StringField('Preferred Village',  validators=[DataRequired()])
    preferred_district = StringField('Preferred District', validators=[DataRequired()])
    storage_from       = DateField('Store From',           validators=[DataRequired()])
    storage_until      = DateField('Store Until',          validators=[DataRequired()])
    submit_booking     = SubmitField('Book Storage')