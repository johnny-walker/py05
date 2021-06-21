# https://www.rs-online.com/designspark/python-tkinter-cn#_Toc61529922
import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np
import time
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
            self.owner.move(self.name)

class Pgm05(ProgramBase):
    threadEventMouse = threading.Event()
    threadMouse = None
    
    def __init__(self, root, path, width=640, height=480):
        super().__init__(root, width, height)
        self.root.title('Canvas')

        self.canvas = tk.Canvas(self.root, bg = "gray", width=width, height=height)
        self.canvas.pack()
        self.imgCV2 = None
        self.rows = 0
        self.cols = 0
        self.imgTK = self.loadImage('data/mouse.png')
        self.mouseImgID = self.canvas.create_image(100, 100, anchor = 'nw', image = self.imgTK)
        self.root.update()
    
    def loadImage(self, path):
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        self.imgCV2 = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
        self.rows, self.cols = self.imgCV2.shape[:2]
        self.rotateImage(90, 0.8)
        return self.resizeAsTKImg()

    def resizeAsTKImg(self):
        im = Image.fromarray(self.imgCV2)               # convert to pillow image fomrat
        im.thumbnail((im.width//12, im.height//12))     # resize by pillow
        return ImageTk.PhotoImage(im)                   # convert to tkinter image

    def rotateImage(self, angle, scale=1.0):
        matrix2D = cv2.getRotationMatrix2D(((self.cols-1)/2.0, (self.rows-1)/2.0), angle, scale)
        self.imgCV2 = cv2.warpAffine(self.imgCV2, matrix2D, (self.cols, self.rows))

    def updateMouseImage(self):
        self.imageTKMouse = self.resizeAsTKImg()
        self.canvas.itemconfig(self.mouseImgID, image=self.imageTKMouse)

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
    
    def move(self, threadName):
        while not self.threadEventMouse.wait(0.2):  # moving for every 100 ms
            #print ('[{0}][{1}] keep moving'.format(threadName, time.time()))
            self.rotateImage(45, 1.0)
            self.updateMouseImage()
        print('[{0}] exit'.format(threadName))

if __name__ == '__main__':
    cwd = os.getcwd()
    mouse = os.path.join(cwd, "data/mouse.png")
    program = Pgm05(tk.Tk(), mouse )

    program.run()
    print("quit, bye bye ...")