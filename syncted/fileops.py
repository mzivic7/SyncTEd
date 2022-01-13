import tkinter as tk
from tkinter import filedialog
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

# save txt file with save dialog
def save_txt(text, file_path, tab_spaces):
    text_save = text.replace(" /n ", "\n")   # remove spaces around "/n"
    text_save = text_save.replace(tab_spaces, "\t")   # convert tab spaces to "\t"
    if file_path == "":   # if there is no path from load file:
        root = tk.Tk()   # define tkinter root
        root.withdraw()   # make tkinter root invisible
        save_file = filedialog.asksaveasfile(mode='w', initialfile = 'Untitled.txt', defaultextension=".txt",
                                    filetypes=[("All Files","*.*"),("Text Documents","*.txt")])
        if save_file is None:   # asksaveasfile return "None" if dialog closed with "cancel"
            return ""
    else:   # if there is path from load file:
        save_file = open(file_path,'w')   # open that existing file
    save_file.write(text_save)   # write text to file
    file_path = save_file.name
    save_file.close()   # close file
    return file_path
    
# load txt file with load dialog
def load_txt(tab_spaces):
    root = tk.Tk()   # define tkinter root
    root.withdraw()   # make tkinter root invisible
    file_path = filedialog.askopenfilename()   # open load file dialog and get path
    try:
        file = open(file_path,"r")   # open file
        text = (file.read())   # load all text from file
        text = text.replace("\n", " /n ")   # add spaces around "/n"
        text = text.replace("\t", tab_spaces)   # convert "\t" to tab spaces
        file.close()
    except:   # if cant open file
        print("Error: File not found")
        text = ""
        file_path = ""
    return text, file_path

# load value from line in config
def load_config_val(position):
    conf_file = open("data/conf.txt")   # open settings file
    conf_lines = conf_file.readlines()   # read settings
    conf_file.close()   # close file
    conf_line = conf_lines[position].replace(" ", "")
    conf_line = conf_line.split("=")   # read line as list
    return conf_line[1]

def load_key():
    root = tk.Tk()   # define tkinter root
    root.withdraw()   # make tkinter root invisible
    file_path = filedialog.askopenfilename()   # get path from dialog
    key = RSA.import_key(open(file_path, 'r').read())   # load key from that path
    return key

def load_saved_key(path):
    return RSA.import_key(open(path, 'r').read())
