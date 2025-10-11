from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("category/<slug:category_slug>/", views.product_list, name="product_list_by_category"),

    # Wishlist routes must come before <slug:slug>
    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("wishlist/remove/<int:item_id>/", views.remove_from_wishlist, name="remove_from_wishlist"),
    path("wishlist/move-to-cart/<int:item_id>/", views.move_to_cart, name="move_to_cart"),

    # Product-specific routes
    path("<slug:slug>/add-to-wishlist/", views.add_to_wishlist, name="add_to_wishlist"),
    path("<slug:slug>/", views.product_detail, name="product_detail"),
    path("wishlist/move-all-to-cart/", views.move_all_to_cart, name="move_all_to_cart"),

]


