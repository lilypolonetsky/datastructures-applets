# Utilities for working with coordinates
# The vector class is used to hold a tuple of coordinates and define many
# operations on them.  The operations return tuples not vectors, but can
# easily be converted by wrapping the result in vector() constructor, e.g.
# vector(*result)

from itertools import *
from operator import *
import math

class vector(object):
    # Constructor accepts multiple coordinate parameters: vector(3, 4, 5) or
    # a sequence containing coordinates: vector([3, 4, 5])
    def __init__(self, *coords):
        self.coords = tuple(coords[0]) if (
            len(coords) == 1 and isinstance(coords[0], (list, tuple, set))
        ) else coords

    def __len__(self):
        return len(self.coords)

    def __str__(self):
        return 'V({})'.format(', '.join(map(str, self.coords)))

    def __eq__(self, other):
        if isinstance(other, vector):
            return self.coords == other.coords
        elif isinstance(other, (list, tuple)):
            return self == vector(other)

    def __lt__(self, other):
        if isinstance(other, vector):
            return self.coords < other.coords
        elif isinstance(other, (list, tuple)):
            return self < vector(other)

    def __gt__(self, other):
        if isinstance(other, vector):
            return self.coords > other.coords
        elif isinstance(other, (list, tuple)):
            return self > vector(other)
         
    def __le__(self, other): return self < other or self == other
    def __ge__(self, other): return self > other or self == other

    def __getitem__(self, key): # Implement posititional field access
        if isinstance(key, int):
            if 0 <= key and key < len(self.coords):
                return self.coords[key]
            raise IndexError
        elif isinstance(key, slice):
            return self.coords[key.start:key.stop:key.step]
        elif isinstance(key, str) and len(key) == 1 and key.lower() in 'xyz':
            return self.coords['xyz'.index(key.lower())]
        raise ValueError('Invalid vector type')

    def __add__(self, other):
        if isinstance(other, vector):
            return tuple(map(add, self.coords, other.coords))
        elif isinstance(other, (list, tuple)):
            return self + vector(other)
        elif isinstance(other, (int, float)):
            return tuple(c + other for c in self.coords)
        raise ValueError('Invalid vector type')

    def __sub__(self, other):
        if isinstance(other, vector):
            return tuple(map(sub, self.coords, other.coords))
        elif isinstance(other, (list, tuple)):
            return self - vector(other)
        elif isinstance(other, (int, float)):
            return tuple(c - other for c in self.coords)
        raise ValueError('Invalid vector type')

    def __mul__(self, other):
        if isinstance(other, vector):
            return tuple(map(mul, self.coords, other.coords))
        elif isinstance(other, (list, tuple)):
            return self * vector(other)
        elif isinstance(other, (int, float)):
            return tuple(c * other for c in self.coords)
        raise ValueError('Invalid vector type')

    def __truediv__(self, other):
        if isinstance(other, vector):
            return tuple(map(truediv, self.coords, other.coords))
        elif isinstance(other, (list, tuple)):
            return self / vector(other)
        elif isinstance(other, (int, float)):
            return tuple(c / other for c in self.coords)
        raise ValueError('Invalid vector type')

    def dot(self, other):
        return sum(self * other)
     
    def len2(self):
        return self.dot(self)

    def vlen(self):
        return math.sqrt(self.len2())

    def unit(self):
        return self / self.vlen()

    def rotate(self, angle, radians=False):
        a = angle if radians else math.radians(angle)
        s, c = math.sin(a), math.cos(a)
        return (self.dot(vector(c, -s)), self.dot(vector(s, c)))

def bbox(*vectors): # Return the bounding box of a sequence of vectors
    minlen = min(len(v) for v in vectors)
    return (
        tuple(min(*(p[i] for p in vectors)) for i in range(minlen)),
        tuple(max(*(p[i] for p in vectors)) for i in range(minlen)))
     
if __name__ == '__main__':
    V = vector
    print('V is short for vector')
    A = V(3, 4, 5)
    print('A = V(3, 4, 5)')
    B = V(4, 3, 2)
    print('B = V(4, 3, 2)')

    expressions = [
        'A', 'B', 'str(A)', 'str(B)', 
        'A + B', 'A - B', 'A * B', 'B * A', 'A / B',
        'A * 2', 'A + 2', 'A - 2', 'A / 2',
        'A < B', 'A == B', 'A > B', 'A == A', 'A <= B', 'A <= A',
        'A[0]', 'A[:2]', 'A[::2]', 'str(V(*A[::2]))', 'str(V(A[::2]))',
        'V(A[::2]).rotate(90)', 'A.rotate(37)',
        'A.dot(B)', 'A.len2()', 'A.vlen()', 'A.unit()',
        'bbox(A, B)', 'bbox(B[1:], A)'
    ]
    for exp in expressions:
        print('{} evaluates to '.format(exp), end='')
        print(repr(eval(exp, globals())))
