__doc__ = """
Helper class for Python visualization applications to display an
output box on the canvas where text items can be output like a printer
"""

from tkinter import *
import re

try:
    from tkUtilities import *
    from Visualization import *
    from coordinates import *
except ModuleNotFoundError:
    from .tkUtilities import *
    from .Visualization import *
    from .coordinates import *

V = vector

class OutputBox(object):
    '''Display an output box showing text across multiple lines in a
    Visualization app's canvas.  Position defaults to being centered at the
    bottom of the canvas.
    '''
    TEXT_ANCHOR = NW
    
    def __init__(  # Constructor
            self,
            visualizationApp,            # Visualization app for display
            bbox=None,                   # Bounding box of output box
            nCharacters=5,               # Characters per line to determine bbox
            nLines=1,                    # Number of lines to determine bbox
            separators=r'[\s,.:;-]+',    # Separator regex where text can break
            lineHeight=None,             # Separation between lines
            label='',                    # Label (title) of output box
            labelPosition=N,             # Label position rel to bbox or coords
            labelAnchor=S,               # Label text anchor to relative pos
            labelOffset=10,              # Spacing of label from bounding box
            labelFont=None,              # Label font & color default to
            labelColor=None,             # to variable font & color in app
            background='beige',          # Output box background color
            borderWidth=1,               # Thickness of border lines
            borderColor='black',         # Border color
            tags=('outputBox',),         # Tags applied to items
            outputFont=None,             # Font and color of output text
            outputColor=None,            # default to the app VALUE font * color
            outputOffset=(5, 5),         # Offset of top left corner of top line
            eventHandlerPairs=(),        # (event, handler) pairs for items
            see=()):                     # Scroll to see box plus items to see

        if not isinstance(visualizationApp, Visualization):
            raise ValueError('OutputBox only works with Visualization objects')
        self.app = visualizationApp
        app = visualizationApp
        if outputFont is None: outputFont = app.VALUE_FONT
        if outputColor is None: outputColor = app.VALUE_COLOR
        self.outputFont, self.outputColor = outputFont, outputColor
        if lineHeight is None: lineHeight = textHeight(outputFont, ' ')
        self.lineHeight = lineHeight
        if bbox is None:
            canvasBBox = app.visibleCanvas()
            width = (nCharacters * textWidth(outputFont, 'W') +
                         outputOffset[0] * 2)
            height = self.lineHeight * nLines + outputOffset[1] * 2
            bbox = (max(borderWidth,
                        canvasBBox[0] + canvasBBox[2] - width) // 2,
                    canvasBBox[3] - height - outputOffset[1],
                    max(borderWidth,
                        canvasBBox[0] + canvasBBox[2] - width) // 2 + width,
                    canvasBBox[3] - outputOffset[1])
        self.bbox = bbox
        self.separators = re.compile(separators)
        self.label = label
        self.labelPosition = labelPosition
        self.labelOffset = labelOffset
        self.labelAnchor = labelAnchor
        self.labelFont = app.VARIABLE_FONT if labelFont is None else labelFont
        self.labelColor = (
            app.VARIABLE_COLOR if labelColor is None else labelColor)
        self.background = background
        self.borderWidth = borderWidth
        self.borderColor = borderColor
        self.tags = tags
        self.outputFont = outputFont
        self.outputColor = outputColor
        self.outputOffset = outputOffset
        self.eventHandlers = eventHandlerPairs

        self.drawOutputBoxAndText(see=see)
        self.drawLabel(see=see)

    def drawOutputBoxAndText(self, see=()):
        self.outputBox = self.app.canvas.create_rectangle(
            *self.bbox, fill=self.background, width=self.borderWidth,
            outline=self.borderColor, tags=self.tags)
        self.outputText = self.app.canvas.create_text(
            *(V(self.bbox[:2]) + V(self.outputOffset)), anchor=self.TEXT_ANCHOR,
            text='', fill=self.outputColor, font=self.outputFont,
            tags=self.tags)
        for event, handler in self.eventHandlers:
            if (callable(handler) and hasattr(OutputBox, handler.__name__)
                and callable(getattr(self, handler.__name__)())):
                handler = getattr(self, handler.__name__)()
            for item in (self.outputBox, self.outputText):
                self.app.canvas.tag_bind(item, event, handler)
        if see:
            self.app.scrollToSee(
                (self.outputBox, self.outputText) +
                (tuple(see) if isinstance(see, (tuple, list, set)) else ()))
        return self.outputBox, self.outputText

    def drawLabel(self, see=()):
        self.labelItem = self.app.canvas.create_text(
            *self.labelCoords(), anchor=self.labelAnchor, text=self.label,
            fill=self.labelColor, font=self.labelFont)
        if see:
            self.app.scrollToSee(
                (self.labelItem,) +
                (tuple(see) if isinstance(see, (tuple, list, set)) else ()))
        return self.labelItem
        
    def items(self):       # Tuple of all canvas items being used
        return self.labelItem, self.outputBox, self.outputText

    def text(self, newValue=None):
        'Get or set text of the output box.  Newlines separate lines.'
        if newValue is None:
            return self.app.canvas_itemConfig(self.outputText, 'text')
        return self.app.canvas_itemConfig(self.outputText, text=newValue)

    def __str__(self):
        return '<{}: {!r}>'.format(type(self).__name__, self.text())
        
    def labelCoords(self):
        center = self.center()
        x = (self.bbox[0] - self.labelOffset if W in self.labelPosition else
             self.bbox[2] + self.labelOffset if E in self.labelPosition else
             center[0])
        y = (self.bbox[1] - self.labelOffset if N in self.labelPosition else
             self.bbox[3] + self.labelOffset if S in self.labelPosition else
             center[1])
        return x, y
    
    def endCoords(self, spacer=''):
        '''Get coordinates where current output text ends for next append.
        Add the spacer string if the last line has some characters but doesn't
        already end with it.
        '''
        lines = self.text().split('\n')
        upperLeft = self.app.canvas_coords(self.outputText)
        return V(upperLeft) + V(
            textWidth(
                self.outputFont,
                lines[-1] +
                (spacer if lines[-1] and not lines[-1].endswith(spacer) else '')
            ) if lines else 0,
            (len(lines) - 1) * self.lineHeight)

    def appendText(
            self,
            textOrItems: 'text string or canvas text item or item list',
            separator: 'separator text' =' ',
            sleepTime: 'animation delay' =0,
            deleteItem: 'delete animated text items if true' =True,
            see: 'additional items to keep visible for scroll' =(),
            expand: 'expand scrolling region as needed if true' =True):
        '''Append new text to output text.  Can provide text string, numeric
        ID of canvas text item, or tuple/list of items to animate
        moving to output position followed by optional deletion.  If
        multiple text items are provided, they should all have the same
        text and font.  If there is already some current text, the
        separator string is appended to it before adding the new text.
        If appending the new text would make the last line go past the
        right side of the box, the line is split at separators until
        it fits.
        '''
        if isinstance(textOrItems, int): # Force single canvas text item
            textOrItems = [textOrItems] # to be a list of one item
        text = (textOrItems if isinstance(textOrItems, str) else
                self.app.canvas_itemConfig(textOrItems[0], 'text'))
        current = self.text()
        newText = current + (separator if current else '') + text
        lines = newText.split('\n')
        maxWidth = (self.bbox[2] - self.bbox[0] - self.outputOffset[0] * 2)
        while lines and textWidth(self.outputFont, lines[-1]) > maxWidth:
            separators = [(mg.group(0), mg.start(), mg.end()) 
                          for mg in self.separators.finditer(lines[-1])]
            if len(separators) == 0: separators = [('', 0, len(lines[-1]) // 2)]
            j = len(separators) - 1
            while j > 0 and textWidth(
                    self.outputFont,
                    lines[-1][:separators[j][1]] + separators[j][0]) > maxWidth:
                j -= 1
            lines[-1:] = [lines[-1][:separators[j][1]] + separators[j][0],
                          lines[-1][separators[j][2]:]]
        animate = isinstance(textOrItems, (list, tuple)) and sleepTime
        if animate:
            for item in textOrItems:
                self.app.canvas.tag_raise(item, self.outputBox)
                self.app.canvas.changeAnchor(self.TEXT_ANCHOR, item)
            coords = [self.endCoords(separator)] * len(textOrItems)
            self.app.moveItemsTo(
                textOrItems, coords, sleepTime=sleepTime, 
                startFont=self.app.canvas.getItemFont(textOrItems[0]),
                endFont=self.outputFont, see=see, expand=expand)
        self.app.canvas_itemConfig(self.outputText, text='\n'.join(lines))
        if animate and deleteItem:
            for item in textOrItems:
                self.app.canvas.delete(item)

    def setToText(
            self, items, coords=None, sleepTime=0, deleteItems=True,
            color=None, see=(), expand=True):
        '''Move a tuple of items to the output box (animating if sleepTime is
        non-zero), then set the output box text to the text in the
        first text item.  Optionally set the background color of the
        output box to the specified color (string) or to the fill color
        of the first non-text item among the items if color is True.
        If coords are provided, there should be coordinates for each
        of the items that place them within the output box.
        Otherwise, coords are calculated to move the first text item
        to the center of output box.  The outputText will be changed
        to have a center anchor, making use of this method incompatible
        with appendText().
        '''
        text1, nontext1, j = None, None, 0
        while j < len(items) and (text1 is None or nontext1 is None):
            if self.app.canvas.type(items[j]) == 'text':
                if text1 is None:
                    text1 = items[j]
            else:
                if nontext1 is None:
                    nontext1 = items[j]
            j += 1
        if text1 is None:
            ValueError('No text items provided in {}'.format(items))
        for item in items:
            if item is text1:
                self.app.canvas.tag_raise(item, self.outputBox)
            else:
                self.app.canvas.tag_lower(item, self.outputBox)
        center = self.center()
        self.app.canvas_itemConfig(self.outputText, anchor=CENTER, text='')
        self.app.canvas.coords(self.outputText, *center)
        if coords is None:
            self.app.canvas.changeAnchor(CENTER, text1)
            delta = V(center) - V(self.app.canvas_coords(text1))
            if sleepTime:
                self.app.moveItemsBy(
                    items, delta, sleepTime=sleepTime, endFont=self.outputFont,
                    startFont=self.app.canvas.getItemFont(text1),
                    see=see, expand=expand)
            else:
                for item in items:
                    self.app.canvas.move(item, *delta)
                if see:
                    self.app.scrollToSee(
                        items +
                        (tuple(see) if isinstance(see, (tuple, list, set))
                         else ()), sleepTime=sleepTime, expand=expand)

        else:
            if sleepTime:
                self.app.canvas.changeAnchor(CENTER, text1)
                self.app.moveItemsLinearly(
                    items, coords, sleepTime=sleepTime, endFont=self.outputFont,
                    startFont=self.app.canvas.getItemFont(text1),
                    see=see, expand=expand)
            else:
                for item, coord in zip(items, coords):
                    self.app.canvas.coords(item, coord)
                if see:
                    self.app.scrollToSee(
                        items +
                        (tuple(see) if isinstance(see, (tuple, list, set))
                         else ()), sleepTime=sleepTime, expand=expand)
                    
        self.app.canvas.copyItemAttributes(text1, self.outputText, 'text')
        if color:
            self.background = (
                color if isinstance(color, str) else
                self.app.canvas_itemConfig(nontext1, 'fill') if nontext1 else
                self.background)
            self.app.canvas_itemConfig(self.outputBox, fill=self.background)
        if deleteItems:
            for item in items:
                self.app.canvas.delete(item)
                    
    def center(self):
        return BBoxCenter(self.bbox)
        
if __name__ == '__main__':
    from drawnValue import *
    import random, sys, argparse
    
    parser = argparse.ArgumentParser(
        description='Test ' + __file__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        'label', nargs='*', help='Label(s) to draw.')
    parser.add_argument(
        '-d', '--duplicate', nargs='*',
        help='Duplicate label(s) to draw and simultaneously animate.')
    parser.add_argument(
        '-s', '--sleep-time', default=0.01, type=float,
        help='Sleep time for animation.')
    args = parser.parse_args()

    app = Visualization(title='OutputBox test', canvasBounds=(0, 0, 800, 400))

    app.startAnimations()
    width, height = 140, 25
    outbox1 = OutputBox(app, (400 - width // 2 - 5, 190,
                              400 + width // 2 + 5, 190 + height),
                        label='Output Item')
    print('Output box 1: {}', outbox1)
    app.wait(1)
    toAdd = 'Item'
    print('Append {!r} to output box 1'.format(toAdd))
    outbox1.appendText(toAdd)
    app.wait(1)

    dataItems = []
    dy = height // 4
    y0 = 40
    gap = 15
    for j in range(2, 6):
        x = j * (width + gap) - 240
        shape = (app.canvas.create_rectangle if j % 2 == 0 else
                 app.canvas.create_oval)(
                     x, y0 + dy * j, x + width, y0 + dy * j + height,
                     fill=drawnValue.palette[j], outline='', width=0)
        text = app.canvas.create_text(
            x + width // 2, y0 + dy * j + height // 2, 
            text=drawnValue.palette[j], font=app.VALUE_FONT)
        if j % 3 == 0:
            app.canvas.changeAnchor(SW, text)
        dataItems.append((shape, text))

    app.wait(0.5)
    st = 0.02
    for dataItem in dataItems:
        print('Setting output item to', 
              app.canvas_itemConfig(dataItem[1], 'text'), 'with anchor',
              app.canvas_itemConfig(dataItem[1], 'anchor'), 'and sleepTime',
              st)
        outbox1.setToText(dataItem, sleepTime=st, color=True)
        st -= 0.007
        if st < 0.001: st = 0
        app.wait(0.1)
        
    region = (50, 50, 750, 300)
    anchors = (NW, N, NE, E, SE, S, SW, W, CENTER)
    items = [app.canvas.create_text(
        random.randrange(region[0], region[2]),
        random.randrange(region[1], region[3]), text=txt, fill='blue',
        anchor=anchors[i % len(anchors)], font=('Helvetica', -12))
             for i, txt in enumerate(
                     args.label +
                     (OutputBox.__doc__ + ' ' + OutputBox.appendText.__doc__)
                     .split())]
    print('Created {} word items'.format(len(items)))

    duplicate_items = [
        (app.canvas.create_text(
            random.randrange(region[0], region[2]),
            random.randrange(region[1], region[3]), text=txt, fill='orange',
            font=('Helvetica', -14)),
         app.canvas.create_text(
            random.randrange(region[0], region[2]),
            random.randrange(region[1], region[3]), text=txt, fill='orange',
            font=('Helvetica', -14)))
        for i, txt in enumerate(args.duplicate)
    ] if args.duplicate else []
    print('Created {} pairs of duplicate word items'.format(
        len(duplicate_items)))

    outbox2 = OutputBox(
        app, background='bisque', label='Multi', labelPosition=W, labelAnchor=E,
        nCharacters=35, nLines=7, see=True)
    print('Appending word items to output box 2')
    for item in items:
        outbox2.appendText(item, sleepTime=args.sleep_time, see=outbox2.items(),
                           expand=True)
        app.wait(0.01)

    if duplicate_items:
        print('Appending duplicate word items in pairs to output box 2')
    for pair in duplicate_items:
        outbox2.appendText(pair, sleepTime=args.sleep_time, see=outbox2.items(),
                           expand=True)

    print('output box 2 contains:', outbox2)
        
    app.runVisualization()
