import random
from django.core.mail import EmailMessage, send_mail

from accountapp.models import User, OneTimePassword
from athAIna_backend import settings


def generateOtp():
    otp = ""
    for i in range(6):
        otp += str(random.randint(0,9))
    return otp

def send_code_to_user(email):
    subject="One Time Password for Email Verification"
    otp_code = generateOtp()
    print(otp_code)
    user = User.objects.get(email=email)
    current_site = "http://Testotp.com"
    email_body = f"Hello {user.email},\n\nYour One Time Password for Email Verification is {otp_code}\n\nRegards,\nTestotp Team"
    from_email = "test@swag.com"

    OneTimePassword.objects.create(user=user, code=otp_code)

    d_email = EmailMessage(subject=subject, body=email_body, from_email=from_email, to=[email])
    d_email.send(fail_silently=True)

def send_normal_email(data):
    send_mail(
        subject=data['email_subject'],
        message=data['email_body'],
        from_email='athAIna@gmail.com',
        recipient_list=[data['to_email']],
        fail_silently=False,
    )