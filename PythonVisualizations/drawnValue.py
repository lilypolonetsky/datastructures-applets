import functools

@functools.total_ordering
class drawnValue(object):
    'A record describing a value drawn in a Tk canvas to represent a value'
    def __init__(            # Constructor
            self,            # The value is usually the key used in sorting
            val=None,        # values in a data structure
            *items):         # List of canvas items depicting the value
        self.val = val       # Store initial arguments
        self.items = items

    __fields = ('val', 'items')
    __legacy_fields = ('display_shape', 'display_val')

    def __getitem__(self, key): # Implement posititional field access
        if isinstance(key, int):
            if 0 == key:        # Index 0 is value
                return self.val
            if 1 <= key and key < 1 + len(self.items): # Indices 1-N are
                return self.items[key-1]  # the canvas items making up the value
            raise IndexError
        elif isinstance(key, slice):
            return [self[k] for k in range(key.start or 0, 
                                           key.stop or 1 + len(self.items), 
                                           key.step or 1)]
        elif isinstance(key, str):
            return getattr(self, key)
        raise ValueError

    def __getattr__(self, name):
        if name in self.__legacy_fields:
            return self[self.__legacy_fields.index(name) + 1]
        raise AttributeError('drawnValue has no attribute {}'.format(
            repr(name)))

    def __setitem__(self, key, val): # Implement posititional field access
        if isinstance(key, int):
            if 0 == key:
                self.val = val
                return self
            if 1 <= key and key < 1 + len(self.items):
                self.items = tuple(
                    val if i == key-1 else v for i, v in enumerate(self.items))
                return self
            raise IndexError
        elif isinstance(key, str):
            return setattr(self, key, val)
        raise ValueError

    def __setattr__(self, name, val):
        if name in self.__fields:
            return object.__setattr__(self, name, val)
        if name in self.__legacy_fields:
            pos = self.__legacy_fields.index(name)
            self.items = tuple(
                val if i == pos else v for i, v in enumerate(self.items))
            return 
        raise AttributeError('drawnValue has no attribute {} to set'.format(
            repr(name)))

    def __eq__(self, other):  # Equality test between drawnValues
        if self._is_valid_operand(other): # Only test value to preserve
            return self.val == other.val  # sort stability
        return NotImplemented

    def __lt__(self, other):  # Less than test between drawnValues
        if self._is_valid_operand(other): # Only test value to preserve
            return self.val < other.val   # sort stability
        return NotImplemented
        
    def _is_valid_operand(self, other): # Check that other is drawnValue
        return isinstance(other, drawnValue)

    def __len__(self):
        return 1 + len(self.items)

    def __str__(self):
        return '<drawnValue: {}>'.format(', '.join(repr(attr) for attr in self))
        
    def copy(self):          # Retun a copy of this drawnValue
        return drawnValue(*(attr for attr in self))

    def color(self, canvas): # Get fill color of first canvas item
        mainItem = None      # Use first non-text item or
        for item in self.items: # first text item if all are text
            if canvas.type(item) != 'text':
                return canvas.itemconfigure(item, 'fill')[-1]
            if mainItem is None:
                mainItem = item
        if mainItem is not None:
            return canvas.itemconfigure(mainItem, 'fill')[-1]
        
    palette = ['indianRed2', 'PaleGreen2', 'SkyBlue2', 'orange2',
               'yellow2', 'magenta2', 'cyan2', 'DodgerBlue2',
               'turquoise3', 'slate gray', 'gold', 'pink']

if __name__ == '__main__':
    from tkinter import *
    window = Tk()
    canvas = Canvas(window, width=800, height=400)
    canvas.pack()

    side = 40
    items = [drawnValue(
        val,
        canvas.create_rectangle(
            side + i*3*side, side, side*2 + i*3*side, side*2,
            fill=drawnValue.palette[i], outline='', width=0),
        canvas.create_oval(
            side*1.5 + i*3*side, side, side*2.5 + i*3*side, side*2,
            fill=drawnValue.palette[i], outline='', width=0),
        canvas.create_text(
            side*1.75 + i*3*side, side*1.5, text=str(val),
            font=('Helvetica', 20)))
             for i, val in enumerate([3, 1, 3, 7, 1])
    ]
    print('Integer drawn values:')
    for i in items:
        print(' ', i)

    print('List of drawn values:', 
          [str(i) + ' ' + i.color(canvas) for i in items])
    print('Display_shapes:', [i.display_shape for i in items])
    items.sort()
    print('After sorting the list:',
          [str(i) + ' ' + i.color(canvas) for i in items])
    items[0].display_val = 'replaced'
    print("Geting the first drawn value's display_shape:", 
          items[0].display_shape)
    print("Geting the first drawn value's index 1:", items[0][1])
    print('After replacing display_val in first item it is', items[0])
    items[0][1] = 'replaced'
    print("After setting the first drawn value's index 1:", items[0])
    
    try:
        print('Attempting to access an invalid attribute...')
        print('The foo attribute of the first item is', items[0].foo)
    except Exception as e:
        print('Caught exception:', e)
    
    try:
        print('Attempting to set an invalid attribute...')
        items[0].foo = 'bar'
        print('The foo attribute of the first item was set to', items[0].foo)
    except Exception as e:
        print('Caught exception:', e)

    window.mainloop()
