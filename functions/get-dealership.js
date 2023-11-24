const express = require('express');
const app = express();
const port = process.env.PORT || 3000;
const Cloudant = require('@cloudant/cloudant');

// Initialize Cloudant connection with IAM authentication
async function dbCloudantConnect(dbName) {
    try {
        const cloudant = Cloudant({
            plugins: { iamauth: { iamApiKey: 'A39AqZN-B49xkaUk9po0IiDMjZo7ykTmKSrewGicBQ1L' } }, // Replace with your IAM API key
            url: 'https://5362390b-8f6c-4605-a37e-a3c623ab04e0-bluemix.cloudantnosqldb.appdomain.cloud', // Replace with your Cloudant URL
        });

        const db = cloudant.use(dbName);
        console.info('Connect success! Connected to ${dbName} DB');
        return db;
    } catch (err) {
        console.error('Connect failure: ' + err.message + ' for Cloudant ${dbName} DB');
        throw err;
    }
}

let dealershipsDb;
//let reviewsDb;

(async () => {
    dealershipsDb = await dbCloudantConnect('dealerships');
//  reviewsDb = await dbCloudantConnect('fullreviews');
//    reviewsDb = await dbCloudantConnect('reviews');
})();

app.use(express.json());

// Define a route to get all dealerships with optional state and ID filters
app.get('/api/dealership', (req, res) => {
    const { state, id } = req.query;

    // Create a selector object based on query parameters
    const selector = {};
    if (state) {
        selector.state = state;
    }
    
    if (id) {
        selector.id = parseInt(id); // Filter by "id" with a value of 1
    }

    const queryOptions = {
        selector,
        limit: 10, // Limit the number of documents returned to 10
    };

    dealershipsDb.find(queryOptions, (err, body) => {
        if (err) {
            console.error('Error fetching dealerships:', err);
            res.status(500).json({ error: 'An error occurred while fetching dealerships.' });
        } else {
            const dealerships = body.docs;
            res.json(dealerships);
        }
    });
});

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});


/*// Adding the Reviews Route.

// Define a route to get all reviews for a given dealership
 app.get('/api/review', (req, res) => {
    const { dealerId } = req.query;

    const selector = {};
    if (dealerId) {
        selector.dealership = parseInt(dealerId);
    }

    const queryOptions = {
        selector,
        limit: 60,  // Adjust this value as needed
    };

    reviewsDb.find(queryOptions, (err, body) => {
        if (err) {
            console.error('Error fetching reviews:', err);
            res.status(500).json({ error: 'An error occurred while fetching reviews.' });
        } else {
            const reviews = body.docs;
            res.json(reviews);
        }
    });
}); */
