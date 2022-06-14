from tkinter import *

try:
    from coordinates import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .coordinates import *
    from .tkUtilities import *
    from .VisualizationApp import *

V = vector

class TowerOfHanoi(VisualizationApp):
    diskColors = (          # Side and top colors for disks
        ('salmon4', 'salmon2'), ('yellow4', 'yellow3'),
        ('chocolate3', 'chocolate1'), ('SteelBlue4', 'SteelBlue2'),
        ('green4', 'green2'), ('orchid3', 'orchid1'),
    )

    def __init__(                    # Create a Tower of Hanoi puzzle
            self,                    # visualization application
            title="Tower of Hanoi",
            bbox=(20, 20, 780, 380), # Fit the display within this bounding box
            minDisks=1,              # on the canvas.  Limit number of disks to
            maxDisks=6,              # between minDisks
            baseSide='khaki3',       # Draw base and spindles with different
            baseTop='khaki1',        # colors on sides and tops
            labelHeight=20,          # Height of spindle labels
            **kwargs):
        kwargs['title'] = title
        super().__init__(**kwargs)
        self.bbox = bbox
        self.minDisks = minDisks
        self.maxDisks = maxDisks
        self.baseSide = baseSide
        self.baseTop = baseTop
        self.spindleSide = baseSide
        self.spindleTop = baseTop
        self.labelHeight = labelHeight
        self.starColor = 'red'
        self.X0, self.Y0 = bbox[:2]
        self.width, self.height = V(bbox[2:]) - V(bbox[:2])
        self.spindles = [[]] * 3      # lists of disk indices
        self.spindleBBoxes = [[]] * 3 # 4 coordinates of spindle's bounding box
        self.disks = []
        self.moves = 0
        self.spindleWidth = max(4, self.width // 90)
        self.diskThickness = max(self.spindleWidth, 18)
        self.padX = self.spindleWidth
        self.buttons = self.makeButtons()
        self.display()
        self.setupDisks(0)

    def spindleX(self, index):
        return (self.X0 + self.width // 2 + 
                ((self.width - self.padX * 2) // 3) * (index - 1))
    
    def __str__(self):
        return str(self.spindles)

    def nDisks(self):
        return len(self.disks)
    
    def display(self):
        self.canvas.delete("all")
        # labels used by solver, shared across recursive calls
        self.spindleLabels = {}

        sw = self.spindleWidth
        baseBottom = self.bbox[3] - self.labelHeight
        starOnAxis = regularStar((self.bbox[2] - 5 * sw, 0),
                                 sw * 2, sw * 2 * 0.6, 6)
        tiltStar = [V(V(vert) / V(1, 3)) + V(0, baseBottom - sw * 2)
                    for vert in starOnAxis]
        self.base = (
            self.canvas.create_rectangle(
                self.bbox[0], baseBottom - sw,
                self.bbox[2], baseBottom, fill=self.baseSide, outline='',
                width=0, tags='base'),
            self.canvas.create_polygon(
                self.bbox[0], baseBottom - sw,
                self.bbox[2], baseBottom - sw,
                self.bbox[2] - 3 * sw, baseBottom - 5 * sw,
                self.bbox[0] + 3 * sw, baseBottom - 5 * sw,
                fill=self.baseTop, outline='', width=0, tags='base'),
            self.canvas.create_polygon(
                *tiltStar, fill=self.starColor, outline='', width=0, 
                tags=('base', 'star'))
           )
        self.spindleDrawings = [     # Create canvas spindles
            self.createSpindleDrawing(j) for j in range(3)]
        self.window.update()

    _init__Code = '''
def __init__(self, nDisks={nDisks}):
   self.__stacks = [None] * 3
   self.__labels = ['L', 'M', 'R']
   self.__nDisks = nDisks
   self.reset()
'''

    resetCode = '''
def reset(self):
   for spindle in range(3):
      self.__stacks[spindle] = Stack(
         self.__nDisks)
      if spindle == 0:
         for disk in range(
               self.__nDisks, 0, -1):
            self.__stacks[spindle].push(disk)
'''

    def setupDisks(self, nDisks, code=_init__Code, start=True):
        wait = 0.05
        callEnviron = None
        if nDisks > 0:
            callEnviron = self.createCallEnvironment(
                code.format(**locals()), sleepTime=wait / 5, 
                startAnimations=start)

        self.spindles = [[] for _ in range(3)]   # Prepare to create spindles
        if callEnviron:
            self.highlightCode('self.__stacks = [None] * 3', callEnviron, wait)
            self.highlightCode("self.__labels = ['L', 'M', 'R']",
                               callEnviron, wait)
            spindleLabels = [
                self.createSpindleLabel(label, spindle) 
                for spindle, label in enumerate(['L', 'M', 'R'])]
            callEnviron |= set(spindleLabels)
            self.highlightCode('self.__nDisks = nDisks', callEnviron, wait)
            self.highlightCode('self.reset()', callEnviron, wait)
            callEnviron2 = self.createCallEnvironment(
                self.resetCode, sleepTime=wait / 5)
            for label in spindleLabels:
                self.canvas.delete(label)
                callEnviron.discard(label)
            self.highlightCode('spindle in range(3)', callEnviron2)

        self.disks = [None] * nDisks # Prepare to create disks
        spindleLabel = None
        for spindle in range(3):
            if callEnviron:
                if spindleLabel is None:
                    spindleLabel = self.createSpindleLabel('spindle', spindle)
                    callEnviron2.add(spindleLabel)

                self.highlightCode(
                    'self.__stacks[spindle] = Stack(\n         self.__nDisks)',
                    callEnviron2, wait)
                self.highlightCode('spindle == 0', callEnviron2, wait)
                
            if spindle == 0: # On left spindle
                if callEnviron:
                    self.highlightCode(
                        'disk in range(\n               self.__nDisks, 0, -1)',
                        callEnviron2, wait)
                for ID in range(nDisks - 1, -1, -1):
                    if callEnviron:
                        self.highlightCode('self.__stacks[spindle].push(disk)',
                                           callEnviron2, wait)
                    # Internally put disk on spindle
                    self.spindles[spindle].append(ID)
                    self.disks[ID] = self.createDiskDrawing(ID)
                    self.moveItemsTo(self.disks[ID], self.diskCoords(ID),
                                     sleepTime=wait / 5)
                    self.updateSpindles(spindle)
                    if callEnviron:
                        self.highlightCode(
                            'disk in range(\n               self.__nDisks, 0, -1)',
                            callEnviron2, wait)
            else:
                self.updateSpindles(spindle)

            if callEnviron:
                self.highlightCode('spindle in range(3)', callEnviron2)
                self.moveItemsTo(
                    spindleLabel, self.spindleLabelCenter(spindle + 1),
                    sleepTime=wait / 5)

        self.picked, self.pickedFrom = None, None
        if callEnviron:
            self.cleanUp(callEnviron2, sleepTime=wait / 5)
            self.highlightCode([], callEnviron, wait)
            self.cleanUp(callEnviron, sleepTime=wait / 5)

    def createSpindleDrawing(self, index):
        tags = ('spindle', self.spindleTag(index))
        coords = self.spindleCoords(index)
        items = (
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
        self.spindleBBoxes[index] = self.canvas.bbox(tags[1])
        return items

    # Compute coordinates for the canvas items making the spindle at
    # the given index
    def spindleCoords(self, index):
        sw = self.spindleWidth
        dt = self.diskThickness
        half = sw // 2
        quarter = half // 2
        baseBottom = self.bbox[3] - self.labelHeight
        baseY = baseBottom - 3 * sw
        topY = baseBottom - (self.maxDisks + 3) * dt - 3 * sw
        # Bottom of spindle goes to top of stack of disks
        bottom = baseY - len(self.spindles[index]) * dt
        return ( # Bottom disk
            (self.spindleX(index) - half, bottom - quarter,
             self.spindleX(index) + (sw - half), bottom + (half - quarter)),
            # Rectangle shaft
            (self.spindleX(index) - half, bottom,
             self.spindleX(index) + (sw - half), topY),
            # Top disk
            (self.spindleX(index) - half, topY - quarter,
             self.spindleX(index) + (sw - half), topY + (half - quarter))
        )

    def spindleLabelCenter(self, index):
        return (self.spindleX(index), self.bbox[3] - self.labelHeight // 2)

    def createSpindleLabel(self, text, index):
        return self.canvas.create_text(
            *self.spindleLabelCenter(index), text=text, font=self.VARIABLE_FONT,
            fill=self.VARIABLE_COLOR, tags='spindle_label')
        
    def createDiskDrawing(self, diskID):
        tags = ('disk', self.diskTag(diskID))
        normal = {'width': 0, 'outline': ''}
        highlight = {'width': 1, 'outline': 'blue'}
        kwargs = dict(normal, tags=tags)
        coords = [moveAboveCanvas(bbox) for bbox in self.diskCoords(diskID)]
        color = max(0, min(len(self.diskColors) - 1, diskID))
        items = (
            self.canvas.create_oval(
                *coords[0], fill=self.diskColors[color][0], **kwargs),
            self.canvas.create_rectangle(
                *coords[1], fill=self.diskColors[color][0], **kwargs),
            self.canvas.create_oval(
                *coords[2], fill=self.diskColors[color][1], **kwargs),
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
        if spindle is None or pos is None:  # If we can't find the disk
            return ((), (), ())  # we don't know where it should be placed
        sw = self.spindleWidth
        tilt = sw
        half = tilt // 2
        dt = self.diskThickness
        radius = (diskID + 2) * sw * 1.5
        baseBottom = self.bbox[3] - self.labelHeight
        baseY = baseBottom - 3 * sw - pos * dt
        topY = baseY - dt
        return ( # Bottom disk
            (self.spindleX(spindle) - radius, baseY - half,
             self.spindleX(spindle) + radius, baseY + tilt - half),
            # Rectangle plate
            (self.spindleX(spindle) - radius, topY,
             self.spindleX(spindle) + radius, baseY),
            # Top disk
            (self.spindleX(spindle) - radius, topY - half,
             self.spindleX(spindle) + radius, topY + tilt - half),
        )

    def diskSpindlePos(self, diskID):
        for spindle in range(3):
            for j, ID in enumerate(self.spindles[spindle]):
                if ID == diskID:
                    return spindle, j
        return None, None
                
    def isPickable(self, diskID):
        spindle, pos = self.diskSpindlePos(diskID)
        return spindle is None or (self.picked is None and
                                   self.spindles[spindle][-1] == diskID)

    def isPlacable(self, diskID, spindle):
        return spindle is not None and (
            len(self.spindles[spindle]) == 0 or
            self.spindles[spindle][-1] > diskID)

    def isDone(self):
        return (len(self.spindles[0]) == 0 and
                len(self.spindles[1]) == 0 and
                len(self.spindles[2]) == len(self.disks) and
                len(self.spindles[2]) > 0)

    def leftSpindleFull(self):
        return len(self.spindles[0]) == len(self.disks)
    
    def enterLeaveHandler(self, ID, tag, normal, highlight):
        def leaveEnterHandler(event):
            kwargs = highlight if (
                event.type == EventType.Enter and self.isPickable(ID) and
                not self.operationMutex.locked()) else normal
            self.canvas.itemconfigure(tag, **kwargs)
        return leaveEnterHandler
    
    def startMoveHandler(self, ID, tag, normal, highlight):
        def startHandler(event):
            if not self.operationMutex.acquire(blocking=False):
                self.setMessage('Cannot move disks during other operation')
                return
            self.cleanUp(ignoreStops=True)  # Clean up any items left by solver
            spindle, pos = self.diskSpindlePos(ID)
            if spindle and pos and ID != self.spindles[spindle][-1]:
                print('Cannot pick up disk', ID, 'with',
                      self.spindles[spindle][-1], 'on top of it')
                return
            if spindle is not None:
                self.spindles[spindle].pop()
            self.picked, self.pickedFrom = ID, spindle
            self.lastPos = (event.x, event.y)
            self.canvas.tag_raise(tag, 'spindle')
            if spindle is not None:
                self.updateSpindles(spindle)
        return startHandler

    def moveHandler(self, ID, tag, normal, highlight):
        def mvHandler(event):
            if self.picked is None or not self.operationMutex.locked():
                return
            self.canvas.move(
                tag, event.x - self.lastPos[0], event.y - self.lastPos[1])
            self.lastPos = (event.x, event.y)
            diskBBox = self.canvas.bbox(tag)
            for spindle, spindleBBox in enumerate(self.spindleBBoxes):
                kwargs = (highlight if BBoxesOverlap(
                    diskBBox, spindleBBox) and self.isPlacable(ID, spindle)
                          else normal)
                self.canvas.itemconfigure(self.spindleTag(spindle), **kwargs)
        return mvHandler

    def releaseHandler(self, ID, tag, normal, highlight):
        def relHandler(event):
            if self.picked is None or not self.operationMutex.locked():
                return
            diskBBox = self.canvas.bbox(tag)
            dropAt = None
            for spindle, spindleBBox in enumerate(self.spindleBBoxes):
                if BBoxesOverlap(
                    diskBBox, spindleBBox) and self.isPlacable(ID, spindle):
                    dropAt = spindle
                    self.moves += 1
                    break
            if dropAt is None:
                if self.pickedFrom is None:
                    self.operationMutex.release()
                    return
                dropAt = self.pickedFrom
            self.spindles[dropAt].append(ID)
            self.canvas.itemconfigure(self.spindleTag(dropAt), **normal)
            diskItems = sorted(self.canvas.find_withtag(tag))
            diskCoords = self.diskCoords(ID)
            self.restoreTo(diskItems, diskCoords, after=lambda items, coords:
                           [self.canvas.coords(i, c)
                            for i, c in zip(items, coords)])
            self.canvas.tag_lower(tag, 'spindle')
            self.updateSpindles(dropAt)
            self.picked, self.pickedFrom = None, None
            if self.isDone():
                self.showCompletion()
            self.operationMutex.release()
            self.enableButtons()
        return relHandler

    def updateSpindles(self, *spindleIDs):
        for spindle in (spindleIDs if spindleIDs else range(3)):
            for item, coords in zip(
                    self.spindleDrawings[spindle], self.spindleCoords(spindle)):
                self.canvas.coords(item, *coords)
                self.canvas.tag_raise(item)
            self.spindleBBoxes[spindle] = self.canvas.bbox(
                self.spindleTag(spindle))
            self.window.update()

    def stop(self, *args):   # Customize stop operation to restore disk
        super().stop(*args)

        for ID in range(len(self.disks)):
            diskItems = sorted(self.canvas.find_withtag(self.diskTag(ID)))
            diskCoords = self.diskCoords(ID)
            self.restoreTo(diskItems, diskCoords, after=lambda items, coords:
                           [self.canvas.coords(i, c)
                            for i, c in zip(items, coords)])

    def showCompletion(self):
        msg = 'Puzzle completed!'
        if self.getMessage() == msg:
            return
        canvasDimensions = widgetDimensions(self.canvas)
        starCenter = V(canvasDimensions) * V(1/3, 1)
        size, ratio, points, angle = 5, 0.38, 5, 270
        rate = 0.92
        targetCenter = V(canvasDimensions) * V(1/2, 1/2)
        targetSize = canvasDimensions[0] / 2
        targetAngle = -90
        callEnviron = self.createCallEnvironment(startAnimations=False)
        self.startAnimations(enableStops=False)
        starCoords = regularStar(starCenter, size, size * ratio, points, angle)
        star = self.canvas.create_polygon(
            *starCoords, fill='goldenrod', outline='red', 
            width=max(1, size / 100))
        callEnviron.add(star)
        while size < targetSize or starCenter != targetCenter:
            starCenter = (   # Move star towards target and increase size
                targetCenter
                if V(V(targetCenter) - V(starCenter)).len2() < 2 else
                (V(V(targetCenter) * (1 - rate)) + V(V(starCenter) * rate)))
            size = (targetSize if abs(targetSize - size) < 2 else
                    (targetSize * (1 - rate) + size * rate))
            angle = (targetAngle if abs(targetSize - size) < 2 else
                     (targetAngle * (1 - rate) + angle * rate))
            starCoords = regularStar(
                starCenter, size, size * ratio, points, angle)
            self.canvas.coords(star, *flat(*starCoords))
            self.canvas.itemconfigure(star, width=max(1, size / 100))
            self.wait(0.01)
        font = ('Helvetica', -max(12, int(size / 10)))
        callEnviron.add(self.canvas.create_text(
            *(V(starCenter) + V(0, font[1])), text='Puzzle Completed',
            font=font, anchor=S))
        callEnviron.add(self.canvas.create_text(
            *starCenter, text='in {} move{}!'.format(
                self.moves, '' if self.moves == 1 else 's'), 
            font=font, anchor=S))
        self.cleanUp(callEnviron)
        self.setMessage(msg)
        
    def diskTag(self, ID): return 'disk {}'.format(ID)
            
    def spindleTag(self, ID): return 'spindle {}'.format(ID)
    solveCode = '''
def solve(self, nDisks={nDisks}, start={start}, goal={goal}, spare={spare}):
   if nDisks <= 0: return
   self.solve(nDisks - 1, start, spare, goal)
   self.move(start, goal)
   self.solve(nDisks - 1, spare, goal, start)
'''
    
    def solve(self, nDisks=None, start=0, goal=2, spare=1, 
              startAnimations=True):
        if nDisks is None:
            nDisks = self.nDisks()
        highlightWait = 0.08
        moveWait = 0.01
        callEnviron = self.createCallEnvironment(
            self.solveCode.format(**locals()), sleepTime=moveWait,
            startAnimations=startAnimations)

        self.highlightCode(
            'nDisks={nDisks}, start={start}, goal={goal}, spare={spare}'
            .format(**locals()), callEnviron)
        
        labels = ('start', 'goal', 'spare')
        labelPositions = list(zip(labels, (start, goal, spare)))
        for label, pos in labelPositions:
            if (label not in self.spindleLabels or 
                len(self.canvas.coords(self.spindleLabels[label])) == 0):
                self.spindleLabels[label] = self.createSpindleLabel(label, pos)
                callEnviron.add(self.spindleLabels[label])
        labelItems = [self.spindleLabels[label] for label in labels]
        startLabel = 'start  nDisks={}'.format(nDisks)
        self.canvas.itemconfigure(labelItems[0], text=startLabel)
        labelCoords = [
            self.canvas.coords(labelItem) for labelItem in labelItems]
        toCoords = [self.spindleLabelCenter(lp[1]) for lp in labelPositions]
        if flat(*labelCoords) != flat(*toCoords):
            self.moveItemsTo(labelItems, toCoords, sleepTime=moveWait)

        self.highlightCode('nDisks <= 0', callEnviron)
        if nDisks <= 0:
            self.highlightCode('return', callEnviron, highlightWait)
            self.cleanUp(callEnviron, sleepTime=0.01)
            return
        
        self.highlightCode('self.solve(nDisks - 1, start, spare, goal)',
                           callEnviron)
        self.solve(nDisks - 1, start, spare, goal)
        self.moveItemsTo(labelItems, toCoords, sleepTime=moveWait)
        self.canvas.itemconfigure(labelItems[0], text=startLabel)
        self.highlightCode('self.move(start, goal)', callEnviron)
        self.moveDisk(start, goal)
        self.moves += 1
        self.highlightCode('self.solve(nDisks - 1, spare, goal, start)',
                           callEnviron)
        self.solve(nDisks - 1, spare, goal, start)
        self.moveItemsTo(labelItems, toCoords, sleepTime=moveWait)
        self.canvas.itemconfigure(labelItems[0], text=startLabel)
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron, sleepTime=0.01)

    def moveDisk(self, fromSpindle, toSpindle):
        ID = self.spindles[fromSpindle].pop()
        tag = self.diskTag(ID)
        wait = 0.01
        diskBBox = self.canvas.bbox(tag)
        fromSpindleTopBBox = self.spindleCoords(fromSpindle)[-1]
        toSpindleTopBBox = self.spindleCoords(toSpindle)[-1]
        self.updateSpindles(fromSpindle)
        self.canvas.tag_raise(tag, 'spindle')
        self.spindles[toSpindle].append(ID)
        self.moveItemsBy(
            self.disks[ID], 
            (0, min(fromSpindleTopBBox[1], fromSpindleTopBBox[3]) - 
             max(diskBBox[1], diskBBox[3])),
            sleepTime=wait)
        delta = V((toSpindleTopBBox[0] - fromSpindleTopBBox[0], 0) * 2)
        toCoords = [delta + V(self.canvas.coords(item))
                    for item in self.disks[ID]]
        self.moveItemsOnCurve(
            self.disks[ID], toCoords, sleepTime=wait,
            startAngle=40 if delta[0] < 0 else -40)
        self.moveItemsTo(self.disks[ID], self.diskCoords(ID),
                         sleepTime=wait)
        self.canvas.tag_lower(tag, 'spindle')
        self.updateSpindles(toSpindle)

    def restoreTo(
            self, items, targetCoords, by=0.2, dist2=4, wait=30,
            increaseBy=1.1, after=None):
        '''Restore a set of canvas items to their target coordinates.  At each
        step, advance linearly by the given "by" factor until the
        squared distance of all (non-deleted) items is less than dist2
        from their target.  Increase the "by" factor by the increaseBy
        ratio after waiting wait milliseconds between steps.  Execute
        tha after function on the item and targetCoords at the end, if
        callable.
        '''
        targets = [
            (item, self.canvas_coords(item), tgt) 
            for item, tgt in zip(items, targetCoords) if self.canvas.type(item)]
        if all(distance2(target[1], target[2]) <= dist2 for target in targets):
            if callable(after):
                after(items, targetCoords)
            return
        by = max(0.01, min(1, by))
        for item, coords, target in targets:
            self.canvas.coords(
                item, V(V(coords) * (1 - by)) + V(V(target) * by))
        self.canvas.after(wait, lambda: self.restoreTo(
            items, targetCoords, by * increaseBy, dist2, wait, increaseBy,
            after))
        
    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.newButton = self.addOperation(
            "New", self.clickNew, numArguments=1, validationCmd=vcmd,
            argHelpText=['number of disks'], 
            helpText='Create a new puzzle of N disks')
        self.solveButton = self.addOperation(
            "Solve", self.clickSolve, helpText='Solve the puzzle')
        self.solveButton['state'] = DISABLED
        #this makes the pause, play and stop buttons 
        self.addAnimationButtons()
        return [self.newButton, self.solveButton]

    def enableButtons(self, enable=True): # Customize enableButtons
        super().enableButtons(enable)  # Perform common operation
        # Only enable solve button when left spindle is full with 1 or
        self.solveButton['state'] = ( # more diskks
            NORMAL if enable and self.nDisks() and self.leftSpindleFull()
            else DISABLED)
        
    def validArgument(self):
        entered_text = self.getArgument()
        if entered_text and entered_text.isdigit():
            val = int(entered_text)
            if self.minDisks <= val and val <= self.maxDisks:
                return val

    def cleanUp(self, callEnviron=None, **kwargs):
        super().cleanUp(callEnviron=callEnviron, **kwargs)
        if callEnviron is None and len(self.callStack) == 0:
            self.setMessage('')
    
    # Button functions
    def clickNew(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input must be an integer from {} to {}"
                            .format(self.minDisks, self.maxDisks))
        else:
            nDisks = int(val)
            self.spindles = [[] for _ in range(3)] # Clear all spindles
            self.display()            # Display empty puzzle
            self.setupDisks(nDisks, start=self.startMode()) # Setup disks
            self.moves = 0
            self.setMessage('You need at least {} move{}.  Good luck!'.format(
                pow(2, nDisks) - 1, '' if nDisks == 1 else 's'))
        self.stopAnimations()   # stopAnimations correctly sets button states
        self.clearArgument()    

    def clickSolve(self):
        if self.leftSpindleFull():
            self.solve(self.nDisks(), startAnimations=self.startMode())
            self.setMessage('{} total move{} made'.format(
                self.moves, '' if self.moves == 1 else 's'))
        else:
            self.setMessage("All {} disks must be on left spindle to solve"
                            .format(self.nDisks()))

def moveAboveCanvas(bbox):
    maxY = max(bbox[1], bbox[3])
    return V(bbox) - V((0, maxY, 0, maxY))

if __name__ == '__main__':
    nonneg, negative, options, otherArgs = categorizeArguments(sys.argv[1:])
    tower = TowerOfHanoi()

    for arg in nonneg:
        tower.setArgument(arg)
        tower.newButton.invoke()
        break
        
    tower.runVisualization()
