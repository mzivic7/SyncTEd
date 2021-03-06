# return list with newline locations in text
def locate_newline(text):
    loc = 0
    loc_prev = 0
    newline_loc = []   # location of newline signs
    while loc != -1:   # while there is location
        loc = text.find(" /n ", loc_prev)   # find location of "/n" from previous one
        loc_prev = loc + 4   # location of previous "/n" without it
        if loc != -1:   # if there is found "/n"
            newline_loc.append(loc)  # append it to list
    return newline_loc

# LEFT arrow
def left_arrow(text, i):
    if text[i-4:i] == " /n ":   # if "/n" is on the way:
        i -= 4   # jump over it
    else:
        if i >= 1:   # if it is not start of string
            i -= 1    # move i left
    return i
            
# RIGHT arrow
def right_arrow(text, i):
    if text[i:i+4] == " /n ":   # if "/n" is on the way:
        i += 4   # jump over it
    else:
        if i < len(text):   # if it is not end of line
            i += 1    # move i right
    return i
            
# UP arrow
def up_arrow(text, i):
    closest_newline = 0
    second_closest = 0
    newline_loc = locate_newline(text)   #locate newlines
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
    return i

# DOWN arrow
def down_arrow(text, i):
    closest_newline = 0
    second_closest = 0
    closest_num = 0
    newline_loc = locate_newline(text)   #locate newlines
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
    return i

# BACKSPACE
def backspace(text, i, i2):
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
    return text, i, i2

# ENTER
def enter(text, i, i2):
    text = text[:i] + " /n " + text[i:]
    if i < i2:   # if i is smaller than i2
        i2 += 4   # move i2 4 character right
    i += 4    # move i right
    return text, i, i2

# TAB
def tab(text, i, i2, tab_spaces, tab_spaces_num):
    text = text[:i] + tab_spaces + text[i:]   # write tab as spaces
    if i < i2:   # if i is smaller than i2
        i2 += tab_spaces_num   # move i2 right
    i += tab_spaces_num   # move i right
    return text, i, i2

# UNICODE
def input_char(text, i, i2, char):
    text = text[:i] + char + text[i:]   # take unicode input from keyboard
    if i2 > i:   # if i is smaller than i2
        i2 += 1   # move i2 right
    i += 1   # move i right
    return text, i, i2
    
