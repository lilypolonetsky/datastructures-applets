import time
from tkinter import *
import math
from PIL import ImageTk
from PIL import Image


WIDTH = 800
HEIGHT = 400

CELL_WIDTH = 70
CELL_HEIGHT = 50
CELL_GAP = 20
DOT_SIZE = 10
LL_X0 = 100
LL_Y0 = 100

window = Tk()
frame = Frame(window)
frame.pack()

waitVar = BooleanVar()

canvas = Canvas(frame, width=WIDTH, height=HEIGHT)
window.title("Linked List")
canvas.pack()

bottomframe = Frame(window)
bottomframe.pack(side=BOTTOM)
ll = [i for i in range(7)]

for i in range(len(ll)):
    offset = i*(CELL_WIDTH + CELL_GAP)
    canvas.create_rectangle(LL_X0 + offset,
                            LL_Y0,
                            LL_X0 + CELL_WIDTH + offset,
                            LL_Y0 + CELL_HEIGHT, fill = "WHITE")
    canvas.create_text(LL_X0 + CELL_HEIGHT//2 + offset,
                       LL_Y0 + CELL_HEIGHT//2,
                       text=str(ll[i]), font=('Helvetica', '20'))
    canvas.create_oval(LL_X0 + CELL_HEIGHT - DOT_SIZE//2 + offset,
                       LL_Y0 + CELL_HEIGHT//2 - DOT_SIZE//2,
                       LL_X0 + CELL_HEIGHT + DOT_SIZE//2 + offset,
                       LL_Y0 + CELL_HEIGHT // 2 + DOT_SIZE//2,
                       fill = "RED", outline = "RED")
    verticalRadius = 0
    horizontalRadius = CELL_GAP + CELL_WIDTH - CELL_HEIGHT
    tailX = LL_X0 + offset + CELL_WIDTH + CELL_GAP - 1
    tailY = verticalRadius * math.sqrt(math.fabs(horizontalRadius*2 - tailX*2)) / horizontalRadius
    arc = canvas.create_arc(LL_X0 + CELL_HEIGHT + offset,
                            LL_Y0 + CELL_HEIGHT // 2 - verticalRadius,
                            LL_X0 + offset + CELL_WIDTH + CELL_GAP,
                            LL_Y0 + CELL_HEIGHT // 2 + verticalRadius,
                            start=0, extent=180, style=ARC
                            )
    coords = canvas.coords(arc)
    arrowSlope = -verticalRadius*2 *(tailX) / horizontalRadius*2 *(tailY)
    #dy/dx = y1 - y0 / x1 - x0
    #(x1 - x0) * dy/dx = y1-y0
    #y0 = y1 - dy/dx * (x0-y0)
    '''canvas.create_line(LL_X0 + offset + CELL_WIDTH + CELL_GAP - verticalRadius,
                       LL_Y0 + CELL_HEIGHT // 2 - verticalRadius,
                       LL_X0 + offset + CELL_WIDTH + CELL_GAP,
                      LL_Y0 + CELL_HEIGHT // 2 + verticalRadius,
                      arrow="last")'''


    points = [LL_X0 + offset + CELL_WIDTH + CELL_GAP - 5, LL_Y0 + CELL_HEIGHT // 2 - 5,
              LL_X0 + offset + CELL_WIDTH + CELL_GAP - 5, LL_Y0 + CELL_HEIGHT // 2 + 5,
              LL_X0 + offset + CELL_WIDTH + CELL_GAP, LL_Y0 + CELL_HEIGHT // 2]
    canvas.create_polygon(points, fill="BLACK")


window.mainloop()

import random


class Node(object):
    # create a linked list node consisting of a key/data pair
    def __init__(self, k, d, n=None):
        self.key = k
        self.data = d
        self.next = n  # reference to next item in list

    def __str__(self):
        return "{" + str(self.key) + ", " + str(self.data) + "}"


class LinkedList(object):
    def __init__(self):
        self.__first = None
        self.__last = None

    def __len__(self):
        cur = self.__first
        ans = 0

        while cur:
            ans += 1
            cur = cur.next

        return ans

    def isEmpty(self):
        return not self.__first

    # insert a key/data pair at the start of the list
    def insert(self, key, data):
        newNode = Node(key, data, self.__first)
        if self.__first == None: self.__last = newNode
        self.__first = newNode

    # return a tuple containing the key/data pair
    # associated with key. return None if key
    # couldn't be found in the list.
    def find(self, key):
        # loop until we hit the end, or find the key
        cur = self.__first
        while cur and cur.key != key: cur = cur.next

        # return the key/data pair if found
        return (cur.key, cur.data) if cur else None

    # attempt to insert a new Node containing newKey/NewData
    # into the linked list immediately after the first node
    # containing key. Return True on success, False otherwise.
    def insertAfter(self, key, newKey, newData):
        # find the first Node that contains key
        cur = self.__first
        while cur and cur.key != key: cur = cur.next

        # if such a node is there, patch in a new Node
        if cur:
            newNode = Node(newKey, newData, cur.next)
            cur.next = newNode
            if not newNode.next: self.__last = newNode

        return cur != None  # return True on success

    def insertLast(self, key, data):
        if not self.__first: return self.insert(key, data)

        newNode = Node(key, data)
        self.__last.next = newNode
        self.__last = newNode

    def reverse(self):
        ans = None
        newLast = cur = self.__first
        while cur:
            next = cur.next
            cur.next = ans
            ans = cur
            cur = next

        self.__first = ans
        self.__last = newLast

    def recursiveReverse(self, l=None):
        # on initialization, first becomes last
        if not l: self.__last = l = self.__first

        # base case: upon reaching last element,
        # remember it as the first in the reversed list
        if not l or not l.next:
            self.__first = l

        else:
            # recursively reverse everything but the first
            self.recursiveReverse(l.next)

            # upon return, what was at l.next is now
            # at the end of the reversed list
            l.next.next = l
            l.next = None

    # delete a node from the linked list, returning the key/data
    # pair of the deleted node. If key == None, then just delete
    # the first node. Otherwise, attempt to find and delete
    # the first node containing key
    def delete(self, key=None):
        # delete the first node?
        if (not key) or (self.__first and key == self.__first.key):
            ans = self.__first
            if not ans: return None
            self.__first = ans.next
            return ans.key, ans.data

        # loop until we hit end, or find key,
        # keeping track of previously visited node
        cur = prev = self.__first
        while cur and cur.key != key:
            prev = cur
            cur = cur.next

        # A node with this key isn't on list
        if not cur: return None

        # otherwise remove the node from the list and
        # return the key/data pair of the found node
        prev.next = cur.next
        if not prev.next: self.__last = prev

        return cur.key, cur.data

    # Splits the list into two approximately equal length parts
    # Self keeps the first half of the list, and the return value
    # is a new LinkedList object that has the second half.
    def split(self):
        ans = LinkedList()

        # Only bother if list has at least 2 elements
        if self.__first and self.__first.next:
            # Use slow/fast pointers to find midpoint
            slow = fast = self.__first
            pred = None
            while fast:
                pred = slow
                slow = slow.next
                fast = fast.next
                if fast: fast = fast.next

            # pred points to predecessor of midpoint Node

            # split off the second half of the list
            ans.__first = pred.next
            ans.__last = self.__last

            # terminate the first part of the list
            self.__last = pred
            pred.next = None

        return ans

        # This is a mutator, and doesn't actually return anything.

    # merge's job is to merge the two LinkedList objects, keeping
    # the keys in ascending order. The "surviving" object is self,
    # and when done, all of other's Nodes will have been merged into
    # the linked list of Nodes referenced by self.
    def merge(self, other):
        pass  # replace this line with your code

    def sort(self):
        # only bother if LinkedList has > 1 nodes
        if self.__first != self.__last:
            # split into two halves
            rightPart = self.split()

            # sort the left and right parts
            self.sort()
            rightPart.sort()

            # merge the results
            self.merge(rightPart)

    def __str__(self):
        ans = "("

        # if the list isn't empty, start the fencepost
        cur = self.__first
        if cur:
            ans += str(cur)
            cur = cur.next

        # each subsequent element of the list follows an arrow
        while cur:
            ans += " ==> " + str(cur)
            cur = cur.next

        return ans + ")"


def __main():
    ll = LinkedList()
    print("Empty linked list:", ll)

    # insert a bunch of nodes
    for i in range(40):
        ll.insert(random.randint(1, 100000), "foo")

    print("List before sorting:", ll)
    print("List has", len(ll), "elements")

    ll.sort()
    print("Sorted list now: ", ll)


if __name__ == '__main__':
    __main()


'''
Useful Links:
http://effbot.org/zone/tkinter-complex-canvas.htm
https://mail.python.org/pipermail/python-list/2000-December/022013.html
'''