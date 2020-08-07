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
                      for ID in range(nDisks - 1, -1, -1)].reverse()

        # Create spindles on top of disks
        self.spindleDrawings = [
            self.createSpindleDrawing(j) for j in range(3)]
        self.window.update()

    def createSpindleDrawing(self, index):
        tags = ('spindle', 'spindle {}'.format(index))
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
        tags = ('disk', 'disk {}'.format(diskID))
        coords = self.diskCoords(diskID)
        return (
            self.canvas.create_oval(
                *coords[0], fill=self.diskSide, outline='', width=0,
                tags=tags),
            self.canvas.create_rectangle(
                *coords[1], fill=self.diskSide, outline='', width=0,
                tags=tags),
            self.canvas.create_oval(
                *coords[2], fill=self.diskTop, outline='', width=0,
                tags=tags),
        )
        pass

    def diskCoords(self, diskID):
        spindle, pos = self.diskSpindlePos(diskID)
        sw = self.spindleWidth
        tilt = sw
        half = tilt // 2
        dt = self.diskThickness
        radius = (diskID + 3) * sw * 1.5
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

    tower.runVisualization()
