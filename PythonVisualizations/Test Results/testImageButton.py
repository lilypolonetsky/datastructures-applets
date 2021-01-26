from PIL import Image as Img
from PIL import ImageTk
from tkinter import *
from tkinter import ttk

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

   def makeButtons(self):
      self.testButton = self.addOperation("Disable", self.clickTest)
      imageFiles = ('play-symbol.png', 'pause-symbol.png',
                    'skip-next-symbol.png', 'stop-symbol.png')
      self.playImages = [None] * len(imageFiles)
      self.imageBtns = [None] * len(imageFiles)
      rect_bg = self.canvas.create_rectangle(
          90, 90, 200, 110 + len(imageFiles) * 60, fil='beige', outline='',
          width=0)
      row, column = 1, 0
      targetSize = (abs(self.CONTROLS_FONT[1]),) * 2
      setMsg = lambda m: lambda: self.setMessage(m)
      for i, imagefile in enumerate(imageFiles):
          self.playImages[i] = Img.open(imagefile)
          imgItem = self.canvas.create_image(
              (column + 1) * 100, row * 100, anchor=NW,
              image=ImageTk.PhotoImage(self.playImages[i]))
          dims = self.playImages[i].size
          ratios = V(targetSize) / V(dims)
          minRatio = min(*ratios)
          self.playImages[i] = ImageTk.PhotoImage(self.playImages[i].resize(
              tuple(int(round(d * minRatio)) for d in dims)))
          Bclass = Button # ttk.Button if i % 2 == 0 else Button
          btn = Bclass(self.operations, image=self.playImages[i])
          btn.image = self.playImages[i]
          btn.grid(row=row, column=column, padx=8, sticky=(E, W))
          self.imageBtns[i] = btn
          btn['command'] = self.runOperation(
              setMsg('Image button {} pressed'.format(row)), True)
          row += 1
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

