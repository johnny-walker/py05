import os
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.constants import FALSE
from PIL import Image, ImageTk
import cv2
import numpy as np
import csv
import threading
from Root import ProgramBase

THREAD_MOUSE_ID = 1    
class MazeThread (threading.Thread):
    def __init__(self, threadID, name, owner):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.owner  = owner       

    def run(self):
        print('[{0}] starts, id={1}'.format(self.name, self.threadID))
        if self.threadID == THREAD_MOUSE_ID :
            self.owner.moveThread(self.name)

# action and info for moving
class Map():
    def __init__(self):
        self.info = []
        self.rows = 0
        self.columns = 0

    def loadMap(self, filepath):
        with open(filepath, newline='') as csvfile:
            rows = csv.reader(csvfile)
            for row in rows:
                print(row)
                self.info.append(row)
        self.rows = len(self.info)
        self.columns = len(self.info[0])
        print('map rows = {0}, columns = {1}'.format(self.rows, self.columns))
    
    def isBlock(self, x, y):
        block = True
        if x in range(0,self.columns) and y in range(0,self.rows):
            block = self.info[y][x] == '0'
        return block
        
    def isEntry(self, x, y):
        return self.info[y][x] == '2'

    def isExit(self, x, y):
        return self.info[y][x] == '3'
        

# movement algorithm
class MazeMove():
    def __init__(self, maze):
        self.mouseRoute = []
        self.candidatesStack = []
        self.maze = maze
        self.currentItem = None
        self.visited = []

    def initState(self, x, y):
        # append route item (direction, parent, son)  
        self.currentItem = (None, None, (x, y))
        self.mouseRoute.append(self.currentItem)
        self.addCandidates(x,y)
        self.visited.append((x,y))

    def popRoute(self):
        return self.mouseRoute.pop()

    def lastRoute(self):
        return self.mouseRoute[-1]

    def canWalk(self, x, y):
        if (x,y) in self.visited:
                return False
        return not self.maze.isBlock(x, y)

    def addCandidates(self, x, y):
        newCandidate = False
        if self.canWalk(x+1, y):  
            item = ('east', (x, y), (x+1, y))
            self.candidatesStack.append(item)
            newCandidate = True
        if self.canWalk(x, y+1): 
            item = ('south', (x, y), (x, y+1))
            self.candidatesStack.append(item)
            newCandidate = True
        if self.canWalk(x-1, y): 
            item = ('west', (x, y), (x-1, y))
            self.candidatesStack.append(item)
            newCandidate = True
        if self.canWalk(x, y-1): 
            item = ('north', (x, y), (x, y-1))
            self.candidatesStack.append(item)
            newCandidate = True
        return newCandidate

    def moveForward(self):
        state = True
        item = None
        if len(self.candidatesStack) > 0:
            item = self.candidatesStack.pop()
            self.addCandidates(item[2][0],item[2][1])
            
        if len(self.candidatesStack) == 0 :
            print('Map Error, no route to exit')
            state = False
        self.visited.append(item[2])
        return (state, item)


class Maze(ProgramBase):
    threadEventMouse = threading.Event()
    threadMouse = None

    def __init__(self, root, width=640, height=480):
        super().__init__(root, width, height)
        # init UI
        self.width = width
        self.height = height
        self.root.title('Mouse Maze')
        self.canvas = tk.Canvas(self.root, bg = "gray", width=width, height=height)
        self.canvas.pack()

        self.map = Map()                        # read csv file
        self.mazeMove = MazeMove(self.map)      # mouse moving algorithm
        
        self.sizeX = 0                          # cell size x
        self.sizeY = 0                          # cell size y
        self.direction = 'east'                 # current image direction
        self.imgMouses = {}                     # prepare 4 directions' mouse images 
        self.imgCake = None
        self.imageTKMouse = None                # must hold the image object, otherwise will be released
        self.imageTKCake = None                # must hold the image object, otherwise will be released
        self.mouseImgID = 0                     # mouse image widget
        self.cakeImgID = 0 
        self.mousePos   = (0,0)                 # mouse current position, use to caculate the offset
        self.gameFinsihed = False

    def loadMap(self, path):
        self.map.loadMap(path)
        self.sizeX = self.width/self.map.columns
        self.sizeY = self.height/self.map.rows
        self.drawMap()
        self.locateMouse()
        self.locateCake()

    def drawDot(self, x, y, radius, color):
        centx, centy = (x*self.sizeX+self.sizeX/2, y*self.sizeY+self.sizeY/2)
        coord_rect = centx-radius, centy-radius, centx+radius, centy+radius
        self.canvas.create_oval(coord_rect, fill=color)

    def drawMap(self):
        radius = 2
        color = 'yellow'
        for x in range (self.map.columns):
            for y in range (self.map.rows):
                if self.map.isBlock(x,y):
                    color = 'green'
                    radius = 5
                else:
                    radius = 2
                    if self.map.isEntry(x,y):
                        radius = 6
                        color = 'red'
                    elif self.map.isExit(x,y):
                        color = 'red'
                    else:
                        color = 'yellow'
                self.drawDot(x, y, radius, color)
    
    def locateMouse(self):
        for x in range (self.map.columns):
            for y in range (self.map.rows):
                if self.map.isEntry(x,y):
                    left, top = (x*self.sizeX, y*self.sizeY)  #top-left corner position
                    cwd = os.getcwd()
                    path = os.path.join(cwd,'data/mouse.png')  
                    print(path)
                    self.imageTKMouse = self.loadMouseImage(path)
                    self.mouseImgID = self.canvas.create_image(left+2, top+2, anchor='nw', image=self.imageTKMouse)
                    self.canvas.pack()
                    self.mazeMove.initState(x,y)
                    self.mousePos = (x,y)

    def locateCake(self):
        for x in range (self.map.columns):
            for y in range (self.map.rows):
                if self.map.isExit(x,y):
                    left, top = (x*self.sizeX, y*self.sizeY)  #top-left corner position
                    cwd = os.getcwd()
                    path = os.path.join(cwd,'data/cake.png')  
                    print(path)
                    self.imageTKCake = self.loadCakeImage(path)
                    self.cakeImgID = self.canvas.create_image(left+16, top+10, anchor='nw', image=self.imageTKCake)
                    self.canvas.pack()

    def loadMouseImage(self, path):
        imgCV2 = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        imgCV2 = cv2.cvtColor(imgCV2, cv2.COLOR_BGRA2RGBA)
        self.rows, self.cols = imgCV2.shape[:2]
        self.imgMouses['south'] = imgCV2 = self.rotateImage(imgCV2, 0, 0.8)
        self.imgMouses['east']  = self.rotateImage(imgCV2,  90, 1.0)
        self.imgMouses['north'] = self.rotateImage(imgCV2, 180, 1.0)
        self.imgMouses['west']  = self.rotateImage(imgCV2, -90, 1.0)
        return self.resizeAsTKImg(self.imgMouses['south'])
    
    def loadCakeImage(self, path):
        self.imgCake = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        self.imgCake = cv2.cvtColor(self.imgCake, cv2.COLOR_BGRA2RGBA)
        im = Image.fromarray(self.imgCake)              # convert to PIL image
        im.thumbnail((im.width//20, im.height//20))     # resize by PIL
        return ImageTk.PhotoImage(im) 
    
    def resizeAsTKImg(self, image):                     # input is CV2 image
        im = Image.fromarray(image)                     # convert to PIL image
        im.thumbnail((im.width//24, im.height//24))     # resize by PIL
        return ImageTk.PhotoImage(im)                   # convert to tkimage PhotoImage

    def rotateImage(self, image, angle, scale=1.0):
        matrix2D = cv2.getRotationMatrix2D(((self.cols-1)/2.0, (self.rows-1)/2.0), angle, scale)
        imgRotate = cv2.warpAffine(image, matrix2D, (self.cols, self.rows))
        return imgRotate

    def updateMouseImage(self, image):
        self.imageTKMouse = self.resizeAsTKImg(image)
        self.canvas.itemconfig(self.mouseImgID, image=self.imageTKMouse)
    
    def updateMousePos(self, pos):
        x, y = pos
        offsetx = (x - self.mousePos[0]) * self.sizeX
        offsety = (y - self.mousePos[1]) * self.sizeY
        self.canvas.move(self.mouseImgID, offsetx, offsety)

    # override
    def onKey(self, event):
        if event.char == event.keysym or len(event.char) == 1:
            if event.keysym == 'Escape':
                self.threadEventMouse.set() # signal the thread loop to quit
                print("key Escape") 
                self.root.destroy()
            else: # any other key
                if not self.threadMouse:
                    self.startThread()
    
    def startThread(self):
        self.threadMouse = MazeThread(THREAD_MOUSE_ID, "Mouse Thread", self)
        self.threadEventMouse.clear()   # reset the thread event
        self.threadMouse.start()
    
    def moveThread(self, threadName):
        while not self.threadEventMouse.wait(0.2):  # moving for every 200 ms
            #print ('[{0}][{1}] keep moving'.format(threadName, time.time()))
            self.nextStep()
        print('[{0}] exit'.format(threadName))
        self.gameOVer()

    def nextStep(self):
        state, item = self.mazeMove.moveForward()
        if state:
            itemRoute = self.mazeMove.lastRoute()
            while itemRoute[2] != item[1]:
                itemRoute = self.mazeMove.popRoute()
                itemRoute = (self.reverseDir(itemRoute[0]), itemRoute[1], itemRoute[2])
                self.mouseBackward(itemRoute)
                itemRoute = self.mazeMove.lastRoute()
            if self.map.isExit(item[2][0],item[2][1]):
                self.threadEventMouse.set() # signal the thread loop to quit
                self.gameFinsihed = True
            else:
                self.mouseForward(item)
                
    def gameOVer(self):
        if self.gameFinsihed:
            messagebox.showinfo(title='Maze', message='Mission Completed')

    def mouseForward(self, item):
        print (item)
        if self.direction != item[0]: 
            self.direction = item[0]
            self.updateMouseImage(self.imgMouses[self.direction])
        self.updateMousePos(item[2])
        self.mousePos = item[2]
        self.mazeMove.mouseRoute.append(item)
        self.mazeMove.currentItem = item

    def mouseBackward(self, item):
        print (item)
        if self.direction != item[0]: 
            self.direction = item[0]
            self.updateMouseImage(self.imgMouses[self.direction])
        self.updateMousePos(item[1])
        self.mousePos = item[1]
        time.sleep(0.2)

    def reverseDir(self, dir):
        reverse = {'east':'west', 'west':'east', 'north':'south', 'south': 'north'}
        return reverse[dir]

if __name__ == '__main__':
    print(tk.TkVersion)
    program = Maze(tk.Tk())
    cwd = os.getcwd()
    program.loadMap(os.path.join(cwd,'data/maze_map01.csv'))    
    program.run()
