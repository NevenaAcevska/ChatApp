from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from Chat import views


urlpatterns = [
    path("", views.chatPage, name="chat-page"),

    # login-section
    path("auth/login/", LoginView.as_view
    (template_name="LoginPage.html"), name="login-user"),
    path("auth/logout/", LogoutView.as_view(), name="logout-user"),
    path('user_list/', views.user_list, name='user_list'),


]
