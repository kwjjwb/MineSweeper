# made by wbjkwjj

import pygame as pg
import numpy as np
import time
from datetime import datetime
import os
if not os.path.exists('record.txt'):
    with open('record.txt','w') as f:
        pass

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
default_color = (0,176,80)
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

# other buttons (basic, boom, flag, etc.)
button = pg.image.load('images/button5.png')
button = pg.transform.scale(button,(35,35))

img_boom = pg.transform.scale(pg.image.load('images/boom.png'),(35,35))
img_boom_selected = pg.transform.scale(pg.image.load('images/selected_boom.png'),(35,35))
img_flag = pg.transform.scale(pg.image.load('images/button5_flag.png'),(35,35))

# by,bx = 25,20
# NUM_MINES = 100 # set number of mines
pg.display.set_caption("Minesweeper") # set title
done = False



clock = pg.time.Clock()
class MineSweeper:
    class Button:
        def __init__(self,y,x):
            self.Y = y # pixel pos
            self.X = x
            # self.y = y // 35 # xy pos
            # self.x = x // 35
            self.num = -1
            self.flag = False
            self.mine = False
            self.selected_mine = False
            self.clicked = False
            self.closed = True # whether the button is open or not
        
        def display(self,screen,pressed_mine,all_mines_found):
            # global pressed_mine,all_mines_found
            if self.selected_mine:
                screen.blit(img_boom_selected,(self.Y,self.X)) # selected boom!
            elif pressed_mine and self.flag:
                screen.blit(img_flag,(self.Y,self.X)) # flag at boom
            elif all_mines_found and self.mine:
                screen.blit(img_flag,(self.Y,self.X))
            elif pressed_mine and self.mine: 
                screen.blit(img_boom,(self.Y,self.X)) # boom!
            elif self.closed and self.flag: 
                screen.blit(img_flag,(self.Y,self.X)) # flag at normal
            elif self.closed and not self.clicked: 
                screen.blit(button,(self.Y,self.X)) # normal unclicked
            elif self.closed and self.clicked:
                pg.draw.rect(screen,default_color,[self.Y,self.X,35,35],0)
            else: 
                screen.blit(numbers[self.num],(self.Y+10,self.X))

    def __init__(self,size_y,size_x):
        self.y = size_y # width
        self.x = size_x # height
        self.screen = pg.display.set_mode([35*self.y,35*self.x+100])
        pg.display.set_caption("Minesweeper")
        self.buttons = [[0 for _ in range(self.x)] for _ in range(self.y)]
        self.NUM_MINES = int(self.y*self.x*0.2)
        self.mine_left = self.NUM_MINES
        self.curr = time.time()
        self.START_TIME = 0
        self.time_taken = 0
        self.finished = False
        self.all_mines_found = True # cleared?
        self.pressed_mine = False
        self.cur_x = -1
        self.cur_y = -1
        
        mine_ind = np.random.choice(self.y*self.x, self.NUM_MINES, replace=False)
        
        # create buttons
        for j in range(0,self.y*35,35):
            for i in range(0,self.x*35,35):
                self.buttons[j//35][i//35] = self.Button(j,i)
        
        # set mines        
        for mine_num in mine_ind:
            j,i = mine_num // self.x, mine_num % self.x
            self.buttons[j][i].mine = True
            # print(f'{j} {i} mined')
            
        for mine_num in mine_ind:
            j,i = mine_num // self.x, mine_num % self.x
            # print(self.buttons[j][i].mine)

            
        def in_range(y,x):
            return y >= 0 and y < self.y and x >= 0 and x < self.x
        def adj(y,x):
            lst = []
            for dy in [-1,0,1]:
                for dx in [-1,0,1]:
                    if dy == 0 and dx == 0: continue
                    lst.append((y+dy,x+dx))
            return lst
        
        # calculate number of mines around
        for j in range(self.y):
            for i in range(self.x):
                cnt = 0
                for ny,nx in adj(j,i):
                    if in_range(ny,nx):
                        if self.buttons[ny][nx].mine:
                            # print("counted")
                            cnt += 1
                    # print(self.buttons[j][i].mine)
                self.buttons[j][i].num = cnt
                # print(j,i,cnt)
    
    def set_mine(self,y,x):
        self.buttons[y][x].mine = True
        
    def has_flag(self,y,x):
        return self.buttons[y][x].flag
    
    def set_flag(self,y,x):
        if self.is_closed(y,x):
            if self.has_flag(y,x): 
                self.buttons[y][x].flag = False
                self.mine_left += 1
            else: 
                self.buttons[y][x].flag = True
                self.mine_left -= 1
    
    def click(self,y,x):
        self.buttons[y][x].clicked = True
        
    def unclick(self,y,x):
        self.buttons[y][x].clicked = False
    
    def has_mine(self,y,x):
        return self.buttons[y][x].mine
    
    def is_closed(self,y,x):
        return self.buttons[y][x].closed
    
    
    def dig(self,y,x):
        # digs current area
        # if there is no mine around here, digs adjacent area recursively
        # until some is found around
        def in_range(y,x):
            return y >= 0 and y < self.y and x >= 0 and x < self.x
        def adj(y,x):
            lst = []
            for dy in [-1,0,1]:
                for dx in [-1,0,1]:
                    if dy != 0 or dx != 0:
                        lst.append((y+dy,x+dx))
            return lst
        
        if self.has_mine(y,x):
            self.buttons[y][x].closed = False
            # digged the mine! 
            self.pressed_mine = True
            self.buttons[y][x].selected_mine = True 
            # display all 
            return
        elif self.buttons[y][x].num != 0 and self.buttons[y][x].closed: # pressed the tile and that was a number tile
            self.buttons[y][x].closed = False
            return
        elif self.buttons[y][x].num != 0: # pressed the number tile that was open
            flag_cnt = 0
            for ny,nx in adj(y,x):
                if in_range(ny,nx):
                    if self.has_flag(ny,nx): flag_cnt += 1
            if flag_cnt < self.buttons[y][x].num: return
            for ny,nx in adj(y,x):
                if in_range(ny,nx):
                    if self.is_closed(ny,nx) and not self.has_flag(ny,nx):
                        self.dig(ny,nx)
        else: # pressed the empty tile
            self.buttons[y][x].closed = False
            for ny,nx in adj(y,x):
                if in_range(ny,nx):
                    if self.is_closed(ny,nx) and not self.has_flag(ny,nx):
                        self.dig(ny,nx)
       
    def display_board(self):
        
        self.screen.fill(default_color)
        
        self.all_mines_found = True
        for j in range(self.y):
            for i in range(self.x):
                if not self.has_mine(j,i) and self.is_closed(j,i):
                    self.all_mines_found = False
        for j in range(self.y):
            for i in range(self.x):
                self.buttons[j][i].display(self.screen,self.pressed_mine,self.all_mines_found)
                    
        
        # if all mines are found, measures how much time it taked to complete
        if self.all_mines_found and not self.finished:
            self.time_taken = time.time()-self.curr
            with open('record.txt','a') as f:
                f.write("%-30s%s\n"%(
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    str(int(self.time_taken))+"seconds"
                ))
            self.finished = True
        pg.draw.rect(self.screen,black,[0,35*self.x,35*self.y,100])
        
        # if the game is not finished, displays time elapsed and number of mines left consistently
        # else, displays congratulating phrase with measured time
        if not self.all_mines_found:
            self.screen.blit(myfont.render(f'Time elapsed: {int(time.time()-self.curr)}',True,white),(0,35*self.x))
            if not self.pressed_mine: self.screen.blit(myfont.render(f'Mines left: {self.mine_left}',True,white),(0,35*self.x+50)) # prev: 35*y-250
            else: self.screen.blit(myfont.render(f'Booom!!! Too bad:(',True,white),(0,35*self.x+50))
        else:
            self.screen.blit(myfont.render(f'Well done!!:D',True,white),(0,35*self.x))
            self.screen.blit(myfont.render(f'Time taken: {int(self.time_taken)}',True,white),(0,35*self.x+50))
            
    
        
        




game_y,game_x = 30,25 # width, height    
game = MineSweeper(game_y,game_x)    

while not done:
    clock.tick(10)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if not game.all_mines_found and not game.pressed_mine:
                MY,MX = pg.mouse.get_pos()
                my,mx = MY // 35, MX // 35
                if my >= 0 and my < game.y and mx >= 0 and mx < game.x:
                    if not game.has_flag(my,mx):
                        game.cur_y,game.cur_x = my,mx
                        game.click(game.cur_y,game.cur_x)
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            # left click then dig
            game.unclick(game.cur_y,game.cur_x)
            if not game.all_mines_found and not game.pressed_mine:
                MY,MX = pg.mouse.get_pos()
                my,mx = MY // 35, MX // 35
                if my >= 0 and my < game.y and mx >= 0 and mx < game.x:
                    if not game.has_flag(my,mx):
                        game.dig(my,mx)
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
            # right click then flag
            if not game.all_mines_found and not game.pressed_mine:
                MY,MX = pg.mouse.get_pos()
                my,mx = MY // 35, MX // 35
                if my >= 0 and my < game.y and mx >= 0 and mx < game.x:
                    game.set_flag(my,mx)
        elif event.type == pg.KEYUP and event.key == pg.K_SPACE:
            # if 'n' button is pressed, start new game
            game = MineSweeper(game_y,game_x)
        
    game.display_board()
    pg.display.flip()
    
pg.quit()


