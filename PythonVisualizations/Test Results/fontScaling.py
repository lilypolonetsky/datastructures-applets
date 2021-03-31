from Visualization import *

if __name__ == '__main__':
    app = Visualization(title='Font Scaling')
    for size in range(20, 0, -1):
       for x, face in enumerate(('Helvetica', 'Courier')):
           font = (face, -size)
           ds = 4
           y0 = (size + ds) * (size + ds) // 2
           x0 = 50 + x * 300
           app.canvas.create_text(
               x0, y0, text=str(font), anchor=NW, font=font,
               fill=app.VALUE_COLOR if x == 0 else app.VARIABLE_COLOR)
           dx = 5
           app.canvas.create_rectangle(
               x0 - size - dx, y0, x0 - dx, y0 + size,
               fill='blue' if x == 0 else 'red', width=0)
           
    app.runVisualization()
