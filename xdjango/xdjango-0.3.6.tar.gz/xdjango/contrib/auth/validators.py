from django.forms import Form, CharField, BooleanField


class LoginFormValidator(Form):
    username = CharField()
    password = CharField()


class UserQueryValidator(Form):
    send_email = BooleanField(required=False)
