var mongoose = require('mongoose');
var Schema = mongoose.Schema;

//Define a model for database storage
var programSchema = new Schema({
    quil:   { type: String, required: [true, 'Please Supply a Program String'] },
    email:  { type: String, required: [true, 'Please Supply an Email'] },
    shots:  { type: Number, required: [true, 'Please Supply a Shots Number'] },
    sent:   { type: Boolean, required: [false]}
});

module.exports = mongoose.model('program', programSchema);
