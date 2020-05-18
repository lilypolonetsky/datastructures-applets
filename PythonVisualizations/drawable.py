class drawable(object):      # A record describing a drawable Tk object
    def __init__(            # Constructor
            self, val=None,  # Internal value
            color=None,      # Background color to display
            display_shape=None, # Shape to display
            display_val=None): # Value to display
        self.val = val       # Store initial arguments
        self.color = color
        self.display_shape = display_shape
        self.display_val = display_val

    __fields = ('val', 'color', 'display_shape', 'display_val')

    def __getitem__(self, key): # Implement posititional field access
        if isinstance(key, int):
            if 0 <= key and key < len(self.__fields):
                return getattr(self, self.__fields[key])
            raise IndexError
        elif isinstance(key, str):
            return getattr(self, key)
        raise ValueError

    def __setitem__(self, key, val): # Implement posititional field access
        if isinstance(key, int):
            if 0 <= key and key < len(self.__fields):
                return setattr(self, self.__fields[key], val)
            raise IndexError
        elif isinstance(key, str):
            return setattr(self, key, val)
        raise ValueError
    
    palette = ['indianRed2', 'PaleGreen2', 'SkyBlue2', 'orange2',
               'yellow2', 'cyan2', 'magenta2', 'DodgerBlue2',
               'turquoise2', 'slate gray', 'gold', 'pink']
