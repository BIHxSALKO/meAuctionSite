
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
import os
from uuid import uuid4
from django.core.validators import validate_image_file_extension
from .tasks import set_auction_as_inactive
from django.core import serializers


class Category(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'

def get_image_path(instance, filename):
    return os.path.join('photos', str(uuid4()) + os.path.splitext(filename)[1])

class Auction(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True, validators=[validate_image_file_extension])
    description = models.CharField(max_length=1000)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    start_price = models.DecimalField(max_digits=8, decimal_places=2)
    buy_it_now_price = models.DecimalField(max_digits=8, decimal_places=2)
    end_price = models.DecimalField(max_digits=8, decimal_places=2)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    categories = models.ManyToManyField(Category)
    isFlagged = models.BooleanField(default=False)
    isActive = models.BooleanField(default=False)
    

    # tell the model how to print an auction
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('auction-detail', kwargs={'pk': self.pk})
'''
    def save(self):

        create_task = False # variable to know if celery task is to be created
        if self.pk is None: # Check if instance has 'pk' attribute set 
            # Celery Task is to created in case of 'INSERT'
            create_task = True # set the variable 

        super(Auction, self).save() # Call the Django's "real" save() method.
        
        if create_task: # check if task is to be created
            # pass the current instance as 'args' and call the task with 'eta' argument 
            # to execute after the race `end_time`
            set_auction_as_inactive.apply_async(args=[serializers.serialize("json", self)], eta=self.end_time) # task will be executed after 'race_end_time'
'''
class Bid(models.Model):
    amount = models.FloatField()
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    bid_placed_time = models.DateTimeField()

    # tell the model how to print an auction
    def __str__(self):
        return 'amount: {} bidder: {} in {}' .format(self.amount, self.bidder.username, self.auction.title)

    class Meta:
        # order the bids according to amount in descending order
        ordering = ['-amount']
