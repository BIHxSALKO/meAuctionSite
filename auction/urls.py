from django.urls import path
from .views import AuctionDetailView, add_auction, auction_detail, auction_list, delete_auction, my_bids, my_selling_auctions, auction_update

urlpatterns = [
    path('<int:pk>/', auction_detail, name='auction_detail'),
    path('add/', add_auction, name='add_auction'),
    path('update/<int:pk>/', auction_update, name='auction_update'),
    path('auction_list', auction_list, name='auction_list'),
    path('delete_auction', delete_auction, name='delete_auction'),
    path('my_bids', my_bids, name='my_bids'),
    path('my_selling_auctions', my_selling_auctions, name='my_selling_auctions')
]