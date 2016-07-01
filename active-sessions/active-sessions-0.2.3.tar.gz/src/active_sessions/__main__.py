import argparse
import active_sessions
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone

# Create an argument parser.
parser = argparse.ArgumentParser('active-sessions')

def get_current_users():
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    user_id_list = []
    for session in active_sessions:
        data = session.get_decoded()
        user_id_list.append(data.get('_auth_user_id', None))
    # Query all logged in users based on id list
    return User.objects.filter(id__in=user_id_list)

from django.core.signals import request_finished
from django.dispatch import receiver

@receiver(request_finished)
def my_callback(sender, **kwargs):
    print("Request finished!")

def main(args=None):
    """Main entry point for your project.
    """

    queryset = get_current_users()
    print(queryset)
    print(queryset.exists())
    print(queryset.count())

if __name__ == '__main__':
    main(['-h'])
