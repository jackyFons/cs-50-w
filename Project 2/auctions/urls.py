from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.categories, name="categories"),
    path("view_all", views.view_all, name="view_all"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("listing/<int:l_id>", views.view_listing, name="view_listing"),
    path("listing/<int:l_id>/close", views.close_listing, name="close_listing"),
    path("listing/<int:l_id>/delete", views.delete_listing, name="delete_listing"),
    path("listing/<int:l_id>/change_watchlist", views.change_watchlist, name="change_watchlist"),
]
