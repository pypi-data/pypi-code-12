from django.conf.urls import url

from .views import RegisterView, VerifyPhoneView, ResendPhoneView, PasswordResetView, PasswordResetConfirmView, \
    ChangePhoneView

urlpatterns = [
    url(r'^$', RegisterView.as_view(), name='phone_quick_register'),
    url(r'^verify-phone/$', VerifyPhoneView.as_view(), name='phone_quick_verify'),
    url(r'^resend-phone/$', ResendPhoneView.as_view(), name='phone_quick_resend'),
    url(r'^change-phone/$', ChangePhoneView.as_view(), name='phone_quick_change'),
    url(r'^password/reset/$', PasswordResetView.as_view(), name='phone_quick_password_reset'),
    url(r'^password/reset/confirm/$', PasswordResetConfirmView.as_view(), name='phone_quick_password_reset_confirm'),
]
