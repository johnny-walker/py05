# -*- coding: utf-8 -*-
"""
Running Man
"""
import os
import random
import time
from tkinter import *
from tkinter import messagebox

######################################################
# constant,
# can't be changed during program running
######################################################
WIN_WIDTH  = 800
WIN_HEIGHT = 600
geom = '%dx%d' %(WIN_WIDTH+5, WIN_HEIGHT+5)

CANDYEXIST  = 0x01
GHOSTEXIST  = 0xf0
GHOSTMASK1 = 0x10  #Ghost1
GHOSTMASK2 = 0x20  #Ghost2
GHOSTMASK3 = 0x40  #Ghost3
GHOSTMASK4 = 0x80  #Ghost4
lstGhostMask = [GHOSTMASK1, GHOSTMASK2, GHOSTMASK3, GHOSTMASK4]

dirRight = 0
dirUp    = 1
dirLeft  = 2
dirDown  = 3

ManSpeed = 0.2
GhostSpeed = 0.3

########################################################################
# global vairable for Window size, candy count,
# can be changed during program running
########################################################################
pw = 50
hw = pw // 2
qw = pw // 4
dimX = WIN_WIDTH  // pw
dimY = WIN_HEIGHT // pw

######################################################
# threading model
######################################################
import threading
threadEvent_GAMEOVER = threading.Event()


class gameDataSet():
    def __init__(self):
        self.dicDATA = {}
        self.candyCount = dimX * dimY
        self.direction = dirRight
        self.lstGhost = []
        
gds = gameDataSet()
gdsLock = threading.Lock()

import queue
qMove = queue.Queue()
                    
class myThread (threading.Thread):
    def __init__(self, threadID, name, tupxy):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.x, self.y  = tupxy        

    def run(self):
        print("Starting " + self.name + " id= " +str(self.threadID))
        
        if self.threadID == 1 :
            #print ("call MoveMan\n")
            MoveMan(self.name, self.x, self.y, 1)
            print ("Man left\n")
        elif self.threadID == 2:
            #print ("call MoveGhost 1\n")
            MoveGhost(self.name, self.x, self.y, 2)
            print ("Ghost 1 left\n")
        elif self.threadID == 3:
            #print ("call MoveGhost 2\n")
            MoveGhost(self.name, self.x, self.y, 3)
            print ("Ghost 2 left\n")
        elif self.threadID == 4:
            #print ("call MoveGhost 3\n")
            MoveGhost(self.name, self.x, self.y, 4)
            print ("Ghost 3 left\n")
        elif self.threadID == 5:
            #print ("call MoveGhost 4\n")
            MoveGhost(self.name, self.x, self.y, 5)
            print ("Ghost 4 left\n")
 

####################################
# global function
####################################
def ResetGlobalData():
    L, T = ((pw-40)/2,  (pw-40)/2)  #top-left corner position    
    canvas.coords(Rman, (L, T))# change coordinates

    for py in range (dimY):
        for px in range (dimX):
            candytag = getCandyID(px,py)
            canvas.itemconfig(candytag, fill="gray")
            gds.dicDATA[candyid] = CANDYEXIST        

def getCandyID(x,y):
    return (x + y*dimX + 1)   #tagid starts from 1

def getManXY(candyid):
    return candyid % dimX -1, candyid // dimX

def MoveMan(threadName, px, py, id=1):  # start from pos (px,py)
    def eatCandy(ds):
        if ds.dicDATA[candytag] & 0x01:  # candy still exists
            canvas.itemconfig(candytag, fill="#1a1a2a")
            
            gdsLock.acquire()
            ds.dicDATA[candytag] = ds.dicDATA[candytag] & 0xfe
            ds.candyCount -= 1
            gdsLock.release()
            #print (ds.candyCount)

    qMove._put(gds)
    while True:
        if threadEvent_GAMEOVER.wait(ManSpeed):
            break
        #time.sleep(delay)
        candytag = getCandyID(px,py)

        # move forward
        item_gds = qMove.get()
        if item_gds.direction == dirRight and px < dimX-1:
            eatCandy(item_gds)
            px = px+1
        elif item_gds.direction == dirLeft and px > 0 :
            eatCandy(item_gds)
            px = px-1
        elif item_gds.direction == dirDown and py < dimY-1 :
            eatCandy(item_gds)
            py = py+1
        elif item_gds.direction == dirUp and py > 0 :
            eatCandy(item_gds)
            py = py-1
        qMove.put(item_gds)

        if item_gds.candyCount == 0 :
            threadEvent_GAMEOVER.set() #quit this thread
            messagebox.showinfo("Game Done", "Yeah!  You win ~")

        candytag = getCandyID(px,py)
        #print (item_gds.dicDATA[candytag])
        L, T = (px*pw + (pw-40)/2, py*pw + (pw-40)/2)  #top-left corner position    
        canvas.coords(Rman, (L, T))# change coordinates

        gdsLock.acquire()
        if item_gds.dicDATA[candytag] & GHOSTEXIST in lstGhostMask:
            threadEvent_GAMEOVER.set() #quit this thread
            messagebox.showinfo("Game Over", "Oops!  You die ~")
        gdsLock.release()

    item_gds = qMove.get()
    
    ResetGlobalData()
    print("Exiting Thread: " + threadName)

def MoveGhost(threadName, px, py, threadid=0):  # start from pos (px,py)
    def updateGhostMask(gds, candytag, ghostid, renewmask = 0):
        # print ("updateMask")
        ghostmask = lstGhostMask[ghostid]

        if ghostmask > 0:
            gdsLock.acquire()
            if renewmask: # fill new ghost mask
                gds.dicDATA[candytag] = gds.dicDATA[candytag] | ghostmask
            else: #reset ghost mask
                gds.dicDATA[candytag] = gds.dicDATA[candytag] & ~ghostmask
            gdsLock.release()
            
    print ("MoveGhost - start: " + threadName)            
    ghost_instance = None
    ghost_id = threadid -2  #index = threadid-2
    item_gds = qMove.get()
    ghost_instance = item_gds.lstGhost[ghost_id]
    qMove.put(item_gds)    

    while True:
        #print ('Move Ghost')
        if threadEvent_GAMEOVER.wait(GhostSpeed) :
            break
        #time.sleep(delay)
        item_gds = qMove.get()
        candytag = getCandyID(px,py)
        updateGhostMask(item_gds, candytag, ghost_id, 0) #clear Ghost Mask

        # move forward
        if ghost_id == 0:
            px = (px+1) % dimX
        elif ghost_id == 1:
            px = (px-1) % dimX
        elif ghost_id == 2:
            py = (py+1) % dimY
        elif ghost_id == 3:
            py = (py-1) % dimY

        candytag = getCandyID(px,py)
        updateGhostMask(item_gds, candytag, ghost_id, 1) # fill Ghost mask
        qMove.put(item_gds)

        # update Ghost position
        if ghost_instance:
            candytag = getCandyID(px,py)
            L, T = (px*pw + (pw-40)/2, py*pw + (pw-40)/2)  #top-left corner position  
            canvas.coords(ghost_instance, (L, T))# change coordinates
            #print (item_gds.dicDATA[candytag])

    #print("Exiting Thread: " + threadName)

def OnStart():
    print (gds.candyCount)
    if gds.candyCount !=  dimX * dimY:
        return
    print ("OnStart  go")    
    
    threadEvent_GAMEOVER.clear()
    
    #create Man thread
    threadRM = myThread(1, "RunMan", (0,0))
    threadRM.start()

    #create ghost1 thread
    threadGhost1 = myThread(2, "Ghost", lstGhostXY[0])
    threadGhost1.start()

    #create ghost2 thread
    threadGhost2 = myThread(3, "Ghost", lstGhostXY[1])
    threadGhost2.start()

    #create ghost3 thread
    threadGhost3 = myThread(4, "Ghost", lstGhostXY[2])
    threadGhost3.start()

    #create ghost4 thread
    threadGhost4 = myThread(5, "Ghost", lstGhostXY[3])
    threadGhost4.start()

def OnStop():
    threadEvent_GAMEOVER.set()

def Onkey(event):
    OnStart()

def OnMoveLeft(event):
    if not qMove.empty():
        item_gdc =qMove.get()
        item_gdc.direction = dirLeft
        qMove.put(item_gdc)
        #print ("Move left ")

def OnMoveRight(event):
    if not qMove.empty():
        item_gdc = qMove.get()
        item_gdc.direction = dirRight
        qMove.put(item_gdc)
        #print ("Move Right ")

def OnMoveUp(event):
    if not qMove.empty():
        item_gdc = qMove.get()
        item_gdc.direction = dirUp
        qMove.put(item_gdc)
        #print ("Move Up ")

def OnMoveDown(event):
    if not qMove.empty():
        item_gdc = qMove.get()
        item_gdc.direction = dirDown
        qMove.put(item_gdc)
        #print ("Move Down ")

##################
# mainWin 
##################
# create main window
mainwin=Tk()
mainwin.title("Runnng Man")
mainwin.geometry(geom)

mainwin.bind("<Key>", Onkey)
mainwin.bind("<Left>", OnMoveLeft)
mainwin.bind("<Right>", OnMoveRight)
mainwin.bind("<Up>", OnMoveUp)
mainwin.bind("<Down>", OnMoveDown)

# create Menu
'''
menu = Menu(mainwin)
mainwin.config(menu = menu)
setting = Menu(menu)
menu.add_cascade(label = 'Setting', menu = setting);
setting.add_command(label = 'Start', command = OnStart);
setting.add_command(label = 'Stop', command = OnStop);
'''

# create frame
frame = Frame(mainwin, width=WIN_WIDTH, height=WIN_HEIGHT)
frame.pack()

# create Canvas
canvas = Canvas(frame, bg = "black", width=WIN_WIDTH, height=WIN_HEIGHT)
canvas.pack()

# create all candies, dimX*dimY, tagid starts from 1
candyCount = dimX*dimY
for y in range (dimY):
    for x in range (dimX):
        coord_rect = x*pw+qw, y*pw+qw,x*pw+qw+hw, y*pw+qw+hw
        candyid = canvas.create_oval(coord_rect, fill="gray")
        gds.dicDATA[candyid] = CANDYEXIST

# draw RunMan & Ghost
curpath = os.getcwd()

#init RunMan
locationPCMan = os.path.join(curpath, "PCMan.gif")
iPCMan = PhotoImage(file = locationPCMan)
Rman = canvas.create_image((pw-40)/2, (pw-40)/2, anchor = NW, image = iPCMan)


#init Ghosts
lstGhostXY = []
lstiGhost = []
for index in range(0,4):
    while True:
        gx = random.randint(3,dimX-1)
        gy = random.randint(3,dimY-1)
        tup = (gx, gy)
        if not lstGhostXY :
            lstGhostXY.append(tup)
            break
        elif tup not in lstGhostXY:
            lstGhostXY.append(tup)
            break
    tempName = "Ghost"+str(index+1)+".gif" #ex: Ghost1.gif
    print (tempName)
    locationGhost = os.path.join(curpath, tempName)
    print (locationGhost)
    lstiGhost.append( PhotoImage(file = locationGhost) )

    L, T = (gx*pw + (pw-40)/2, gy*pw + (pw-40)/2)  #top-left corner position
    gds.lstGhost.append(index)
    gds.lstGhost[index] = canvas.create_image(L, T, anchor = NW, image = lstiGhost[index])
    candyid = getCandyID(gx, gy)
    gds.dicDATA[candyid] = gds.dicDATA[candyid] | lstGhostMask[index]
    print ("(%d, %d)" %(gx, gy))

#event loop to wait event input    
mainwin.mainloop()
print("bye bye ...")
