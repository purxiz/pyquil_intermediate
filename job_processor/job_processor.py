
from flask import Flask
from pyquil import get_qc, Program
from pymongo import MongoClient
import warnings
import smtplib

#Components written by Robert Smith @ Rigetti 
app = Flask(__name__)

#TODO Set up and Authenticate QMI
#LATTICE = '<lattice name booked with QCS>'
LATTICE = '9q-generic-qvm'
QC = get_qc(LATTICE)

def process_job(quil_program, shots):
    p = Program().inst(quil_program)
    #p.wrap_in_numshots_loop(shots) #NOTE modified. Original commented out
    #exe = QC.compile(p)
    #return str(QC.run(exe))
    return QC.run_and_measure(p, trials=shots)

#NOTE: We are using node for the server, saving to a local MongoDB. This is unused
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

#Email Setup
smtpUser = '239pyquilserver@gmail.com'
smtpPass = 'pyquil420' #dont steal the server's gmail account!
subject = 'CS239 PyQuil Server Results'
fromAdd = '239pyquilserver@gmail.com'

#ssmtp email results back to sender
def email_back(email, body):
    mail = smtplib.SMTP('smtp.gmail.com',587)
    mail.ehlo()
    mail.starttls()
    mail.ehlo()
    mail.login(smtpUser, smtpPass)
    header = 'From:'+fromAdd+'\nSubject: '+subject+'\n'
    try:
      mail.sendmail(fromAdd, email, header+'\n\n'+body)
    except: 
        print('failed to email to: '+ email)
    mail.quit()


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
            response = process_job(quil_program, shots)
        except Exception as inst: 
            response = str(inst) #catch errors to send back to student
        
        warns = []
        for warning in ws: 
            warns.append(str(warning.message))
    
    #email response @ email 
    email_body = \
            'Query:\n' + str(quil_program) +\
            '\nShots:\n' + str(shots) +\
            '\nResponse:\n' + str(response) +\
            '\nWarnings:\n' + str(warns)

    email_back(email, email_body)

    #update database, indicating that the request has been run
    client.requests.requests.update({'_id':identifier},{'$set':{'sent':True}}) 

    
