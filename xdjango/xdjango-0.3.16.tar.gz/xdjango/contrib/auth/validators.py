from django.forms import Form, CharField, BooleanField, EmailField


class LoginFormValidator(Form):
    username = CharField()
    password = CharField()


class UserQueryValidator(Form):
    send_email = BooleanField(required=False)


class PasswordResetFormValidator(Form):
    new_password = CharField()
    token = CharField()
    email = EmailField()


class EmailFormValidator(Form):
    email = EmailField()


class OneTimeTokenFormValidator(Form):
    one_time_token = CharField()
