import os
import win32gui, win32con
import random
import time

hwnd = win32gui.GetForegroundWindow()
win32gui.ShowWindow(hwnd,win32con.SW_SHOWMAXIMIZED)

os.system('color')

def getSize():
    return os.get_terminal_size()

def printAt(x, y, char, color):
    y1 = 0 if y - 1 <= 0 else y - 2
    x1 = 0 if x - 1 <= 0 else x - 2 
    c = f'\x1b[38;5;{16+6*color}m'
    s = f'\x1b[{y1};{x1}H'
    print(c + s + chr(char) )

class movingChar():
    def __init__(self, mx, my):
        self.mx = mx
        self.my = my
        self.c = random.randrange(96)+32
        self.x = random.randrange(mx)
        self.y = random.randrange(int(my/2))
        self.dead = False
        self.col = 5

    def step(self):
        self.y += 1
        if self.y > self.my:
            self.die()
        else:
            printAt(self.x, self.y, self.c, 5)
            if self.col > 1:
                self.col -= 1
            printAt(self.x, self.y-1, self.c, self.col)

    def die(self):
        printAt(self.x, self.y-1, 32, 0)
        self.dead = True

a = []

for i in range(100):
    a.append(movingChar(getSize().columns, getSize().lines))

while(True):
    for i in range(50):
        printAt(random.randrange(getSize().columns),random.randrange(getSize().lines),random.randrange(96)+32,random.randrange(6))
        printAt(random.randrange(getSize().columns),random.randrange(getSize().lines),32,0)
    for c in a:
        c.step()
        if c.dead == True:
            a.remove(c)
    if len(a) <100:
        a.append(movingChar(getSize().columns, getSize().lines))
    time.sleep(0.01)

