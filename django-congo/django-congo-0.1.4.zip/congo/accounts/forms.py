# -*- coding: utf-8 -*-
from congo.utils.form import add_widget_css_class
from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField, AuthenticationForm as DjangoAuthenticationForm, SetPasswordForm as DjangoSetPasswordForm, PasswordResetForm as DjangoPasswordResetForm
from django.utils.translation import ugettext_lazy as _
import re
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from congo.conf import settings
from django.core.urlresolvers import reverse

password_widget = forms.PasswordInput(attrs = {'autocomplete':'off'})

class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length = 60, required = False, label = _('First name'))
    last_name = forms.CharField(max_length = 80, required = False, label = _('Last name'))
    email1 = forms.EmailField(widget = forms.TextInput(), label = _('E-mail address'))
    email2 = forms.EmailField(widget = forms.TextInput(attrs = {'autocomplete':'off'}), label = _('Confirm e-mail address'))
    password1 = forms.CharField(max_length = 255, widget = password_widget, label = _("Password"), help_text = _("At least 8 characters, use numbers and letters."))
    password2 = forms.CharField(max_length = 255, widget = password_widget, label = _("Confirm password"))

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        add_widget_css_class(self, 'form-control')

    def clean_email1(self):
        email = self.cleaned_data['email1']
        model = get_user_model()

        if model.objects.filter(email = email).exists():
            raise forms.ValidationError(_("A user with that e-mail already exists."))

        return email

    def clean_password1(self):
        password = self.cleaned_data['password1']

        if len(password) < 8:
            raise forms.ValidationError(_("Password is too short. Minimum password length is 8 characters."))
        elif not re.compile('^.*(?=.*\d)(?=.*[a-zA-Z]).*$').search(password):
            raise forms.ValidationError(_("The password must contain at least one letter and one number."))

        return password

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()

        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        email1 = cleaned_data.get('email1')
        email2 = cleaned_data.get('email2')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        accept_newsletter = cleaned_data.get('accept_newsletter')

        if email1 and email2 and email1 != email2:
            self._errors['email2'] = self.error_class([_("Entered e-mail addresses don't match.")])
            del cleaned_data['email2']

        if password1 and password2 and password1 != password2:
            self._errors['password2'] = self.error_class([_("Entered passwords don't match.")])
            del cleaned_data['password2']

        if accept_newsletter and not (first_name or last_name):
            self._errors['first_name'] = self.error_class([_("To become our subscriber, fill in your name.")])

        return cleaned_data

    def save(self):
        data = self.cleaned_data
        user = get_user_model().objects.create_user(DjangoUserManager.normalize_email(data['email1']), data['password1'])
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.is_active = False
        user.save()

#        @OG - obsluzyc maile
#        from communication.models import EmailRecipient
#        email = user.email
#        name = user.get_full_name()
#        source = EmailRecipient.ON_LINE_FORM
#
#        if name:
#            EmailRecipient.subscribe(email, name, source)

        return user

class AuthenticationForm(DjangoAuthenticationForm):
    def __init__(self, request = None, *args, **kwargs):
        super(AuthenticationForm, self).__init__(request, *args, **kwargs)

        self.fields['username'].label = _("Your e-mail")
        add_widget_css_class(self, 'form-control')

class SetPasswordForm(DjangoSetPasswordForm):
    new_password1 = forms.CharField(label = _("New password"), widget = forms.PasswordInput, help_text = _("At least 8 characters, use numbers and letters."))
    new_password2 = forms.CharField(label = _("Confirm new password"), widget = forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        super(SetPasswordForm, self).__init__(user, *args, **kwargs)
        add_widget_css_class(self, 'form-control')

    def clean_new_password1(self):
        password = self.data["new_password1"]
        if len(password) < 8:
            raise forms.ValidationError(_("Password is too short. Minimum password length is 8 characters."))
        elif not re.compile('^.*(?=.*\d)(?=.*[a-zA-Z]).*$').search(password):
            raise forms.ValidationError(_("The password must contain at least one letter and one number."))
        return password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("Entered passwords don't match."))
        return password2

class PasswordChangeForm(SetPasswordForm):
    old_password = forms.CharField(label = _("Current password"), widget = forms.PasswordInput)

    def clean_old_password(self):
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(_("Your current password was entered incorrectly. Please enter it again."))
        return old_password
PasswordChangeForm.base_fields.keyOrder = ['old_password', 'new_password1', 'new_password2']

class PasswordResetForm(DjangoPasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = _("Your e-mail")
        add_widget_css_class(self, 'form-control')

    def clean_email(self):
        email = self.cleaned_data["email"]
        model = get_user_model()

        self.users_cache = model.objects.filter(email__iexact = email)
        if not len(self.users_cache):
            raise forms.ValidationError(_("That e-mail address doesn't have an associated user account. Are you sure you've registered?"))
        if any((not user.has_usable_password()) for user in self.users_cache):
            raise forms.ValidationError(_("The user associated with this e-mail address cannot reset the password."))
        return email

    def save(self, *args, **kwargs):
        for user in self.users_cache:
            if user.first_name or user.last_name:
                recipient_name = ("%s %s" % (user.first_name, user.last_name)).strip()
            else:
                recipient_name = None

            subject = _("Password reset")

            data_dict = {
                'email': user.email,
                'uid': urlsafe_base64_encode(force_bytes(user.id)),
                'user': user,
                'token': default_token_generator.make_token(user),
                'protocol': 'https' if settings.SSL_ENABLED else 'http',
            }

#            @OG - Uruchomic maila
            print "######## MAIL ########"
            print reverse('demo:password_reset_confirm', kwargs = {'uidb64':data_dict['uid'], 'token':data_dict['token']})
            print "######## MAIL ########"
            
            
#            email_message = SimpleEmailMessage(subject, recipient_email = user.email, recipient_name = recipient_name, data_dict = data_dict, site = site, template = "password_reset")
#            email_message.send()

# For the purposes of Django Admin

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label = _("Password"), widget = forms.PasswordInput)
    password2 = forms.CharField(label = _("Confirm password"), widget = forms.PasswordInput, help_text = _("Enter the same password as above, for verification."))

    class Meta:
        model = get_user_model()
        fields = ('email',)

    def clean_username(self):
        model = get_user_model()
        email = self.cleaned_data["email"]

        if model.objects.filter(email = email).exists():
            raise forms.ValidationError(_("A user with that e-mail already exists."))
        else:
            return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Entered passwords don't match."))
        return password2

    def save(self, commit = True):
        user = super(UserCreationForm, self).save(commit = False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label = _("Password"), help_text = _("Raw passwords are not stored, so there is no way to see this user's password, but you can change the password using <a href=\"password/\">this form</a>."))

    class Meta:
        model = get_user_model()
        # @OG "django.core.exceptions.ImproperlyConfigured: Creating a ModelForm without either the 'fields' attribute or the 'exclude' attribute is prohibited; form UserChangeForm needs updating."
        # Zostawiam to dla Ciebie...
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        field = self.fields.get('user_permissions', None)
        if field is not None:
            field.queryset = field.queryset.select_related('content_type')

    def clean_password(self):
        return self.initial["password"]
