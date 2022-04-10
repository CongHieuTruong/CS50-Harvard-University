from django.conf import settings
from django.urls import include, path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.loginPage, name="login"),
    path("logout", views.logoutPage, name="logout"),
    path("register", views.registerForApp, name="register"),
    path("following", views.userFollowFunction, name="following"),
    path("post-message", views.userPostSent, name="postmessage"),
    path("like/<int:id>", views.handleLikeForUser, name="like"),
    path("profile/<str:username>", views.userProfile, name="profile"),
    path("follow/<int:id>", views.userFollow, name="follow"),
    path("editpost/<int:id>", views.userPostEdit, name="editpost"),
    path("user", views.getLoginUser, name="editpost")


]
