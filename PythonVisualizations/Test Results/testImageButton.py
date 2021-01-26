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

V = vector

class TestImageButton(VisualizationApp):
   def __init__(self):
      super().__init__()
      self.testsRun = 0
      self.makeButtons()

   def makeButtons(self, maxRows=4):
      self.testButton = self.addOperation("Disable", self.clickTest)
      self.insertButton = self.addOperation(
          "Insert", self.clickInsert, numArguments=1, argHelpText=['item'],
          helpText='Insert item nowhere')
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
      
      self.playControlsFrame = Frame(self.operations, bg=self.OPERATIONS_BG)
      gridItems = gridDict(self.operations) # Operations inserted in grid
      nColumns, nRows = self.operations.grid_size()
      withArgument = [
         gridItems[0, row] for row in range(nRows)
         if isinstance(gridItems[0, row], self.buttonTypes)]
      withoutArgument = [
         gridItems[col, row]
         for row in range(nRows) for col in range(4, nColumns)
         if isinstance(gridItems[col, row], self.buttonTypes)]
      buttonRow = len(withoutArgument) % maxRows + 1
      self.playControlsFrame.grid(column=4 + len(withoutArgument) // maxRows,
                                  row=buttonRow, sticky=(E,W))

      row, column = 0, 0
      targetSize = (abs(self.CONTROLS_FONT[1]),) * 2
      setMsg = lambda m: lambda: self.setMessage(m)
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
          btn = Bclass(self.playControlsFrame, image=self.images[i])
          btn.image = self.images[i]
          btn.grid(row=row, column=column, padx=0, sticky=(E, W))
          self.imageBtns[i] = btn
          btn['command'] = self.runOperation(
              setMsg('{} button pressed'.format(imagefile)), True)
          column += 1
          setattr(btn, 'required_args', 0)

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

