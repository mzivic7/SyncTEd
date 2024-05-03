import pygame
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
host = eval(fileops.load_config(0))
ask_save = eval(fileops.load_config(1))
encryption = eval(fileops.load_config(2))
tab_spaces_num = int(fileops.load_config(3))
screen_w = int(fileops.load_config(4))
screen_h = int(fileops.load_config(5))
client_ip = str(fileops.load_config(6)).replace("\n", "").replace(" ", "")
client_port = int(fileops.load_config(7))
local_ip = str(fileops.load_config(8)).replace("\n", "").replace(" ", "")
local_port = int(fileops.load_config(9))



###### --initialize GUI-- ######
pygame.init()
pygame.display.set_caption('SyncTED')
screen = pygame.display.set_mode([screen_w, screen_h])
clock = pygame.time.Clock()
font = pygame.font.Font("LiberationMono-Regular.ttf", 16)



###### --Initial variables-- ######
run = True
text = ""   # main text string
n = 0   # timer for blinking line
i = 0   # indexes
i2 = 0

client_input = "/i/"   # default input sent from client
client_upload = False   # is client uploading
text_upload = ""   # what text is client uploading

line_x = line_y = 0
line2_x = line2_y = 0

arrow_l = arrow_r = arrow_u = arrow_d = backspace = enter = tab = False   # if key is pressed and held
key_trig = False   # if any input key is pressed
push = True   # first iteration when pressed key
hold = 0   # timer for move delay

# delays
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
    try:
        priv_key = fileops.load_saved_key("data/private_key.pem")   # load and convert private key
    except Exception:
        try:
            priv_key = fileops.load_key()   # try to load key from dialog
        except Exception:
            pub_key, priv_key = txtrsa.gen_key()   # if key is not loaded: generate keys
    # load peer public key
    try:
        peer_pub_key = fileops.load_saved_key("data/peer_public_key.pem")   # load and convert public key
    except Exception:
        try:
            peer_pub_key = fileops.load_key()   # try to load key from dialog
        except Exception:
            run = False   # if key is not loaded: end program



###### --TCP protocol setup-- ######
if run is True:
    if host is True:
        s = socket.socket()   # start socket
        s.bind((local_ip, int(local_port)))   # bind to local ip
        s.listen(5)  # wait for client
        conn, address = s.accept()   # establish connection
    else:
        s = socket.socket()   # start socket
        s.connect((str(client_ip), int(client_port)))   # connect to host



###### --Main loop-- ######
while run is True:

    ###### --Communication-- ######
    if host is True:   # host
        try:
            data = str(i) + "/" + str(i2) + "/" + text   # pack all data in single variable
            if encryption is True:
                conn.send(txtrsa.encrypt(data, peer_pub_key))
                client_input_enc = conn.recv(2048)
                client_input = txtrsa.decrypt(client_input_enc, priv_key)
            else:
                conn.send(data.encode())
                client_input = conn.recv(2048).decode()
            if client_input == "/f/":   # if host will upload text
                if encryption is True:
                    text_enc = conn.recv(2048)
                    text = txtrsa.decrypt(text_enc, priv_key)
                else:
                    text = conn.recv(2048).decode()   # receive uploaded text from client
                i, i2 = 0, 0
                client_input = "/i/"   # reset client input to default
        except Exception:   # if connection is lost
            if text != "" and ask_save is True:
                file_path = fileops.save_txt(text, file_path, tab_spaces)
            conn.close()
            exit()

    else:   # client
        try:
            ping_start = time.perf_counter()
            if encryption is True:
                data = s.recv(2048)
                data = txtrsa.decrypt(data, priv_key)
            else:
                data = s.recv(2048).decode()
            if not data:
                file_path = fileops.save_txt(text, file_path, tab_spaces)
                s.close()
                exit()
            data_lst = data.split('/')
            i = int(data_lst[0])
            i2 = int(data_lst[1])
            header = len(str(i2)) + len(str(i)) + 2   # size of header containing i and i2
            text = data[header:]   # get text from without header
            if encryption is True:
                s.send(txtrsa.encrypt(client_input, peer_pub_key))
            else:
                s.send(client_input.encode())
            ping_end = time.perf_counter()
            ping_time = round((ping_end - ping_start) * 1000)   # calculate ping time in ms
            if client_upload is True:   # if client loaded text from file
                if encryption is True:
                    s.send(txtrsa.encrypt(text_upload, peer_pub_key))
                else:
                    s.send(text_upload.encode())
                client_upload = False
        except Exception:   # if connection is lost
            if text != "" and ask_save is True:
                file_path = fileops.save_txt(text, file_path, tab_spaces)
            s.close()
            exit()



    ###### --Host pygame interface-- ######
    if host is True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                if text != "" and ask_save is True:   # if there is some text
                    file_path = fileops.save_txt(text, file_path, tab_spaces)   # save before load
                conn.close()
                run = False
            if e.type == pygame.KEYDOWN:

                if pygame.key.get_mods() == pygame.KMOD_LCTRL and e.key == pygame.K_s:  # if CTRL+S:
                    file_path = fileops.save_txt(text, file_path, tab_spaces)   # save text to file

                if pygame.key.get_mods() == pygame.KMOD_LCTRL and e.key == pygame.K_l:  # if CTRL+L:
                    if text != "" and ask_save is True:   # if there is some text
                        file_path = fileops.save_txt(text, file_path, tab_spaces)   # save before load
                    text, file_path = fileops.load_txt(tab_spaces)
                    i, i2 = 0, 0

                if e.key == pygame.K_BACKSPACE:
                    backspace = True  # BACKSPACE
                if e.key == pygame.K_LEFT:
                    arrow_l = True   # LEFT arrow
                if e.key == pygame.K_RIGHT:
                    arrow_r = True   # RIGHT arrow
                if e.key == pygame.K_UP:
                    arrow_u = True   # UP arrow
                if e.key == pygame.K_DOWN:
                    arrow_d = True   # DOWN arrow
                if e.key == pygame.K_RETURN:
                    enter = True   # ENTER
                if e.key == pygame.K_TAB:
                    tab = True   # TAB
                if e.unicode in characters:   # if unicode input is in characters set
                    text, i, i2 = editor.input_char(text, i, i2, e.unicode)
                key_trig = True   # some key is presses

            # reset arrow keys states if key is released
            if e.type == pygame.KEYUP:
                backspace = arrow_l = arrow_r = arrow_u = arrow_d = enter = tab = False
                hold = hold_first   # reset delay length after pushing button
                push = True   # reset activation of delay after pushing button
                key_trig = False   # no keys are pressed



        ###### --Host input processing-- ######
        # in client input processing i and i2 have swapped places, here - not
        if key_trig is True:   # if any input key is pressed
            n = blinking_line_off   # make blinking line not blinking
            if hold >= hold_first:   # after delay, do processing
                if arrow_l is True:   # LEFT arrow
                    i = editor.left_arrow(text, i)
                if arrow_r is True:   # RIGHT arrow
                    i = editor.right_arrow(text, i)
                if arrow_u is True:   # UP arrow
                    i = editor.up_arrow(text, i)
                if arrow_d is True:   # DOWN arrow
                    i = editor.down_arrow(text, i)
                if backspace is True:   # BACKSPACE
                    text, i, i2 = editor.backspace(text, i, i2)
                if enter is True:   # ENTER
                    text, i, i2 = editor.enter(text, i, i2)
                if tab is True:   # TAB
                    text, i, i2 = editor.tab(text, i, i2, tab_spaces, tab_spaces_num)
                # delay and repeat after pushing and holding key
                if push is True:   # if this is first iteration:
                    hold = 0   # large delay at start
                    push = False   # stop that from repeating
                else:
                    hold = hold_first - hold_delay   # after that, make delay small
            hold += 1   # iterate delay



    ###### --Client pygame interface-- ######
    else:
        client_input = "/i/"   # reset client input
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                if text != "" and ask_save is True:   # if there is some text
                    file_path = fileops.save_txt(text, file_path, tab_spaces)   # save before load
                s.close()
                run = False
            if e.type == pygame.KEYDOWN:

                if pygame.key.get_mods() == pygame.KMOD_LCTRL and e.key == pygame.K_s:  # CTRL+S
                    file_path = fileops.save_txt(text, file_path, tab_spaces)   # save text to file

                if pygame.key.get_mods() == pygame.KMOD_LCTRL and e.key == pygame.K_l:  # CTRL+L
                    if text != "" and ask_save is True:   # if there is some text
                        file_path = fileops.save_txt(text, file_path, tab_spaces)   # save before load
                    text_upload, file_path = fileops.load_txt(tab_spaces)   # load text from file
                    if file_path != "":   # if there is loaded file
                        client_upload = True   # activate upload of loaded text
                        client_input = "/f/"   # notify host that client will upload

                if e.key == pygame.K_BACKSPACE:
                    client_input_buff = "/b/"   # BACKSPACE
                if e.key == pygame.K_LEFT:
                    client_input_buff = "/l/"   # LEFT arrow
                if e.key == pygame.K_RIGHT:
                    client_input_buff = "/r/"   # RIGHT arrow
                if e.key == pygame.K_UP:
                    client_input_buff = "/u/"   # UP arrow
                if e.key == pygame.K_DOWN:
                    client_input_buff = "/d/"   # DOWN arrow
                if e.key == pygame.K_RETURN:
                    client_input_buff = "/e/"   # ENTER
                if e.key == pygame.K_TAB:
                    client_input_buff = "/t/"   # TAB
                if e.unicode in characters:   # if unicode input is in characters set
                    client_input_buff = e.unicode   # take unicode input from keyboard
                key_trig = True   # some key is presses

            # reset arrow keys states if key is released
            if e.type == pygame.KEYUP:
                hold = hold_first
                push = True
                key_trig = False
                client_input = client_input_buff = "/i/"

        # delay and repeat after pushing and holding key
        if key_trig is True:
            n = blinking_line_off   # make blinking line not blinking
            if hold >= hold_first:   # after delay
                client_input = client_input_buff
                if push is True:   # if this is first iteration:
                    hold = 0   # large delay at start
                    push = False   # stop that from repeating
                else:
                    hold = hold_first - hold_delay   # after that, make delay small
            hold += 1   # iterate delay



    ###### --Client input processing on host-- ######
    # here, i and i2 have swaped places, in host - not
    if host is True:
        if client_input == "/l/":     # LEFT arrow
            i2 = editor.left_arrow(text, i2)
        if client_input == "/r/":     # RIGHT arrow
            i2 = editor.right_arrow(text, i2)
        if client_input == "/u/":     # UP arrow
            i2 = editor.up_arrow(text, i2)
        if client_input == "/d/":   # DOWN arrow
            i2 = editor.down_arrow(text, i2)
        if client_input == "/b/":   # if BACKSPACE
            text, i2, i = editor.backspace(text, i2, i)
        if client_input == "/e/":   # if ENTER
            text, i2, i = editor.enter(text, i2, i)
        if client_input == "/t/":  # if TAB
            text, i2, i = editor.tab(text, i2, i, tab_spaces, tab_spaces_num)
        if client_input in characters:   # if unicode input is in characters set
            text, i2, i = editor.input_char(text, i2, i, client_input)



    ###### --Graphics-- ######
    screen.fill((255, 255, 255))
    graphics.text_wrap(screen, text, (0, 0, screen_w, screen_h), font)

    if n >= blinking_line_off:   # make blinking line invisible
        graphics.blinking_line(screen, host, text, i)
        graphics.blinking_line(screen, host, text, i2, invert=True)
    if n >= blinking_line_off + blinking_line_on:   # make blinking line visible
        n = 0
    n += 1

    if host is False:   # only for client
        graphics.print_ping(screen, (screen_w, screen_h), font, ping_time)

    pygame.display.flip()
    clock.tick(100)
