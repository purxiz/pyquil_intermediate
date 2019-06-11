
# job_utils.py
# Holds utility functions and attributes that are shared by job_processor and job_verifier
# Written by: 
#   Robert Smith @ Rigetti
#   Nikolai Norona
#   Auguste Hirth @ UCLA

from pyquil import get_qc, Program
import warnings
import smtplib
from email.message import EmailMessage
import time
from functools import wraps

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
    mail = smtplib.SMTP()
    mail.connect('smtp.gmail.com',587)
    mail.ehlo()
    mail.starttls()
    mail.ehlo()
    mail.login(smtpUser, smtpPass)
    return mail

#ssmtp email results back to sender
def email_back(mail, email, subject, body):
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


def run_job(request, QC):
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
        except AttributeError as inst:
            QCresponse = str(type(inst))+': '+'QPU not properly configured\n'+str(inst)
            QCruntime = 'Did not run'
            success = False
        except Exception as inst: 
            QCresponse = str(type(inst))+': '+str(inst)#catch errors to send back to student
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

    return identifier, email, email_body, warns, success


timed_process_job = timerator(process_job) #wrap process_job in timer

#Email Setup
with open('/home/forest/pyquil_intermediate/job_processor/credentials', 'r') as file:
    smtpUser = file.readline().strip()
    smtpPass = file.readline().strip()
fromAdd = '239pyquilserver@gmail.com'
LATTICE = "Aspen-4-12Q-A"
