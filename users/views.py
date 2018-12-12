from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, CheckoutCart, WatchlistForm
from django.contrib.auth.decorators import login_required
from .models import Profile, Cart, CartItem
from auction.models import Auction
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.urls import reverse

# Create your views here.
def add_watchlist(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            
            form = WatchlistForm(request.POST)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                #form.save()
                username = form.cleaned_data.get('username')
                messages.success(request, f'Your watchlist has been updated!')
                return redirect('profile')
        else:
            form = WatchlistForm()
        return render(request, 'users/watchlist.html', {'form':form})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to login.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'users/profile.html', context)

def cart(request):
    cart, new = Cart.objects.new_or_get(request)
    cart_items = CartItem.objects.filter(cart_id=cart.id)
    auctions = Auction.objects.all()
    auctions_ids = []
    for item in cart_items:
        auctions_ids.append(item.item_id)
    auction_items = auctions.filter(pk__in=auctions_ids)

    cart.total = 0
    for auction in auction_items:
        cart.total += auction.end_price

    paginator = Paginator(auction_items, 5)

    get_copy = request.GET.copy()
    params = get_copy.pop('page', True) and get_copy.urlencode()

    page = request.GET.get('page')
    auctions = paginator.get_page(page)
    checkout_cart = CheckoutCart()
    if request.POST:
        for item in cart_items:
            item.delete()
        messages.success(request, 'Checkout Success!')
        return redirect('cart')
    return render(request, 'users/cart.html', {'cart': cart, 'cart_items': auction_items, 'auctions': auctions, 'params': params, 'checkout_cart': checkout_cart})


@login_required
def user_homepage(request):
    if request.user.is_authenticated:
        return render(request, 'users/home.html', {})

@login_required
def delete_user(request):
    user = get_object_or_404(User, pk=request.user.pk)
    user.delete()
    messages.success(request, f'Account successfully deleted!')
    return redirect(reverse('register'))

@login_required
def deactivate_user(request):
    user = get_object_or_404(User, pk=request.user.pk)
    user.is_active = False
    user.save()
    messages.success(request, f'Profile successfully disabled. Please contact administrators to re-enable.')
    return redirect(reverse('home'))