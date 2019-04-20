//routes/pyquil.js
var express     = require('express');
var router      = express.Router();

//import our model for database operations
var Program	= require('../models/request');


//respond to requests sent to /send, i.e. <IP>/api/pyquil/send
router.route('/send')
    .get( (request, response) => { 
        response.status(200).json({message: 'Please send a POST instead!'})
    })

    .post( (request, response) => { //new programs to be added to DB
        console.log(request);
        //log the details of the post request (JSON object expected)
        console.log('Received POST request with quil: ' + request.body.quil + ', email: ' + request.body.email + ', and shots: ' + request.body.shots);

	    //TODO: Implement logic to make sure data is written to database
	    //TODO: Write data to database
        var program = new Program();
        program.quil = request.body.quil;
        program.email = request.body.email;
        program.shots = request.body.shots;
        program.sent = 'false';
        program.save( (err) => { 
            if (err){
                response.send(err);
                return;
            }
            response.status(200).json({message: 'Saved to DB'})
        });
   
    });

module.exports = router;
