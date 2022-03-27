from django.shortcuts import render
from django.http import HttpResponse
from config import url_helper,templates
from django.shortcuts import render, get_object_or_404




# Create your views here.


def home(request):
    """
    Displays a home page for Tor Weather with basic information about
    the application.
    """
    
    
    return render(request, 'home.html')

def subscribe(request):
    """
    Displays the subscription form (all fields empty or default) if the
    form hasn't been submitted. After the user hits the submit button,
    redirects to the pending page if all of the fields were acceptable.
    If the user is already subscribed to that Tor node, they are sent to 
    an error page.
    """

    
    return render(request, 'subscribe.html')



