from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_user_view, name="login"),
    path("logout", views.user_logout, name="logout"),
    path("user_register", views.user_register, name="user_register"),
    path("add_auction_item", views.add_auction_item, name="add_auction_item"),
    path("category/<str:category>", views.category, name="category"),
    path("my_listings_view/<str:user>", views.my_listings_view, name="my_listings_view"),
    path("watchlist_item", views.watchlist_item, name="watchlist_item"),
    path("add_watchlist/<str:auction>", views.add_watchlist, name="add_watchlist"),
    path("update_auction_bid/<str:auction>", views.update_auction_bid, name="update_auction_bid"),
    path("auction/<str:auction>", views.auction_view_page, name="auction_view_page"),
    path("add_user_comment/<str:auction>", views.add_user_comment, name="add_user_comment"),
    path("delete_user_comment/<str:comment>", views.delete_user_comment, name="delete_user_comment"),
    path("delete_item_from_watchlist_page/<str:auction>", views.delete_item_from_watchlist_page, name="delete_item_from_watchlist_page"),
    path("user_delete_auction/<str:auction>", views.user_delete_auction, name="user_delete_auction"),
    path("user_close_listing/<str:auction>", views.user_close_listing, name="user_close_listing"),
]
