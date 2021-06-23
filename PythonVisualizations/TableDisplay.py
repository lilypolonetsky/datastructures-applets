__doc__ = """
Helper class for Python visualization applications to display an array (table)
on the canvas.  Multiple Table objects can be created to animate arrays, 
stacks, queues, etc.
"""

from tkinter import *

try:
    from Visualization import *
    from coordinates import *
except ModuleNotFoundError:
    from .Visualization import *
    from .coordinates import *

V = vector

class Table(list):     # Display a table (array/list) in a visualization app

    def __init__(  # Constructor
            self,
            visualizationApp,            # Visualization app for display
            origin,                      # Upper left corner point of cell 0
            *args,                       # Initial elements in table
            cellWidth=50, cellHeight=50, # Cell dimensions
            vertical=False,              # Orientation
            direction=1,                 # +1 means higher indices to right/down
            segmentLength=1000000,       # Max number of consecutive cells in
            segmentGap=100,              # one row/column separated by gap
            label='',                    # Label (title) of table
            labelOffset=10,              # Spacing of label from cell 0
            labelAnchor=None,            # Label anchor, S for vertical else E
            labelFont=None,              # Label font & color default to
            labelColor=None,             # to variable font & color in app
            cellBorderWidth=2,           # Thickness of cell border lines
            cellBorderColor='black',     # Cell border color
            cellBorderTags=('cell',),
            indicesFont=None,            # If provided, draw numeric cell
            indicesColor='gray60',       # indices to the left or above cells
            indicesOffset=4,             # with the given offset
            indicesTags=('cell', 'cellIndex'),
            eventHandlerPairs=(),        # (event, handler) pairs for indices
            labeledArrowFont=None,       # Labeled arrow font and color default
            labeledArrowColor=None,      # to variable font & color in app
            labeledArrowOffset=4):       # Offset of arrow tip from cell

        if not isinstance(visualizationApp, Visualization):
            raise ValueError('Table only works with Visualization objects')
        super().__init__(args)
        self.app = visualizationApp
        app = visualizationApp
        self.x0, self.y0 = origin
        self.VOrigin = V(origin)
        self.cellWidth, self.cellHeight = cellWidth, cellHeight
        self.VBox = V(cellWidth, cellHeight)
        self.vertical = vertical
        self.direction = direction
        self.segmentLength = segmentLength
        self.segmentGap = segmentGap
        self.label = label
        self.labelOffset = labelOffset
        self.labelAnchor = (((S if direction > 0 else N) if vertical else
                             (E if direction > 0 else W)) if labelAnchor is None
                            else labelAnchor)
        self.labelFont = app.VARIABLE_FONT if labelFont is None else labelFont
        self.labelColor = (
            app.VARIABLE_COLOR if labelColor is None else labelColor)
        self.cellBorderWidth = cellBorderWidth
        self.cellBorderColor = cellBorderColor
        self.cellBorderTags = cellBorderTags
        self.indicesFont = indicesFont
        self.indicesColor = indicesColor
        self.indicesOffset = indicesOffset
        self.indicesTags = indicesTags
        self.eventHandlers = eventHandlerPairs
        self.labeledArrowFont = (
            app.VARIABLE_FONT if labeledArrowFont is None else 
            labeledArrowFont)
        self.labeledArrowColor = (
            app.VARIABLE_COLOR if labeledArrowColor is None else
            labeledArrowColor)
        self.labeledArrowOffset = labeledArrowOffset
        self.cells, self.indices = [], []
        
        self.drawLabel()
        self.drawCells()

    def drawCells(self):
        while len(self.cells) > len(self):  # Remove any excess cells/indices
            self.app.canvas.delete(self.cells.pop())
            if len(self.indices) > len(self.cells):
                self.app.canvas.delete(self.indices.pop())
        self.cells = [                      # Create any needed new cells
            self.cells[j] if (
                j < len(self.cells) and
                self.app.canvas.type(self.cells[j]) == 'rectangle') else
            self.app.canvas.create_rectangle(
                *self.arrayCellCoords(j), fill='', outline=self.cellBorderColor,
                width=self.cellBorderWidth, tags=self.cellBorderTags)
            for j in range(len(self))]
        if self.indicesFont and self.indicesColor: # Create any needed indices
            self.indices = [
                self.indices[j] if (
                    j < len(self.indices) and
                    self.app.canvas.type(self.indices[j]) == 'text') else
                self.app.canvas.create_text(
                    *self.arrayCellIndexCoords(j), text=str(j),
                    anchor=E if self.vertical else S, font=self.indicesFont,
                    fill=self.indicesColor, tags=self.indicesTags)
                for j in range(len(self))]
        for textItem in self.indices:
            for event, handler in self.eventHandlers:
                if (callable(handler) and hasattr(Table, handler.__name__) and
                    callable(getattr(self, handler.__name__)())):
                    handler = getattr(self, handler.__name__)()
                self.app.canvas.tag_bind(textItem, event, handler)

    def drawLabel(self):
        self.labelItem = self.app.canvas.create_text(
            *self.labelCoords(), anchor=self.labelAnchor, text=self.label,
            fill=self.labelColor, font=self.labelFont)

    def items(self):       # Tuple of all canvas items being used
        return self.labelItem, *self.cells, *self.indices
    
    def cellCoords(self, indexOrCoords):
        if isinstance(indexOrCoords, int):
            row = (indexOrCoords // self.segmentLength) * self.direction
            col = (indexOrCoords % self.segmentLength) * self.direction
        upperLeft = (
            tuple(indexOrCoords) 
            if isinstance(indexOrCoords, (list, tuple)) else
            V(self.VOrigin + V(V((1, 0) if self.vertical else (0, 1)) * 
                               (row * self.segmentGap))) +
            V( self.VBox * V(0 if self.vertical else col,
                             col if self.vertical else 0)))
        return upperLeft + (
            V(V(upperLeft) + self.VBox) - V((self.cellBorderWidth,) * 2))

    def cellCenter(self, indexOrCoords):
        return BBoxCenter(self.cellCoords(indexOrCoords))
    
    def arrayCellCoords(self, indexOrCoords):
        half = self.cellBorderWidth // 2
        shift = (self.cellBorderWidth - half,) * 2 + (-half, ) * 2
        return V(self.cellCoords(indexOrCoords)) - V(shift)

    def arrayCellIndexCoords(self, indexOrCoords):
        cell = self.cellCoords(indexOrCoords)
        center = BBoxCenter(cell)
        gap = self.indicesOffset + self.cellBorderWidth
        return (cell[0] - self.indicesOffset, center[1]) if self.vertical else (
            center[0], cell[1] - self.indicesOffset)

    def labeledArrowCoords(self, indexOrCoords, level=1, orientation=0):
        cell = self.cellCoords(indexOrCoords)
        center = BBoxCenter(cell)
        gap = (-1 if level < 0 else 1) * (
            self.cellBorderWidth + self.labeledArrowOffset +
            (abs(self.indicesFont[1]) if self.indicesFont and level > 0 else 0))
        side = 0 if level > 0 else 2
        tip = (cell[side] - gap, center[1]) if self.vertical else (
            center[0], cell[side + 1] - gap)
        Vdelta = V(
            V(V((-1, 0) if self.vertical else (0, -1)).rotate(orientation)) *
            abs(self.labeledArrowFont[1]))
        base = V(tip) + V(Vdelta * level)
        return base + tip, base
        
    def labelCoords(self):
        cell0 = self.cellCoords(0)
        center = BBoxCenter(cell0)
        side = 0 if self.direction > 0 else 2
        gap = self.labelOffset * self.direction
        return (center[0] if self.vertical else cell0[side] - gap,
                cell0[side + 1] - gap if self.vertical else center[1])

    arrayCellCenter = cellCenter

    def updateCells(func):  # Wrapper to update cells after changes to list
        def fWrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            self.drawCells()
            return result
        return fWrapper

    pop = updateCells(list.pop)
    insert = updateCells(list.insert)
    append = updateCells(list.append)
    extend = updateCells(list.extend)
    remove = updateCells(list.remove)

    def __delitem__(self, key):
        result = super().__delitem__(key)
        while len(self.cells) > len(self):
            self.app.canvas.delete(self.cells.pop())
            if len(self.indices) > len(self.cells):
                self.app.canvas.delete(self.indices.pop())
        return result

    def createLabeledArrow(
            self, labeledArrowIndexOrCoords, label, color=None, font=None,
            width=1, anchor=None, tags=('arrow',), **kwargs):
        if color is None: color = self.labeledArrowColor
        if font is None: font = self.labeledArrowFont
        coords = (self.labeledArrowCoords(labeledArrowIndexOrCoords, **kwargs)
                  if isinstance(labeledArrowIndexOrCoords, int) else
                  labeledArrowIndexOrCoords)
        if anchor is None: 
            anchor = self.labeledArrowAnchor(coords[0])
        arrow = self.app.canvas.create_line(
            *coords[0], arrow=LAST, fill=color, width=width, tags=tags)
        text = self.app.canvas.create_text(
            *coords[1], anchor=anchor, text=label, fill=color, tags=tags)
        return arrow, text

    def labeledArrowAnchor(self, arrowCoords):
        dx, dy = V(arrowCoords[2:]) - V(arrowCoords[:2])
        return (W if dx < 0 else E) if abs(dx) > abs(dy) else (
            N if dy < 0 else S)
        
    def populateArgWithCellIndexHandler(self, argIdx=0):
        def cellIndexHandler(event):
            can = self.app.canvas
            if event.widget is can:
                for item in can.find_closest(can.canvasx(event.x),
                                             can.canvasy(event.y)):
                    if item in self.indices:
                        self.app.setArgument(
                            self.app.canvas_itemConfig(item, 'text'), argIdx)
        return cellIndexHandler
        
if __name__ == '__main__':
    from drawnValue import *
    app = Visualization(title='Table test')

    app.setArgument = lambda arg, argIndex: print(
        'Set argument', argIndex, 'to {!r}'.format(arg))

    app.startAnimations()
    table1 = Table(app, (100, 50), 'foo', 'bar', label='Foo bar',
                   vertical=True, indicesFont=('Courier', -14),
                   cellHeight=30, cellBorderWidth=4,
                   eventHandlerPairs=(('<Button-1>', 
                                       Table.populateArgWithCellIndexHandler),))
    print('table1 contains:', table1)

    table2 = Table(app, (100, 300), 'lime', 'apple', 'fig', 'pear',
                   label='Stack', vertical=True, direction=-1,
                   indicesFont=('Courier', -14), cellWidth=60, cellHeight=30,
                   eventHandlerPairs=(('<Button-1>', 
                                       Table.populateArgWithCellIndexHandler),))
    print('table2 contains:', table2)
    l1arrow = table2.createLabeledArrow(1, 'level -1', level=-1)
    l2arrow = table2.createLabeledArrow(
        table2.labeledArrowCoords(2, level=2), 'level 2')


    table3 = Table(app, (300, 50), *tuple(range(17, -1, -1)), label='Numbers+',
                   vertical=False, segmentLength=7, cellHeight=40, 
                   segmentGap=90, cellBorderWidth=1)
    print('table3 contains:', table3)
    extras = (True, False, True)
    app.wait(0.5)
    
    table3.extend(extras)
    print('After extending with', extras, 'table3 contains:', table3)

    count = 0
    for tbl in (table1, table2, table3):
        for i in range(len(tbl)):
            tbl[i] = drawnValue(
                tbl[i],
                app.canvas.create_rectangle(
                    *tbl.cellCoords(i), fill=drawnValue.palette[count],
                    outline='', width=0),
                app.canvas.create_text(*tbl.cellCenter(i), text=str(tbl[i])))
            count = (count + 1) % len(drawnValue.palette)
    print('Filled in', count, 'table cells')
    app.wait(1)

    while table3[0].val > 15:
        print('Popping first item,', table3[0].val, ', off', table3.label)
        app.moveItemsBy(table3[0].items, (-3 * len(table3), -table3.y0),
                        sleepTime=0.02)
        app.moveItemsTo(
            flat(*(dv.items for dv in table3[1:])),
            flat(*((table3.cellCoords(j), table3.cellCenter(j))
                   for j in range(len(table3) - 1))), sleepTime=0.02)
        table3.pop(0)
    
    j = 0
    movedItems = []
    jArrowConfig = {'level': 1, 'orientation': -40}
    jArrow = table3.createLabeledArrow(0, 'j', **jArrowConfig)
    
    while j < len(table3):
        if isinstance(table3[j].val, bool):
            print('Deleting cell', j, 'of table', table3.label, 'item',
                  table3[j].val)
            movedItems.extend(table3[j].items)
            app.moveItemsBy(movedItems, (table3.cellWidth, table3.cellHeight),
                            sleepTime=0.02)
            del table3[j]
        else:
            j += 1
            app.moveItemsTo(
                jArrow, table3.labeledArrowCoords(j, **jArrowConfig),
                sleepTime=0.02)

    print('Contents of table3, ', table3.label, ':')
    for j in range(len(table3)):
        print('{:3d}: {}'.format(j, table3[j]))
    for tbl in (table2, table3):
        print('The', len(tbl.items()), 
              'canvas items used to draw the cells and label of the',
              tbl.label, 'table are:', tbl.items())
        
    app.runVisualization()
