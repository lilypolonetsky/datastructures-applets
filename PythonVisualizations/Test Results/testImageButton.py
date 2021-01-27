from tkinter import *
from tkinter import ttk

try:
   from PIL import Image as Img
   from PIL import ImageTk
except ModuleNotFoundError as e:
   print('Pillow module not found.  Did you try running:')
   print('pip3 install -r requirements.txt')
   raise e

try:
   from coordinates import *
   from VisualizationApp import *
except ModuleNotFoundError:
   from .coordinates import *
   from .VisualizationApp import *

from pprint import pprint

V = vector

class TestImageButton(VisualizationApp):
   def __init__(self, title='Test Image Button'):
      super().__init__(title=title)
      self.testsRun = 0
      self.makeButtons()

   def makeButtons(self, maxRows=4):
      self.testButton = self.addOperation(
         "Disable", self.clickTest, maxRows=maxRows)
      self.nothingButton = self.addOperation(
         "Do nothing", self.clickNothing, buttonType=Button, maxRows=maxRows)
      self.insertButton = self.addOperation(
          "Insert", self.clickInsert, numArguments=1, argHelpText=['item'],
          helpText='Insert item nowhere', maxRows=maxRows)
      self.playControls = self.makePlayControls(maxRows=maxRows)

   def clickInsert(self):
      self.setMessage('Insert {} nowhere'.format(self.getArgument()))

   def makePlayControls(self, maxRows=4):
      imageFiles = ('play-symbol.png', 'pause-symbol.png',
                    'skip-next-symbol.png', 'stop-symbol.png')
      self.images = [None] * len(imageFiles)
      self.imageBtns = [None] * len(imageFiles)
      rect_bg = self.canvas.create_rectangle(
          90, 90, 200, 110 + len(imageFiles) * 60, fil='beige', outline='',
          width=0)
      
      self.controlsFrame = Frame(self.operations, bg=self.OPERATIONS_BG)
      withArgs, withoutArgs, nColumns, nRows = self.getOperations()
      buttonRow = len(withoutArgs) % maxRows + 1
      self.controlsFrame.grid(column=4 + len(withoutArgs) // maxRows,
                                  row=buttonRow, sticky=(E,W))

      row, column = 0, 0
      targetSize = (abs(self.CONTROLS_FONT[1]),) * 2
      for i, imagefile in enumerate(imageFiles):
          self.images[i] = Img.open(imagefile)
          imgItem = self.canvas.create_image(
              (column + 1) * 100, (row + 1) * 100, anchor=NW,
              image=ImageTk.PhotoImage(self.images[i]))
          dims = self.images[i].size
          ratios = V(targetSize) / V(dims)
          minRatio = min(*ratios)
          self.images[i] = ImageTk.PhotoImage(self.images[i].resize(
              tuple(int(round(d * minRatio)) for d in dims)))
          Bclass = Button # ttk.Button if i % 2 == 0 else Button
          btn = Bclass(self.controlsFrame, image=self.images[i])
          btn.image = self.images[i]
          btn.grid(row=row, column=column, padx=0, sticky=(E, W))
          self.imageBtns[i] = btn
          btn['command'] = self.runOperation(
              self.setMsg('{} button pressed'.format(imagefile)), True)
          column += 1
          setattr(btn, 'required_args', 0)

   def setMsg(self, msg):
      count = 0
      def handler(event=None):
         nonlocal count
         count += 1
         self.setMessage(msg + '\n{} time{}'.format(
            count, '' if count == 1 else 's'))
      return handler

   def clickNothing(self):
      self.testsRun += 1
      self.setMessage('After {} test{} run\ndo nothing'.format(
         self.testsRun, '' if self.testsRun == 1 else 's'))
      
   def clickTest(self):
      self.testsRun += 1
      self.setMessage('{} test{} run'.format(
         self.testsRun, '' if self.testsRun == 1 else 's'))
      text = self.testButton['text']
      if text == 'Enable':
          for btn in self.imageBtns:
              self.widgetState(btn, NORMAL)
          self.testButton['text'] = 'Disable'
          print('Enabled')
          self.wait(1)
      else:
          for btn in self.imageBtns:
              self.widgetState(btn, DISABLED)
          self.testButton['text'] = 'Enable'
          print('Disabled')
          self.wait(1)

if __name__ == '__main__':
    app = TestImageButton()

    app.runVisualization()

