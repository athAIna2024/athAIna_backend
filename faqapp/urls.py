from django.urls import path
from . import views

urlpatterns = [
    path('save/', views.CreateFAQ.as_view(), name='create_faq'),
    path('<int:id>/', views.UpdateAndDeleteFAQ.as_view(), name='update_delete_faq'),
    path('list/', views.ListOfFAQs.as_view(), name='list_faqs'),

]