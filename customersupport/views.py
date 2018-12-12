from django.shortcuts import render, redirect
from .models import CustomerSupportMessage
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

class PostCreateView(SuccessMessageMixin,LoginRequiredMixin, CreateView):
	model = CustomerSupportMessage
	fields=['title','content']
	success_url = '/profile'
	success_message = 'Successfully committed customer support message!'
	def form_valid(self, form):
		form.instance.author=self.request.user
		return super().form_valid(form)

# Create your views here.
