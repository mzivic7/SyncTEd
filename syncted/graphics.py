import pygame

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


# calculate blinking line position for i
def blinking_line(screen, host, text, i, invert=False):
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
    if host is not invert:   # draw black line for local index
        pygame.draw.line(screen, (0, 0, 0), (line_x, line_y), (line_x, line_y + 19))
    else:   # draw red line for peer index
        pygame.draw.line(screen, (255, 0, 0), (line_x, line_y), (line_x, line_y + 19))

def print_ping(screen, screen_dim, font, ping_time):
    screen_w, screen_h = screen_dim
    if ping_time < 50:   # print green ping
        screen.blit(font.render(str(ping_time) + "ms", True, (100, 200, 100)), (screen_w - 50, screen_h - 21))
    elif ping_time > 100:   # print red ping
        screen.blit(font.render(str(ping_time) + "ms", True, (200, 50, 50)), (screen_w - 50, screen_h - 21))
    else:   # print orange ping
        screen.blit(font.render(str(ping_time) + "ms", True, (200, 100, 50)), (screen_w - 50, screen_h - 21))
