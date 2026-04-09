from django.urls import path

from . import views

urlpatterns = [
    path("", views.post_list, name="post_list"),
    path("home/", views.home_test, name="home_test"),
    path("new/", views.post_create, name="post_create"),
    path("<int:post_id>/", views.post_detail, name="post_detail"),
    path("<int:post_id>/edit/", views.post_edit, name="post_edit"),
    path("<int:post_id>/delete/", views.post_delete, name="post_delete"),
    path("cart/", views.cart_view, name="cart_view"),
    path("cart/add/<int:post_id>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:post_id>/", views.cart_remove, name="cart_remove"),
]
