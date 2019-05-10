// server.js
// job queueing server written for UCLA PyQuil server
// Written by: 
//  Nikolai Norona
//  Auguste Hirth @ UCLA
//
// Listens for POSTs and adds the requests to a localhosted mongodb

// BASE SETUP
// =============================================================================
var mongoose = require('mongoose');
// mongoose.Promise = global.Promise;
// Start a MongoDB client and connect to it here
mongoose.connect('mongodb://localhost/requests', {useNewUrlParser: true});      
       
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
app.use('', require('./routes/pyquil'));

// START THE SERVER
// =============================================================================
app.listen(port);
console.log('Server Listening On ' + port);
