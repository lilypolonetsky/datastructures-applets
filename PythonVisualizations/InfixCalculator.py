from tkinter import *

try:
    from coordinates import *
    from tkUtilities import *
    from drawnValue import *
    from VisualizationApp import *
    from OutputBox import *
except ModuleNotFoundError:
    from .coordinates import *
    from .tkUtilities import *
    from .drawnValue import *
    from .VisualizationApp import *
    from .OutputBox import *

V = vector

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
    OUTPUT_BOX_X0 = 570
    OUTPUT_BOX_Y0 = 350
    OUTPUT_BOX_WIDTH = 210
    OUTPUT_BOX_HEIGHT = 30
    TR_STACK_X0 = INPUT_BOX_X0
    TR_STACK_Y0 = 380
    TR_QUEUE_X0 = 280
    TR_QUEUE_Y0 = TR_STACK_Y0
    EV_STACK_X0 = TR_QUEUE_X0 + TR_QUEUE_X0 - TR_STACK_X0
    EV_STACK_Y0 = TR_STACK_Y0
    ARRAY_X0s = [TR_STACK_X0, TR_QUEUE_X0, EV_STACK_X0]
    PRECEDENCE_X0 = OUTPUT_BOX_X0 + 10
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
        self.TRstackID = 0
        self.TRqueueID = 1
        self.EVstackID = 2
        self.indices = [None] * 3
        self.buttons = self.makeButtons()
        self.display()

    def cellCoords(self, index, arrayID=0):
        'Bounding box of a cell in one of the arrays for stacks & queue'
        return (self.ARRAY_X0s[arrayID],
                self.TR_STACK_Y0 - self.CELL_HEIGHT * (index + 1),
                self.ARRAY_X0s[arrayID] + self.CELL_WIDTH - self.CELL_BORDER,
                self.TR_STACK_Y0 - self.CELL_HEIGHT * index - self.CELL_BORDER)

    def cellCenter(self, index, arrayID=0):
        box = self.cellCoords(index, arrayID)
        return BBoxCenter(box)

    # Get the coordinates of an index arrow pointing at a cell in an array
    def indexCoords(self, index, arrayID=0, level=0):
        cell_coords = self.cellCoords(index, arrayID)
        cell_center = self.cellCenter(index, arrayID)
        x0 = cell_coords[0] - self.CELL_WIDTH * 3 // 5 - level * 45
        x1 = cell_coords[0] - self.CELL_WIDTH * 1 // 10
        y0 = y1 = cell_center[1]
        return x0, y0, x1, y1
    
    # Create an index arrow to point at a cell in one of the arrays
    def createIndex(
            self, index, arrayID=0, name=None, level=0, color=None, font=None, 
            tags=()):
        if color is None:
            color = self.VARIABLE_COLOR
        if font is None:
            font = self.VARIABLE_FONT
        arrowCoords = self.indexCoords(index, arrayID, level)
        arrow = self.canvas.create_line(
            *arrowCoords, arrow="last", fill=color, tags=tags)
        if name:
            label = self.canvas.create_text(
                *arrowCoords[:2], text=name, anchor=NE, font=font, fill=color, 
                tags=tags)
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

    def operandAndOperatorCoords(self):
        oBox = self.outputBoxCoords()
        y0 = oBox[1] - 3 * (oBox[3] - oBox[1])
        return (((oBox[0] * 4 + oBox[2]) // 5, y0),
                ((oBox[0] + oBox[2]) // 2, y0 + oBox[1] - oBox[3]),
                ((oBox[0] + oBox[2] * 4) // 5, y0))
    
    def createArrayCell(self, index, arrayID=0, tags=()):
        'Create a box representing an array cell'
        cell_coords = self.cellCoords(index, arrayID)
        half_border = self.CELL_BORDER // 2
        other_half = self.CELL_BORDER - half_border
        cell = V(cell_coords) + V(-half_border, -half_border,
                                  other_half, other_half)
        rect = self.canvas.create_rectangle(
            cell, fill=None, outline=self.CELL_BORDER_COLOR,
            width=self.CELL_BORDER, tags=tags)
        self.canvas.lower(rect)
        return rect

    def createCellValue(self, indexOrCoords, value, arrayID=0, color=None):
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
            rectPos = self.cellCoords(indexOrCoords, arrayID)
            valPos = self.cellCenter(indexOrCoords, arrayID)
        else:
            rectPos = indexOrCoords
            valPos = BBoxCenter(rectPos)

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
            text='  Infix\nformula', anchor=E, font=self.VARIABLE_FONT, 
            fill=self.VARIABLE_COLOR)

        # Text input string
        self.infixInputString = self.canvas.create_text(
            inBoxCoords[0] + 10, (inBoxCoords[1] + inBoxCoords[3]) // 2,
            text=inputString, anchor=W, font=self.VALUE_FONT,
            fill=self.VALUE_COLOR)

        self.createOperatorPrecedenceTable(
            self.PRECEDENCE_X0, self.PRECEDENCE_Y0, self.PRECEDENCE_SPACING)
            
        outBoxCoords = self.outputBoxCoords()
        self.outputBox = OutputBox(self, outBoxCoords, label='Output')
        
        # No structures yet
        self.TRstackTopIndex = None
        self.TRqueueRearIndex = None
        self.TRqueueFrontIndex = None
        self.EVstackTopIndex = None
        self.postfixLabel = None
        self.postfixInputString = None

    def createOperatorPrecedenceTable(
            self, x0=PRECEDENCE_X0, y0=PRECEDENCE_Y0, dY=PRECEDENCE_SPACING,
            title="Operator Precedence", font=None, operatorColor='black',
            precedenceColor='gray20', titleColor='black'):
        if font is None: font = self.VARIABLE_FONT
        self.canvas.create_text(
            x0, y0, text=title, anchor=W, font=font, fill=titleColor)
        nLevels = len(self.operators)
        width = textWidth(font, title)
        for j, operatorString in enumerate(self.operators):
            self.canvas.create_rectangle(
                x0,         y0 + int((nLevels - j - 0.5) * dY),
                x0 + width, y0 + int((nLevels - j + 0.5) * dY),
                fill=drawnValue.palette[j], outline='', width=0)
            self.canvas.create_text(
                x0 + width // 2, y0 + (nLevels - j) * dY,
                text='  '.join(c for c in operatorString),
                font=font, fill=operatorColor)
            self.canvas.create_text(
                x0 + abs(font[1]) // 3, y0 + (nLevels - j) * dY,
                text=str(self.precedence(operatorString[0])), anchor=W,
                font=font, fill=precedenceColor)
        
    def createTranslateStructues(self, callEnviron):
        colors = [[dValue and dValue.val and dValue.color(self.canvas) 
                   for dValue in struct]
                  for struct in self.structures]
            
        # Create array structures for PostfixTranslate
        for arrayID in (self.TRstackID, self.TRqueueID):
            aboveArray = self.indexCoords(self.ARRAY_SIZE, arrayID, level=1)[:2]
            tag = 'array-{}'.format(arrayID)
            for i in range(self.ARRAY_SIZE):
                cell = self.createArrayCell(i, arrayID, tags=tag)
                callEnviron.add(cell)
                cellCoords = self.canvas.coords(cell)

            for i, value in enumerate(self.structures[arrayID]):
                if value.val is not None:
                    value.items = self.createCellValue(
                        i, value.val, arrayID, color=colors[arrayID][i])
                    callEnviron |= set(value.items)
            tag = 'index-{}'.format(arrayID)
            callEnviron.add(self.canvas.create_text(
                *(V(aboveArray) + V(0, -abs(self.VARIABLE_FONT[1]))),
                text='Translate stack' if arrayID == self.TRstackID
                else 'Translate queue', anchor=SW,
                font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR, tags=tag))
            callEnviron.add(self.canvas.create_text(
                (cellCoords[0] + cellCoords[2]) // 2,  aboveArray[1],
                text='s' if arrayID == self.TRstackID else 'postfix', anchor=S,
                font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR, tags=tag))

        # Create index pointers for translation stack and queue
        self.TRstackTopIndex = self.createIndex(
            len(self.TRstack), arrayID=self.TRstackID, name='top', 
            tags='index-{}'.format(self.TRstackID))
        self.indices[self.TRstackID] = self.TRstackTopIndex
        self.TRqueueRearIndex = self.createIndex(
            self.TRqueueRear, arrayID=self.TRqueueID, name='rear',
            tags='index-{}'.format(self.TRqueueID))
        self.TRqueueFrontIndex = self.createIndex(
            self.TRqueueFront, arrayID=self.TRqueueID, name='front', level=1, 
            tags='index-{}'.format(self.TRqueueID))
        self.indices[self.TRqueueID] = (
            self.TRqueueRearIndex, self.TRqueueFrontIndex)
        callEnviron |= set(self.TRstackTopIndex + self.TRqueueRearIndex +
                           self.TRqueueFrontIndex)

        inBoxCoords = self.inputBoxCoords()
        self.postfixLabel = self.canvas.create_text(
            inBoxCoords[0] - 10, inBoxCoords[3] + self.INPUT_BOX_HEIGHT,
            text='token', anchor=E, font=self.VARIABLE_FONT,
            fill=self.VARIABLE_COLOR)
        self.postfixInputString = self.canvas.create_text(
            inBoxCoords[0] + 10, inBoxCoords[3] + self.INPUT_BOX_HEIGHT,
            text='', anchor=W, font=self.VALUE_FONT, fill=self.VALUE_COLOR)

    def createEvaluateStructues(self, postfix, callEnviron=None):
        colors = [[dValue.color(self.canvas) for dValue in struct]
                  for struct in self.structures]
            
        # Create array structured for Evaluate
        arrayID = self.EVstackID
        aboveArray = self.indexCoords(self.ARRAY_SIZE, arrayID, level=1)[:2]
        tag = 'array-{}'.format(self.EVstackID)
        for i in range(self.ARRAY_SIZE):
            cell = self.createArrayCell(i, arrayID, tags=tag)
            cellCoords = self.canvas.coords(cell)
            if callEnviron:
                callEnviron.add(cell)
        tag = 'index-{}'.format(self.EVstackID)
        EVstackLabel = (
            self.canvas.create_text(
                *(V(aboveArray) + V(0, -abs(self.VARIABLE_FONT[1]))),
                text='Evaluate stack', anchor=SW,
                font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR, tags=tag),
            self.canvas.create_text(
                (cellCoords[0] + cellCoords[2]) // 2,  aboveArray[1],
                text='s', anchor=S,
                font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR, tags=tag))
        if callEnviron:
            callEnviron |= set(EVstackLabel)

        for i, value in enumerate(self.structures[arrayID]):
            if value.val is not None:
                value.items = self.createCellValue(
                    i, value.val, arrayID, color=colors[arrayID][i])
                if callEnviron:
                    callEnviron |= set(value.items)

        # Create index pointers for translation stack and queue
        self.EVstackTopIndex = self.createIndex(
            len(self.EVstack), arrayID=self.EVstackID, name='top', tags=tag)
        self.indices[self.EVstackID] = self.EVstackTopIndex
        if callEnviron:
            callEnviron |= set(self.EVstackTopIndex)

        self.canvas.itemConfig(self.postfixInputString, text=postfix)
        
    def makeButtons(self):
        vcmd = (self.window.register(lambda P: self.updateInput(P)), '%P')

        self.evaluateButton = self.addOperation(
            "Evaluate", lambda: self.clickEvaluate(), numArguments=1,
            argHelpText=['infix expression'], validationCmd=vcmd,
            helpText='Evaluate infix expression')

        self.addAnimationButtons()
        return [self.evaluateButton]

    def validExpression(self, text):
        return all(c.isdigit() or c.isspace() or c in self.allOperators
                   for c in text)
    
    def updateInput(self, newText):
        valid = (self.validExpression(newText) and
                 len(newText) < self.MAX_EXPRESSION_LENGTH)
        if self.animationsStopped() and valid:
            if self.postfixInputString:
                self.display(newText)
            else:
                self.canvas.itemConfig(self.infixInputString, text=newText)
        return valid

    # Button functions
    def clickEvaluate(self):
        try:
            result = self.PostfixEvaluate(
                self.getArgument(), start=self.startMode())
            self.setMessage('Expression evaluates to {}'.format(result))
        except UserStop:
            self.setMessage('Evaluation stopped prematurely')
            self.cleanUp(self.callStack[0] if self.callStack else None)
        except IndexError as e:
            self.setMessage('Error! {}'.format(e))
            self.setArgumentHighlight(color=self.ERROR_HIGHLIGHT)
            raise e   # For debugging only
        
    postfixEvaluateCode = '''
def PostfixEvaluate(formula={infixExpression!r}):
   postfix = PostfixTranslate(formula)
   s = Stack({ARRAY_SIZE})
   
   token, postfix = nextToken(postfix)
   while token:
      prec = precedence(token)

      if prec:
         right = s.pop()
         left = s.pop()
         if token == '|':
            s.push(left | right)
         elif token == '&':
            s.push(left & right)
         elif token == '+':
            s.push(left + right)
         elif token == '-':
            s.push(left - right)
         elif token == '*':
            s.push(left * right)
         elif token == '/':
            s.push(left / right)
         elif token == '%':
            s.push(left % right)
         elif token == '^':
            s.push(left ^ right)
             
      else:
         s.push(int(token))

      token, postfix = nextToken(postfix)

   return s.pop()
'''
    
    def PostfixEvaluate(
            self, infixExpression, code=postfixEvaluateCode, start=True):
        env = locals()
        env['ARRAY_SIZE'] = self.ARRAY_SIZE
        callEnviron = self.createCallEnvironment(
            code=code.format(**env), startAnimations=start)
        wait = 0.1
        errorValue = 'Error!'
        hlColor = self.CODE_HIGHLIGHT
        self.canvas.itemConfig(self.infixInputString, text=infixExpression)
        for item in (self.postfixLabel, self.postfixInputString):
            if item:
                self.canvas.itemConfig(item, text='')
        del self.EVstack[:]
        
        self.highlightCode('postfix = PostfixTranslate(formula)', callEnviron,
                           color=hlColor)
        postfixExpression = self.PostfixTranslate(infixExpression)

        # Restore infix expression that was parsed
        self.canvas.itemConfig(self.infixInputString, text=infixExpression)
        self.canvas.itemConfig(self.postfixLabel, text='postfix')
        
        self.highlightCode('s = Stack({ARRAY_SIZE})'.format(**env), callEnviron,
                           color=hlColor)
        self.createEvaluateStructues(postfixExpression, callEnviron=callEnviron)

        left, operator, right = [
            self.canvas.create_text(
                *coords, text='', font=self.VALUE_FONT, fill=self.VALUE_COLOR)
            for coords in self.operandAndOperatorCoords()]
        callEnviron |= set((left, operator, right))
        operatorCoords = self.canvas.coords(operator)
        
        self.highlightCode(('token, postfix = nextToken(postfix)', 1),
                           callEnviron, color=hlColor)
        tokenLabel = self.canvas.create_text(
            *(V(self.canvas.coords(self.postfixLabel)) +
              V(self.extractDelta(self.postfixLabel))), text='token',
            font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR, anchor=E)
        callEnviron.add(tokenLabel)
        token, postfixExpression = self.nextToken(self.postfixInputString)
        tokenItem = self.extractToken(token, self.postfixInputString,
                                      callEnviron)
        labelCoords = self.canvas.coords(self.postfixLabel)
        precValue = self.canvas.create_text(
            labelCoords[0] + 300, labelCoords[1], text='',
            font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR, anchor=W)
        callEnviron.add(precValue)
        
        self.highlightCode(('token', 2), callEnviron, wait=wait, color=hlColor)
        while token:
            
            self.highlightCode('prec = precedence(token)', callEnviron,
                               wait=wait, color=hlColor)
            prec = self.precedence(token)
            self.canvas.itemConfig(precValue, text='prec = {}'.format(prec))
            
            self.highlightCode(('prec', 3), callEnviron, wait=wait,
                               color=hlColor)
            if prec:
                
                self.moveItemsTo(tokenItem, operatorCoords, sleepTime=0.01)
                self.canvas.itemConfig(operator, text=token)
                self.canvas.delete(tokenItem)
                callEnviron.discard(tokenItem)
                
                self.highlightCode('right = s.pop()', callEnviron, 
                                   color=hlColor)
                result, attempts = None, 0
                try:
                    rightDValue = self.popToken(
                        callEnviron, arrayID=self.EVstackID, toString=right)
                except IndexError as e:
                    self.setMessage(e)
                    hlColor = self.EXCEPTION_HIGHLIGHT
                    self.highlightCode('right = s.pop()', callEnviron,
                                       color=hlColor)
                    self.wait(1)
                    rightDValue, result = errorValue, errorValue
                    
                self.highlightCode('left = s.pop()', callEnviron, color=hlColor)
                try:
                    leftDValue = self.popToken(
                        callEnviron, arrayID=self.EVstackID, toString=left)
                except IndexError as e:
                    self.setMessage(e)
                    hlColor = self.EXCEPTION_HIGHLIGHT
                    self.highlightCode('left = s.pop()', callEnviron,
                                       color=hlColor)
                    self.wait(1)
                    leftDValue, result = errorValue, errorValue

                op = token
                try:
                    L = eval(leftDValue.val)
                except:
                    L = errorValue
                    hlColor = self.EXCEPTION_HIGHLIGHT
                try:
                    R = eval(rightDValue.val)
                except:
                    R = errorValue
                    hlColor = self.EXCEPTION_HIGHLIGHT
                check = lambda o: self.highlightOp(
                    op, o, callEnviron, wait, hlColor)
                while result is None:
                    try:
                        attempts += 1
                        result = (errorValue
                                  if L is errorValue or R is errorValue else
                                  L|R if check('|') else L&R if check('&') else
                                  L+R if check('+') else L-R if check('-') else
                                  L*R if check('*') else L/R if check('/') else
                                  L%R if check('%') else L^R if check('^') else
                                  None)
                    except Exception as e:
                        self.setMessage(e)
                        hlColor = self.EXCEPTION_HIGHLIGHT
                        self.wait(1)
                        if attempts > 1 or not isinstance(e, TypeError):
                            result = errorValue
                            break
                        L = int(L)
                        self.canvas.itemConfig(left, text=str(L))
                        R = int(R)
                        self.canvas.itemConfig(right, text=str(R))
                        self.setMessage('Convert values to integer')
                        hlColor = self.CODE_HIGHLIGHT
                        self.wait(1)
                        
                self.moveItemsTo(
                    (left, right), (operatorCoords, operatorCoords), 
                    sleepTime=0.01)
                resultString = (
                    '{:3.5f}'.format(result) if isinstance(result, float)
                    else str(result))
                if isinstance(result, float) and '.' in resultString:
                    resultString = resultString.rstrip('0.')
                tokenItem = self.canvas.create_text(
                    *operatorCoords, text=resultString, font=self.VALUE_FONT,
                    fill=self.VALUE_COLOR)
                for displayString, coords in zip(
                        (left, operator, right),
                        self.operandAndOperatorCoords()):
                    self.canvas.itemConfig(displayString, text='')
                    self.canvas.coords(displayString, *coords)
                    
            else:
                self.highlightCode('s.push(int(token))', callEnviron, 
                                   color=hlColor)
            self.pushToken(tokenItem, callEnviron, arrayID=self.EVstackID)
                          
            self.highlightCode(('token, postfix = nextToken(postfix)', 2),
                               callEnviron, color=hlColor)
            token, postfixExpression = self.nextToken(self.postfixInputString)
            tokenItem = self.extractToken(token, self.postfixInputString,
                                          callEnviron)
            self.highlightCode(('token', 2), callEnviron, wait=wait, 
                               color=hlColor)

        self.canvas.itemConfig(precValue, text='')
        self.canvas.itemConfig(operator, text='')
        self.highlightCode('return s.pop()', callEnviron, color=hlColor)
        try:
            dValue = self.popToken(callEnviron, arrayID=self.EVstackID)
            self.outputBox.setToText(dValue.items, sleepTime=wait / 10)
        except:
            hlColor = self.EXCEPTION_HIGHLIGHT
            self.highlightCode('return s.pop()', callEnviron, color=hlColor)
            dValue = drawnValue(errorValue)
            
        self.cleanUp(callEnviron)
        return dValue.val

    def highlightOp(self, actual, target, callEnviron, wait=0.1, color=None):
        self.highlightCode("token == '{}'".format(target), callEnviron, 
                           wait=wait, color=color)
        if actual == target:
            self.highlightCode("s.push(left {} right)".format(target),
                               callEnviron, color=color)
            return True

    postfixTranslateCode = '''
def PostfixTranslate(formula={infixExpression!r}):
   postfix = Queue({ARRAY_SIZE})
   s = Stack({ARRAY_SIZE})
    
   token, formula = nextToken(formula)
   while token:
      prec = precedence(token)
      delim = delimiter(token)
      if delim:
         if token == '(':
            s.push(token)
         else:
            while not s.isEmpty():
               top = s.pop()
               if top == '(':
                  break
               else:
                  postfix.insert(top)
                        
      elif prec:
         while not s.isEmpty():
            top = s.pop()
            if (top == '(' or
                precedence(top) < prec):
                s.push(top)
                break
            else:
                postfix.insert(top)
         s.push(token)

      else:
         postfix.insert(token)
        
      token, formula = nextToken(formula)
    
   while not s.isEmpty():
      postfix.insert(s.pop())

   ans = ""
   while not postfix.isEmpty():
      if len(ans) > 0:
         ans += " "
      ans += postfix.remove()
   return ans
'''

    def PostfixTranslate(self, infixExpression, code=postfixTranslateCode):
        del self.TRstack[:]
        self.TRqueue = [drawnValue(None) for i in self.TRqueue]
        self.TRqueueRear = 0
        self.TRqueueFront = 1
        self.TRqueueSize = 0

        env = locals()
        env['ARRAY_SIZE'] = self.ARRAY_SIZE
        callEnviron = self.createCallEnvironment(code=code.format(**env))
        wait = 0.1

        self.highlightCode(
            ['postfix = Queue({ARRAY_SIZE})'.format(**env),
             's = Stack({ARRAY_SIZE})'.format(**env)], callEnviron)
        self.display(inputString=infixExpression)
        self.createTranslateStructues(callEnviron)
        self.wait(wait)

        self.highlightCode('token, formula = nextToken(formula)', callEnviron)
        token, infixExpression = self.nextToken(self.infixInputString)
        tokenItem = self.extractToken(
            token, self.infixInputString, callEnviron,
            toString=self.postfixInputString)

        labelCoords = self.canvas.coords(self.postfixLabel)
        precValue = self.canvas.create_text(
            labelCoords[0] + 150, labelCoords[1], text='',
            font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR, anchor=W)
        delimValue = self.canvas.create_text(
            labelCoords[0] + 300, labelCoords[1], text='',
            font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR, anchor=W)
        callEnviron |= set((precValue, delimValue))
        
        self.highlightCode(('token', 2), callEnviron, wait=wait)
        while token:
            self.highlightCode('prec = precedence(token)', callEnviron,
                               wait=wait)
            prec = self.precedence(token)
            self.canvas.itemConfig(precValue, text='prec = {}'.format(prec))
            self.highlightCode('delim = delimiter(token)', callEnviron,
                               wait=wait)
            delim = self.delimiter(token)
            self.canvas.itemConfig(
                delimValue, text='delim = {}'.format(delim))

            self.highlightCode(('delim', 3), callEnviron, wait=wait)
            if delim:
                
                self.highlightCode("token == '('", callEnviron, wait=wait)
                if token == '(':
                    
                    self.highlightCode(('s.push(token)', 1), callEnviron)
                    self.pushToken(
                        tokenItem, callEnviron, arrayID=self.TRstackID,
                        color=drawnValue.palette[prec - 1])
                else:
                    self.canvas.delete(tokenItem)
                    callEnviron.discard(tokenItem)
                    self.highlightCode(('not s.isEmpty()', 1), callEnviron, 
                                       wait=wait)
                    while self.TRstack:
                        self.highlightCode('top = s.pop()', callEnviron)
                        top = self.popToken(callEnviron, arrayID=self.TRstackID)

                        self.highlightCode(("top == '('", 1), callEnviron, 
                                           wait=wait)
                        if top.val == '(':
                            for item in top.items:
                                self.canvas.delete(item)
                                callEnviron.discard(item)
                            self.highlightCode(('break', 1), callEnviron, 
                                               wait=wait)
                            break
                        else:
                            self.highlightCode(
                                ('postfix.insert(top)', 1), callEnviron)
                            self.insertToken(top, callEnviron)
                            
                        self.highlightCode(('not s.isEmpty()', 1), callEnviron, 
                                           wait=wait)
                            
            elif prec:                # Input token is an operator
                self.highlightCode(('prec', 3), callEnviron, wait=wait)
                
                self.highlightCode(('not s.isEmpty()', 2), callEnviron,
                                   wait=wait)
                while self.TRstack:
                    self.highlightCode(('top = s.pop()', 2), callEnviron)
                    top = self.popToken(callEnviron, arrayID=self.TRstackID)

                    self.highlightCode(("top == '('", 2), callEnviron,
                                       wait=wait)
                    if top.val != '(':
                        self.highlightCode(
                            'precedence(top) < prec', callEnviron, wait=wait)
                        
                    if top.val == '(' or self.precedence(top.val) < prec:
                        # Just put drawnValue back in place
                        self.highlightCode(("s.push(top)", 1), callEnviron)
                        self.pushToken(top, callEnviron, arrayID=self.TRstackID)

                        self.highlightCode(("break", 2), callEnviron, wait=wait)
                        break
                    else:
                        self.highlightCode(('postfix.insert(top)', 2),
                                           callEnviron)
                        self.insertToken(top, callEnviron)
                        
                    self.highlightCode(('not s.isEmpty()', 2), callEnviron,
                                       wait=wait)
                        
                self.highlightCode(('s.push(token)', 2), callEnviron)
                self.pushToken(tokenItem, callEnviron,
                               arrayID=self.TRstackID, color=drawnValue.palette[prec - 1])
                
            else:                     # Input token is an operand
                self.highlightCode(('prec', 3), callEnviron, wait=wait)
                self.highlightCode('postfix.insert(token)', callEnviron)
                self.insertToken(tokenItem, callEnviron)

            self.highlightCode(('token, formula = nextToken(formula)', 2),
                               callEnviron)
            token, infixExpression = self.nextToken(self.infixInputString)
            tokenItem = self.extractToken(
                token, self.infixInputString, callEnviron,
                toString=self.postfixInputString)
            self.highlightCode(('token', 2), callEnviron, wait=wait)

        self.highlightCode(('not s.isEmpty()', 3), callEnviron, wait=wait)
        while self.TRstack:
            self.highlightCode('postfix.insert(s.pop())', callEnviron)
            self.insertToken(self.popToken(callEnviron, arrayID=self.TRstackID), callEnviron)
            self.highlightCode(('not s.isEmpty()', 3), callEnviron, wait=wait)

        self.canvas.itemConfig(self.postfixLabel, text='ans')
        self.canvas.itemConfig(precValue, text='')
        self.canvas.itemConfig(delimValue, text='')
        ans = ""
        self.highlightCode('ans = ""', callEnviron, wait=wait)
        self.highlightCode('not postfix.isEmpty()', callEnviron, wait=wait)
        while self.TRqueueSize > 0:
            self.highlightCode('len(ans) > 0', callEnviron, wait=wait)
            if len(ans) > 0:
                self.highlightCode('ans += " "', callEnviron, wait=wait)
                ans += " "
            self.highlightCode('ans += postfix.remove()', callEnviron)
            ans += self.removeToken(callEnviron, self.postfixInputString)
            
            self.highlightCode('not postfix.isEmpty()', callEnviron, wait=wait)
                
        self.highlightCode('return ans', callEnviron)
        self.cleanUp(callEnviron)
        return ans
    
    def nextToken(self, fromString, waitForStrip=0.1):
        text = self.canvas.itemConfig(fromString, 'text')
        token = ''
        stripped = text.strip()
        if stripped != text:
            self.canvas.itemConfig(fromString, text=stripped)
            text = stripped
            if waitForStrip:
                self.wait(waitForStrip)
        if len(text) > 0:
            if self.precedence(text[0]):
                token = text[0]
                text = text[1:]
            else:
                while len(text) > 0 and not (   # to next operator or space
                        self.precedence(text[0]) or text[0].isspace()):
                    token += text[0]
                    text = text[1:]
        return token, text  # Return the token, and remaining input string

    def extractDelta(self, fromString, toString=None):
        return ((0, self.INPUT_BOX_HEIGHT) if toString is None else
                V(self.canvas.coords(toString)) -
                V(self.canvas.coords(fromString)))
    
    def extractToken(self, token, fromString, callEnviron, anchor=None,
                     font=None, color=None, toString=None):
        '''Get a canvas text item to repesent a token extracted from the
        beginning of a displayed string'''
        text = self.canvas.itemConfig(fromString, 'text')
        if not text.startswith(token):
            raise ValueError('Token does not match beginning of string')
        coords = self.canvas.coords(fromString)
        if font is None:
            font = self.VALUE_FONT
        if color is None:
            color = self.VALUE_COLOR
        tokenItem = self.canvas.create_text(
            *coords, text=token, font=font, fill=color, anchor=W)
        callEnviron.add(tokenItem)
        self.moveItemsBy(tokenItem, self.extractDelta(fromString, toString),
                         sleepTime=0.01)
        self.canvas.itemConfig(tokenItem, anchor=anchor)
        self.canvas.itemConfig(fromString, text=text[len(token):])
        return tokenItem
        
    def pushToken(self, token, callEnviron, arrayID=0, color=None):
        '''Push a token on a stack.  The token can either be canvas text
        item or a drawnValue.'''
        index = len(self.structures[arrayID])
        if index >= self.ARRAY_SIZE:
            raise IndexError('Stack overflow')
        toCoords = self.cellCoords(index, arrayID)
        toCenter = self.cellCenter(index, arrayID)
        if isinstance(token, int):
            self.moveItemsTo(token, toCenter, sleepTime=0.01)
            text = self.canvas.itemConfig(token, 'text')
            dValue = drawnValue(
                text, *self.createCellValue(index, text, arrayID, color=color))
            self.canvas.delete(token)
            callEnviron.discard(token)
        else:
            if V(V(toCoords) - V(self.canvas.coords(token.items[0]))).len2() > 0.1:
                self.moveItemsTo(token.items, (toCoords, toCenter),
                                 sleepTime=0.01)
            dValue = token
        callEnviron |= set(dValue.items)
        self.structures[arrayID].append(dValue)
        self.moveItemsBy(
            self.indices[arrayID], (0, - self.CELL_HEIGHT), sleepTime=0.01)

    def popToken(self, callEnviron, arrayID=0, toString=0, sleepTime=0.01):
        '''Pop a drawnValue record from an array structure and optionally
        move a copy of its value text to a toString'''
        index = len(self.structures[arrayID]) - 1
        if index < 0:
            raise IndexError('Stack underflow')
        top = self.structures[arrayID].pop()
        if toString:
            text = self.canvas.itemConfig(toString, 'text')
            if len(text) > 0 and not text.endswith(' '):
                text += ' '
            copyItem = self.canvas.copyItem(top.items[1])
            callEnviron.add(copyItem)
            self.dispose(callEnviron, *top.items)
            toCoords = V(self.canvas.coords(toString)) + V(
                textWidth(self.VALUE_FONT, text + top.val) // 2, 0)
            self.moveItemsTo(copyItem, toCoords, sleepTime=0.01)
            self.canvas.itemConfig(toString, text=text + top.val)
            self.dispose(callEnviron, copyItem)
        self.moveItemsBy(
            self.indices[arrayID], (0, self.CELL_HEIGHT), sleepTime=sleepTime)
        return top
    
    def insertToken(self, token, callEnviron, color=None):
        '''Insert a token at the rear of the queue.  Token can either be a
        drawnValue on a stack, or a canvas text item ID (int)'''
        if self.TRqueueSize >= self.ARRAY_SIZE:
            raise IndexError('Queue overflow')
        index = (self.TRqueueRear + 1) % len(self.TRqueue)
        indexCoords = self.indexCoords(index, arrayID=self.TRqueueID, level=0)
        self.moveItemsTo(self.TRqueueRearIndex, (indexCoords, indexCoords[:2]),
                         sleepTime=0.01)
        toCoords = self.cellCoords(index, arrayID=self.TRqueueID)
        toCenter = self.cellCenter(index, arrayID=self.TRqueueID)
        if isinstance(token, int):
            items = (token,)
            dValue = None
        elif isinstance(token, drawnValue):
            items = token.items
            dValue = token
        self.moveItemsTo(
            items, (toCoords, toCenter) if len(items) == 2 else (toCenter,),
            sleepTime=0.01)
        if dValue is None:
            text = self.canvas.itemConfig(token, 'text')
            dValue = drawnValue(
                text, 
                *self.createCellValue(index, text, arrayID=self.TRqueueID,
                                      color=color))
            callEnviron |= set(dValue.items)
            for item in items:
                self.canvas.delete(item)
                callEnviron.discard(item)
        self.TRqueue[index] = dValue
        self.TRqueueRear = index
        self.TRqueueSize += 1

    def removeToken(self, callEnviron, toString=None):
        '''Remove a token from the front of the queue and optionally move it
        to the end of a text item on the canvas, toString'''
        if self.TRqueueSize <= 0:
            raise IndexError('Queue underflow')
        dValue = self.TRqueue[self.TRqueueFront]
        removed = dValue.val
        index = (self.TRqueueFront + 1) % len(self.TRqueue)
        if toString:
            text = self.canvas.itemConfig(toString, 'text')
            if len(text) > 0 and not text.endswith(' '):
                text += ' '
            copyItem = self.canvas.copyItem(dValue.items[1])
            callEnviron.add(copyItem)
            bbox = self.canvas.bbox(copyItem)
            self.canvas.move(copyItem, (bbox[0] - bbox[2]) // 2, 0)
            self.canvas.itemConfig(copyItem, anchor=W)
            toCoords = V(self.canvas.coords(toString)) + V(
                textWidth(self.VALUE_FONT, text), 0)
            self.moveItemsTo(copyItem, toCoords, sleepTime=0.01)
            self.canvas.itemConfig(toString, text=text + removed)
            self.canvas.delete(copyItem)
            callEnviron.discard(copyItem)
        self.TRqueueFront = index
        self.TRqueueSize -= 1
        indexCoords = self.indexCoords(
            self.TRqueueFront, arrayID=self.TRqueueID, level=1)
        self.moveItemsTo(self.TRqueueFrontIndex, (indexCoords, indexCoords[:2]),
                         sleepTime=0.01)
        for item in dValue.items:
            self.canvas.delete(item)
            callEnviron.discard(item)
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
    if len(sys.argv) > 1:
        app.setArgument(' '.join(sys.argv[1:]))
        app.evaluateButton.invoke()
    app.runVisualization()
