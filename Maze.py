import os
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.constants import FALSE
from PIL import Image, ImageTk
import cv2
import numpy as np
import threading

from Root import ProgramBase
from MazeMap import Map
from MazeCtrl import MazeMove

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

class Maze(ProgramBase):
    threadEventMouse = threading.Event()
    threadMouse = None

    def __init__(self, root, width=640, height=480):
        super().__init__(root, width, height)
        # init UI
        self.width = width
        self.height = height
        self.root.title('老鼠覓食')
        self.canvas = tk.Canvas(self.root, bg = "gray", width=width, height=height)
        self.canvas.pack()

        self.map = Map()                        # read csv file
        self.mazeMove = MazeMove(self.map)      # mouse moving algorithm

        self.walkSpeed = 0.18                    # interval for every step
        self.sizeX = 0                          # cell size x
        self.sizeY = 0                          # cell size y
        self.direction = 'east'                 # current image direction
        self.imgMouses = {}                     # prepare 4 directions' mouse images 
        
        self.imageTKMouse = None                # must hold the image object, otherwise will be released
        self.imageTKHome = None                 # must hold the image object, otherwise will be released
        self.imageTKCake = None                 # must hold the image object, otherwise will be released
        self.imageTKBlock = None                # must hold the image object, otherwise will be released

        self.mouseImgID = 0                     # mouse image widget
        self.mousePos   = (0,0)                 # mouse current position, use to caculate the offset
        self.gameFinsihed = False
        self.isHomeDrawn = False

        self.loadImages()

    def loadImages(self):
        cwd = os.getcwd()
        path = os.path.join(cwd,'data/mouse.png')  
        self.loadMouseImage(path)

        path = os.path.join(cwd,'data/home.png')  
        self.imageTKHome = self.loadImage(path, 50)

        path = os.path.join(cwd,'data/cake.png')  
        self.imageTKCake = self.loadImage(path, 18)

        path = os.path.join(cwd,'data/block.png')  
        self.imageTKBlock = self.loadImage(path, 22.7)

    def loadMouseImage(self, path):
        imgCV2 = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        imgCV2 = cv2.cvtColor(imgCV2, cv2.COLOR_BGRA2RGBA)
        self.rows, self.cols = imgCV2.shape[:2]
        self.imgMouses['south'] = imgCV2 = self.rotateImage(imgCV2, 0, 0.8)
        self.imgMouses['east']  = self.rotateImage(imgCV2,  90, 1.0)
        self.imgMouses['north'] = self.rotateImage(imgCV2, 180, 1.0)
        self.imgMouses['west']  = self.rotateImage(imgCV2, -90, 1.0)
        self.imageTKMouse = self.resizeAsTKImg(self.imgMouses['south'])

    def loadImage(self, path, scale):
        imgCake = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        imgCake = cv2.cvtColor(imgCake, cv2.COLOR_BGRA2RGBA)
        im = Image.fromarray(imgCake)              # convert to PIL image
        im.thumbnail((im.width//scale, im.height//scale))     # resize by PIL
        return ImageTk.PhotoImage(im) 

    def loadMap(self, path):
        self.map.loadMap(path)
        self.sizeX = self.width/self.map.columns
        self.sizeY = self.height/self.map.rows
        self.drawMap()

    def drawMap(self):
        for x in range (self.map.columns):
            for y in range (self.map.rows):
                if self.map.isBlock(x,y):
                    self.drawBlock(x,y)
                elif self.map.isExit(x,y):
                    self.drawCake(x,y)
                elif self.map.isEntry(x,y):
                    self.drawMouse(x,y)
                #else:
                #    self.drawDot(x, y, 2, 'yellow')
                
    def drawImage(self, tkimg, x, y, offsetx, offsety):
        left, top = (x*self.sizeX, y*self.sizeY)  #top-left corner position
        id =  self.canvas.create_image(left+offsetx, top+offsety, anchor='nw', image=tkimg)
        self.canvas.pack()
        return id

    def drawMouse(self, x, y):
        self.mouseImgID = self.drawImage(self.imageTKMouse, x, y, 6, 2)
        self.canvas.pack()
        self.mazeMove.initState(x,y)
        self.mousePos = (x,y)

    def drawHome(self, x, y):
        # only draw once after first moving
        if not self.isHomeDrawn:
            self.drawImage(self.imageTKHome, x, y, 12, 10)
            self.isHomeDrawn = True

    def drawCake(self, x, y):
        self.drawImage(self.imageTKCake, x, y, 13, 10)
    
    def drawBlock(self, x, y):
        self.drawImage(self.imageTKBlock, x, y, 5, 3)
   
    def drawDot(self, x, y, radius, color):
        centx, centy = (x*self.sizeX+self.sizeX/2, y*self.sizeY+self.sizeY/2)
        coord_rect = centx-radius, centy-radius, centx+radius, centy+radius
        self.canvas.create_oval(coord_rect, fill=color)
   
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
        while not self.threadEventMouse.wait(self.walkSpeed):  # moving for every 200 ms
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
        self.updateMousePos(item[2])    # step forward from child info
        self.drawHome(self.mazeMove.currentItem[2][0], self.mazeMove.currentItem[2][1])
        self.mousePos = item[2]
        self.mazeMove.mouseRoute.append(item)
        self.mazeMove.currentItem = item

    def mouseBackward(self, item):
        print (item)
        if self.direction != item[0]: 
            self.direction = item[0]
            self.updateMouseImage(self.imgMouses[self.direction])
        self.updateMousePos(item[1])    # step backword from parent info
        self.mousePos = item[1]
        time.sleep(self.walkSpeed)

    def reverseDir(self, dir):
        reverse = {'east':'west', 'west':'east', 'north':'south', 'south': 'north'}
        return reverse[dir]

if __name__ == '__main__':
    print(tk.TkVersion)
    program = Maze(tk.Tk())
    cwd = os.getcwd()
    program.loadMap(os.path.join(cwd,'data/maze_map01.csv'))    
    program.run()
