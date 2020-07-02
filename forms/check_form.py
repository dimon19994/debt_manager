from flask_wtf import Form
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, HiddenField, IntegerField, FloatField
from flask_wtf.file import FileField
from wtforms import validators


class CheckForm(Form):
    check_id = HiddenField()

    check_description = StringField("Описание: ", [
        validators.DataRequired("Please enter your username."),
        validators.Length(5, 200, "Username should be from 3 to 20 symbols")
    ])

    check_sum = FloatField("Сумма: ", [
        validators.DataRequired("Please enter your username."),
        validators.NumberRange(0.01, 100000, "Username should be from 0.01 to 100000 symbols")
    ])

    check_item = StringField("Продукт: ", [
        validators.DataRequired("Please enter your password."),
        validators.Length(5, 100, "Password should be from 5 to 100 symbols")
    ])

    submit = SubmitField("Save")


