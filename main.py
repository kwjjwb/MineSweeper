# made by wbjkwjj

import pygame as pg
import numpy as np
import time
# start!
pg.init()

# color settings
black = (0,0,0)
white = (255,255,255)
blue = (0,0,255)
green = (0,255,0)
red = (255,0,0)
sky = (48,200,248)
brown = (168,88,0)
purple = (144,96,248)
neat_white = (200,248,248)
mango = (248,192,0)
dark_pink = (248,0,248)
dark_indigo = (0,152,152)
default_color = (0,169,0)

# font
myfont = pg.font.Font("EliceDigitalBaeum_Bold.ttf",30)
myfont_num = pg.font.Font("EliceDigitalBaeum_Bold.ttf",23)
txt_test = myfont.render("Hello World!",True,black)

# number displays 
numbers = [
    myfont_num.render('0',True,default_color),
    myfont_num.render('1',True,sky),
    myfont_num.render('2',True,neat_white),
    myfont_num.render('3',True,red),
    myfont_num.render('4',True,blue),
    myfont_num.render('5',True,brown),
    myfont_num.render('6',True,dark_pink),
    myfont_num.render('7',True,mango),
    myfont_num.render('8',True,dark_indigo)
]

size = [700,750]
screen = pg.display.set_mode(size)

# other buttons (basic, boom, flag, etc.)
button = pg.image.load('images/button4.png')
button = pg.transform.scale(button,(35,35))

img_boom = pg.transform.scale(pg.image.load('images/boom.png'),(35,35))
img_flag = pg.transform.scale(pg.image.load('images/button_flag.png'),(35,35))


NUM_MINES = 80 # set number of mines
pg.display.set_caption("Minesweeper") # set title
done = False



clock = pg.time.Clock()
class Button:
    def __init__(self,y,x):
        self.Y = y # pixel pos
        self.X = x
        self.y = y // 35 # xy pos
        self.x = x // 35
        self.num = -1
        self.flag = False
        self.mine = False
        self.closed = True # whether the button is open or not
    
    def display(self):
        global pressed_mine
        if pressed_mine and self.mine: 
            screen.blit(img_boom,(self.Y,self.X))
        elif self.closed and self.flag: 
            screen.blit(img_flag,(self.Y,self.X))
        elif self.closed: 
            screen.blit(button,(self.Y,self.X))
        else: 
            screen.blit(numbers[self.num],(self.Y+10,self.X))


    def set_mine(self):
        self.mine = True
    
    def has_flag(self):
        return self.flag
    
    def set_flag(self):
        global mine_left
        if not self.flag: 
            self.flag = True
            mine_left -= 1
        else: 
            self.flag = False
            mine_left += 1
    
    def has_mine(self):
        return self.mine
    
    def is_closed(self):
        return self.closed
    
    def detect_around(self):
        # calculates number of mines around here
        cnt = 0
        def in_range(y,x):
            return y >= 0 and y < 20 and x >= 0 and x < 20
        def adj(y,x):
            lst = []
            for dy in [-1,0,1]:
                for dx in [-1,0,1]:
                    if dy != 0 or dx != 0:
                        lst.append((y+dy,x+dx))
            return lst
        
        for ny,nx in adj(self.y,self.x):
            if in_range(ny,nx):
                if buttons[ny][nx].has_mine(): cnt += 1
        self.num = cnt
    
    def dig(self):
        # digs current area
        # if there is no mine around here, digs adjacent area recursively
        # until some is found around
        global pressed_mine
        def in_range(y,x):
            return y >= 0 and y < 20 and x >= 0 and x < 20
        def adj(y,x):
            lst = []
            for dy in [-1,0,1]:
                for dx in [-1,0,1]:
                    if dy != 0 or dx != 0:
                        lst.append((y+dy,x+dx))
            return lst
        if self.mine:
            self.closed = False
            # digged the mine! 
            pressed_mine = True
            # display all 
            return
        elif self.num != 0 and not self.closed:
            for ny,nx in adj(self.y,self.x):
                if in_range(ny,nx):
                    if buttons[ny][nx].is_closed() and not buttons[ny][nx].has_flag():
                        buttons[ny][nx].dig()
        elif self.num != 0:
            self.closed = False
            return
        else:
            self.closed = False
            for ny,nx in adj(self.y,self.x):
                if in_range(ny,nx):
                    if buttons[ny][nx].is_closed() and not buttons[ny][nx].has_flag():
                        buttons[ny][nx].dig()

# intialize all related variables                       
buttons = [[0 for _ in range(20)] for _ in range(20)]
pressed_mine = False
all_mines_found = False
curr = time.time()
mine_left = NUM_MINES
finished = False
time_taken = 0

def initialize():
    # initialize current situation
    global buttons,pressed_mine,all_mines_found,curr,mine_left,finished,time_taken
    buttons = [[0 for _ in range(20)] for _ in range(20)]
    
    # create buttons
    mine_ind = np.random.choice(400, NUM_MINES, replace=False)
    for j in range(0,700,35):
        for i in range(0,700,35):
            buttons[j//35][i//35] = Button(j,i)
    # set mines        
    for mine_num in mine_ind:
        y,x = mine_num // 20, mine_num % 20
        buttons[y][x].set_mine()
    
    pressed_mine = False
    all_mines_found = False
    curr = time.time()
    mine_left = NUM_MINES
    finished = False
    time_taken = 0

    # calculate number of mines around
    for j in range(20):
        for i in range(20):
            buttons[j][i].detect_around()
    
def display_board():
    #displaying function
    global mine_left,pressed_mine,all_mines_found,curr,finished,time_taken
    screen.fill(default_color)

    check_cnt = 0
    # checks if all mines are successfully flagged
    for j in range(20):
        for i in range(20):
            if buttons[j][i].has_flag() and buttons[j][i].has_mine():
                check_cnt += 1
            buttons[j][i].display()
    all_mines_found = check_cnt == NUM_MINES
    
    # if all mines are found, measures how much time it taked to complete
    if all_mines_found and not finished:
        time_taken = time.time()-curr
        finished = True
    pg.draw.rect(screen,white,[0,700,700,50])
    
    # if the game is not finished, displays time elapsed and number of mines left consistently
    # else, displays congratulating phrase with measured time
    if not all_mines_found:
        screen.blit(myfont.render(f'Time elapsed: {int(time.time()-curr)}',True,black),(0,700))
        if not pressed_mine: screen.blit(myfont.render(f'Mine left: {mine_left}',True,black),(350,700))
        else: screen.blit(myfont.render(f'Booom!!! Too bad:(',True,black),(350,700))
    else:
        elapsed = time.time()
        screen.blit(myfont.render(f'Well done!!:D',True,black),(0,700))
        screen.blit(myfont.render(f'Time taken: {int(time_taken)}',True,black),(350,700))


    
initialize()    

while not done:
    clock.tick(10)
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            # left click then dig
            if not all_mines_found and not pressed_mine:
                MY,MX = pg.mouse.get_pos()
                my,mx = MY // 35, MX // 35
                if my >= 0 and my < 20 and mx >= 0 and mx < 20:
                    if not buttons[my][mx].has_flag():
                        buttons[my][mx].dig()
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
            # right click then flag
            if not all_mines_found and not pressed_mine:
                MY,MX = pg.mouse.get_pos()
                my,mx = MY // 35, MX // 35
                if my >= 0 and my < 20 and mx >= 0 and mx < 20:
                    buttons[my][mx].set_flag()
        elif event.type == pg.KEYUP and event.key == pg.K_n:
            # if 'n' button is pressed, start new game
            initialize()
        
    display_board()
    pg.display.flip()
    
pg.quit()


