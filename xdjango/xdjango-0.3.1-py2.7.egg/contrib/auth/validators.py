from django.forms import Form, CharField


class LoginFormValidator(Form):
    username = CharField()
    password = CharField()