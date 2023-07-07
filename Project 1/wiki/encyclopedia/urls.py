from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search, name="search"),
    path("wiki/<str:title>", views.entry, name="entry"),
    path("new_page/", views.new_page, name="new_page"),
    path("edit/<str:title>", views.edit, name="edit"),
    path("random_page", views.random_page, name="random_page")
]
