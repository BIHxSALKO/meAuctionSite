
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Auction, Bid
from django.db.models import Max
from users.models import Cart, CartItem, CartManager, Watchlist
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.http import request
import datetime
from django.utils import timezone
from django.core.paginator import Paginator
from .forms import AddAuction, AddBid, BuyNow, Flag, UpdateAuction, SearchCategory
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .tasks import set_auction_as_inactive, set_auction_as_active


# Create your views here.
class AuctionDetailView(DetailView):
    model = Auction

def add_auction(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = AddAuction(request.POST, request.FILES)
            if form.is_valid():
                auction = form.save(commit=False)
                auction.seller = request.user
                auction.end_price = auction.start_price
                #auction.start_time = timezone.now()
                watchlist=Watchlist.objects.all()
                
                for watchlistitem in watchlist:
                    if watchlistitem.start_price>=auction.start_price and form.cleaned_data.get('title').find(watchlistitem.name)!=-1:
                        subj='Auction satisfying watchlist item '+watchlistitem.name
                        msg='An auction for '+watchlistitem.name+' has been created at startprice of '+str(auction.start_price)
                        send_mail(subj, msg, 'noreply@meauctionsite.com', [str(watchlistitem.user.email)])
                auction.save()
                if auction.start_time <= timezone.now():
                    auction.isActive = True
                    auction.save()
                else:
                    set_auction_as_active.apply_async([auction.id], eta=auction.start_time)
                set_auction_as_inactive.apply_async([auction.id], eta=auction.end_time)
                form.save_m2m()
                return redirect('auction_detail', pk=auction.pk)
        else:
            form = AddAuction()
        return render(request, 'auction/add_auction.html', {'form':form})
    else:
        return redirect(reverse('login'))

def auction_detail(request, pk):
    if request.user.is_authenticated:
        cart, new = Cart.objects.new_or_get(request)
        auction = get_object_or_404(Auction, pk=pk)
        if request.method == "POST":
                buy_now = BuyNow(request.POST, auction_pk=pk, cart=cart.id)
                bid_form = AddBid(request.POST, auction_pk=pk)
                flag_form = Flag(request.POST, auction_id=pk)
                if buy_now.is_valid():
                    cart_item = buy_now.save(commit=False)
                    cart_item.item = auction
                    cart_item.cart = cart
                    cart_item.save()
                    auction.end_price = auction.buy_it_now_price
                    auction.isActive = False
                    auction.save()
                    return redirect(reverse('cart'))
                if flag_form.is_valid():
                    auction = Auction.objects.get(pk=pk)
                    auction.isFlagged = True
                    auction.save()
                    bid_form = AddBid(auction_pk=pk)
                    flag_form = Flag(auction_id=pk)
                    return render(request, 'auction/auction_detail.html', {'bid_form':bid_form, 'flag_form':flag_form, 'auction':auction, 'buy_now':buy_now})
                if bid_form.is_valid():
                    bids_on_auction = Bid.objects.filter(auction=auction)
                    if bids_on_auction:
                        max_bid = bids_on_auction.all().aggregate(Max('amount'))['amount__max']
                        max_bid_obj = Bid.objects.get(auction=auction, amount=max_bid)
                    bid = bid_form.save(commit = False)
                    bid.bidder = request.user
                    bid.bid_placed_time = timezone.now()
                    bid.save()
                    auction.end_price = bid.amount
                    auction.save()
                    send_mail(
                        'Auction item bid',
                        'Someone bid $' + str(bid.amount) + ' on ' + auction.title + '!',
                        'auto@meAuction.com',
                        [auction.seller.email],
                        fail_silently=False,
                    )
                    if bids_on_auction:
                        send_mail(
                            "You've been outbid!",
                            'Someone bid $' + str(bid.amount) + ' on ' + auction.title + '!',
                            'auto@meAuction.com',
                            [max_bid_obj.bidder.email],
                            fail_silently=False,
                        )
                else:
                    return render(request, 'auction/auction_detail.html', {'bid_form':bid_form, 'flag_form':flag_form, 'auction':auction, 'buy_now':buy_now})

        bid_form = AddBid(auction_pk=pk)
        buy_now = BuyNow(auction_pk=pk, cart=cart.id)
        flag_form = Flag(auction_id=pk)

        return render(request, 'auction/auction_detail.html', {'bid_form':bid_form, 'auction':auction, 'buy_now':buy_now, 'flag_form':flag_form})
    else:
        return redirect(reverse('login'))

def delete_auction(request):
    auction = get_object_or_404(Auction, pk=request.POST['auction_hede'])
    if request.user == auction.seller:
        if auction.start_price == auction.end_price:
            auction.delete()
            messages.success(request, 'Auction was deleted successfully.')
            return redirect(reverse('home'))
    else:
        messages.error(request, 'Auction could not be deleted.')

def auction_update(request, pk):
    auction = get_object_or_404(Auction, pk=pk)
    if request.user == auction.seller:
        form = UpdateAuction(request.POST or None, request.FILES or None , instance=auction)
        if form.is_valid():
            form.save()
            messages.success(request, "Item was edited successfully.")
            return redirect('auction_detail', pk=auction.pk)
        else:
            return render(request, 'auction/auction_update.html', {'form': form})
    else:
        messages.error(request, "You can't update another's auction.")
        return redirect(reverse('home'))

@login_required
def auction_list(request):
    # https://www.youtube.com/watch?v=7QBsRpRLmA4

    auctions = Auction.objects.filter(isActive=True)
    search_category = SearchCategory()

    search_term = request.GET['Search']
    auctions = auctions.filter(title__icontains=search_term)

    if request.POST:
        category = request.POST['options']
        if category == 'All':
            category = ''
        if search_category.is_valid:
            search_category.initial = {request.POST['options']:request.POST['options']}
            if category:
                auctions = auctions.filter(categories__name__icontains=category)

    paginator = Paginator(auctions, 5)

    get_copy = request.GET.copy()
    params = get_copy.pop('page', True) and get_copy.urlencode()

    page = request.GET.get('page')
    auctions = paginator.get_page(page)

    context = {'auctions': auctions, 'params': params, 'search_term': search_term, 'search_category': search_category}

    return render(request, 'auction/auction_list.html', context)

@login_required
def my_bids(request):
    bids = Bid.objects.filter(bidder=request.user)
    auctions = []
    for bid in bids:
        if bid.auction.isActive:
            if bid.amount > bid.auction.start_price:
                bid.auction.start_price = bid.amount
            auctions.append(bid.auction)

    paginator = Paginator(auctions, 5)

    get_copy = request.GET.copy()
    params = get_copy.pop('page', True) and get_copy.urlencode()

    page = request.GET.get('page')
    auctions = paginator.get_page(page)

    context = {'auctions': auctions, 'params': params, 'my_bids': True}

    return render(request, 'auction/auction_list.html', context)

@login_required
def my_selling_auctions(request):
    auctions = Auction.objects.filter(seller=request.user)

    paginator = Paginator(auctions, 5)

    get_copy = request.GET.copy()
    params = get_copy.pop('page', True) and get_copy.urlencode()

    page = request.GET.get('page')
    auctions = paginator.get_page(page)

    context = {'auctions': auctions, 'params': params, 'my_auctions' : True}

    return render(request, 'auction/auction_list.html', context)