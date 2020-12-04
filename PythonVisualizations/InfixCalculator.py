from tkinter import *

try:
    from drawnValue import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawnValue import *
    from .VisualizationApp import *

class InfixCalculator(VisualizationApp):
    nextColor = 0
    MAX_ARG_WIDTH = 20
    ARRAY_SIZE = 14
    MAX_EXPRESSION_LENGTH = ARRAY_SIZE * 2
    CELL_WIDTH = 50
    CELL_HEIGHT = 18
    CELL_BORDER = 2
    CELL_BORDER_COLOR = 'black'
    INPUT_BOX_X0 = 90
    INPUT_BOX_Y0 = 10
    INPUT_BOX_WIDTH = 400
    INPUT_BOX_HEIGHT = 30
    INPUT_BOX_BG = 'powder blue'
    OUTPUT_BOX_X0 = 600
    OUTPUT_BOX_Y0 = 350
    OUTPUT_BOX_WIDTH = 180
    OUTPUT_BOX_HEIGHT = 30
    OUTPUT_BOX_BG = VisualizationApp.OPERATIONS_BG
    TR_STACK_X0 = INPUT_BOX_X0
    TR_STACK_Y0 = 380
    TR_QUEUE_X0 = 280
    TR_QUEUE_Y0 = TR_STACK_Y0
    EV_STACK_X0 = TR_QUEUE_X0 + TR_QUEUE_X0 - TR_STACK_X0
    EV_STACK_Y0 = TR_STACK_Y0
    ARRAY_X0s = [TR_STACK_X0, TR_QUEUE_X0, EV_STACK_X0]
    PRECEDENCE_X0 = 600
    PRECEDENCE_Y0 = 30
    PRECEDENCE_SPACING = 25
    operators = ["|", "&", "+-", "*/%", "^", "()"]
    allOperators = ''.join(operators)
    MAX_OPERATOR_STRING_WIDTH = max(len(s) for s in operators)

    def __init__(self, maxArgWidth=MAX_ARG_WIDTH, title="Infix Calculator", 
                 **kwargs):
        kwargs['title'] = title
        kwargs['maxArgWidth'] = maxArgWidth
        super().__init__(**kwargs)
        self.TRstack = []
        self.TRqueue = [drawnValue(None) for i in range(self.ARRAY_SIZE)]
        self.TRqueueRear = 0
        self.TRqueueFront = 1
        self.TRqueueSize = 0
        self.EVstack = []
        self.structures = [self.TRstack, self.TRqueue, self.EVstack]
        self.indices = [None] * 3
        self.buttons = self.makeButtons()
        self.display()

    def cellCoords(self, index, array=0):
        'Bounding box of a cell in one of the arrays for stacks & queue'
        return (self.ARRAY_X0s[array],
                self.TR_STACK_Y0 - self.CELL_HEIGHT * (index + 1),
                self.ARRAY_X0s[array] + self.CELL_WIDTH - self.CELL_BORDER,
                self.TR_STACK_Y0 - self.CELL_HEIGHT * index - self.CELL_BORDER)

    def cellCenter(self, index, array=0):
        box = self.cellCoords(index, array)
        return divide_vector(add_vector(box[:2], box[2:]), 2)

    # Get the coordinates of an index arrow pointing at a cell in an array
    def indexCoords(self, index, array=0, level=0):
        cell_coords = self.cellCoords(index, array)
        cell_center = self.cellCenter(index, array)
        x0 = cell_coords[0] - self.CELL_WIDTH * 3 // 5 - level * 45
        x1 = cell_coords[0] - self.CELL_WIDTH * 1 // 10
        y0 = y1 = cell_center[1]
        return x0, y0, x1, y1
    
    # Create an index arrow to point at a cell in one of the arrays
    def createIndex(
            self, index, array=0, name=None, level=0, color=None, font=None):
        if color is None:
            color = self.VARIABLE_COLOR
        if font is None:
            font = self.VARIABLE_FONT
        arrowCoords = self.indexCoords(index, array, level)
        arrow = self.canvas.create_line(*arrowCoords, arrow="last", fill=color)
        if name:
            label = self.canvas.create_text(
                *arrowCoords[:2], text=name, anchor=NE, font=font, fill=color)
            return (arrow, label)

        return (arrow,)

    def inputBoxCoords(self):
        return (self.INPUT_BOX_X0, self.INPUT_BOX_Y0,
                self.INPUT_BOX_X0 + self.INPUT_BOX_WIDTH,
                self.INPUT_BOX_Y0 + self.INPUT_BOX_HEIGHT)

    def outputBoxCoords(self):
        return (self.OUTPUT_BOX_X0, self.OUTPUT_BOX_Y0,
                self.OUTPUT_BOX_X0 + self.OUTPUT_BOX_WIDTH,
                self.OUTPUT_BOX_Y0 + self.OUTPUT_BOX_HEIGHT)
    
    def createArrayCell(self, index, array=0):
        'Create a box representing an array cell'
        cell_coords = self.cellCoords(index, array)
        half_border = self.CELL_BORDER // 2
        other_half = self.CELL_BORDER - half_border
        cell = add_vector(cell_coords,
                          (-half_border, -half_border, other_half, other_half))
        rect = self.canvas.create_rectangle(
            cell, fill=None, outline=self.CELL_BORDER_COLOR,
            width=self.CELL_BORDER)
        self.canvas.lower(rect)
        return rect

    def createCellValue(self, indexOrCoords, value, array=0, color=None):
        """Create new canvas items to represent a cell value.  A rectangle
        is created filled with a particular color with an text value centered
        inside.  The position of the cell can either be an integer index in
        one of the arrays or the bounding box coordinates of the rectangle.
        If color is not supplied, the next color in the palette among
        those not used for operator precedence is chosen.
        Returns the tuple, (square, text), of canvas items
        """
        # Determine position and color of cell
        if isinstance(indexOrCoords, int):
            rectPos = self.cellCoords(indexOrCoords, array)
            valPos = self.cellCenter(indexOrCoords, array)
        else:
            rectPos = indexOrCoords
            valPos = divide_vector(add_vector(rectPos[:2], rectPos[2:]), 2)

        if color is None:
            # Take the next color from the palette
            color = drawnValue.palette[len(self.operators) + self.nextColor]
            self.nextColor = (self.nextColor + 1) % (
                len(drawnValue.palette) - len(self.operators))
        cell_rect = self.canvas.create_rectangle(
            *rectPos, fill=color, outline='', width=0)
        cell_val = self.canvas.create_text(
            *valPos, text=value, font=self.tokenFont, fill=self.VALUE_COLOR)
        return cell_rect, cell_val

    def display(self, inputString=''):
        self.tokenFont = (self.VALUE_FONT[0], self.VALUE_FONT[1] * 2 // 3)
        self.canvas.delete("all")

        inBoxCoords = self.inputBoxCoords()
        self.inputBox = self.canvas.create_rectangle(
            *inBoxCoords, fill=self.INPUT_BOX_BG, width=1, outline='black')
        self.inputLabel = self.canvas.create_text(
            inBoxCoords[0] - 10, (inBoxCoords[1] + inBoxCoords[3]) // 2,
            text='Infix', anchor=E, font=self.VARIABLE_FONT, 
            fill=self.VARIABLE_COLOR)

        # Text input string
        self.infixInputString = self.canvas.create_text(
            inBoxCoords[0] + 10, (inBoxCoords[1] + inBoxCoords[3]) // 2,
            text=inputString, anchor=W, font=self.VALUE_FONT,
            fill=self.VALUE_COLOR)

        # Operator prececedence table
        tableTitle = "Operator Precedence"
        self.canvas.create_text(
            self.PRECEDENCE_X0, self.PRECEDENCE_Y0, text=tableTitle,
            anchor=W, font=self.VARIABLE_FONT, fill='black')
        nLevels = len(self.operators)
        pad = 5
        x0, y0 = self.PRECEDENCE_X0, self.PRECEDENCE_Y0 
        dY = self.PRECEDENCE_SPACING
        width = self.textWidth(self.VARIABLE_FONT, tableTitle)
        for j, operatorString in enumerate(self.operators):
            self.canvas.create_rectangle(
                x0 - pad,         y0 + int((nLevels - j - 0.5) * dY),
                x0 + width + pad, y0 + int((nLevels - j + 0.5) * dY),
                fill=drawnValue.palette[j], outline='', width=0)
            self.canvas.create_text(
                x0, y0 + (nLevels - j) * dY,
                text=', '.join(c for c in operatorString),
                anchor=W, font=self.VARIABLE_FONT, fill='black')
            
        outBoxCoords = self.outputBoxCoords()
        self.outputBox = self.canvas.create_rectangle(
            *outBoxCoords, fill=self.OUTPUT_BOX_BG, width=1, outline='black')
        self.outputLabel = self.canvas.create_text(
            (outBoxCoords[0] + outBoxCoords[2]) // 2, outBoxCoords[1] - 10,
            text='Output', anchor=S, font=self.VARIABLE_FONT, 
            fill=self.VARIABLE_COLOR)
        
        # No structures yet
        self.TRstackTopIndex = None
        self.TRqueueRearIndex = None
        self.TRqueueFrontIndex = None
        self.EVstackTopIndex = None
        self.postfixInputString = None

    def createTranslateStructues(self):
        colors = [[dValue and dValue.val and dValue.color(self.canvas) 
                   for dValue in struct]
                  for struct in self.structures]
            
        # Create array structured for PostfixTranslate
        for array in (0, 1):  # Draw cells for translation stack and queue
            for i in range(self.ARRAY_SIZE):
                self.createArrayCell(i, array)

            for i, value in enumerate(self.structures[array]):
                if value.val is not None:
                    value.items = self.createCellValue(
                        i, value.val, array, color=colors[array][i])

        # Create index pointers for translation stack and queue
        self.TRstackTopIndex = self.createIndex(
            len(self.TRstack), array=0, name='top')
        self.indices[0] = self.TRstackTopIndex
        self.TRqueueRearIndex = self.createIndex(
            self.TRqueueRear, array=1, name='rear')
        self.TRqueueFrontIndex = self.createIndex(
            self.TRqueueFront, array=1, name='front', level=1)
        self.indices[1] = (self.TRqueueRearIndex, self.TRqueueFrontIndex)

        inBoxCoords = self.inputBoxCoords()
        self.postfixLabel = self.canvas.create_text(
            inBoxCoords[0] - 10, inBoxCoords[3] + self.INPUT_BOX_HEIGHT,
            text='Postfix', anchor=E, font=self.VARIABLE_FONT,
            fill=self.VARIABLE_COLOR)
        self.postfixInputString = self.canvas.create_text(
            inBoxCoords[0] + 10, inBoxCoords[3] + self.INPUT_BOX_HEIGHT,
            text='', anchor=W, font=self.VALUE_FONT, fill=self.VALUE_COLOR)

    def createEvaluateStructues(self, postfix, callEnviron=None):
        colors = [[dValue.color(self.canvas) for dValue in struct]
                  for struct in self.structures]
            
        # Create array structured for Evaluate
        array = 2
        for i in range(self.ARRAY_SIZE):
            cell = self.createArrayCell(i, array)
            if callEnviron:
                callEnviron.add(cell)

        for i, value in enumerate(self.structures[array]):
            if value.val is not None:
                value.items = self.createCellValue(
                    i, value.val, array, color=colors[array][i])
                if callEnviron:
                    callEnviron |= set(value.items)

        # Create index pointers for translation stack and queue
        self.EVstackTopIndex = self.createIndex(
            len(self.EVstack), array=2, name='top')
        self.indices[2] = self.EVstackTopIndex
        if callEnviron:
            callEnviron |= set(self.EVstackTopIndex)

        self.canvas.itemconfigure(self.postfixInputString, text=postfix)
        
    def makeButtons(self):
        vcmd = (self.window.register(lambda P: self.updateInput(P)), '%P')

        evalButton = self.addOperation(
            "Evaluate", lambda: self.clickEvaluate(), numArguments=1,
            argHelpText=['infix expression'], validationCmd=vcmd,
            helpText='Evaluate infix expression')

        self.addAnimationButtons()
        return [evalButton]

    def validExpression(self, text):
        return all(c.isdigit() or c.isspace() or c in self.allOperators
                   for c in text)
    
    def updateInput(self, newText):
        valid = (self.validExpression(newText) and
                 len(newText) < self.MAX_EXPRESSION_LENGTH)
        if valid:
            if self.postfixInputString:
                self.display(newText)
            else:
                self.canvas.itemconfigure(self.infixInputString, text=newText)
        return valid

    # Button functions
    def clickEvaluate(self):
        try:
            result = self.PostfixEvaluate(self.getArgument())
            self.setMessage('Expression evaluates to {}'.format(result))
        except UserStop:
            self.setMessage('Evaluation stopped prematurely')
        except IndexError as e:
            self.setMessage('Error! {}'.format(e))
            self.setArgumentHighlight(color=self.ERROR_HIGHLIGHT)
            raise e   # For debugging only

    def PostfixEvaluate(self, infixExpression):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        postfixExpression = self.PostfixTranslate(infixExpression)

        # Restore infix expression that was parsed
        self.canvas.itemconfigure(self.infixInputString, text=infixExpression)
        
        del self.EVstack[:]
        self.createEvaluateStructues(postfixExpression, callEnviron=callEnviron)
        
        self.cleanUp(callEnviron)
        return postfixExpression

    def PostfixTranslate(self, infixExpression):
        del self.TRstack[:]
        self.TRqueue = [drawnValue(None) for i in self.TRqueue]
        self.TRqueueRear = 0
        self.TRqueueFront = 1
        self.TRqueueSize = 0
        self.display(inputString=infixExpression)
        self.createTranslateStructues()

        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        token, infixExpression = self.nextToken(self.infixInputString)
        while token:
            prec = self.precedence(token)
            delim = self.delimiter(token)
            if delim:
                if token == '(':
                    self.pushToken(
                        token, self.infixInputString, callEnviron, array=0,
                        color=drawnValue.palette[prec - 1])
                else:
                    while self.TRstack:
                        top = self.popToken(callEnviron, array=0)
                        if top.val == '(':
                            break
                        else:
                            self.insertToken(top, callEnviron)
            elif prec:                # Input token is an operator
                while self.TRstack:
                    top = self.popToken(callEnviron, array=0)
                    if top.val == '(':
                        # Just put drawnValue back in place
                        self.TRstack.append(top)
                        self.moveItemsBy(
                            self.TRstackTopIndex, (0, - self.CELL_HEIGHT),
                            sleepTime=0.001)
                        break
                    else:
                        if self.precedence(top.val) >= prec:
                            self.insertToken(top, callEnviron)
                        else:
                            self.TRstack.append(top)
                            self.moveItemsBy(
                                self.TRstackTopIndex, (0, - self.CELL_HEIGHT),
                                sleepTime=0.001)
                            break
                self.pushToken(token, self.infixInputString, callEnviron,
                               array=0, color=drawnValue.palette[prec - 1])
            else:                     # Input token is an operand
                self.insertToken(token, callEnviron, self.infixInputString)

            token, infixExpression = self.nextToken(self.infixInputString)

        while self.TRstack:
            self.insertToken(self.popToken(callEnviron, array=0), callEnviron)

        ans = ""
        while self.TRqueueSize > 0:
            if len(ans) > 0:
                ans += " "
            ans += self.removeToken(callEnviron, self.postfixInputString)
                
        self.cleanUp(callEnviron)
        return ans
    
    def nextToken(self, displayString):
        text = self.canvas.itemconfigure(displayString, 'text')[-1]
        token = ''
        stripped = text.strip()
        if stripped != text:
            self.canvas.itemconfigure(displayString, text=stripped)
            text = stripped
            self.wait(0.5)
        if len(text) > 0:
            if self.precedence(text[0]):
                token = text[0]
                text = text[1:]
                self.canvas.itemconfigure(displayString, text=text)
            else:
                while len(text) > 0 and not (   # to next operator or space
                        self.precedence(text[0]) or text[0].isspace()):
                    token += text[0]
                    text = text[1:]
                    self.canvas.itemconfigure(displayString, text=text)
        return token, text  # Return the token, and remaining input string

    def pushToken(self, token, displayString, callEnviron, array=0, color=None):
        index = len(self.structures[array])
        if index >= self.ARRAY_SIZE:
            raise IndexError('Stack overflow')
        coords = self.canvas.coords(displayString)
        tokenItem = self.canvas.create_text(
            *coords, text=token, font=self.VALUE_FONT, fill=self.VALUE_COLOR,
            anchor=W)
        callEnviron.add(tokenItem)
        toCoords = subtract_vector(
            self.cellCenter(index, array), 
            (self.textWidth(self.VALUE_FONT, token) / 2, 0))
        self.moveItemsTo(tokenItem, toCoords, sleepTime=0.01)
        self.structures[array].append(drawnValue(
            token, *self.createCellValue(index, token, array, color=color)))
        self.canvas.delete(tokenItem)
        callEnviron.discard(tokenItem)
        self.moveItemsBy(
            self.indices[array], (0, - self.CELL_HEIGHT), sleepTime=0.01)

    def popToken(self, callEnviron, array=0, displayString=0):
        index = len(self.structures[array]) - 1
        if index < 0:
            raise IndexError('Stack underflow')
        top = self.structures[array].pop()
        if displayString:
            text = self.canvas.itemconfigure(displayString, 'text')[-1]
            if len(text) > 0 and not text.endswith(' '):
                text += ' '
            copyItem = self.copyCanvasItem(top.items[1])
            callEnviron.add(copyItem)
            self.canvas.itemconfigure(copyItem, anchor=W)
            toCoords = add_vector(
                self.canvas.coords(displayString),
                (self.textWidth(self.VALUE_FONT, text), 0))
            self.moveItemsTo(copyItem, toCoords, sleepTime=0.01)
            self.canvas.itemconfigure(displayString, text=text + top.val)
            self.canvas.delete(copyItem)
        self.moveItemsBy(
            self.indices[array], (0, self.CELL_HEIGHT), sleepTime=0.01)
        return top
    
    def insertToken(self, token, callEnviron, displayString=None, color=None):
        if self.TRqueueSize >= self.ARRAY_SIZE:
            raise IndexError('Queue overflow')
        index = (self.TRqueueRear + 1) % len(self.TRqueue)
        indexCoords = self.indexCoords(index, array=1, level=0)
        self.moveItemsTo(self.TRqueueRearIndex, (indexCoords, indexCoords[:2]),
                         sleepTime=0.01)
        toCoords = self.cellCoords(index, array=1)
        toCenter = self.cellCenter(index, array=1)
        if isinstance(token, str) and displayString:
            coords = self.canvas.coords(displayString)
            tokenItem = self.canvas.create_text(
                *coords, text=token, font=self.VALUE_FONT,
                fill=self.VALUE_COLOR)
            callEnviron.add(tokenItem)
            items = (tokenItem,)
            dValue = None
        elif isinstance(token, drawnValue) and displayString is None:
            items = token.items
            dValue = token
        self.moveItemsTo(
            items, (toCoords, toCenter) if len(items) == 2 else (toCenter),
            sleepTime=0.01)
        if dValue is None:
            dValue = drawnValue(
                token, 
                *self.createCellValue(index, token, array=1, color=color))
            for item in items:
                self.canvas.delete(item)
                callEnviron.discard(item)
        self.TRqueue[index] = dValue
        self.TRqueueRear = index
        self.TRqueueSize += 1

    def removeToken(self, callEnviron, displayString=None):
        if self.TRqueueSize <= 0:
            raise IndexError('Queue underflow')
        dValue = self.TRqueue[self.TRqueueFront]
        removed = dValue.val
        index = (self.TRqueueFront + 1) % len(self.TRqueue)
        if displayString:
            text = self.canvas.itemconfigure(displayString, 'text')[-1]
            if len(text) > 0 and not text.endswith(' '):
                text += ' '
            copyItem = self.copyCanvasItem(dValue.items[1])
            callEnviron.add(copyItem)
            self.canvas.itemconfigure(copyItem, anchor=W)
            toCoords = add_vector(
                self.canvas.coords(displayString),
                (self.textWidth(self.VALUE_FONT, text), 0))
            self.moveItemsTo(copyItem, toCoords, sleepTime=0.01)
            self.canvas.itemconfigure(displayString, text=text + removed)
            self.canvas.delete(copyItem)
        self.TRqueueFront = index
        self.TRqueueSize -= 1
        indexCoords = self.indexCoords(self.TRqueueFront, array=1, level=1)
        self.moveItemsTo(self.TRqueueFrontIndex, (indexCoords, indexCoords[:2]),
                         sleepTime=0.01)
        for item in dValue.items:
            self.canvas.delete(item)
        dValue.val, dValue.items = None, ()
        
        return removed
    
    def precedence(self, operator):    # Get the precedence of an operator
        for p, ops in enumerate(self.operators):  # Loop through operators
            if operator in ops:              # If found,
                return p + 1                 # return precedence (low = 1)
        # else not an operator, return None
        
    def delimiter(self, character):  # Determine if character is delimiter
        return self.precedence(character) == len(self.operators)

if __name__ == '__main__':
    # random.seed(3.14159)    # Use fixed seed for testing consistency
    app = InfixCalculator()
    app.runVisualization()

