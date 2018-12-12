from django.forms import widgets, ModelForm, DateTimeField, TextInput, DateTimeInput, FileField, ValidationError, Form, IntegerField, MultipleChoiceField, ChoiceField, Select
from django.utils.timezone import now
from .models import Auction, Bid, Category
from users.models import CartItem, Cart
from datetime import timedelta
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, HTML
from crispy_forms.bootstrap import PrependedText, FormActions

class AddAuction(ModelForm):
    end_time = DateTimeField(initial=now() + timedelta(days=1), required=True, widget=DateTimeInput())
    start_time = DateTimeField(initial=now(), required=True, widget=DateTimeInput())
    image = FileField()
    helper = FormHelper()
    helper.form_method = 'POST'
    helper.layout = Layout(
        'title',
        'image',
        'description',
        PrependedText('start_price', '$'),
        PrependedText('buy_it_now_price', '$'),
        'start_time',
        'end_time',
        'categories',
        FormActions(Submit('List Item', 'List this item for auction'))
    )
    
    def clean(self):
        cleaned_data = super(AddAuction, self).clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        if end_time <= start_time:
            raise ValidationError("End time must be later than start time.")

    class Meta:
        model = Auction
        fields = ['title', 'image', 'description', 'start_price', 'buy_it_now_price', 'start_time', 'end_time', 'categories']

class AddBid(ModelForm):

    def __init__(self, *args, **kwargs):
        self.auction_pk = kwargs.pop('auction_pk', False)
        self.auction = Auction.objects.get(pk=self.auction_pk)
        super(AddBid, self).__init__(*args, **kwargs)
        self.fields['auction'].initial = self.auction

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.layout = Layout(
        PrependedText('amount', '$'),
        Field('auction', type='hidden'),
        FormActions(Submit('Submit', 'Submit this bid'))
    )


    def clean(self):
        if 'amount' in self.cleaned_data:
            current_price = self.auction.end_price
            if self.cleaned_data['amount'] <= current_price:
                raise ValidationError("Bid amount must be greater than current price.")
        else:
            raise ValidationError("Form is empty.")
        

    class Meta:
        model = Bid
        fields = ['amount', 'auction']
        labels = {
            'amount': 'Place a bid on this item:'
        }

class UpdateAuction(ModelForm):
    image = FileField()
    helper = FormHelper()
    helper.form_method = 'POST'
    helper.layout = Layout(
        'title',
        'image',
        'description',
        PrependedText('buy_it_now_price', '$'),
        'categories',
        FormActions(Submit('Update', 'Update this auction'))
    )
    class Meta:
        model = Auction
        fields = ['title', 'image', 'description', 'categories', 'buy_it_now_price']

class BuyNow(ModelForm):
    def __init__(self, *args, **kwargs):
        self.auction_pk = kwargs.pop('auction_pk', False)
        self.auction = Auction.objects.get(pk=self.auction_pk)
        self.cart_id = kwargs.pop('cart', False)
        self.cart = Cart.objects.get(pk=self.cart_id)
        super(BuyNow, self).__init__(*args, **kwargs)
        self.fields['item'].initial = self.auction
        self.fields['cart'].initial = self.cart

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.layout = Layout(
        Field('item', type='hidden'),
        Field('cart', type='hidden'),
        FormActions(Submit('Buy Now', 'Buy Now')))

    def clean(self):
        pass

    class Meta:
        model = CartItem
        fields = ['item', 'cart']


class SearchCategory(Form):

    categories = list(Category.objects.all())
    cats = [(' ', ' '),('All', 'All')]
    for cat in categories:
        cats.append((cat, cat))

    options = ChoiceField(choices=cats, label="Category", required=False,
                widget=Select(attrs={'onchange': 'this.form.submit();'}))




class Flag(Form):
    id = IntegerField()
    def __init__(self, *args, **kwargs):
        self.auction_id = kwargs.pop('auction_id', False)
        super(Flag, self).__init__(*args, **kwargs)
        self.fields['id'].initial = self.auction_id
    class Meta:
        fields = ['id']

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.layout = Layout(
        Field('id', type='hidden'),
        HTML(
        '<button type="submit" class="btn btn-outline-danger" style="display: inline-block; float: right">Flag this item</button>'))