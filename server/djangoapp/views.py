from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, get_dealer_by_id_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from django.db import IntegrityError
from .models import CarModel

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    return render(request,'djangoapp/about.html')

# Create a `contact` view to return a static contact page
def contact(request):
    return render(request,'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            return render(request, 'djangoapp/index.html')
    else:
        return render(request, 'djangoapp/index.html')


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')


# Create a `registration_request` view to handle sign up request
def registration_request(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        firstname = request.POST["firstname"]
        lastname = request.POST["lastname"]

        # Attempt to create new user
        try:
            user = User.objects.create_user(username=username, password=password, first_name=firstname, last_name=lastname)
            user.save()
        except IntegrityError:
            return render(request, "djangoapp/registration.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return redirect('djangoapp:index')
    else:
        return render(request,'djangoapp/registration.html')

# Update the `get_dealerships` view to render the index page with a list of dealerships
def index_view(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/index.html', context)

   
def get_dealerships(request):
    if request.method == "GET":
        
        context = {}
        
        url = "http://localhost:3000/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        
        # # Concat all dealer's short name
        # dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        # return HttpResponse(dealer_names)
        
        context["dealerships_list"] = dealerships
        #print(context)
        
        return render(request, 'djangoapp/index.html', context)
        

# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...

def get_dealer_details(request, dealer_id):
    #context = {}
    if request.method == "GET":
        
        context = {}
        
        dealer_url = "http://localhost:3000/api/dealership"
        dealer_obj = get_dealer_by_id_from_cf(dealer_url, id=dealer_id)
        context['dealer'] = dealer_obj
        print("Dealer id: ", dealer_obj.id)

        reviews_url = f"http://127.0.0.1:5000/api/review?id={dealer_id}"
        all_reviews_for_dealer = get_dealer_reviews_from_cf(reviews_url, dealer_id=dealer_id)
        context['reviews_list'] = all_reviews_for_dealer

        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review

def add_review(request, id):
    context = {}
    dealer_url = "http://localhost:3000/api/dealership"
    dealer = get_dealer_by_id_from_cf(dealer_url, id=id)
    context['dealer'] = dealer

    if request.method == 'GET':
        cars = CarModel.objects.all()
        print("CARS: ", cars)
        context['cars'] = cars

        return render(request, 'djangoapp/add_review.html', context)

    elif request.method == 'POST':
        if request.user.is_authenticated:
            username = request.user.username
            print(request.POST)
            car_id = request.POST["car"]
            car = CarModel.objects.get(pk=car_id)
            print("CAR: ",car)
            user_review = {}
            user_review["time"] = datetime.utcnow().isoformat()
            user_review["name"] = username
            user_review["dealership"] = id
            user_review["id"] = id
            user_review['review'] = request.POST['content']
            user_review['purchase'] = False

            if 'purchasecheck' in request.POST:
                if request.POST['purchasecheck'] == 'on':
                    user_review['purchase'] = True
                    user_review['purchase_date'] = request.POST['purchasedate']
                    user_review['car_make'] = car.make.name
                    user_review['car_model'] = car.name
                    user_review['car_year'] = int(car.year.strftime("%Y"))
            
            payload = {}
            payload['review'] = user_review
            review_post_url = "http://127.0.0.1:5000/api/post_review"
            post_request(review_post_url, payload)
        return redirect('djangoapp:dealer_details', dealer_id=id)
