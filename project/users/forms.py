from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from project.models import User


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=40)])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=100)])
    password = PasswordField('Password', validators=[DataRequired()])
    theme = SelectField('Theme', default='flatly', choices=[("slate", 'Slate'), 
                                            ("flatly", 'Flatly'),
                                            ("darkly", 'Darkly'), 
                                            ("materia", 'Materia'),
                                            ('grakn', 'Grakn')]
                        )
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')
    