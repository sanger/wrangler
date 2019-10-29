import csv
import re
from os import listdir
from os.path import isfile, join, getsize
import json
import sys


from flask import Flask

app = Flask(__name__)


def _get_rack_barcode(tube_rack_barcode=None):
    # pattern = re.compile(r'DN\d{6}[A-Z]\.csv')

    # directory = '/Volumes/team134/0 - Rack Layout scanned FluidX Tube/'
    directory = './'
    jsonStr = ''

    if isfile(join(directory, f'{tube_rack_barcode}.csv')) and getsize(join(directory, f'{tube_rack_barcode}.csv')) > 0:
        rack_file = join(directory, f'{tube_rack_barcode}.csv')
        with open(rack_file) as open_rack_file:
            csv_plate_file = csv.reader(open_rack_file, delimiter=',')
            layout = []
            for row in csv_plate_file:
                postition_dict = {row[0].strip(): row[1].strip()}
                layout.append(postition_dict)
            jsonStr = json.dumps({'rack_barcode': tube_rack_barcode, 'layout':layout})
    else:
        return 'File not found', 404

    if(jsonStr != ''):
        return jsonStr, {'Content-Type': 'application/json; charset=utf-8'}

    return 'Hello, World!'


@app.route('/rack/<tube_rack_barcode>')
def get_rack_barcode(tube_rack_barcode=None):
    try: 
        return _get_rack_barcode(tube_rack_barcode)
    except Exception:
        return 'Server error', 500