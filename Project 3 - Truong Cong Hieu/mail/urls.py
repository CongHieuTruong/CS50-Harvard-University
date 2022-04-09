from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("account/login", views.userLoginHandleLogic, name="account/login"),
    path("user/logout", views.userLogoutHandleLogic, name="user/logout"),
    path("user/register", views.userRegisterHandleLogic, name="user/register"),
    path("emails", views.sendEmailForUser, name="sendEmailForUser"),
    path("emails/<int:id>", views.getEmailContentData, name="getEmailContentData"),
    path("emails/<str:typeMail>", views.getMailData, name="getMailData"),
]
