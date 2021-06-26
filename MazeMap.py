import csv

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