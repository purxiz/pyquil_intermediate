//routes/pyquil.js
var express     = require('express');
var router      = express.Router();

//import our model for database operations
var Program	= require('../models/program');

//respond to requests sent to /send, i.e. <IP>/api/pyquil/send
router.route('/send')
    .post( (request, response) => { //new programs to be added to DB

        //log the details of the post request (JSON object expected)
        console.log('Received POST request with quil: ' + request.body.quil + ', email: ' + request.body.email + ', and shots: ' + request.body.shots);

	    //TODO: Implement logic to make sure data is written to database
	    //TODO: Write data to database
        //
        //Immediately send back an OK (200) response, with the message below
	    response.status(200).json( { message: 'POST successfully received' } );
    });

module.exports = router;
