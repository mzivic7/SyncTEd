import pygame
import os.path
import socket
import time
import tkinter as tk
from tkinter import filedialog
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


version = "Pre-alpha 0.3.8"
date = "(18.12.2021)"


# --Functions-- #
# prints text in box with word wrapping
def text_wrap(surface, text, pos, font, color=(0,0,0)):
    words = text.split(' ')   # convert string to list of words
    space = font.size(' ')[0]   # the width of a space
    x, y, maxw, maxh = pos   # get dimension
    for word in words:   # for each word in list:
        if word != "/n":   # if word is not newline
            word_surf = font.render(word, True, color)   # create word surface
        wordw, wordh = word_surf.get_size()   # get word size
        if x + wordw >= maxw or word == "/n":   # if word goes over max or it is newline
            x = pos[0]   # reset x
            y += wordh   # start on new row
        if word != "/n":   # if word is not newline
            surface.blit(word_surf, (x, y))   # show word
            x += wordw + space   # go to next word position

# save txt file with save dialog
def save_txt(text, file_path):
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
def load_txt():
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

# generate RSA keypair
def rsa_gen_key():
    priv_key = RSA.generate(2048)   # generate private key with size
    pub_key = priv_key.publickey()   # generate public key from private
    priv_pem = priv_key.export_key().decode()   # convert private key to string
    pub_pem = pub_key.export_key().decode()   # convert public key to string
    with open("data/private_key.pem", 'w') as priv:   # write keys to pem files
        priv.write(priv_pem)
    with open("data/public_key.pem", 'w') as pub:
        pub.write(pub_pem)
    return pub_key, priv_key

# RSA encryption
def rsa_enc(plaintext, peer_pub_key):
    cipher = PKCS1_OAEP.new(key=peer_pub_key)   # prepare for encryption with key
    cipher_text = cipher.encrypt(plaintext.encode())   # encrypt data
    return cipher_text

# RSA decryption
def rsa_dec(cipher_text, priv_key):
    decrypt = PKCS1_OAEP.new(key=priv_key)   # prepare for decryption with key
    plaintext = decrypt.decrypt(cipher_text).decode()   # decrypt data
    return plaintext


# --Load config-- #
host = eval(load_config_val(0))
ask_save = eval(load_config_val(1))
encryption = eval(load_config_val(2))
tab_spaces_num = int(load_config_val(3))
screen_w = int(load_config_val(4))
screen_h = int(load_config_val(5))
client_ip = str(load_config_val(6))
client_port = int(load_config_val(7))
local_ip = str(load_config_val(8))
local_port = int(load_config_val(9))
client_ip = client_ip[:len(client_ip)-1]   # remove whitespace
local_ip = local_ip[:len(local_ip)-1]   # remove whitespace


# --initialize GUI-- #
pygame.init()   # initialize pygame
pygame.display.set_caption('SyncTED')   # window tittle
screen = pygame.display.set_mode([screen_w, screen_h])   # set window size
clock = pygame.time.Clock()   # start clock
font = pygame.font.Font("data/LiberationMono-Regular.ttf", 16)   # text font
# keys unicode blacklist
blst = [pygame.K_BACKSPACE, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_RETURN, pygame.K_TAB]
blst_client = ["/i/", "/b/", "/l/", "/r/", "/u/", "/d/", "/e/", "/t/"]

# --Initial variables-- #
text = ''   # empty text string
n = 0
i = 0
i2 = 0
line_x = 0
line_y = 0
line2_x = 0
line2_y = 0
client_input = "/i/"
client_upload = False
text_upload = ""
file_path = ""
tab_spaces = " " * tab_spaces_num   # create tab from spaces
run = True


# --RSA keys-- #
# load private key
if encryption is True:
    try: priv_key = RSA.import_key(open("data/private_key.pem", 'r').read())   # load and convert private key
    except: 
        root = tk.Tk()   # define tkinter root
        root.withdraw()   # make tkinter root invisible
        file_path = filedialog.askopenfilename()   # get path from dialog
        try: priv_key = RSA.import_key(open(file_path, 'r').read())   # load key from that path
        except: pub_key, priv_key = rsa_gen_key()   # if key is not loaded: generate keys
    # load peer public key
    try: peer_pub_key = RSA.import_key(open("data/peer_public_key.pem", 'r').read())   # load and convert public key
    except: 
        root = tk.Tk()   # define tkinter root
        root.withdraw()   # make tkinter root invisible
        file_path = filedialog.askopenfilename()   # get path from dialog
        try: peer_pub_key = RSA.import_key(open(file_path, 'r').read())   # load key from that path
        except: run = False   # if key is not loaded: end program


## --TCP protocol setup-- ##
if run is True:
    if host is True:
        s = socket.socket()   # start socket
        s.bind((local_ip, int(local_port)))   # bind to local ip
        s.listen(5)  # wait for client
        conn, address = s.accept()   # establish connection
    else:
        s = socket.socket()   # start socket
        s.connect((str(client_ip), int(client_port))) # connect to host


# --Main loop-- #
while run is True:
    
    # --Comunication-- #
    if host is True:   # host
        try:
            data = str(i) + "/" + str(i2) + "/" + text   # pack all data in single var
            if encryption is True: 
                conn.send(rsa_enc(data, peer_pub_key))   # send encrypted data
                client_input_enc = conn.recv(2048)   # recive input from client
                client_input = rsa_dec(client_input_enc, priv_key)   # decrypt it
            else:
                conn.send(data.encode())   # send data
                client_input = conn.recv(2048).decode()   # recive input from client
            if client_input == "/f/":   # if host will upload text
                if encryption is True: 
                    text_enc = conn.recv(2048)   # recive input from client
                    text = rsa_dec(text_enc, priv_key)   # decrypt it
                else: text = conn.recv(2048).decode()   # recive uploaded text from client
                i, i2 = 0, 0   # reset index positions
                client_input = "/i/"   # reset client input to default
        except:   # if connection is lost:
            if text != "" and ask_save is True:   # save text to file
                file_path = save_txt(text, file_path)
            run = False   # break main loop
        
    else:   # client
        try:
            ping_start = time.perf_counter()   # start ping time
            if encryption is True: 
                data = s.recv(2048)   # recive data
                data = rsa_dec(data, priv_key)   # decrypt it
            else:
                data = s.recv(2048).decode()   # recive data
            data_lst = data.split('/')   # unpack data in list
            i = int(data_lst[0])   # take i from list
            i2 = int(data_lst[1])   # take i2 from list
            header = len(str(i2)) + len(str(i)) + 2   # size of header containing i and i2
            text = data[header:]   # get text from without header
            if encryption is True: s.send(rsa_enc(client_input, peer_pub_key))   # send encrypted data
            else: s.send(client_input.encode())  # send client input
            ping_end = time.perf_counter()   # end ping time
            ping_time = round((ping_end - ping_start) * 1000)   # calculate ping time in ms
            if client_upload is True:   # if client loaded text from file
                if encryption is True: 
                    s.send(rsa_enc(text_upload, peer_pub_key))   # send encrypted data
                else: s.send(text_upload.encode())   # upload text to host
                client_upload = False   # stop uploading
        except:   # if connection is lost:
            if text != "" and  ask_save is True:   # save text to file
                file_path = save_txt(text, file_path)
            run = False   # break main loop
    
    
    # --Locate newlines-- #
    loc = 0
    loc_prev = 0
    newline_loc = []   # location of newline signs
    while loc != -1:   # while there is location
        loc = text.find(" /n ", loc_prev)   # find location of "/n" from previous one
        loc_prev = loc + 4   # location of previous "/n" without it
        if loc != -1:   # if there is found "/n"
            newline_loc.append(loc)  # append it to list
    
    
    # --Pygame interface-- #
    if host is True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: # if quit
                if text != "" and ask_save is True:   # if there is some text
                        file_path = save_txt(text, file_path)   # save before load
                conn.close()   # disconnect
                run = False   # break main loop
            if e.type == pygame.KEYDOWN:
                n = 30   # make line visible
                
                if pygame.key.get_mods() == pygame.KMOD_LCTRL and e.key == pygame.K_s:  # if CTRL+S:
                    file_path = save_txt(text, file_path)   # save text to file
                
                if pygame.key.get_mods() == pygame.KMOD_LCTRL and e.key == pygame.K_l:  # if CTRL+L:
                    if text != "" and ask_save is True:   # if there is some text
                        file_path = save_txt(text, file_path)   # save before load
                    text, file_path = load_txt() # load text from file
                    i, i2 = 0, 0   # reset index positions
                
                if e.key == pygame.K_BACKSPACE:   # if BACKSPACE:
                    if i > 0:   # if it is not start of string
                        if text[i-4:i] == " /n ":   # if "/n" is to be deleted
                            text = text[:i-4] + text[i:]   # delete 4 chars
                            if i2 >= i:   # if i is smaller or equal than i2
                                i2 -= 4   # move i2 left
                            i -= 4   # move i left
                        else:
                            text = text[:i-1] + text[i:]   # remove last char
                            if i >= 1:   # if it is not start of string
                                if i2 >= i:   # if i is smaller or equal than i2
                                    i2 -= 1   # move i2 left
                                i -= 1    # move i left
                                
                
                if e.key == pygame.K_LEFT:     # if LEFT arrow:
                    if text[i-4:i] == " /n ":   # if "/n" is on the way:
                        i -= 4   # jump over it
                    else:
                        if i >= 1:   # if it is not start of string
                            i -= 1    # move i left
                
                if e.key == pygame.K_RIGHT:     # if RIGHT arrow:
                    if text[i:i+4] == " /n ":   # if "/n" is on the way:
                        i += 4   # jump over it
                    else:
                        if i < len(text):   # if it is not end of line
                            i += 1    # move i right
                
                if e.key == pygame.K_UP:     # if UP arrow:
                    closest_newline = 0
                    second_closest = 0
                    for newline in newline_loc:   # for each "/n":
                        if newline < i:   # if newline loc is smaller than index loc
                            second_closest = closest_newline   # second closest to left is previous closest
                            closest_newline = newline    # closest newline to left
                    # if there is closest newline
                    if closest_newline != 0:
                        # if index loc on current line is greater than length of above line:
                        if closest_newline - second_closest - 4  < i - closest_newline - 4: 
                            if second_closest == 0:   # if above line is first one there is ofset by 4 in detection
                                if closest_newline - second_closest < i - closest_newline - 4:   # here
                                    i = closest_newline   # go to end of above line
                                else:
                                    i -= closest_newline - second_closest   # go to same loc but on above line
                                    if second_closest == 0: i -= 4   # if it is on first line add 4 to skip "/n" sign
                            else:
                                i = closest_newline   # go to end of above line
                        else:
                            i -= closest_newline - second_closest   # go to same loc but on above line
                            if second_closest == 0: i -= 4   # if it is on first line add 4 to skip "/n" sign
                
                if e.key == pygame.K_DOWN:   # if DOWN arrow:
                    closest_newline = 0
                    second_closest = 0
                    closest_num = 0
                    for linenum, newline in enumerate(newline_loc):   # for each "/n":
                        if newline >= i:   # if newline loc is greater than index loc
                            closest_newline = newline   # second closest to right
                            closest_num = linenum   # where in list is closest_newline
                            break
                    try: second_closest = newline_loc[closest_num + 1]   # find second_closest
                    except: second_closest = len(text)   # it it doesnt exist, it is end of string
                    if closest_num > 0: left_closest = newline_loc[closest_num - 1]   # find left_closest 
                    else: left_closest = 0   # it it doesnt exist, it is start of string
                    # if there is closest newline
                    if closest_newline != 0:
                        # if index loc on current line is greater than length of below line:
                        if second_closest - closest_newline - 4 < i - left_closest - 4: 
                            i = second_closest  # go to end of below line 
                        else:
                            i += closest_newline - left_closest   # go to same loc but on below line
                            if left_closest == 0: i += 4   # if it is on first line add 4 to skip "/n" sign
                
                if e.key == pygame.K_RETURN:   # if ENTER:
                    text = text[:i] + " /n " + text[i:]
                    if i < i2:   # if i is smaller than i2
                        i2 += 4   # move i2 4 character right
                    i += 4    # move i right
                
                if e.key == pygame.K_TAB:  # if TAB:
                    text = text[:i] + tab_spaces + text[i:]   # write tab as spaces
                    if i2 > i:   # if i is smaller than i2
                        i2 += tab_spaces_num   # move i2 right
                    i += tab_spaces_num   # move i right
                
                if e.key not in blst and pygame.key.get_mods() == pygame.KMOD_NONE:   # if not any of above
                    text = text[:i] + e.unicode + text[i:]   # take unicode input from keyboard
                    if i2 > i:   # if i is smaller than i2
                        i2 += 1   # move i2 right
                    i += 1   # move i right
    else:
        client_input = "/i/"
        for e in pygame.event.get():
            if e.type == pygame.QUIT:   # if quit:
                if text != "" and ask_save is True:   # if there is some text
                        file_path = save_txt(text, file_path)   # save before load
                s.close()   # disconnect
                run = False   # break main loop
            if e.type == pygame.KEYDOWN:
                n = 30   # make line visible
                if pygame.key.get_mods() == pygame.KMOD_LCTRL and e.key == pygame.K_s:  # if CTRL+S:
                    file_path = save_txt(text, file_path)   # save text to file
                if pygame.key.get_mods() == pygame.KMOD_LCTRL and e.key == pygame.K_l:  # if CTRL+L:
                    if text != "" and ask_save is True:   # if there is some text
                        file_path = save_txt(text, file_path)   # save before load
                    text_upload, file_path = load_txt()   # load text from file
                    if file_path != "":   #if there is loaded file
                        client_upload = True   # activate upload of loaded text
                        client_input = "/f/"   # send host that client will uload
                if e.key == pygame.K_BACKSPACE:   # if BACKSPACE:
                    client_input = "/b/"
                if e.key == pygame.K_LEFT:     # if LEFT arrow:
                    client_input = "/l/"
                if e.key == pygame.K_RIGHT:     # if RIGHT arrow:
                    client_input = "/r/"
                if e.key == pygame.K_UP:     # if UP arrow:
                    client_input = "/u/"
                if e.key == pygame.K_DOWN:   # if DOWN arrow:
                    client_input = "/d/"
                if e.key == pygame.K_RETURN:   # if ENTER:
                    client_input = "/e/"
                if e.key == pygame.K_TAB:  # if TAB:
                    client_input = "/t/"
                if e.key not in blst and pygame.key.get_mods() == pygame.KMOD_NONE:   # if not any of above
                    client_input =  e.unicode   # take unicode input from keyboard 
    
    
    # --Client input-- #
    if host is True:
        if client_input == "/b/":   # if BACKSPACE:
            if i2 > 0:   # if it is not start of string
                if text[i2-4:i2] == " /n ":   # if "/n" is to be deleted
                    text = text[:i2-4] + text[i2:]   # delete 4 chars
                    if i >= i2:   # if i is greater or equal to i2
                        i -= 4   # move i left
                    i2 -= 4   # move i2 right
                else:
                    text = text[:i2-1] + text[i2:]   # remove last char
                    if i2 >= 1:   # if it is not start of string
                        if i >= i2:   # if if i is greater or equal to i2
                            i -= 1   # move i left
                        i2 -= 1   # move i2 left
                        
        if client_input == "/l/":     # if LEFT arrow:
            if text[i2-4:i2] == " /n ":   # if "/n" is on the way:
                i2 -= 4   # jump over it
            else:
                if i2 >= 1:   # if it is not start of string
                    i2 -= 1   # move i2 left
        
        if client_input == "/r/":     # if RIGHT arrow:
            if text[i2:i2+4] == " /n ":   # if "/n" is on the way:
                i2 += 4   # jump over it
            else:
                if i2 < len(text):   # if it is not end of line
                    i2 += 1   # move i2 right
        
        if client_input == "/u/":     # if UP arrow:
            closest_newline = 0
            second_closest = 0
            for newline in newline_loc:   # for each "/n":
                if newline < i2:   # if newline loc is smaller than index loc
                    second_closest = closest_newline   # second closest to left is previous closest
                    closest_newline = newline    # closest newline to left
            # if there is closest newline
            if closest_newline != 0:
                # if index loc on current line is greater than length of above line:
                if closest_newline - second_closest - 4  < i2 - closest_newline - 4: 
                    if second_closest == 0:   # if above line is first one there is ofset by 4 in detection
                        if closest_newline - second_closest < i2 - closest_newline - 4:   # here
                            i2 = closest_newline   # go to end of above line
                        else:
                            i2 -= closest_newline - second_closest   # go to same loc but on above line
                            if second_closest == 0: i2 -= 4   # if it is on first line add 4 to skip "/n" sign
                    else:
                        i2 = closest_newline   # go to end of above line
                else:
                    i2 -= closest_newline - second_closest   # go to same loc but on above line
                    if second_closest == 0: i2 -= 4   # if it is on first line add 4 to skip "/n" sign
        
        if client_input == "/d/":   # if DOWN arrow:
            closest_newline = 0
            second_closest = 0
            closest_num = 0
            for linenum, newline in enumerate(newline_loc):   # for each "/n":
                if newline >= i2:   # if newline loc is greater than index loc
                    closest_newline = newline   # second closest to right
                    closest_num = linenum   # where in list is closest_newline
                    break
            try: second_closest = newline_loc[closest_num + 1]   # find second_closest
            except: second_closest = len(text)   # it it doesnt exist, it is end of string
            if closest_num > 0: left_closest = newline_loc[closest_num - 1]   # find left_closest 
            else: left_closest = 0   # it it doesnt exist, it is start of string
            # if there is closest newline
            if closest_newline != 0:
                # if index loc on current line is greater than length of below line:
                if second_closest - closest_newline - 4 < i2 - left_closest - 4: 
                    i2 = second_closest  # go to end of below line 
                else:
                    i2 += closest_newline - left_closest   # go to same loc but on below line
                    if left_closest == 0: i2 += 4   # if it is on first line add 4 to skip "/n" sign
        
        if client_input == "/e/":   # if ENTER:
            text = text[:i2] + " /n " + text[i2:]
            if i > i2:   # if i is greater than i2
                i += 4   # move i right
            i2 += 4   # move i2 right
            
        if client_input == "/t/":  # if TAB:
            text = text[:i2] + tab_spaces + text[i2:]   # write tab as spaces
            if i > i2:   # if i is smaller than i2
                i += 4   # move i right
            i2 += 4   # move i2 right
            
        if client_input not in blst_client:  # if not any of above
            text = text[:i2] + client_input + text[i2:]   # take unicode input from keyboard
            if i > i2:   # if i is smaller than i2
                i += 1   # move i right
            i2 += 1   # move i2 right
        
            
    # --Display-- #
    screen.fill((255, 255, 255))   # fill screen with white color
    text_wrap(screen, text, (0, 0, screen_w, screen_h), font)
    if n >= 30:   # make cursor invisible for 30 itterations
        
        # calculate cursor position for i
        text_lines = text.split(' /n ')   # get list with strings separated by text lines
        line, line_i, line_i_prev = 0, 0, 0   # initial values
        while line_i < i:    # while index is greater than line ih which it is
            line_i += len(text_lines[line]) + 4   # get length of that line from start
            if line != 0:    # if index is not in first line
                line_i_prev += len(text_lines[line - 1]) + 4   # find previous line
            line += 1   # go to next line in list
        line_y = 19 * (line - 1)   # calculate y coordinate
        line_x = 10 * (i - line_i_prev)   # calculate x coordinate
        if line_i <= i:   # if index is past invisible "/n"
            line_y += 19   # jump to next line
            line_x = 0   # move index on start of line
        if host is True:   # draw black line for hosts index
            pygame.draw.line(screen, (0, 0, 0), (line_x, line_y), (line_x, line_y + 19))
        else:   # draw red line for hosts index
            pygame.draw.line(screen, (255, 0, 0), (line_x, line_y), (line_x, line_y + 19))
        
        # calculate cursor position for i2
        text_lines = text.split(' /n ')
        line, line_i2, line_i2_prev = 0, 0, 0
        while line_i2 < i2:
            line_i2 += len(text_lines[line]) + 4
            if line != 0: 
                line_i2_prev += len(text_lines[line - 1]) + 4
            line += 1
        line_y_2 = 19 * (line - 1)
        line_x_2 = 10 * (i2 - line_i2_prev)
        if line_i2 <= i2:
            line_y_2 += 19
            line_x_2 = 0
        if host is True:   # draw red line for clients index
            pygame.draw.line(screen, (255, 0, 0), (line_x_2, line_y_2), (line_x_2, line_y_2 + 19))
        else:   # draw red line for clients index
            pygame.draw.line(screen, (0, 0, 0), (line_x_2, line_y_2), (line_x_2, line_y_2 + 19))
            
    if n >= 70:   # make cursor visible for 40 itterations
        n = 0   # reset counter
    n += 1   # counter
    
    # prit ping
    if host is False:   # only for client
        screen.blit(font.render(str(ping_time) + "ms", True, (100, 100, 100)), (screen_w - 50, screen_h - 21))   # print ping
    
    pygame.display.flip()   # update screen
    clock.tick(60)   # screen update frequency
