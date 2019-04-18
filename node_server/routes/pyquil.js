var express     = require('express');
var router      = express.Router();

var Program	= require('../models/program');

router.route('/send')
    .post( (request, response) => {
        console.log('Received POST request with quil: ' + request.body.quil + ', email: ' + request.body.email + ', and shots: ' + request.body.shots);

	    //TODO: Implement logic to make sure data is written to database
	    //TODO: Write data to database
	    response.status(200).json( { message: 'POST successfully received' } );
    });
