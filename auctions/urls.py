from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("auction/new", views.new, name="new"),
    path("auction/<int:auction_id>", views.auction, name="auction"),
    path("watchlist/<str:user_username>", views.watchlist, name="watchlist"),
    path("auction/<int:auction_id>/rate", views.rate, name="rate"),
    path("auction/<int:auction_id>/comment", views.comment, name="comment"),
    path("categories", views.categories, name = "categories"),
    path("category/<str:category>", views.category, name = "category"),
    path("auction/<int:auction_id>/close", views.close, name = "close"),
]


