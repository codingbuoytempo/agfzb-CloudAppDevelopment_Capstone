import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

def get_request(url, api_key=False, **kwargs ):
    print(kwargs)
    print("GET from {} ".format(url))
    if api_key:
        # Basic authentication GET
        try:
        # Call get method of requests library with URL and parameters
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                        params=kwargs, auth=HTTPBasicAuth('apikey', api_key))
            #response = requests.get(url, headers={'Content-Type': 'application/json'},
            #                            params=kwargs)
        except:
            # If any error occurs
            print("Network exception occurred during Authenticated GET ")
    else:
        # No authentication GET
        try:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
        except:
            print("Network exception occurred during No Authentication GET ")

    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    print("get_request_result:",json_data)
    return json_data

def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    dealers = get_request(url)
    #print(dealers)
    if dealers:
        # For each dealer object
        for dealer in dealers:
            # Create a CarDealer object with values in dealer dictionary
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], zip=dealer["zip"])
            results.append(dealer_obj)

    return results

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list

def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    # Perform a GET request with the specified dealer id
    reviews_json_result = get_request(url, dealerId=dealer_id)
    print(reviews_json_result)

    if reviews_json_result:
        # Get all review data from the response
        for review in reviews_json_result:
            # Check if any value is missing
            try:
                review_content = review["review"]
                id = review["_id"]
                name = review["name"]
                purchase = review["purchase"]
                dealership = review["dealership"]
                car_make = review["car_make"]
                car_model = review["car_model"]
                car_year = review["car_year"]
                purchase_date = review["purchase_date"]

                # Create a review object
                review_obj = DealerReview(dealership=dealership, id=id, name=name, 
                                          purchase=purchase, review=review_content, car_make=car_make, 
                                          car_model=car_model, car_year=car_year, purchase_date=purchase_date
                                          )

            except KeyError:
                print("Something is missing from this review. Using default values.")
                # Creating a review object with some default values

            # Analysing the sentiment of the review object's review text and saving it to the object attribute "sentiment"
            review_obj.sentiment = analyze_review_sentiments(review["review"])
            #review_obj.sentiment = "default stub value"
            print(f"sentiment: {review_obj.sentiment}")

            # Saving the review object to the list of results
            results.append(review_obj)

    #analyze_review_sentiments()
    return results

    
def analyze_review_sentiments(review):
    # Using example at https://cloud.ibm.com/apidocs/natural-language-understanding?code=python#sentiment
    # https://cloud.ibm.com/apidocs/natural-language-understanding?utm_medium=Exinfluencer&utm_source=Exinfluencer&utm_content=000026UJ&utm_term=10006555&utm_id=NA-SkillsNetwork-Channel-SkillsNetworkCoursesIBMCD0321ENSkillsNetwork1046-2022-01-01&code=python#authentication
    url = 'https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/08d7d585-021a-42de-8304-40b970a5628a'
    api_key = '7Y5Gox7L5uwu1NjMHKFQdj0RIYUU5l03Ri1pMhYuCYjt' 
    authenticator = IAMAuthenticator(api_key) 
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2022-04-07',authenticator=authenticator) 
    natural_language_understanding.set_service_url(url)
    #review = "This sucks!" 
    #review = "This is awesome!"
    #review = "This is so-so." 
    response = natural_language_understanding.analyze(text=review,features=Features(sentiment=SentimentOptions(targets=[review]))).get_result() 
    print("NLP Response of review:",response)
    label = response['sentiment']['targets'][0]['label']
    return label



# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative

def get_dealer_by_id_from_cf(url, id):
    dealer_json_result=get_request(url, id=id)
    print(dealer_json_result)
    if dealer_json_result:
        dealer_details = dealer_json_result[0]
        dealer_obj = CarDealer(
            address=dealer_details["address"], 
            city=dealer_details["city"], 
            full_name=dealer_details["full_name"], 
            id=dealer_details["id"], 
            lat=dealer_details["lat"], 
            long=dealer_details["long"], 
            short_name=dealer_details["short_name"], 
            st=dealer_details["st"], 
            zip=dealer_details["zip"])
        return dealer_obj
    else:
        print('No result from get_dealer_by_id_from_cf') 


def post_request(url, json_payload):
    print(json_payload)
    print("POST from {} ".format(url))
    try:
        response=requests.post(url, json=json_payload)
    except:
        print("Network exception occurred")
    status_code=response.status_code
    print("With status {} ".format(status_code))
    if response.text:
        try:
            json_data = json.loads(response.text)
        except json.JSONDecodeError:
            print("Error decoding JSON response")
            json_data = None
    else:
        print("Empty response")
        json_data = None
    return json_data


