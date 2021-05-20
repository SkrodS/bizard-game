import json
from datetime import datetime
import os
from cryptography.fernet import Fernet

def save(wave, difficulty):
    data = {}
    data['difficulty'] = difficulty
    data['wave'] = wave
    data_string = json.dumps(data)

    fernet = Fernet(Fernet.generate_key())
    data_encrypted = fernet.encrypt(data_string.encode())

    date = datetime.today().strftime('%Y-%m-%d-%H:%M')

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
            with open(f'save_files/{difficulty_string} wave {wave} ({date})'+index, 'x') as outfile:
                outfile.write(str(data_encrypted))
            break
        except IOError:
            if index:
                index = '('+str(int(index[1:-1])+1)+')'
            else:
                index = '(1)'
            pass
