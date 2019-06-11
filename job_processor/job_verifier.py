
# job_verifier.py
# Pulls Quil requests from a localhosted server, runs them on a QVM, verifies that they correctly run, updates the server to flag the job as verified, and sends a confirmation email to the associated email address
# Written by: 
#   Robert Smith @ Rigetti
#   Nikolai Norona
#   Auguste Hirth @ UCLA


from pyquil import get_qc, Program
from pymongo import MongoClient
import warnings
import smtplib
from email.message import EmailMessage
import time
from functools import wraps
import job_utils

QC = get_qc(job_utils.LATTICE+"-qvm")


#connect to database and pull all not verified requests
client = MongoClient('localhost', 27017)
requests = [request for request in client.requests.requests.find({'verified':{'$ne':True}})]

responses = []
#Unwrap and send requests. Modeled after Robert Smith's outline. 
for request in requests: 

    identifier, email, email_body, warns, success = job_utils.run_job(request, QC)

    if success and not warns:
        #update database, indicating that the request has been verified
        client.requests.requests.update({'_id':identifier},{'$set':{'verified':True}}) 
        
        email_body += '\n\n QVM SIMULATION: \n Your job has been verified to run duing the next reservation period\n'

    else:
        #Update the database, removing that request
        client.requests.requests.remove({'_id':identifier})

        email_body += '\n\n QVM SIMULATION: \n Your job could not be verified (It either failed to run on the simulator, or had warnings)\n'  

    #print(email_body)
    responses.append((email, email_body))   

subject = 'CS239 PyQuil Server Results: QVM'
mail = job_utils.email_setup()
for email, email_body in responses:  
    try:
        job_utils.email_back(mail, email, subject, email_body)
    except Exception as inst: 
        mail = job_utils.email_setup()

mail.quit()
