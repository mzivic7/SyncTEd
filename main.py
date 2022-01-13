import pygame
import os.path
import socket
import time
import string

from syncted import fileops
from syncted import txtrsa
from syncted import graphics


version = "Pre-alpha 0.4.0"
date = "(13.1.2022)"



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
text = ''   # empty text string
n = 0   # timer for blinking line
i = i2 = 0   # indexes

client_input = "/i/"   # default input sent from client
client_upload = False   # is client uploading
text_upload = ""   #what text is client uploading

line_x = line_y = 0
line2_x = line2_y = 0

backspace = arrow_l = arrow_r = arrow_u = arrow_d = enter = tab = False   # if key is pressed and held
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
            run = False   # break main loop
            exit()   # quit now
        
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
            run = False   # break main loop
            exit()   # quit now
    
    
    ###### --Locate newlines-- #####
    loc = 0
    loc_prev = 0
    newline_loc = []   # location of newline signs
    while loc != -1:   # while there is location
        loc = text.find(" /n ", loc_prev)   # find location of "/n" from previous one
        loc_prev = loc + 4   # location of previous "/n" without it
        if loc != -1:   # if there is found "/n"
            newline_loc.append(loc)  # append it to list
    
    
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
                
                if e.key == pygame.K_BACKSPACE: backspace = key_trig = True  # if BACKSPACE:         
                if e.key == pygame.K_LEFT: arrow_l = key_trig = True   # if LEFT arrow:
                if e.key == pygame.K_RIGHT: arrow_r = key_trig = True   # if RIGHT arrow:
                if e.key == pygame.K_UP: arrow_u = key_trig = True   # if UP arrow:
                if e.key == pygame.K_DOWN: arrow_d = key_trig = True   # if DOWN arrow:
                if e.key == pygame.K_RETURN: enter = key_trig = True   # if ENTER:
                if e.key == pygame.K_TAB: tab = key_trig = True   # if TAB:
                if e.unicode in characters:   # if unicode input is in characters set   ###
                    text = text[:i] + e.unicode + text[i:]   # take unicode input from keyboard
                    if i2 > i:   # if i is smaller than i2
                        i2 += 1   # move i2 right
                    i += 1   # move i right
            
            # reset arrow keys states if key is released
            if e.type == pygame.KEYUP:
                if e.key == pygame.K_BACKSPACE: backspace = False
                if e.key == pygame.K_LEFT: arrow_l = False
                if e.key == pygame.K_RIGHT: arrow_r = False
                if e.key == pygame.K_UP: arrow_u = False
                if e.key == pygame.K_DOWN: arrow_d = False
                if e.key == pygame.K_RETURN: enter = False
                if e.key == pygame.K_TAB: tab = False
                hold = hold_first   # reset delay after pushing button
                push = True   # reset activation of delay after button
                key_trig = False   # no input keys are pressed
                
                
                
        ###### --Host input processing-- ######
        if key_trig is True:   # if any input key is pressed
            n = blinking_line_off   # make blinking line not blinking
            if hold >= hold_first:   # after delay, do processing
                if backspace is True:   # BACKSPACE
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

                if arrow_l is True:   # LEFT arrow:
                    if text[i-4:i] == " /n ":   # if "/n" is on the way:
                        i -= 4   # jump over it
                    else:
                        if i >= 1:   # if it is not start of string
                            i -= 1    # move i left
                            
                if arrow_r is True:   # RIGHT arrow:
                    if text[i:i+4] == " /n ":   # if "/n" is on the way:
                        i += 4   # jump over it
                    else:
                        if i < len(text):   # if it is not end of line
                            i += 1    # move i right
                            
                if arrow_u is True:   # UP arrow:
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
                
                if arrow_d is True:   # DOWN arrow:
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
                
                if enter is True:   # ENTER
                    text = text[:i] + " /n " + text[i:]
                    if i < i2:   # if i is smaller than i2
                        i2 += 4   # move i2 4 character right
                    i += 4    # move i right
                    
                if tab is True:   # TAB
                    text = text[:i] + tab_spaces + text[i:]   # write tab as spaces
                    if i2 > i:   # if i is smaller than i2
                        i2 += tab_spaces_num   # move i2 right
                    i += tab_spaces_num   # move i right
                    
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
                if e.key == pygame.K_BACKSPACE:   # if BACKSPACE:
                    client_input_buff = "/b/"
                    key_trig = True
                if e.key == pygame.K_LEFT:     # if LEFT arrow:
                    client_input_buff = "/l/"
                    key_trig = True
                if e.key == pygame.K_RIGHT:     # if RIGHT arrow:
                    client_input_buff = "/r/"
                    key_trig = True
                if e.key == pygame.K_UP:     # if UP arrow:
                    client_input_buff = "/u/"
                    key_trig = True
                if e.key == pygame.K_DOWN:   # if DOWN arrow:
                    client_input_buff = "/d/"
                    key_trig = True
                if e.key == pygame.K_RETURN:   # if ENTER:
                    client_input_buff = "/e/"
                    key_trig = True
                if e.key == pygame.K_TAB:  # if TAB:
                    client_input_buff = "/t/"
                    key_trig = True
                if e.unicode in characters:   # if unicode input is in characters set
                    client_input_buff = e.unicode   # take unicode input from keyboard 
                    key_trig = True
            
            # reset arrow keys states if key is released
            if e.type == pygame.KEYUP:
                hold = hold_first   # reset delay after pushing button
                push = True   # reset activation of delay after button
                key_trig = False   # no input keys are pressed
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
            
        if client_input in characters:   # if unicode input is in characters set
            text = text[:i2] + client_input + text[i2:]   # write unicode input
            if i > i2:   # if i is smaller than i2
                i += 1   # move i right
            i2 += 1   # move i2 right
        
         

    ###### --Graphics-- ######
    screen.fill((255, 255, 255))   # fill screen with white color
    graphics.text_wrap(screen, text, (0, 0, screen_w, screen_h), font)
    if n >= blinking_line_off:   # make blinking line invisible for 30 iterations
        graphics.blinking_line(screen, host, text, i)   # black line for local index
        graphics.blinking_line(screen, host, text, i2, invert=True)   # red line for peer index
    if n >= blinking_line_off + blinking_line_on:   # make blinking line visible
        n = 0   # reset counter
    n += 1   # counter
    
    # print ping
    if host is False:   # only for client
        if ping_time < 50:   # print green ping
            screen.blit(font.render(str(ping_time) + "ms", True, (100, 200, 100)), (screen_w - 50, screen_h - 21))
        elif ping_time > 100:   # print red ping
            screen.blit(font.render(str(ping_time) + "ms", True, (200, 50, 50)), (screen_w - 50, screen_h - 21))
        else:   # print orange ping
            screen.blit(font.render(str(ping_time) + "ms", True, (200, 100, 50)), (screen_w - 50, screen_h - 21))
    
    pygame.display.flip()   # update screen
    clock.tick(100)   # screen update frequency
