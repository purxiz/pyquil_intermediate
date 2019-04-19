

from flask import Flask
from pyquil import get_qc, Program
from pymongo import MongoClient
import warnings
import smtplib

#Email Setup
smtpUser = '239pyquilserver@gmail.com'
smtpPass = 'pyquil420'
subject = 'PyQuil Server Results'
mail = smtplib.SMTP('smtp.gmail.com',587)
fromAdd = '239pyquilserver@gmail.com'
toAdd = 'theToEmailAddress'
mail.ehlo()
mail.starttls()
mail.ehlo()
mail.login(smtpUser, smtpPass)
header = 'From:'+fromAdd+'\nSubject: '+subject+'\n'
try:
    mail.sendmail(fromAdd, toAdd, header+'\n\ntesttest2')
except: 
    pass
mail.quit()

#Components written by Robert Smith @ Rigetti 
app = Flask(__name__)

#TODO Set up and Authenticate QMI
#LATTICE = '<lattice name booked with QCS>'
LATTICE = '9q-generic-qvm'
QC = get_qc(LATTICE)

def process_job(quil_program, shots):
    p = Program().inst(quil_program)
    p.wrap_in_numshots_loop(shots)
    exe = QC.compile(p)
    return str(QC.run(exe))

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
#TODO Query for all requests not yet sent to QMI
#TODO Email responses to associated address
#connect to database and pull all unsent requests
client = MongoClient('localhost', 27017)
requests = [db for db in client.requests.requests.find()]#{'sent':True})]a

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

    #TODO email response @ email 
    print(response, warns)

    #update database, indicating that the request has been run
    client.requests.requests.update({'_id':identifier},{'$set':{'sent':True}}) 

