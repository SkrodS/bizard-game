from gamestate import *
import tkinter as tk
from tkinter import filedialog
import base64
import json

def load():
    '''
    Ladda en spelomgång. Returnerar wave, difficulty och bunny
    '''
    root = tk.Tk()
    root.withdraw()

    filepath = filedialog.askopenfile(initialdir='save_files')
    if not filepath:
        return 0, 0, 0, Gamestate.MENU

    try:
        with open(filepath.name, 'r') as f:
            data = f.read()
            data = base64.b64decode(data.encode('utf-8')).decode('utf-8')
            data = data.replace("'", '"')
            data = json.loads(data)
    except BaseException:
        return 0, 0, 0, Gamestate.MENU

    return data['wave'], data['difficulty'], data['bunny'], Gamestate.RUNNING
