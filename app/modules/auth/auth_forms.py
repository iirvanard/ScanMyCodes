from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class LoginForm(FlaskForm):
    email_or_username = StringField('email_or_username',
                                    validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('login')


class RegistrationForm(FlaskForm):
    first_name = StringField(
        'first_name', validators=[DataRequired(),
                                  Length(min=2, max=50)])
    last_name = StringField('last_name',
                            validators=[DataRequired(),
                                        Length(min=2, max=50)])
    username = StringField('username',
                           validators=[DataRequired(),
                                       Length(min=4, max=25)])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password',
                             validators=[DataRequired(),
                                         Length(min=6)])
    submit = SubmitField('register')
