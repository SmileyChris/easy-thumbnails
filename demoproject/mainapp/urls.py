from django.urls import path

from .views import edit_image, index

urlpatterns = [
    path("", index, name="index"),
    path("edit/<int:pk>/", edit_image, name="edit_image"),
]
