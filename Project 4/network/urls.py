from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:username>", views.view_profile, name="view_profile"),
    path("post", views.new_post, name="new_post"),
    path("following", views.following, name="following"),

    # API ROUTES
    path("like/<int:id>", views.change_likes, name="change_likes"),
    path("save_edit/<int:id>", views.save_edit, name="save_edit")
]