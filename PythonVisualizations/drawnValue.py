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

    def __getitem__(self, key): # Implement positIonal access
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
        return '<drawnValue: {}>'.format(', '.join(
            '{}: {}'.format(attr, repr(getattr(self, attr))) 
            for attr in self.__fields))
        
    def copy(self):          # Retun a copy of this drawnValue
        return drawnValue(*(attr for attr in self))

    def color(self, canvas): # Get fill color of first canvas item
        mainItem = None      # Look for canvas item IDs among items and get
        for item in self.items: # fill attribute of first one, with a
            if isinstance(item, int) and item > 0: # preference for non-text
                if canvas.type(item) != 'text':
                    return canvas.itemconfigure(item, 'fill')[-1]
                if mainItem is None:
                    mainItem = item
        if mainItem is not None:
            return canvas.itemconfigure(mainItem, 'fill')[-1]
        
    palette = ['indianRed1', 'PaleGreen2', 'SkyBlue2', 'orange2',
               'yellow', 'medium orchid', 'dark sea green', 'DodgerBlue2',
               'cyan2', 'forest green', 'navajo white', 'dark goldenrod',
               'gold', 'maroon1', 'plum1']

if __name__ == '__main__':
    from tkinter import *
    import random
    window = Tk()
    canvas = Canvas(window, width=800, height=400)
    canvas.pack()

    side = 50
    N = 20
    row = 5
    numbers = [random.randrange(10) for j in range(N)]
    items = [drawnValue(
        (val, drawnValue.palette[i % len(drawnValue.palette)]),
        canvas.create_rectangle(
            (i % row * 3 + 1) * side, (i // row * 2 + 1) * side,
            (i % row * 3 + 2) * side, (i // row * 2 + 2) * side,
            fill=drawnValue.palette[i % len(drawnValue.palette)],
            outline=''),
        canvas.create_oval(
            (i % row * 3 + 1.5) * side, (i // row * 2 + 1) * side,
            (i % row * 3 + 2.5) * side, (i // row * 2 + 2) * side,
            fill=drawnValue.palette[i % len(drawnValue.palette)],
            outline=''),
        canvas.create_text(
            (i % row * 3 + 1.75) * side, (i // row * 2 + 1.5) * side,
            text='{}, {}'.format(
                val, drawnValue.palette[i % len(drawnValue.palette)]),
            font=('Helvetica', -side // 3)))
             for i, val in enumerate(numbers)
    ]
    print('Drawn values:')
    for i in items:
        print(' ', i)

    print('Colors of first', row, 'drawn values:', 
          [i.color(canvas) for i in items[:row]])
    print('Display_shapes:', [i.display_shape for i in items])

    print('Sorting list by their values...')
    items.sort()
    print('After sorting the list by their values')
    for i in items:
        print(' ', i)

    first = items[0]
    first.display_val = 'replaced'
    print("Geting the first sorted drawn value's display_shape:", 
          first.display_shape)
    print("The first drawn value's index 1 is:", first[1], 
          "and its display_val is:", first.display_val)
    first[1] = '2nd replacement'
    print("After 2nd update to the first drawn value's index 1 it is:", first)
    
    try:
        print('Attempting to access an invalid foo attribute...')
        print('The foo attribute of the first item is', first.foo)
    except Exception as e:
        print('Caught exception:', e)
    
    try:
        print('Attempting to set an invalid foo attribute...')
        first.foo = 'bar'
        print('The foo attribute of the first item was set to', first.foo)
    except Exception as e:
        print('Caught exception:', e)

    print('All tests complete')
    window.mainloop()
