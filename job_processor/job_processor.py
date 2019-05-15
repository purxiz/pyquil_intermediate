
# job_processor.py
# Pulls Quil requests from a localhosted server, runs them on a QuantumComputer, and emails the results back to the identified email address
# Written by: 
#   Robert Smith @ Rigetti
#   Auguste Hirth @ UCLA
#   Nikolai Norona


from flask import Flask
from pyquil import get_qc, Program
from pymongo import MongoClient
import warnings
import smtplib
from email.message import EmailMessage
import time
from functools import wraps

#Components written by Robert Smith @ Rigetti 
app = Flask(__name__)

#TODO switch to real QPU lattice
#LATTICE = '<lattice name booked with QCS>'
#LATTICE = '9q-generic-qvm'
LATTICE = "Aspen-4-10Q-A"
QC = get_qc(LATTICE+"-qvm")
try:
    QPU = get_qc(LATTICE)
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

#NOTE: We are using node for the server, saving to a local MongoDB. 
# This is unused, but may be a preferred implementation to the node server for later. 
@app.route('/', methods = ['POST'])
def index():
    request_data = request.get_json()
    quil_program = request_data['quil']
    shots = request_data['shots']
    email = request_data['email']
    try: 
        return process_job(quil_program, shots)
    except: # an error happened somewhere
        return '500'

#Components written by Auguste Hirth @ UCLA

#Email Setup#TODO move this somewhere secure
smtpUser = '239pyquilserver@gmail.com'
smtpPass = 'pyquil239' #dont steal the server's gmail account!
subject = 'CS239 PyQuil Server Results'
fromAdd = '239pyquilserver@gmail.com'

#ssmtp email results back to sender
def email_back(email, body):
    with smtplib.SMTP('smtp.gmail.com',587) as mail:
         mail.ehlo()
         mail.starttls()
         mail.ehlo()
         mail.login(smtpUser, smtpPass)
         msg = EmailMessage()
         msg['Subject'] = subject
         msg['From'] = fromAdd
         msg.set_content(body)
         try:
            mail.send_message(msg, from_addr=fromAdd, to_addrs=email)
         except Exception as error: 
            print('failed to email to: '+ email + '\nWith error: ' + str(error))
         mail.quit()

def timerator(func):
     @wraps(func)
     def wrapped(*args, **kwargs):
             start = time.perf_counter()
             result = func(*args, **kwargs)
             end = time.perf_counter()
             return result, end-start
     return wrapped

timed_process_job = timerator(process_job)

#connect to database and pull all unsent requests
client = MongoClient('localhost', 27017)
requests = [db for db in client.requests.requests.find({'sent':False})]

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
            QVMresponse, QVMruntime = timed_process_job(QC, quil_program, shots)
            simsuccess = True
        except Exception as inst: 
            QVMresponse = str(inst) #catch errors to send back to student
            QVMruntime = 'Did not run'
            simsuccess = False
        
        warns = []
        for warning in ws: 
            warns.append(str(warning.message))
        
        QPUresponse = 'QVM run failed!'
        QPUruntime = 'Did not run'
        if simsuccess and not warns:
            try: 
                QPUresponse, QPUruntime = timed_process_job(QPU, quil_program, shots)
            except Exception as inst: 
                QPUresponse = str(inst)
                QPUruntime = 'Did not run'
            for warning in ws: 
                warns.append(str(warning.message))

    #email response @ email 
    email_body = \
            'Query:\n' + str(quil_program) +\
            '\nShots:\n' + str(shots) +\
            '\nQVM Response:\n' + str(QVMresponse) +\
            '\nQVM Runtime:\n' + str(QVMruntime) +\
            '\nQPU Response:\n' + str(QPUresponse) +\
            '\nQPU Runtime:\n' + str(QPUruntime) +\
            '\nWarnings:\n' + str(warns)
    
    #print(email_body)
    email_back(email, email_body)

    #update database, indicating that the request has been run and sent
    client.requests.requests.update({'_id':identifier},{'$set':{'sent':True}}) 

    
