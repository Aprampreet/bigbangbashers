from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True)
def send_registration_email(self, email, username):
    """
    Sends a welcome email to newly registered users.
    """
    subject = "Welcome to EventHub!"
    message = (
        f"Hi {username},\n\n"
        "Thank you for joining EventHub!\n\n"
        "We're thrilled to have you onboard. You can now explore events, connect with others, "
        "and make the most of your experience on our platform.\n\n"
        "If you have any questions, feel free to reach out to our support team.\n\n"
        "Best regards,\n"
        "The Big Bang Bashers Team"
    )
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return f"Registration email sent to {email}"
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)
        return f"Failed to send registration email to {email}: {str(e)}"


@shared_task
def send_login_email(email, username):
    subject = "Login Successful - EventHub"
    message = (
        f"Hi {username},\n\n"
        "You’ve successfully logged into your EventHub account.\n\n"
        "If this wasn’t you, please change your password immediately or contact our support team.\n\n"
        "Happy exploring!\n"
        "The Big Bang Bashers Team"
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
    return f"Login email sent to {email}"

