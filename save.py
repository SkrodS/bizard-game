import json
import base64
from datetime import datetime
import os

def save(wave, difficulty, bunny):
    '''
    Spara en spelomgång
    '''
    data = {}
    data['wave'] = wave
    data['difficulty'] = difficulty
    data['bunny'] = bunny

    data_obscured = base64.b64encode(str(data).encode('utf-8')).decode('utf-8')

    date = datetime.today().strftime('%Y-%m-%d-%H.%M')

    difficulty_string = ''

    if difficulty == 2:
        difficulty_string = 'easy'
    elif difficulty == 4:
        difficulty_string = 'medium'
    elif difficulty == 6:
        difficulty_string = 'hard'

    index = ''

    while True:
        try:
            if not os.path.exists('save_files'):
                os.makedirs('save_files')
            with open(f'save_files/{difficulty_string} wave {wave} ({date})'+index, 'x') as f:
                f.write(str(data_obscured))
            break
        except IOError:
            if index:
                index = '('+str(int(index[1:-1])+1)+')'
            else:
                index = '(1)'
            pass