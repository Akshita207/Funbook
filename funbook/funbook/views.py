from django.http import HttpResponse
from django.shortcuts import redirect

def home_view(request):
    response = redirect('accounts/login/')
    return response
