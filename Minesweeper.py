# made by wbjkwjj

import pygame as pg
import numpy as np
import time
from datetime import datetime
import os
TXT_LST = ['record.txt','save.txt']
for txt in TXT_LST:
    if os.path.exists(txt): os.chmod(txt,128) # unlock

if not os.path.exists('record.txt'):
    with open('record.txt','w') as f:
        pass
    
record_dict = {
    "3025": [],
    "2520": [],
    "2020": [],
    "2015": []    
}

with open('record.txt','r') as f:
    while True:
        s = f.readline()
        if not s: break
        date, time, taken, gy, _, gx = s.split()
        if gy == "30" and gx == "25":
            record_dict["3025"].append((date + " " + time, taken))
        elif gy == "25" and gx == "20":
            record_dict["2520"].append((date + " " + time, taken))
        elif gy == "20" and gx == "20":
            record_dict["2020"].append((date + " " + time, taken))
        elif gy == "20" and gx == "15":
            record_dict["2015"].append((date + " " + time, taken))
# 30,25 (150 mines)
# 25,20 (100 mines)
# 20,20 (80 mines )
# 20,15 (45 mines )
'''        
score tab
recent score
size1,size2,..
best score
size1,size2,..
'''

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
myfont_help = pg.font.Font("EliceDigitalBaeum_Bold.ttf",20)
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
gorani = pg.transform.scale(pg.image.load('images/gorani.png'),(100,100))
gorani_boom = pg.transform.scale(pg.image.load('images/gorani_boom.png'),(100,100))
gorani_love = pg.transform.scale(pg.image.load('images/gorani_love.png'),(100,100))
# gorani = pg.image.load('images/gorani.png')
# img_boom = pg.transform.scale(pg.image.load('images/gorani_boom.png'),(35,35))
img_boom = pg.transform.scale(pg.image.load('images/boom.png'),(35,35))
# img_boom_selected = pg.transform.scale(pg.image.load('images/gorani_boom_selected.png'),(35,35))
img_boom_selected = pg.transform.scale(pg.image.load('images/selected_boom.png'),(35,35))
img_flag = pg.transform.scale(pg.image.load('images/button5_flag.png'),(35,35))

# by,bx = 25,20
# NUM_MINES = 100 # set number of mines
pg.display.set_caption("Minesweeper") # set title
done = False
'''
inside save file:
by,bx,mine_ratio,mine_left,choice,finished,time_taken,pressed_mine,all_mines_found

for every y_ind,x_ind:
    y_ind,x_ind, num,flag,mine,selected_mine,clicked,closed
'''


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

    def __init__(self,size_y,size_x,mine_ratio):
        self.y = size_y # width
        self.x = size_x # height
        self.mine_ratio = mine_ratio
        self.screen = pg.display.set_mode([35*self.y,35*self.x+100])
        pg.display.set_caption("Minesweeper")
        self.buttons = [[0 for _ in range(self.x)] for _ in range(self.y)]
        self.NUM_MINES = int(self.y*self.x*self.mine_ratio)
        self.mine_left = self.NUM_MINES
        self.curr = time.time()
        self.START_TIME = 0
        self.time_taken = 0
        self.finished = False
        self.all_mines_found = True # cleared?
        self.pressed_mine = False
        self.cur_x = -1
        self.cur_y = -1
        self.temp_time = 0
        self.loaded = False
        self.saved = False
        
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
       
    def display_board(self,paused):
        # temp_time = 0
        
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
                f.write("%-30s %-20s %d x %d\n"%(
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    str(int(self.time_taken)),
                    self.y,self.x
                ))
            self.finished = True
        pg.draw.rect(self.screen,black,[0,35*self.x,35*self.y,100])
        self.screen.blit(myfont.render(f'Made by wbjkwjj',True,white),(35*self.y-250,35*self.x+50))
        # myfont_help = pg.font.Font("EliceDigitalBaeum_Bold.ttf",17)
        # self.screen.blit(myfont_help.render(f's  key: save',True,white),(35*self.y-130,35*self.x))
        # self.screen.blit(myfont_help.render(f'p  key: pause',True,white),(35*self.y-140,35*self.x+20))
        # if the game is not finished, displays time elapsed and number of mines left consistently
        # else, displays congratulating phrase with measured time
        if not self.all_mines_found:
            if not paused: 
                self.screen.blit(myfont.render(f'Time elapsed: {int(time.time()-self.curr)}',True,white),(0,35*self.x))
                self.temp_time = int(time.time()-self.curr)
            else:
                self.screen.blit(myfont.render(f'Time elapsed: {self.temp_time}',True,white),(0,35*self.x))
            if not self.pressed_mine: self.screen.blit(myfont.render(f'Mines left: {self.mine_left}',True,white),(0,35*self.x+50)) # prev: 35*y-250
            else: self.screen.blit(myfont.render(f'Booom!!! Too bad:(',True,white),(0,35*self.x+50))
        else:
            self.screen.blit(myfont.render(f'Well done!!:D',True,white),(0,35*self.x))
            self.screen.blit(myfont.render(f'Time taken: {int(self.time_taken)}',True,white),(0,35*self.x+50))
    
    def save_current_game(self):
        '''
        inside save file:
        by,bx,mine_left,finished,time_taken,pressed_mine,all_mines_found

        for every y_ind,x_ind:
            y_ind,x_ind, num,flag,mine,selected_mine,clicked,closed
        '''
        self.saved = True
        with open('save.txt','w') as f:
            f.write("%d %d\n"
                    %(self.y,self.x)
                    )
            f.write("%f\n"
                    %(self.mine_ratio)
                    )
            f.write("%d %d\n"
                    %(self.mine_left,(time.time()-self.curr)) # _, time_elapsed
                    )
            f.write("%d %d %d\n"
                    %(int(self.finished),
                      int(self.pressed_mine),
                      int(self.all_mines_found))
                    )
            for j in range(self.y):
                for i in range(self.x):
                    e = self.buttons[j][i]
                    f.write("%d %d %d %d %d %d %d %d\n"
                            %(j,i,e.num,int(e.flag),
                              int(e.mine),int(e.selected_mine),
                              int(e.clicked),int(e.closed))
                            )

def load_saved_game(file_path):
    ret = None
    with open(file_path,'r') as f:
        y,x = map(int,f.readline().strip().split())
        mine_ratio = float(f.readline().strip())
        ret = MineSweeper(y,x,mine_ratio)
        ret.mine_left,ret.time_taken = map(int,f.readline().strip().split())
        ret.finished,ret.pressed_mine,ret.all_mines_found = map(lambda x:bool(int(x)),f.readline().strip().split())
        ret.curr -= ret.time_taken
        ret.loaded = True
        while True:
            line = f.readline().strip()
            if not line: break
            j,i,num,flag,mine,s_mine,clicked,closed = map(int,line.split())
            ret.buttons[j][i].num = num
            ret.buttons[j][i].flag = bool(flag)
            ret.buttons[j][i].mine = bool(mine)
            ret.buttons[j][i].selected_mine = bool(s_mine)
            ret.buttons[j][i].clicked = bool(clicked)
            ret.buttons[j][i].closed = bool(closed)
    return ret
            
            
        
            
    
        
        


# 30,25 (150 mines)
# 25,20 (100 mines)
# 20,20 (80 mines )
# 20,15 (45 mines )
# game_y,game_x = 30,25 # width, height    
# game = MineSweeper(game_y,game_x)
screen = pg.display.set_mode([500,600])    

txt_title = myfont.render('Minesweeper!',True,black)

choice,save_tick,paused_time,load_error_tick = 0,0,0,0
saved,paused,load_error = False,False,False

txt_saved = myfont_num.render('saved',True,white)
txt_paused = myfont_num.render('paused',True,white)

MODE_START,MODE_GAME,MODE_HELP,MODE_SCORE = 0,1,2,3
MODE = MODE_START

while not done:
    clock.tick(10)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
        elif MODE == MODE_START:
            # screen = pg.display.set_mode([500,500])
            screen.fill(white)
            screen.blit(gorani,(300,35))
            screen.blit(myfont.render('Minesweeper!',True,black),(95,60))
            screen.blit(myfont.render('Select map',True,black),(150,150))
            screen.blit(myfont.render('20 x 15 (45 mines)',True,black),(100,200))
            screen.blit(myfont.render('20 x 20 (80 mines)',True,black),(100,250))
            screen.blit(myfont.render('25 x 20 (100 mines)',True,black),(100,300))
            screen.blit(myfont.render('25 x 25 (125 mines)',True,black),(100,350))
            screen.blit(myfont.render('Load game',True,black),(100,400))
            screen.blit(myfont.render('Help',True,black),(100,450))
            screen.blit(myfont.render('Scores',True,black),(100,500))
            screen.blit(myfont.render(f'Made by wbjkwjj',True,black),(250,550))
            if event.type == pg.KEYDOWN and event.key == pg.K_DOWN:
                choice = (choice + 1) % 7
            elif event.type == pg.KEYDOWN and event.key == pg.K_UP:
                choice = (choice - 1) % 7
            screen.blit(myfont.render('★',True,black),(60,200+50*choice))
            if load_error:
                screen.blit(myfont.render('no saved file',True,red),(270,400))
                load_error_tick += 2
            if load_error_tick == 6:
                load_error_tick = 0
                load_error = False
            if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                if choice == 0:
                    game_y,game_x,mine_ratio = 20,15,0.015
                elif choice == 1:
                    game_y,game_x,mine_ratio = 20,20,0.02
                elif choice == 2:
                    game_y,game_x,mine_ratio = 25,20,0.02
                elif choice == 3:
                    game_y,game_x,mine_ratio = 25,25,0.02
                elif choice == 4:
                    try:
                        game = load_saved_game('save.txt')
                        MODE = MODE_GAME
                    except:
                        load_error = True
                        load_error_tick = 0
                elif choice == 5:
                    MODE = MODE_HELP
                    # help_screen = True
                elif choice == 6:
                    MODE = MODE_SCORE
                if choice < 4:
                    game = MineSweeper(game_y,game_x,mine_ratio)
                    MODE = MODE_GAME
                if load_error: MODE = MODE_START
                # if not load_error:
                #     # starting_screen = False
                #     if choice <= 4: MODE = MODE_GAME
        elif MODE == MODE_HELP:
            screen.fill(white)
            screen.blit(myfont_help.render('- Press p key to pause game',True,black),(20,90))
            screen.blit(myfont_help.render('- Press p key to resume paused game',True,black),(20,120))
            screen.blit(myfont_help.render('- Press s key to save current game',True,black),(20,150))
            screen.blit(myfont_help.render('- You can play saved game later through',True,black),(20,180))
            screen.blit(myfont_help.render('   \'Load game\'',True,black),(20,210))
            screen.blit(myfont_help.render('- Note that current saved game(or current',True,black),(20,240))
            screen.blit(myfont_help.render('   loaded game) will be cleared up if mine is',True,black),(20,270))
            screen.blit(myfont_help.render('   pressed',True,black),(20,300))
            screen.blit(myfont_help.render('- Press backspace key to move to previous page',True,black),(20,330))
            screen.blit(myfont_help.render('- Press space key to start different game',True,black),(20,360))
            screen.blit(myfont_help.render('   with current size',True,black),(20,390))
            screen.blit(myfont_help.render('Good luck!',True,black),(70,490))
            screen.blit(gorani_love,(0,500))
            screen.blit(myfont.render(f'Made by wbjkwjj',True,black),(250,550))
            if event.type == pg.KEYDOWN and (event.key == pg.K_BACKSPACE or event.key == pg.K_ESCAPE):
                # help_screen = False
                # starting_screen = True
                MODE = MODE_START
                
        elif MODE == MODE_SCORE:
            screen.fill(white)
            screen.blit(myfont_help.render(' <recent score>',True,black),(0,20))
            screen.blit(myfont_help.render("%-10s"%("game size"),True,black),(0,50))
            
            if event.type == pg.KEYDOWN and (event.key == pg.K_BACKSPACE or event.key == pg.K_ESCAPE):
                # help_screen = False
                # starting_screen = True
                MODE = MODE_START
            
            
                
        
        elif MODE == MODE_GAME:
            if not paused:    
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
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
                
                elif event.type == pg.KEYDOWN and (event.key == pg.K_BACKSPACE or event.key == pg.K_ESCAPE):
                    # if space button is pressed, start new game
                    # starting_screen = True
                    MODE = MODE_START
                    screen = pg.display.set_mode([500,600])
            

                elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    y,x,mine_ratio = game.y,game.x,game.mine_ratio
                    # print(y,x,mine_ratio)
                    game = MineSweeper(y,x,mine_ratio)
                
                elif event.type == pg.KEYDOWN and event.key == pg.K_s:
                    game.save_current_game()
                    saved = True
                
            if event.type == pg.KEYDOWN and event.key == pg.K_p:
                if not paused:
                    paused = True
                    paused_time = time.time()
                else:
                    paused = False
                    game.curr += (time.time()-paused_time)
            
            
        
    if MODE == MODE_GAME:
        game.display_board(paused)
        if saved:
            game.screen.blit(txt_saved,((35*game.y)//2 - 50,35*game.x))
            save_tick += 1
            # print("saved")
        if save_tick == 10:
            save_tick = 0
            saved = False
            # print("saved erased")
        if game.pressed_mine:
            if game.loaded or game.saved: 
                if os.path.exists('save.txt'): os.remove('save.txt')
        if paused:
            game.screen.blit(txt_paused,((35*game.y)//2 - 50,35*game.x+50))
    pg.display.flip()

# make additional button to explain keys
for txt in TXT_LST:
    if os.path.exists(txt):os.chmod(txt,256) # lock
pg.quit()

# stat.S_IRUSR (256) -> OWNER HAS READ PERMISSION (LOCK)
# stat.S_IWUSR (128) -> OWNER HAS WRITE PERMISSION (UNLOCK)