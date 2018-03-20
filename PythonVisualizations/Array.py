from tkinter import *
import time
import random

WIDTH = 800
HEIGHT = 600

window = Tk()
frame = Frame(window)
frame.pack()

canvas = Canvas(frame, width=WIDTH, height=HEIGHT)
window.title("Array")
canvas.pack()

# Button functions
def clickFind():
    entered_text=textBox.get()
    txt = ''
    if array.find(int(entered_text)):
        txt = "Found!"
    else:
        txt = "Value not found"
    outputText.set(txt)

def close_window():
    window.destroy()
    exit()


bottomframe = Frame(window)
bottomframe.pack( side = BOTTOM )

Label (bottomframe, text="Find:", font="none 12 bold").grid(row=0, column=0, sticky=W)
textBox = Entry(bottomframe, width=20, bg="white")
textBox.grid(row=0, column=1, sticky=W)

# add a submit button
Button(bottomframe, text="Enter", width=6, command=clickFind).grid(row=0, column=2, sticky=W)
outputText = StringVar()
outputText.set('')
output = Label (bottomframe, textvariable=outputText, font="none 12 bold")
output.grid(row=0, column=3, sticky=E)

# exit button
Button(bottomframe, text="EXIT", width=4, command=close_window).grid(row=2, column=0, sticky=W)

class Array(object):
    colors = ['red', 'green', 'blue', 'orange', 'yellow', 'cyan', 'magenta',
              'dodgerblue', 'turquoise', 'grey', 'gold', 'pink']
    nextColor = 0

    def __init__(self):
        self.list = []
        self.arrow = None
        self.foundBox = None

    def get(self, index):
        try:
            return self.list[index][0]
        except:
            print("Invalid list index")
            return -1

    def set(self, index, val):
        self.list[index] = (val, Array.colors[Array.nextColor])
        Array.nextColor = (Array.nextColor + 1)%len(Array.colors)

    def append(self, val):
        self.list.append((val, Array.colors[Array.nextColor]))
        Array.nextColor = (Array.nextColor + 1) % len(Array.colors)
        self.display()

    def delete(self):
        self.list.pop()

    def display(self):
        xpos = 50
        ypos = 50
        for n in self.list:
            print(n)
            canvas.create_rectangle(xpos, ypos, xpos+50, ypos+50, fill=n[1])
            canvas.create_text(xpos+25, ypos+25, text=n[0], font=('Helvetica', '20'))
            xpos += 50
        window.update()

    def find(self, val):
        x = 75
        y0 = 10
        y1 = 35
        if self.arrow:
            canvas.coords(self.arrow, x, y0, x, y1)
            canvas.delete(self.foundBox)
        else:
            self.arrow = self.drawArrow(x, y0, x, y1)
        arrow = self.arrow
        for n in self.list:
            if n[0] == val:
                pos = canvas.coords(arrow)
                self.foundBox = canvas.create_rectangle(pos[0]-(x-50), 50, pos[2]+(x-50), 100, fill='', outline="green2", width="5")
                return True
            self.display()
            time.sleep(1)
            canvas.move(arrow, 50, 0)

        return False

    def drawArrow(self, x0, y0, x1, y1):
        return canvas.create_line(x0, y0, x1, y1, arrow="last")


class Ball:
    def __init__(self, color, size):
        self.shape = canvas.create_oval(10, 10, size, size, fill=color)
        self.xspeed = random.randrange(-10,10)
        self.yspeed = random.randrange(-10,10)

    def move(self):
        canvas.move(self.shape, self.xspeed, self.yspeed)
        pos = canvas.coords(self.shape)
        if pos[3] >= HEIGHT or pos[1] <= 0:
            self.yspeed = -self.yspeed
        if pos[0] <= 0 or pos[2] >= WIDTH:
            self.xspeed = -self.xspeed


def main():
    array = Array()
    for i in range(10):
        array.append(i)

    array.display()

    time.sleep(1)

    array.find(6)

    window.mainloop()

main()

'''
To Do:
- make it look pretty
- disable use of buttons when a function is in progress
'''