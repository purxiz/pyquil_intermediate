
# job_processor.py
# Pulls Quil requests from a localhosted server, runs them on a QuantumComputer, and emails the results back to the identified email address
# Written by: 
#   Robert Smith @ Rigetti
#   Auguste Hirth @ UCLA
#   Nikolai Norona


from pyquil import get_qc, Program
from pymongo import MongoClient
import warnings
import smtplib
from email.message import EmailMessage
import time
from functools import wraps

#TODO switch to real QPU lattice
#LATTICE = '<lattice name booked with QCS>'
#LATTICE = '9q-generic-qvm'
LATTICE = "Aspen-4-10Q-A"
try:
    QC = get_qc(LATTICE)
except:
    print("QPU Lattice not available")

def process_job(qam, quil_program, shots):
    p = Program().inst(quil_program)
    return qam.run_and_measure(p, trials=shots)
    #NOTE modified. Original commented out below
    # This may be switched back later. 
    #p.wrap_in_numshots_loop(shots) 
    #exe = QC.compile(p)
    #return str(QC.run(exe))


#Components written by Auguste Hirth @ UCLA


def email_setup():
    mail = smtplib.SMTP('smtp.gmail.com',587)
    mail.ehlo()
    mail.starttls()
    mail.ehlo()
    mail.login(smtpUser, smtpPass)
    return mail

#ssmtp email results back to sender
def email_back(mail, email, body):
         msg = EmailMessage()
         msg['Subject'] = subject
         msg['From'] = fromAdd
         msg.set_content(body)
         try:
            mail.send_message(msg, from_addr=fromAdd, to_addrs=email)
         except Exception as error: 
            print('failed to email to: '+ email + '\nWith error: ' + str(error))

def timerator(func):
     @wraps(func)
     def wrapped(*args, **kwargs):
             start = time.perf_counter()
             result = func(*args, **kwargs)
             end = time.perf_counter()
             return result, end-start
     return wrapped

timed_process_job = timerator(process_job) #wrap process_job in timer

#Email Setup
with open('/home/forest/pyquil_intermediate/job_processor/credentials', 'r') as file: 
    smtpUser = file.readline().strip()
    smtpPass = file.readline().strip()
subject = 'CS239 PyQuil Server Results: QPU'
fromAdd = '239pyquilserver@gmail.com'


#connect to database and pull all not verified requests
client = MongoClient('localhost', 27017)
requests = [request for request in client.requests.requests.find({'$and':[{'verified':True}, {'sent':False}]})]

starttime = time.perf_counter()
responses = []
#Unwrap and send requests. Modeled after Robert Smith's outline. 
for request in requests: 
    #unwrap elements of request
    identifier = request['_id']
    quil_program = request['quil']
    shots = request['shots']
    email = request['email']

    #catch warnings to send back to student
    with warnings.catch_warnings(record=True) as ws:
        try:
            QCresponse, QCruntime = timed_process_job(QC, quil_program, shots)
            success = True
        except Exception as inst: 
            QCresponse = str(inst) #catch errors to send back to student
            QCruntime = 'Did not run'
            success = False
        
        warns = []
        for warning in ws: 
            warns.append(str(warning.message))

    #email response @ email 
    email_body = \
        'Query:\n' + str(quil_program) +\
        '\nShots:\n' + str(shots) +\
        '\nQC Response:\n' + str(QCresponse) +\
        '\nQC Runtime:\n' + str(QCruntime) +\
        '\nWarnings:\n' + str(warns)

    if success:
        #update database, indicating that the request has been verified
        #client.requests.requests.update({'_id':identifier},{'$set':{'sent':True}})

        email_body += '\n\n Your job has been successfully run\n'

    else:
        #Update the database, removing that request
        #client.requests.requests.remove({'_id':identifier})

        email_body += '\n\n Your job could not be run for some reason!\n'

    print(email_body)
    #responses.append((email, email_body))   

endtime = time.perf_counter()

print(endtime-starttime, len(responses))

mail = email_setup()
for email, email_body in responses:  
    email_back(mail, email, email_body)

mail.quit()
