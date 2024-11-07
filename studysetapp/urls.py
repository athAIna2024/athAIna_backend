from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'create', views.CreateStudySet, basename='create_studyset')

urlpatterns = [
    path('', include(router.urls)),
]