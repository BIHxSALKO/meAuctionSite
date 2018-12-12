from django.contrib import admin

from .models import Auction, Bid, Category

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

class AuctionAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'end_price', 'end_time', 'isFlagged']

admin.site.register(Auction, AuctionAdmin)
admin.site.register(Bid)
admin.site.register(Category, CategoryAdmin)