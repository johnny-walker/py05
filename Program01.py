#https://blog.gtwang.org/programming/python-threading-multithreaded-programming-tutorial/
import os
import tkinter as tk
from PIL import Image, ImageTk
import cv2
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
            self.owner.funcMouse1(self.name)
        elif self.threadID == THREAD_MOUSE_ID+1 :
            self.owner.funcMouse2(self.name)

class Pgm05(ProgramBase):
    threadEventMouse1 = threading.Event()
    threadEventMouse2 = threading.Event()
    threadMouse1 = None
    threadMouse2 = None
    
    def __init__(self, root, path, width=640, height=480):
        super().__init__(root, width, height)
        self.root.title('mouse moving')
        self.canvas = tk.Canvas(self.root, bg = "gray", width=width, height=height)
        self.canvas.pack()
        self.mouse1PosX = 50
        self.mouse1PosY = 50
        self.mouse2PosX = 500
        self.mouse2PosY = 300

        self.imgCV2 = self.imgCV2_90 = None
        self.rows = 0
        self.cols = 0
        
        # create 2 mouses
        self.loadImage('data/mouse.png')
        self.mouse1ImgID = self.canvas.create_image(self.mouse1PosX, self.mouse1PosY, anchor = 'nw', image = self.imgTK90)
        self.mouse2ImgID = self.canvas.create_image(self.mouse2PosX, self.mouse2PosY, anchor = 'nw', image = self.imgTK)
        self.root.update()
    
    def loadImage(self, path):
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
        self.rows, self.cols = img.shape[:2]
        # create 2 TK images
        im = self.rotateImage(img, 0, 0.8)
        self.imgTK = self.resizeAsTKImg(im)
        im = self.rotateImage(img, 90, 0.8)
        self.imgTK90 = self.resizeAsTKImg(im)

    def resizeAsTKImg(self, img):
        im = Image.fromarray(img)               # convert to pillow image fomrat
        im.thumbnail((im.width//12, im.height//12))     # resize by pillow
        return ImageTk.PhotoImage(im)                   # convert to tkinter image

    def rotateImage(self, img, angle, scale=1.0):
        matrix2D = cv2.getRotationMatrix2D(((self.cols-1)/2.0, (self.rows-1)/2.0), angle, scale)
        return cv2.warpAffine(img, matrix2D, (self.cols, self.rows))

    # override
    def onKey(self, event):
        if event.char == event.keysym or len(event.char) == 1:
            if event.keysym == 'Escape':
                self.threadEventMouse1.set() # signal the thread loop to quit
                self.threadEventMouse2.set() # signal the thread loop to quit
                print("key Escape") 
                self.root.destroy()
            else: # any other key
                if not self.threadMouse1 and not self.threadMouse2:
                    self.startThread()
    
    def startThread(self):
        self.threadMouse1 = MazeThread(THREAD_MOUSE_ID, "Mouse1 Thread", self)
        self.threadEventMouse1.clear()   # reset the thread event
        self.threadMouse1.start()
    
        self.threadMouse2 = MazeThread(THREAD_MOUSE_ID+1, "Mouse2 Thread", self)
        self.threadEventMouse2.clear()   # reset the thread event
        self.threadMouse2.start()

    def funcMouse1(self, threadName):
        while not self.threadEventMouse1.wait(0.2):  # moving for every 200 ms
            #print ('[{0}][{1}] keep moving'.format(threadName, time.time()))
            self.mouse1Forward()
        print('[{0}] exit'.format(threadName))
    
    def funcMouse2(self, threadName):
        while not self.threadEventMouse2.wait(0.15):  # moving for every 150 ms
            #print ('[{0}][{1}] keep moving'.format(threadName, time.time()))
            self.mouse2Forward()
        print('[{0}] exit'.format(threadName))
    
    def mouse1Forward(self):
        if self.mouse1PosX + 50 < self.root.width - 100:
            offsetx = 50  
            self.mouse1PosX += 50
        else:
            offsetx = 50 - self.mouse1PosX 
            self.mouse1PosX = 50
        self.canvas.move(self.mouse1ImgID, offsetx, 0)     
    
    def mouse2Forward(self):
        if self.mouse2PosY + 30 < self.root.height - 100:
            offsety = 30  
            self.mouse2PosY += 30
        else: 
            offsety = 30 - self.mouse2PosY 
            self.mouse2PosY = 30
        self.canvas.move(self.mouse2ImgID, 0, offsety)     


if __name__ == '__main__':
    cwd = os.getcwd()
    mouse = os.path.join(cwd, "data/mouse.png")
    program = Pgm05(tk.Tk(), mouse )

    program.run()
    print("quit, bye bye ...")