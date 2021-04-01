import sys
from coordinates import *
from drawnValue import *
from VisualizationApp import *

V = vector

class paletteTest(VisualizationApp):
    def __init__(self, title='Palette Test', **kwargs):
        super().__init__(title=title, maxArgWidth=30, **kwargs)
        self.selected = None
        self.nextPoint = (20, 20)
        self.boxSize = (200, 40)
        self.boxes = set()
        self.makeButtons()

    def boxCoords(self, upperLeft=None):
        if upperLeft is None: upperLeft = self.nextPoint
        return (upperLeft + (V(upperLeft) + V(self.boxSize)), 
                V(upperLeft) + V(V(self.boxSize) / 2))

    def createBox(self, color, upperLeft=None):
        if upperLeft is None: upperLeft = self.nextPoint
        coords = self.boxCoords(upperLeft=upperLeft)
        box = self.canvas.create_rectangle(
            *coords[0], fill=color, width=0, outline='red', tags=('box'))
        text = self.canvas.create_text(
            *coords[1], text=color, fill='black', font=self.VALUE_FONT,
            tags=('text'))
        items = (box, text)

        if upperLeft == self.nextPoint:
            self.nextPoint = V(self.nextPoint) + V(0, self.boxSize[1])
            if not BBoxContains(
                    self.visibleCanvas(),
                    self.nextPoint + (V(self.nextPoint) + V(self.boxSize))):
                self.nextPoint = (self.nextPoint[0] + self.boxSize[0] * 5 // 4,
                                  self.boxSize[1] // 2)
        result = drawnValue(color, *items)
        for item in items:
            self.canvas.tag_bind(item, '<Button-1>', self.startMove(result))
            self.canvas.tag_bind(item, '<B1-Motion>', self.moveBox(result))
            self.canvas.tag_bind(item, '<ButtonRelease-1>', self.dropBox(result))
            self.canvas.tag_bind(item, '<Double-Button-1>', self.killBox(result))
        return result

    def startMove(self, dValue):
        def startHandler(event):
            if self.selected:
                return
            self.selected = dValue
            self.lastPos = (event.x, event.y)
            for item in dValue.items:
                self.canvas.tag_raise(item)
            self.canvas.itemconfigure(dValue.items[0], width=2)
        return startHandler

    def moveBox(self, dValue):
        def moveHandler(event):
            if not self.selected:
                return
            for item in self.selected.items:
                self.canvas.move(item, *(V(event.x, event.y) - V(self.lastPos)))
            self.lastPos = (event.x, event.y)
        return moveHandler

    def dropBox(self, dValue):
        def dropHandler(event):
            if not self.selected:
                return
            self.canvas.itemconfigure(self.selected.items[0], width=0)
            self.selected = None
        return dropHandler

    def killBox(self, dValue):
        def killBoxHandler(event):
            if self.selected:
                return
            for item in dValue.items:
                self.canvas.delete(item)
            self.boxes.discard(dValue.val)
        return killBoxHandler
    
    def insert(self, color, location=None):
        try:
            box = self.createBox(color, upperLeft=location)
            self.boxes.add(color)
        except TclError as e:
            self.setMessage(str(e))

    def print(self):
        print(self.boxes)

    def clickInsert(self):
        self.insert(self.getArgument())
        self.clearArgument()

    def makeButtons(self):
        width_vcmd = (self.window.register(makeWidthValidate(self.maxArgWidth)),
                      '%P')
        self.insertButton = self.addOperation(
            "Insert", self.clickInsert, numArguments=1,
            validationCmd=width_vcmd, argHelpText=['color'], 
            helpText='Add a new color box')
        self.printButton = self.addOperation(
            "Print", self.print, helpText='Print current colors')
   
if __name__ == '__main__':
    app = paletteTest()
    for color in (sys.argv[1:] if len(sys.argv) > 1 else drawnValue.palette):
        app.setArgument(color)
        app.insertButton.invoke()
           
    app.runVisualization()
