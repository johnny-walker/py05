# https://www.rs-online.com/designspark/python-tkinter-cn#_Toc61529916

import tkinter as tk

class ProgramBase(tk.Frame):
    def __init__(self, root, width=600, height=400):
        super().__init__(root)
        self.root = root
        self.frame = self

        # configure window
        x = 450
        y = 150
        root.width = width
        root.height = height
        geometry = '{0:d}x{1:d}+{2:d}+{3:d}'.format(root.width+5, root.height+5, x, y) 
        root.geometry(geometry)    # ex. root.geometry('600x400+250+150')
        root.title("window")

        # bind events
        root.bind_all('<Key>', self.onKey)

    def run(self):
        self.root.mainloop()

    def onKey(self, event):
        if event.char == event.keysym or len(event.char) == 1:
            if event.keysym == 'Right':
                print("key Right") 
            elif event.keysym == 'Left':
                 print("key Left") 
            elif event.keysym == 'Space':
                 print("key Space") 
            elif event.keysym == 'Escape':
                print("key Escape") 
                self.root.destroy()

if __name__ == '__main__':
    program = ProgramBase(tk.Tk())
    program.run()
    print("quit, bye bye ...")





        