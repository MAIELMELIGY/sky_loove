# tasks.py
from datetime import timedelta

from celery.decorators import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from .models import CustomUser

logger = get_task_logger(__name__)


@shared_task
def send_welcome_email(user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        subject = 'Welcome to our website!'
        message = render_to_string('welcome_email.html', {
            'user': user,
            'website_name': 'skyloov',
        })
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        send_mail(subject, message, from_email, recipient_list)
        logger.info(f"Welcome email sent to {user.email}")
    except CustomUser.DoesNotExist:
        logger.warning(f"User with id {user_id} does not exist")


@shared_task
def send_welcome_email_delayed(user_id):
    send_welcome_email.apply_async(
        args=[user_id],
        eta=timezone.now() +
        timedelta(
            days=1))
