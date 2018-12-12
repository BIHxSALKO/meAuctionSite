from django.db import models
from django.contrib.auth.models import User
from auction.models import Auction
from django.db.models.signals import post_save
from PIL import Image

class Watchlist(models.Model):
    name = models.CharField(max_length=100)
    start_price = models.DecimalField(max_digits=8, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
class Profile(models.Model):
    #user = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, **kwargs):
        super().save()

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

# https://stackoverflow.com/questions/48716346/django-cart-and-item-model-getting-quantity-to-update

class CartManager(models.Manager):
    def new_or_get(self, request):
        qs = self.get_queryset().filter(user=request.user)
        if qs.count() >= 1:
            new_obj = False
            cart_obj = qs.first()
            if request.user.is_authenticated and cart_obj.user is None:
                cart_obj.user = request.user
                cart_obj.save()
        else:
            cart_obj = Cart.objects.new(user=request.user)
            new_obj = True
        return cart_obj, new_obj


    def new(self, user=None):
        user_obj = None
        if user is not None:
            if user.is_authenticated:
                user_obj = user
        return self.model.objects.create(user=user_obj)

class Cart(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete='CASCADE')
    items = models.ManyToManyField(Auction, blank=True)
    total = models.DecimalField(default=0.0, max_digits=8, decimal_places=2)

    objects = CartManager()

class CartItem(models.Model):
    item = models.ForeignKey(Auction, null=True, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, null=True, on_delete=models.CASCADE)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

