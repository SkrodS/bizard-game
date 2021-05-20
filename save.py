import json
import bcrypt
from datetime import datetime
import os

def save(wave, difficulty):
    data = {}
    data['difficulty'] = difficulty
    data['wave'] = wave
    data_string = json.dumps(data).encode('UTF-8')
    hashed = bcrypt.hashpw(data_string, bcrypt.gensalt())
    date = datetime.today().strftime('%Y-%m-%d-%H:%M')

    index = ''
    while True:
        try:
            if not os.path.exists('save_files'):
                os.makedirs('save_files')
            with open(f'save_files/save {date}'+index, 'x') as outfile:
                print(hashed, file=outfile)
            break
        except IOError:
            if index:
                index = '('+str(int(index[1:-1])+1)+')'
            else:
                index = '(1)'
            pass
