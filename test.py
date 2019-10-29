import csv
import re
from os import listdir
from os.path import isfile, join, getsize
import json
import sys


from flask import Flask

app = Flask(__name__)

@app.route('/<tube_rack_barcode>')
def hello_world(tube_rack_barcode=None):
    print(f'tube_rack_barcode: {tube_rack_barcode}')
    # pattern = re.compile(r'DN\d{6}[A-Z]\.csv')

    directory = '/Volumes/team134/0 - Rack Layout scanned FluidX Tube/'

    if isfile(join(directory, tube_rack_barcode)) and getsize(join(directory, tube_rack_barcode)) > 0:
        rack_file = join(directory, tube_rack_barcode)
        with open(rack_file) as open_rack_file:
            csv_plate_file = csv.reader(open_rack_file, delimiter=',')
            for row in csv_plate_file:
                print(row)

        print('file exists')



    return 'Hello, World!'
