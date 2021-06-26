# movement algorithm
class MazeMove():
    def __init__(self, maze):
        self.mouseRoute = []
        self.candidatesStack = []
        self.maze = maze
        self.currentItem = None
        self.visited = []

    def initState(self, x, y):
        # append route item (direction, parent, child)  
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