
# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.db.models import Max

@shared_task
def set_auction_as_inactive(auction_id):
    from .models import Auction, Bid
    from users.models import Cart, CartItem
    auction_object = Auction.objects.get(id=auction_id)
    auction_object.isActive = False # set the auction as not active
    bids_on_auction = Bid.objects.filter(auction=auction_object)
    if bids_on_auction:
        # place in cart
        max_bid = bids_on_auction.all().aggregate(Max('amount'))['amount__max']
        max_bid_obj = Bid.objects.get(auction=auction_object, amount=max_bid)
        max_bidder = max_bid_obj.bidder
        cart = Cart.objects.filter(user=max_bidder).first()
        cart_item = CartItem.objects.create()
        cart_item.item = auction_object
        cart_item.cart = cart
        cart_item.save()
    auction_object.save() # save the auction object

@shared_task
def set_auction_as_active(auction_id):
    from .models import Auction
    auction_object = Auction.objects.get(id=auction_id)
    auction_object.isActive = True # set the auction as not active 
    auction_object.save() # save the auction object