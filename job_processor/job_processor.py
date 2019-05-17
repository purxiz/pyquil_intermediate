
# job_processor.py
# Pulls Quil verified requests from a localhosted server, runs them on the real QPU. Emails the results back to the associated email address, and sends a small summary to ahirth
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

try:
    QC = get_qc(job_utils.LATTICE)
except:
    print("QPU Lattice not available")
    QC = "QPU Lattice not available"

#connect to database and pull all not verified requests
client = MongoClient('localhost', 27017)
requests = [request for request in client.requests.requests.find({'$and':[{'verified':True}, {'sent':False}]})]

starttime = time.perf_counter()
responses = []
#Unwrap and send requests. Modeled after Robert Smith's outline. 
for request in requests: 

    identifier, email, email_body, warns, success = job_utils.run_job(request, QC)

    if success:
        #update database, indicating that the request has been verified
        client.requests.requests.update({'_id':identifier},{'$set':{'sent':True}})

        email_body += '\n\n QPU RUN \n Your job has been successfully run\n'

    else:
        #Update the database, removing that request
        client.requests.requests.remove({'_id':identifier})

        email_body += '\n\n QPU RUN \n Your job could not be run for some reason!\n'

    #print(email_body)
    responses.append((email, email_body))   

endtime = time.perf_counter()

print(endtime-starttime, len(responses))

subject = 'CS239 PyQuil Server Results: QPU'
mail = job_utils.email_setup()
for email, email_body in responses:  
    job_utils.email_back(mail, email, subject, email_body)

#Inform me about how many batch stats
subject = 'PyQuil Server Batch Run Info'
email_body = '\n Batch completed at: ' + time.ctime() +\
             '\n Batch runtime: ' + str(endtime-starttime) +\
             '\n Number of jobs run: ' + str(len(responses))

if responses: 
    job_utils.email_back(mail, 'ahirth@ucla.edu', subject, email_body)

mail.quit()
