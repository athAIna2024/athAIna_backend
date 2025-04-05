import random
import mailtrap as mt
from django.core.mail import EmailMessage, send_mail
import environ
import requests

from accountapp.models import User, OneTimePassword
from athAIna_backend import settings

env = environ.Env(
    DEBUG=(bool, False)
)

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
    current_site = "http://athAIna.com"
    email_body = f"Hello {user.email},\n\nYour One Time Password for Email Verification is {otp_code}\n\nRegards,\nathAIna Team"
    from_email = "no_reply@athAIna.com"

    OneTimePassword.objects.create(user=user, code=otp_code)
    print("jisatsu shijou")

# original email otp
    # d_email = EmailMessage(subject=subject, body=mail, from_email=from_email, to=[email])
    # d_email.send(fail_silently=True)

# for testing
    url = "https://sandbox.api.mailtrap.io/api/send/3571963"

    payload = "{\"from\":{\"email\":\"hello@demomailtrap.co\",\"name\":\"Mailtrap Test\"},\"to\":[{\"email\":\"athaina2024@gmail.com\"}],\"template_uuid\":\"0543fda7-d8cd-4f2c-ab26-559a13a76466\",\"template_variables\":{\"otp_code\":\""+otp_code+"\"}}"

    print(env('MAILTRAP_API_TOKEN'))
    headers = {

        "Authorization": "Bearer "+ env('MAILTRAP_API_TOKEN'),

        "Content-Type": "application/json"

    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)


def send_normal_email(data):
    send_mail(
        subject=data['email_subject'],
        message=data['email_body'],
        from_email='athAIna@gmail.com',
        recipient_list=[data['to_email']],
        fail_silently=False,
    )



