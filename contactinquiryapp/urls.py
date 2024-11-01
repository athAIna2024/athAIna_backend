from django.urls import path
from contactinquiryapp.views import ContactInquiryCreate

urlpatterns = [
    path('', ContactInquiryCreate.as_view(), name='contact_inquiry'),
]