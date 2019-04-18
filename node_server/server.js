// server.js
// BASE SETUP
// =============================================================================
var mongoose = require('mongoose');
// mongoose.Promise = global.Promise;
// mongoose.connect('DB_ADDRESS', {useMongoClient: true}); //connect to database
   
    
     
      
       
// call the packages we need
var express    = require('express');        // call express
var app        = express();                 // define our app using express
var bodyParser = require('body-parser');    // allows us to process html requests
        
                 
// configure app to use bodyParser()
// this will let us get the data from a POST
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
                  
var port = process.env.PORT || 8080;        // set our port
                   
                    
// REGISTER OUR ROUTES -------------------------------
// all of our routes will be prefixed with /api
app.use('/api/pyquil', require('routes/pyquil'));

// START THE SERVER
// =============================================================================
app.listen(port);
console.log('Server Listening On ' + port);
