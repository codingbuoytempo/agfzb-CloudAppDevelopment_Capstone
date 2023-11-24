from cloudant.client import Cloudant
from cloudant.query import Query
from flask import Flask, jsonify, request, abort
import atexit
import json

#Add your Cloudant service credentials here
cloudant_username = '5362390b-8f6c-4605-a37e-a3c623ab04e0-bluemix'
cloudant_api_key = 'A39AqZN-B49xkaUk9po0IiDMjZo7ykTmKSrewGicBQ1L'
cloudant_url = 'https://5362390b-8f6c-4605-a37e-a3c623ab04e0-bluemix.cloudantnosqldb.appdomain.cloud'
client = Cloudant.iam(cloudant_username, cloudant_api_key, connect=True, url=cloudant_url)

session = client.session()
print('Databases:', client.all_dbs())

db = client['reviews']
#db = client['fullreviews']


app = Flask(__name__)


@app.route('/api/review', methods=['GET'])
def get_reviews():
    dealership_id = request.args.get('id')
#    dealership_id = request.args.get('dealer_id')
    print("dealership id in reviews.py:", dealership_id)

    # Check if "id" parameter is missing
    if dealership_id is None:
        return jsonify({"error": "Missing 'id' parameter in the URL"}), 400

    # Convert the "id" parameter to an integer (assuming "id" should be an integer)
    try:
        dealership_id = int(dealership_id)
    except ValueError:
        return jsonify({"error": "'id' parameter must be an integer"}), 400

    # Define the query based on the 'dealership' ID
    selector = {
        'dealership': dealership_id
    }

    # Execute the query using the query method
    result = db.get_query_result(selector)

    # Create a list to store the documents
    data_list = []

    # Iterate through the results and add documents to the list
    for doc in result:
        data_list.append(doc)

    # Return the data as JSON
    return jsonify(data_list)


@app.route('/api/post_review', methods=['POST'])
def post_review():
    print("Received POST request.")
    if not request.json:
        print("Invalid JSON data.")
        abort(400, description='Invalid JSON data')
    
    review_data = request.json
    print(f"Review data: {review_data}")

    required_fields = ['id', 'name', 'dealership', 'review', 'purchase', 'purchase_date', 'car_make', 'car_model', 'car_year']
    for field in required_fields:
        if field not in review_data['review']:
            print(f"Missing required field: {field}")
            abort(400, description=f'Missing required field: {field}')


    print("All required fields are present.")
    print("review--------->", review_data)

    if not isinstance(review_data, dict):
        review_data = json.loads(review_data)
        if not isinstance(review_data, dict):
            print("Invalid JSON data after parsing.")
            abort(400, description='Invalid JSON data')

    print("Creating document in the database.")
    db.create_document(review_data)
    print("Document created successfully.")

    return jsonify({"message": "Review posted successfully"}), 201


if __name__ == '__main__':
    app.run(debug=True)