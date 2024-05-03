import tkinter as tk
from tkinter import filedialog
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


def save_txt(text, file_path, tab_spaces):
    """Save txt file with save dialog"""
    text_save = text.replace(" /n ", "\n")   # remove spaces around "/n"
    text_save = text_save.replace(tab_spaces, "\t")   # convert tab spaces to "\t"
    if file_path == "":   # if there is no path from load file:
        root = tk.Tk()
        root.withdraw()
        save_file = filedialog.asksaveasfile(mode='w', initialfile='Untitled.txt', defaultextension=".txt",
                                             filetypes=[("All Files", "*.*"), ("Text Documents", "*.txt")])
        if save_file is None:   # asksaveasfile return "None" if dialog closed with "cancel"
            return ""
    else:   # if there is path from load file:
        save_file = open(file_path, 'w')   # open that existing file
    save_file.write(text_save)   # write text to file
    file_path = save_file.name
    save_file.close()   # close file
    return file_path


def load_txt(tab_spaces):
    """Load txt file with load dialog"""
    root = tk.Tk()   # define tkinter root
    root.withdraw()   # make tkinter root invisible
    file_path = filedialog.askopenfilename()   # open load file dialog and get path
    try:
        with open(file_path) as file:
            text = file.read()   # load all text from file
            text = text.replace("\n", " /n ")   # add spaces around "/n"
            text = text.replace("\t", tab_spaces)   # convert "\t" to tab spaces
    except Exception:   # if cant open file
        print("Error: File not found")
        text, file_path = "", ""
    return text, file_path


def load_config(position):
    """Load config"""
    conf_file = open("data/conf.txt")
    conf_lines = conf_file.readlines()
    conf_file.close()   # close file
    conf_line = conf_lines[position].replace(" ", "")
    conf_line = conf_line.split("=")
    return conf_line[1]


def load_key():
    """Load key from file with tkinter filedialog"""
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    key = RSA.import_key(open(file_path, 'r').read())
    return key


def load_saved_key(path):
    """Load key from specific path"""
    return RSA.import_key(open(path, 'r').read())
