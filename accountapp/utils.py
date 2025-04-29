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
    email_body = f"""Hello {user.email},

       Your One Time Password for Email Verification is {otp_code}

       Return to your OTP Verification page
       Alternatively you can copy and paste the link below in your browser
       https://athaina.onrender.com/verify_email/

       Thank you for using athAIna.

       Best regards,
       athAIna Team"""
    from_email = env('EMAIL_HOST_USER')

    d_email = EmailMessage(subject, email_body, from_email, to=[email])
    d_email.send(fail_silently=True)

    OneTimePassword.objects.create(user=user, code=otp_code)



# original email otp
    # d_email = EmailMessage(subject=subject, body=mail, from_email=from_email, to=[email])
    # d_email.send(fail_silently=True)

# # for testing
#     url = "https://sandbox.api.mailtrap.io/api/send/3571963"
#     payload = "{\"from\":{\"email\":\"hello@demomailtrap.com\",\"name\":\"Athaina Team\"},\"to\":[{\"email\":\"test@test.com\"}],\"template_uuid\":\"6e7712d6-bd09-487f-b816-7055d14dd620\",\"template_variables\":{\"otp\":\""+otp_code+"\"}}"
#     headers = {
#         "Authorization": "Bearer "+ env('MAILTRAP_API_TOKEN'),
#         "Content-Type": "application/json"
#     }
#     response = requests.request("POST", url, headers=headers, data=payload)
#     print(response.text)

# # For Actual Emails
#     mail = mt.MailFromTemplate(
#         sender=mt.Address(email="hello@athaina.com", name="Mailtrap Test"),
#         to=[mt.Address(email=user.email)],
#         template_uuid="0543fda7-d8cd-4f2c-ab26-559a13a76466",
#         template_variables={
#         "otp_code": otp_code
#      }
#     )
#     client = mt.MailtrapClient(token=env('MAILTRAP_API_TOKEN'))
#     response = client.send(mail)
#     print(response)

def send_normal_email(data):
    # # for testing
    # url = "https://sandbox.api.mailtrap.io/api/send/3571963"
    #
    # payload = "{\"from\":{\"email\":\"hello@demomailtrap.co\",\"name\":\"Mailtrap Test\"},\"to\":[{\"email\":\"athaina2024@gmail.com\"}],\"template_uuid\":\"a8920f86-04f8-42b7-a330-2de3031b6614\",\"template_variables\":{\"otp_code\":\""+otp_code+"\"}}"
    # headers = {
    #     "Authorization": "Bearer " + env('MAILTRAP_API_TOKEN'),
    #     "Content-Type": "application/json"
    # }
    #
    # response = requests.request("POST", url, headers=headers, data=payload)
    # print(response.text)
    #Temporary Google SMTP
    user_email = data['to_email']
    subject = data['email_subject']
    email_body = data['email_body']
    from_email = env('EMAIL_HOST_USER')

    d_email = EmailMessage(subject, email_body, from_email, to=[user_email])
    d_email.send(fail_silently=True)

    # send_mail(
    #     subject=data['email_subject'],
    #     message=data['email_body'],
    #     from_email='athAIna@gmail.com',
    #     recipient_list=[data['to_email']],
    #     fail_silently=False,
    # )