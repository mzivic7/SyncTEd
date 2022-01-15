import pygame
import os.path
import socket
import time
import string

from syncted import fileops
from syncted import txtrsa
from syncted import graphics
from syncted import editor


version = "Pre-alpha 0.4.1"
date = "(15.1.2022)"



###### --Load config-- ######
host = eval(fileops.load_config_val(0))
ask_save = eval(fileops.load_config_val(1))
encryption = eval(fileops.load_config_val(2))
tab_spaces_num = int(fileops.load_config_val(3))
screen_w = int(fileops.load_config_val(4))
screen_h = int(fileops.load_config_val(5))
client_ip = str(fileops.load_config_val(6)).replace("\n", "").replace(" ", "")
client_port = int(fileops.load_config_val(7))
local_ip = str(fileops.load_config_val(8)).replace("\n", "").replace(" ", "")
local_port = int(fileops.load_config_val(9))



###### --initialize GUI-- ######
pygame.init()   # initialize pygame
pygame.display.set_caption('SyncTED')   # window tittle
screen = pygame.display.set_mode([screen_w, screen_h])   # set window size
clock = pygame.time.Clock()   # start clock
font = pygame.font.Font("data/LiberationMono-Regular.ttf", 16)   # text font



###### --Initial variables-- ######
run = True   # start main loop
text = ""   # empty text string
n = 0   # timer for blinking line
i = i2 = 0   # indexes

client_input = "/i/"   # default input sent from client
client_upload = False   # is client uploading
text_upload = ""   # what text is client uploading

line_x = line_y = 0
line2_x = line2_y = 0

arrow_l = arrow_r = arrow_u = arrow_d = backspace = enter = tab = False   # if key is pressed and held
key_trig = False   # if any input key is pressed
push = True   # first iteration when pressed key
hold = 0   # timer for move delay

# auto-tune ### todo
hold_first = 40   # delay on first step on button hold
hold_delay = 4   # delay between 2 steps on button hold
blinking_line_on = 70   # how long will blinking line be visible
blinking_line_off = 50   # how long will blinking line be invisible

file_path = ""   # path to loaded text file
tab_spaces = " " * tab_spaces_num   # create tab from spaces
characters = set(string.ascii_letters + string.digits + string.punctuation + " ")   # create all characters set



###### --RSA keys-- ######
if encryption is True:
    # load private key
    try: priv_key = fileops.load_saved_key("data/private_key.pem")   # load and convert private key
    except: 
        try: priv_key = fileops.load_key()   # try to load key from dialog
        except: pub_key, priv_key = txtrsa.gen_key()   # if key is not loaded: generate keys
    # load peer public key
    try: peer_pub_key = fileops.load_saved_key("data/peer_public_key.pem")   # load and convert public key
    except: 
        try: peer_pub_key = fileops.load_key()   # try to load key from dialog
        except: run = False   # if key is not loaded: end program



###### --TCP protocol setup-- ######
if run is True:
    if host is True:
        s = socket.socket()   # start socket
        s.bind((local_ip, int(local_port)))   # bind to local ip
        s.listen(5)  # wait for client
        conn, address = s.accept()   # establish connection
    else:
        s = socket.socket()   # start socket
        s.connect((str(client_ip), int(client_port))) # connect to host



###### --Main loop-- ######
while run is True:
    
    ###### --Comunication-- ######
    if host is True:   # host
        try:
            data = str(i) + "/" + str(i2) + "/" + text   # pack all data in single var
            if encryption is True: 
                conn.send(txtrsa.enc(data, peer_pub_key))   # send encrypted data
                client_input_enc = conn.recv(2048)   # recive input from client
                client_input = txtrsa.dec(client_input_enc, priv_key)   # decrypt it
            else:
                conn.send(data.encode())   # send data
                client_input = conn.recv(2048).decode()   # recive input from client
            if client_input == "/f/":   # if host will upload text
                if encryption is True: 
                    text_enc = conn.recv(2048)   # recive input from client
                    text = txtrsa.dec(text_enc, priv_key)   # decrypt it
                else: text = conn.recv(2048).decode()   # recive uploaded text from client
                i, i2 = 0, 0   # reset index positions
                client_input = "/i/"   # reset client input to default
        except:   # if connection is lost:
            if text != "" and ask_save is True:   # save text to file
                file_path = fileops.save_txt(text, file_path, tab_spaces)
            exit()   # quit now to avoid errors
        
    else:   # client
        try:
            ping_start = time.perf_counter()   # start ping time
            if encryption is True: 
                data = s.recv(2048)   # recive data
                data = txtrsa.dec(data, priv_key)   # decrypt it
            else:
                data = s.recv(2048).decode()   # recive data
            data_lst = data.split('/')   # unpack data in list
            i = int(data_lst[0])   # take i from list
            i2 = int(data_lst[1])   # take i2 from list
            header = len(str(i2)) + len(str(i)) + 2   # size of header containing i and i2
            text = data[header:]   # get text from without header
            if encryption is True: s.send(txtrsa.enc(client_input, peer_pub_key))   # send encrypted data
            else: s.send(client_input.encode())  # send client input
            ping_end = time.perf_counter()   # end ping time
            ping_time = round((ping_end - ping_start) * 1000)   # calculate ping time in ms
            if client_upload is True:   # if client loaded text from file
                if encryption is True: 
                    s.send(txtrsa.enc(text_upload, peer_pub_key))   # send encrypted data
                else: s.send(text_upload.encode())   # upload text to host
                client_upload = False   # stop uploading
        except:   # if connection is lost:
            if text != "" and  ask_save is True:   # save text to file
                file_path = fileops.save_txt(text, file_path)
            exit()   # quit now to avoid errors
    
    
    
    ###### --Host pygame interface-- ######
    if host is True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: # if quit
                if text != "" and ask_save is True:   # if there is some text
                        file_path = fileops.save_txt(text, file_path, tab_spaces)   # save before load
                conn.close()   # disconnect
                run = False   # break main loop
            if e.type == pygame.KEYDOWN:

                if pygame.key.get_mods() == pygame.KMOD_LCTRL and e.key == pygame.K_s:  # if CTRL+S:
                    file_path = fileops.save_txt(text, file_path, tab_spaces)   # save text to file
                
                if pygame.key.get_mods() == pygame.KMOD_LCTRL and e.key == pygame.K_l:  # if CTRL+L:
                    if text != "" and ask_save is True:   # if there is some text
                        file_path = fileops.save_txt(text, file_path, tab_spaces)   # save before load
                    text, file_path = fileops.load_txt(tab_spaces) # load text from file
                    i, i2 = 0, 0   # reset index positions
                
                if e.key == pygame.K_BACKSPACE: backspace = True  # if BACKSPACE:         
                if e.key == pygame.K_LEFT: arrow_l = True   # if LEFT arrow:
                if e.key == pygame.K_RIGHT: arrow_r = True   # if RIGHT arrow:
                if e.key == pygame.K_UP: arrow_u = True   # if UP arrow:
                if e.key == pygame.K_DOWN: arrow_d = True   # if DOWN arrow:
                if e.key == pygame.K_RETURN: enter = True   # if ENTER:
                if e.key == pygame.K_TAB: tab = True   # if TAB:
                if e.unicode in characters:   # if unicode input is in characters set   ###
                    text, i, i2 = editor.input_char(text, i, i2, e.unicode)
                key_trig = True   # some key is presses
            
            # reset arrow keys states if key is released
            if e.type == pygame.KEYUP:
                backspace = arrow_l = arrow_r = arrow_u = arrow_d = enter = tab = False
                hold = hold_first   # reset delay length after pushing button
                push = True   # reset activation of delay after pushing button
                key_trig = False   # no keys are pressed
                
                
                
        ###### --Host input processing-- ######
        # in client input processing i and i2 have swaped places, here - not
        if key_trig is True:   # if any input key is pressed
            n = blinking_line_off   # make blinking line not blinking
            if hold >= hold_first:   # after delay, do processing
                if arrow_l is True:   # LEFT arrow:
                    i = editor.left_arrow(text, i)
                if arrow_r is True:   # RIGHT arrow:
                    i = editor.right_arrow(text, i)
                if arrow_u is True:   # UP arrow:
                    i = editor.up_arrow(text, i)
                if arrow_d is True:   # DOWN arrow:
                    i = editor.down_arrow(text, i)
                if backspace is True:   # BACKSPACE
                    text, i, i2 = editor.backspace(text, i, i2)
                if enter is True:   # ENTER
                    text, i, i2 = editor.enter(text, i, i2)
                if tab is True:   # TAB
                    text, i, i2 = editor.tab(text, i, i2, tab_spaces, tab_spaces_num)
                # delay and repeat after pushing and holding key
                if push is True:   # if this is first iteration:
                    hold = 0   # large delay at begining
                    push = False   # stop that from repeating
                else: hold = hold_first - hold_delay   # after that, make delay small
            hold += 1   # iterrate delay
        
    
    
    ###### --Client pygame interface-- ######
    else:
        client_input = "/i/"   # reset client input
        for e in pygame.event.get():
            if e.type == pygame.QUIT:   # if quit:
                if text != "" and ask_save is True:   # if there is some text
                        file_path = fileops.save_txt(text, file_path, tab_spaces)   # save before load
                s.close()   # disconnect
                run = False   # break main loop
            if e.type == pygame.KEYDOWN:
                
                if pygame.key.get_mods() == pygame.KMOD_LCTRL and e.key == pygame.K_s:  # if CTRL+S:
                    file_path = fileops.save_txt(text, file_path, tab_spaces)   # save text to file
                    
                if pygame.key.get_mods() == pygame.KMOD_LCTRL and e.key == pygame.K_l:  # if CTRL+L:
                    if text != "" and ask_save is True:   # if there is some text
                        file_path = fileops.save_txt(text, file_path, tab_spaces)   # save before load
                    text_upload, file_path = fileops.load_txt(tab_spaces)   # load text from file
                    if file_path != "":   #if there is loaded file
                        client_upload = True   # activate upload of loaded text
                        client_input = "/f/"   # notify host that client will uload
                
                if e.key == pygame.K_BACKSPACE: client_input_buff = "/b/"   # if BACKSPACE:
                if e.key == pygame.K_LEFT: client_input_buff = "/l/"   # if LEFT arrow:
                if e.key == pygame.K_RIGHT: client_input_buff = "/r/"   # if RIGHT arrow:
                if e.key == pygame.K_UP: client_input_buff = "/u/"   # if UP arrow:
                if e.key == pygame.K_DOWN: client_input_buff = "/d/"   # if DOWN arrow:
                if e.key == pygame.K_RETURN: client_input_buff = "/e/"   # if ENTER:
                if e.key == pygame.K_TAB: client_input_buff = "/t/"   # if TAB:
                if e.unicode in characters:   # if unicode input is in characters set
                    client_input_buff = e.unicode   # take unicode input from keyboard 
                key_trig = True   # some key is presses
            
            # reset arrow keys states if key is released
            if e.type == pygame.KEYUP:
                hold = hold_first   # reset delay after pushing button
                push = True   # reset activation of delay after button
                key_trig = False   # no keys are pressed
                client_input = client_input_buff = "/i/"   # reset client input and buffer
                
        # delay and repeat after pushing and holding key
        if key_trig == True:
            n = blinking_line_off   # make blinking line not blinking
            if hold >= hold_first:   # after delay, do processing
                client_input = client_input_buff
                if push is True:   # if this is first iteration:
                    hold = 0   # large delay at begining
                    push = False   # stop that from repeating
                else: hold = hold_first - hold_delay   # after that, make delay small
            hold += 1   # iterrate delay
    
    
    
    ###### --Client input processing on host-- ######
    # here, i and i2 have swaped places, in host - not
    if host is True:
        if client_input == "/l/":     # LEFT arrow:
            i2 = editor.left_arrow(text, i2)
        if client_input == "/r/":     # RIGHT arrow:
            i2 = editor.right_arrow(text, i2)
        if client_input == "/u/":     # UP arrow:
            i2 = editor.up_arrow(text, i2)
        if client_input == "/d/":   # DOWN arrow:
            i2 = editor.down_arrow(text, i2)
        if client_input == "/b/":   # if BACKSPACE:
            text, i2, i = editor.backspace(text, i2, i)
        if client_input == "/e/":   # if ENTER:
            text, i2, i = editor.enter(text, i2, i)
        if client_input == "/t/":  # if TAB:
            text, i2, i = editor.tab(text, i2, i, tab_spaces, tab_spaces_num)
        if client_input in characters:   # if unicode input is in characters set
            text, i2, i = editor.input_char(text, i2, i, client_input)
        
         

    ###### --Graphics-- ######
    screen.fill((255, 255, 255))   # fill screen with white color
    graphics.text_wrap(screen, text, (0, 0, screen_w, screen_h), font)   # display text
    
    if n >= blinking_line_off:   # make blinking line invisible for 30 iterations
        graphics.blinking_line(screen, host, text, i)   # black line for local index
        graphics.blinking_line(screen, host, text, i2, invert=True)   # red line for peer index
    if n >= blinking_line_off + blinking_line_on:   # make blinking line visible
        n = 0   # reset counter
    n += 1   # counter
    
    if host is False:   # only for client
        graphics.print_ping(screen, (screen_w, screen_h), font, ping_time) # print ping
    
    pygame.display.flip()   # update screen
    clock.tick(100)   # screen update frequency
