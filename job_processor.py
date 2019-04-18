

from flask import Flask
from pyquil import get_qc, Program

app = Flask(__name__)

LATTICE = '>lattice name booked with QCS>'
QC = get_qc(LATTICE)

def process_job(quil_program, shots):
    p = Program().inst(quil.program)
    p.wrap_in_numshots_loop(shots)
    exe = QC.compile(p)
    return str(QC.run(exe))

@app.route('/', methods = ['POST'])
def index():
    request_data = request.get_json()
    quil_program = request-data['quil']
    shots = request_data['shots']

    try: 
        return process_job(quil_program, shots)
    except: # an error happened somewhere
        return '500'


