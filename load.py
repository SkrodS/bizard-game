import tkinter as tk
from tkinter import filedialog
import base64
import json

def load():
    root = tk.Tk()
    root.withdraw()


    filepath = filedialog.askopenfile(initialdir='save_files')

    with open(filepath.name, 'r') as f:
        data = f.read()
        data = base64.b64decode(data.encode('utf-8')).decode('utf-8')
        data = data.replace("'", '"')
        data = json.loads(data)

    return data['wave'], data['difficulty']
