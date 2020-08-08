from tkinter import *

try:
    from VisualizationApp import *
    from coordinates import *
except ModuleNotFoundError:
    from .VisualizationApp import *
    from .coordinates import *

V = vector

class TowerOfHanoi(VisualizationApp):

    def __init__(                  # Create a Tower of Hanoi puzzle
            self,                    # visualization application
            title="Tower of Hanoi",
            bbox=(20, 20, 780, 380), # Fit the display within this bounding box
            minDisks=1,              # on the canvas.  Limit number of disks to
            maxDisks=6,              # between minDisks
            diskSide='salmon4',      # Draw disks with one color for their sides
            diskTop='salmon2',       # and one for the tops
            baseSide='khaki3',       # Draw base and spindles with different
            baseTop='khaki1',        # colors on sides and tops
            **kwargs):
        kwargs['title'] = title
        super().__init__(**kwargs)
        self.bbox = bbox
        self.minDisks = minDisks
        self.maxDisks = maxDisks
        self.diskSide = diskSide
        self.diskTop = diskTop
        self.baseSide = baseSide
        self.baseTop = baseTop
        self.spindleSide = baseSide
        self.spindleTop = baseTop
        self.starColor = 'red'
        self.X0, self.Y0 = bbox[:2]
        self.width, self.height = V(bbox[2:]) - V(bbox[:2])
        self.spindles = [[]] * 3  # lists of disk indices
        self.disks = []
        self.picked = None
        self.spindleWidth = max(4, self.width // 90)
        self.diskThickness = max(self.spindleWidth, 18)
        self.padX = self.spindleWidth
        self.spindleX = [
           self.X0 + self.width // 2 + ((self.width - self.padX * 2) // 3) * x
           for x in range(-1, 2)]
        self.buttons = self.makeButtons()
        self.display(0)

    def __str__(self):
        return str(self.spindles)

    def display(self, nDisks):
        self.canvas.delete("all")

        sw = self.spindleWidth
        starOnAxis = regularStar((self.bbox[2] - 5 * sw, 0),
                                 sw * 2, sw * 2 * 0.6, 6)
        tiltStar = [V(V(vert) / V(1, 3)) + V(0, self.bbox[3] - sw * 2)
                    for vert in starOnAxis]
        self.base = (
            self.canvas.create_rectangle(
                self.bbox[0], self.bbox[3] - sw,
                self.bbox[2], self.bbox[3], fill=self.baseSide, outline='',
                width=0, tags='base'),
            self.canvas.create_polygon(
                self.bbox[0], self.bbox[3] - sw,
                self.bbox[2], self.bbox[3] - sw,
                self.bbox[2] - 3 * sw, self.bbox[3] - 5 * sw,
                self.bbox[0] + 3 * sw, self.bbox[3] - 5 * sw,
                fill=self.baseTop, outline='', width=0, tags='base'),
            self.canvas.create_polygon(
                *tiltStar, fill=self.starColor, outline='', width=0, 
                tags=('base', 'star'))
           )
        
        # Put all disks on left spindle, largest first
        self.spindles = [list(range(nDisks - 1, -1, -1)), [], []]
        
        # Create largest first for stacking order
        self.disks = [self.createDiskDrawing(ID)
                      for ID in range(nDisks - 1, -1, -1)]
        self.disks.reverse()

        # Create spindles on top of disks
        self.spindleDrawings = [
            self.createSpindleDrawing(j) for j in range(3)]
        self.window.update()

    def createSpindleDrawing(self, index):
        tags = ('spindle', self.spindleTag(index))
        coords = self.spindleCoords(index)
        return (
            self.canvas.create_oval(
                *coords[0], fill=self.spindleSide, outline='', width=0,
                tags=tags),
            self.canvas.create_rectangle(
                *coords[1], fill=self.spindleSide, outline='', width=0,
                tags=tags),
            self.canvas.create_oval(
                *coords[2], fill=self.spindleTop, outline='', width=0,
                tags=tags),
        )

    # Compute coordinates for the canvas items making the spindle at
    # the given index
    def spindleCoords(self, index):
        sw = self.spindleWidth
        dt = self.diskThickness
        half = sw // 2
        quarter = half // 2
        baseY = self.bbox[3] - 3 * sw
        topY = self.bbox[3] - (self.maxDisks + 3) * dt - 3 * sw
        # Bottom of spindle goes to top of stack of disks
        bottom = baseY - len(self.spindles[index]) * dt
        return ( # Bottom disk
            (self.spindleX[index] - half, bottom - quarter,
             self.spindleX[index] + (sw - half), bottom + (half - quarter)),
            # Rectangle shaft
            (self.spindleX[index] - half, bottom,
             self.spindleX[index] + (sw - half), topY),
            # Top disk
            (self.spindleX[index] - half, topY - quarter,
             self.spindleX[index] + (sw - half), topY + (half - quarter))
        )
        
    def createDiskDrawing(self, diskID):
        tags = ('disk', self.diskTag(diskID))
        normal = {'width': 0, 'outline': ''}
        highlight = {'width': 1, 'outline': 'yellow'}
        kwargs = dict(normal, tags=tags)
        coords = self.diskCoords(diskID)
        items = (
            self.canvas.create_oval(*coords[0], fill=self.diskSide, **kwargs),
            self.canvas.create_rectangle(
                *coords[1], fill=self.diskSide, **kwargs),
            self.canvas.create_oval(
                *coords[2], fill=self.diskSide, **kwargs),
        )
        ELHandler = self.enterLeaveHandler(diskID, tags[1], normal, highlight)
        startMoveHandler = self.startMoveHandler(
            diskID, tags[1], normal, highlight)
        moveHandler = self.moveHandler(diskID, tags[1], normal, highlight)
        releaseHandler = self.releaseHandler(diskID, tags[1], normal, highlight)
        self.canvas.tag_bind(tags[1], '<Enter>', ELHandler)
        self.canvas.tag_bind(tags[1], '<Leave>', ELHandler)
        self.canvas.tag_bind(tags[1], '<Button-1>', startMoveHandler)
        self.canvas.tag_bind(tags[1], '<B1-Motion>', moveHandler)
        self.canvas.tag_bind(tags[1], '<ButtonRelease-1>', releaseHandler)
        return items

    def diskCoords(self, diskID):
        spindle, pos = self.diskSpindlePos(diskID)
        sw = self.spindleWidth
        tilt = sw
        half = tilt // 2
        dt = self.diskThickness
        radius = (diskID + 2) * sw * 1.5
        baseY = self.bbox[3] - 3 * sw - pos * dt
        topY = baseY - dt
        return ( # Bottom disk
            (self.spindleX[spindle] - radius, baseY - half,
             self.spindleX[spindle] + radius, baseY + tilt - half),
            # Rectangle plate
            (self.spindleX[spindle] - radius, topY,
             self.spindleX[spindle] + radius, baseY),
            # Top disk
            (self.spindleX[spindle] - radius, topY - half,
             self.spindleX[spindle] + radius, topY + tilt - half),
        )

    def diskSpindlePos(self, diskID):
        for spindle in range(3):
            for j, ID in enumerate(self.spindles[spindle]):
                if ID == diskID:
                    return spindle, j
        return None, None
                
    def isPickable(self, diskID):
        spindle, pos = self.diskSpindlePos(diskID)
        return (spindle is not None and self.picked is None and
                self.spindles[spindle][-1] == diskID)

    def enterLeaveHandler(self, ID, tag, normal, highlight):
        def handler(event):
            print(event.type, 'for', tag)
            kwargs = highlight if (event.type == EventType.Enter and
                                   self.isPickable(ID)) else normal
            if event.type == EventType.Enter and not self.isPickable(ID):
                spindle, pos = self.diskSpindlePos(ID)
                if spindle is None:
                    print('Disk', ID, 'is not on any spindle')
                else:
                    print('Disk', ID,
                          'is not pickable ({}, {}, topID={})'.format(
                              spindle, pos, self.spindles[spindle][-1]))
            self.canvas.itemconfigure(tag, **kwargs)
            # print('Set appearance to:', kwargs)
        return handler
    
    def startMoveHandler(self, ID, tag, normal, highlight):
        def handler(event):
            print(event.type, 'for', tag)
            spindle, pos = self.diskSpindlePos(ID)
            self.pickedFrom = spindle
            self.picked = self.spindles[spindle].pop()
            self.lastPos = (event.x, event.y)
            self.canvas.tag_raise(tag, 'spindle')
            self.updateSpindles(spindle)
        return handler

    def moveHandler(self, ID, tag, normal, highlight):
        def handler(event):
            if self.picked is None:
                return
            print(event.type, 'for', tag)
            self.canvas.move(
                tag, event.x - self.lastPos[0], event.y - self.lastPos[1])
            self.lastPos = (event.x, event.y)
        return handler

    def releaseHandler(self, ID, tag, normal, highlight):
        def handler(event):
            if self.pickedFrom is None:
                return
            print(event.type, 'for', tag)
            print('Placing disk', ID, 'on spindle', self.pickedFrom)
            self.spindles[self.pickedFrom].append(ID)
            self.restoreDisks()
            self.canvas.tag_lower(tag, 'spindle')
            self.updateSpindles(self.pickedFrom)
            self.picked, self.pickedFrom = None, None
        return handler

    def updateSpindles(self, *spindleIDs):
        for spindle in (spindleIDs if spindleIDs else range(3)):
            print('Update spindle', spindle, 'with', 
                  len(self.spindles[spindle]), 'disk(s) coords:',
                  self.spindleCoords(spindle))
            for item, coords in zip(
                    self.spindleDrawings[spindle], self.spindleCoords(spindle)):
                self.canvas.coords(item, *coords)
            self.window.update()

    def restoreDisks(self, *diskIDs):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()
        for ID in (diskIDs if diskIDs else range(len(self.disks))):
            tag = self.diskTag(ID)
            items = sorted(self.canvas.find_withtag(tag))
            current = [self.canvas.coords(item) for item in items]
            target = self.diskCoords(ID)
            self.moveItemsTo(items, target, steps=10, sleepTime=0.01)
        self.cleanUp(callEnviron)
            
    def diskTag(self, ID): return 'disk {}'.format(ID)
            
    def spindleTag(self, ID): return 'spindle {}'.format(ID)
            
    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        newButton = self.addOperation(
            "New", self.clickNew, numArguments=1, validationCmd=vcmd)
        #this makes the pause, play and stop buttons 
        self.addAnimationButtons()
        return [newButton]

    def validArgument(self):
        entered_text = self.getArgument()
        if entered_text and entered_text.isdigit():
            val = int(entered_text)
            if val < 100:
                return val

    # Button functions
    def clickNew(self):
        val = self.validArgument()
        if val is None or int(val) < self.minDisks or self.maxDisks < int(val):
            self.setMessage("Input must be an integer from {} to {}"
                            .format(self.minDisks, self.maxDisks))
        else:
            nDisks = int(val)
            self.display(nDisks)
            self.setMessage('You need at least {} move{}.  Good luck!'.format(
                pow(2, nDisks) - 1, '' if nDisks == 1 else 's'))
        self.clearArgument()

if __name__ == '__main__':
    tower = TowerOfHanoi()

    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        tower.display(int(sys.argv[1]))
        
    tower.runVisualization()
