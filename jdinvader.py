import os
import msvcrt
import winsound
import time

fps = 0
stopme = False

def map_range(old_value, old_min, old_max, new_min, new_max):
    return int((((old_value - old_min) * (new_max - new_min)) / (old_max - old_min)) + new_min)

def asciiRGB(r,g,b):
    r = map_range(r, 0, 255, 0, 5)
    g = map_range(g, 0, 255, 0, 5)
    b = map_range(b, 0, 255, 0, 5)
    return (f'\x1b[38;5;{16+(36 * r)+(6*g+b)}m')

def asciiRGB_BC(r,g,b):
    r = map_range(r, 0, 255, 0, 5)
    g = map_range(g, 0, 255, 0, 5)
    b = map_range(b, 0, 255, 0, 5)
    return (f'\x1b[48;5;{16+(36 * r)+(6*g+b)}m')

def setcurser(on: bool):
    if on:
        print('\033[?25h', end="")
    else:
        print('\033[?25l', end="")

def hit(a, b, w, h):
    return ((a.y >= b.y and a.y < (b.y + h)) and (a.x+(w/2)) >= b.x and (a.x+(w/2)) < (b.x + w) and b.visible == True)

class canvas:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.fc = ''
        self.bc = ''
        self.visible = True
        os.terminal_size((w,h))

    def forecolor(self, c):
        self.fc = c

    def backcolor(self, c):
        self.bc = c

    def pos(self, x, y):
        print(f'\x1b[{y};{x}H', end='', flush=True)

    def set_char(self, x, y, ch):
        self.pos(x, y)
        self.write(chr(ch))

    def write(self, text):
        print(self.fc + text, end='', flush=True)

    def swap(self):
        pass

    def cls(self):
        os.system ('cls')

class texture:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.frame = 0
        self.c = ''
        self.vis = False
        self.textures = []
    
    def fill(self, c, data):
        self.c = c
        self.textures.append(data)
        self.frame += 1

    def draw(self):
        s = self.textures[self.frame]
        print(f'\x1b[{self.y};{self.x}H' + self.c + s[:self.w] + f'\x1b[{self.y+1};{self.x}H' + s[self.w:], end='', flush=True)

    def frame(self, f):
        self.frame = f

    def move(self, x, y):
        self.x = x
        self.y = y

    def pos(self, x, y):
        self.x = x
        self.y = y

    def visible(self, v):
        self.vis = v

class sprite:
    def __init__(self, myprite, x, y):
        self.sprite = myprite
        self.x = x
        self.y = y
        self.ix = x
        self.iy = y
        self.visible = True
        self.direction = 1

    def draw(self, frame):
        self.sprite.frame = frame
        self.sprite.pos(self.x,self.y)
        self.sprite.draw()

    def move(self, x,y):
        self.x = self.x + x
        self.y = self.y + y
        self.sprite.move(x,y)

    def die(self):
        self.visible = False
        self.sprite.visible(False)

class alien(sprite):
    num = 0

    def __init__(self, myprite, x, y, points):
        sprite.__init__(self, myprite, x, y)
        self.points = points
        alien.num += 1

    def die(self):
        sprite.die(self)
        #winsound.PlaySound("DIE.WAW", winsound.SND_ALIAS)
        return self.points

class block(sprite):
    num = 0

    def __init__(self, myprite, x, y):
        sprite.__init__(self, myprite, x, y)
        self.frame = 0
        block.num += 1

    def hit(self):
        self.frame +=1
        if (self.frame>2):
            self.die()

    def die(self):
        sprite.die(self)
        #winsound.PlaySound("DIE.WAW", winsound.SND_ALIAS)
        return 1

class player(sprite):
    def __init__(self, myprite, x, y):
        sprite.__init__(self, myprite, x, y)
        self.speed = 1
        self.respawn = 0

    def step(self):
        self.respawn -= 1
        if (self.respawn==1):
            self.visible = True
            self.sprite.visible(True)

    def die(self):
        #winsound.PlaySound("DIE.WAW", winsound.SND_ALIAS)
        sprite.die(self)
        self.respawn = 10
        return 1

class player_missile(sprite):
    def __init__(self, myprite, x, y):
        sprite.__init__(self, myprite, x, y)
        self.isshooting = False
        self.visible = False
    
    def fire(self, x, y):
        self.x = x
        self.y = y - 8
        self.direction = -4
        self.visible = True
        self.isshooting = True

    def die(self):
        sprite.die(self)
        self.isshooting = False

    def step(self, aliens, miny):
        self.move(0,self.direction)
        points = 0
        for a in aliens:
            if (hit(self, a, 5, 2)):
                points = points + a.die()
        if (points>0 or self.y < miny):
            self.die()
        return points

class alien_missile(sprite):
    def __init__(self, myprite, x, y):
        sprite.__init__(self, myprite, x, y)
        self.isshooting = False
        self.visible = False
    
    def fire(self, x, y):
        self.x = x
        self.y = y + 8
        self.direction = 3
        self.visible = True
        self.isshooting = True

    def die(self):
        sprite.die(self)
        self.isshooting = False

    def step(self, player, blocks, miny):
        dead = 0
        self.move(0,self.direction)
        for b in blocks:
            if (b.visible):
                if (hit(self, b , 5, 2)):
                    b.hit()
                    self.die()
        if (hit(self, player, 5, 2)):
            dead = player.die()
            self.die()
        if (self.y>miny):
            self.die()
        return dead

class game:
    playwindow_x = 8
    playwindow_y = 4
    distance_x = 8
    distance_y = 3
    number_cols = 8
    number_rows = 5
    speed = 20
    global_y = 0
    aliens = []
    blocks = []
    player = object
    player_missile = object
    alien_missile = object
    score = 0
    life = 3
    frame = 0
    sframe = 0
    playwindow_moves_x = 4
    playwindow_max_x = playwindow_x + (number_cols*distance_x+playwindow_moves_x)
    gameover = 0
    difficulty = 10

    def init(self):
        os.system('color')
        setcurser(on = False)
        for j in range(game.number_rows):
            for i in range(game.number_cols):
                x = game.playwindow_x+i*game.distance_x
                y = game.playwindow_y+(j)*game.distance_y
                if (i==0):
                    tsprite=texture(x,y,4,2)
                    if (j==0): 
                        tpoints = 500
                        c = asciiRGB(255,0,0)
                        tsprite.fill(c,'▗▇▇▖▞  ▚')
                        tsprite.fill(c,'▗▇▇▖▚  ▞')
                    if (j==1 or j==2): 
                        tpoints = 300
                        c = asciiRGB(0,255,0)
                        tsprite.fill(c,'▗▇▇▖ ▚▞ ')
                        tsprite.fill(c,'▗▇▇▖ ▞▚')
                    if (j>2): 
                        tpoints = 100
                        c = asciiRGB(0,255,255)
                        tsprite.fill(c,'▛▀▀▜▚▅▅▞')
                        tsprite.fill(c,'▛▀▀▜▚▁▁▞')

                a = alien(tsprite,x,y,tpoints)
                game.aliens.append(a)
        for i in range(4):
            x = int(game.playwindow_x*1.5)+i*int((game.playwindow_max_x-(game.playwindow_x*2))/4)
            y = 30
            c = asciiRGB(128,128,128)
            tsprite=texture(x,y,4,2)
            tsprite.fill(c,'▗▇▇▖████')
            tsprite.fill(c,'    ████')
            tsprite.fill(c,'    ▚▞▚▞')
            b = block(tsprite,x,y)
            game.blocks.append(b)

        x = 40
        y = 35
        tsprite=texture(x,y,4,2)
        tsprite.fill(asciiRGB(0,0,255),' ▞▚ ▛▀▀▜')
        game.player = player(tsprite,x,y)

        tsprite=texture(x,y,3,2)
        tsprite.fill(asciiRGB(128,128,128),' |    ')
        tsprite.visible(False)
        game.player_missile = player_missile(tsprite,x,y)

        tsprite=texture(x,y,3,2)
        tsprite.fill(asciiRGB(255,0,0),' ┇    ')
        tsprite.visible(False)
        game.alien_missile = alien_missile(tsprite,x,y)

    def newlevel(self):
        game.gameover = 0
        game.life += 1
        for a in game.aliens:
            a.x = a.ix
            a.y = a.iy
            a.visible = True
            a.direction = 1
        game.player_missile.die()
        game.alien_missile.die()
        game.speed = 20
        if (game.difficulty>3):
            game.difficulty-=1

    def restart(self):
        game.life = 2
        game.score = 0
        game.difficulty = 11
        game.newlevel(self)

    def fire(self):
        if (not game.player_missile.isshooting):
            game.player_missile.fire(game.player.x, game.player.y)
            #winsound.PlaySound("FIRE.WAW", winsound.SND_ALIAS)

    def movedown(self):
        for s in game.aliens:
            if (s.visible):
                s.move(0,2)
                s.direction = s.direction * -1
        if (game.speed>game.difficulty): 
            game.speed-=1

    def step(self):
        tmovedown = False
        leftalive = False
        points = 0
        for s in game.aliens:
            if (s.visible):
                if (not game.alien_missile.isshooting and s.x > game.player.x-4 and s.x < game.player.x+4 and game.frame == 0):
                    game.alien_missile.fire(s.x, s.y)
                    #winsound.PlaySound("FIRE.WAW", winsound.SND_ALIAS)
                leftalive = True
                if (s.y > game.player.y - 8):
                    leftalive = False
                    break
                if (s.x+s.direction<game.playwindow_x or s.x+s.direction>game.playwindow_max_x):
                    tmovedown = True
        if (leftalive==False):
            game.gameover = 1
        if tmovedown == True:
            game.movedown(self)
        else:
            for s in game.aliens:
                if (s.visible):
                    s.move(s.direction,0)
        if (game.player_missile.visible):
            points = game.player_missile.step(game.aliens, game.playwindow_y)
            if (points>0):
                game.score += points
        if (game.alien_missile.visible):
            dead = game.alien_missile.step(game.player,game.blocks, game.player.y+8)
            if (dead==1 and game.gameover == 0):
                game.life -= 1
                if (game.life==0):
                    game.gameover = 2
        game.player.step()                    
        game.frame+=1
        game.sframe+=1
        if (game.sframe==10):
            #winsound.PlaySound("STEP1.WAW", winsound.SND_ALIAS)
            pass
        elif (game.sframe==20):
            #winsound.PlaySound("STEP2.WAW", winsound.SND_ALIAS)
            game.sframe = 0

        if (game.frame>1):
            game.frame = 0
        if (game.player.x+game.player.direction < game.playwindow_max_x and game.player.x+game.player.direction > game.playwindow_x):
            game.player.move(game.player.direction,0)
        else:
            game.player.direction = 0

    def render(self, ca):
        ca.forecolor(asciiRGB(0,0,255))
        for i in range(40):
            ca.pos(0, i)
            ca.write(' ' * 80)
        ca.pos(30,1)
        ca.write("jd Invader")
        ca.forecolor(asciiRGB(255,0,0))
        ca.pos(0,1)
        ca.write("Lifes: " + str(game.life))
        ca.pos(65,1)
        ca.write("Score: " + str(game.score))
        ca.pos(0,2)
        ca.write('-' * 80)
        for s in game.aliens:
            if (s.visible):
                s.draw(game.frame)
        for b in game.blocks:
            if (b.visible):
                b.draw(b.frame)
        if (game.player.visible == True):
            game.player.draw(0)
        if (game.player_missile.visible):
            game.player_missile.draw(0)
        if (game.alien_missile.visible):
            game.alien_missile.draw(0)
        if (game.gameover>0):
            ca.pos(15,20)
            ca.write("Game Over")
            if (game.gameover==1):
                ca.pos(11,20)
                ca.write("press n for next level")
            else:
                ca.pos(15,21)
                ca.write("you lost")
                ca.pos(11,22)
                ca.write("press n to restart")
    
    def setdir(self,d):
        if (d==0):
            game.player.direction = d
        elif (abs(game.player.direction)<4):
            game.player.direction = game.player.direction + d

    def setscore(self,score):
        game.score = score

ca = canvas(80,40)
ca.cls()
g = game()
g.init()

while  stopme==False:
    k = ''
    if msvcrt.kbhit():
        k = msvcrt.getch()
    if k == b'z':
        stopme = True
    if k == b'n' and g.gameover > 0:
        if (g.gameover == 1):
            g.newlevel()
        else:
            g.restart()
    if k == b'a':
        g.setdir(-1)
    if k == b's':
        g.setdir(0)
    if k == b'd':
        g.setdir(1)
    if k == b' ':
        g.fire()
    fps=fps+1
    if (fps%g.speed==1 and g.gameover == 0):
        g.step()
    g.render(ca)
    time.sleep(0.01)
setcurser(on = True)
