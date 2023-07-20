# Implement a hash table usnig open addressing
# To experiment with different types of open addressing,
# users provide both a hashing function and a probe generator

from Hashing import *
import sys

def simpleHash(key):        # A simple hashing function
   if isinstance(key, int): # Integers hash to themselves
      return key
   elif isinstance(key, str): # Strings are hashed by letters
      return sum(           # Multiply the code for each letter by
         256 ** i * ord(key[i]) # 256 to the power of its position
         for i in range(len(key))) # in the string
   elif isinstance(key, (list, tuple)): # For sequences,
      return sum(           # Multiply the simpleHash of each element
         256 ** i * simpleHash(key[i]) # by 256 to the power of its
         for i in range(len(key))) # position in the sequence
   raise Exception(         # Otherwise it's an unknown type
      'Unable to hash key of type ' + str(type(key)))

def linearProbe(            # Generator to probe linearly from a
      start, key, size):    # starting cell through all other cells
   for i in range(size):    # Loop over all possible increments
      yield (start + i) % size # and wrap around after end of table

def quadraticProbe(         # Generator to probe quadratically from a
      start, key, size):    # starting cell through all other cells
   for i in range(size):    # Loop over all possible cells
      yield (start + i ** 2) % size # Use quadratic increments

def doubleHashProbe(        # Generator to determine probe interval
      start, key, size):    # from a secondary hash of the key
   yield start % size       # Yield the first cell index
   step = doubleHashStep(key, size) # Get the step size for this key
   for i in range(1, size): # Loop over all remaining cells using
      yield (start + i * step) % size # step from second hash of key

def doubleHashStep(key, size): # Determine step size for a given key
   prime = primeBelow(size) # Find largest prime below array size
   return prime - (         # Step size is based on second hash and
      simpleHash(key) % prime) # is in range [1, prime]

def primeBelow(n):          # Find the largest prime below n
   n -= 1 if n % 2 == 0 else 2 # Start with an odd number below n
   while (3 < n and not is_prime(n)): # While n is bigger than 3 or
      n -= 2                # is not prime, go to next odd number
   return n                 # Return prime number or 3

def fibonacciProbe(         # Generator to probe by steps in the
      start, key, size):    # Fibonacci sequence
   last = 1
   index = 0
   for i in range(size):    # Loop over all possible cells
      yield (start + index) % size # Yield current index & advance the
      last, index = max(index, 1), last + index # Fibonacci sequence

def plusOneProbe(           # Generator to probe by steps that grow
      start, key, size):    # linearly
   step = 1
   index = start
   for i in range(size):    # Loop over all possible cells
      yield index % size    # Yield current index, then increment
      index, step = step + index, step + 1 # by step and step by 1

def times5Probe(            # Generator to probe by steps following a
      start, key, size):    # geometric progression
   for i in range(size):    # Loop over all possible cells
      yield start % size    # Yield current index, then multiply
      start = 5 * start + 1 # by 5 and add 1

# Determine percentage of cells not visited by a probe method for all
# prime table sizes up to a limit
def missedCoverage(probe, upTo=100, key=0):
   size = 3
   result = []
   while size < upTo:
      if is_prime(size):
         visited = {i for i in probe(0, key, size)}
         missed = size - len(visited)
         result.append((size, missed / size))
      size += 2
   return result
   
class HashTable(object):    # A hash table using open addressing
   def __init__(            # The constructor takes the initial
         self, size=7,      # size of the table,
         hash=simpleHash,   # a hashing function,
         probe=linearProbe, # the open address probe sequence, and
         maxLoadFactor=0.5): # the max load factor before growing
      self.__table = [None] * size # Allocate empty hash table
      self.__nItems = 0     # Track the count of items in the table
      self.__hash = hash    # Store given hash function, probe
      self.__probe = probe  # sequence generator, and max load factor
      self.__maxLoadFactor = maxLoadFactor

   def __len__(self):       # The length of the hash table is the
      return self.__nItems  # number of cells that have items

   def cells(self):         # Get the size of the hash table in
      return len(self.__table) # terms of the number of cells

   def hash(self, key):     # Use the hashing function to get the
      return self.__hash(key) % self.cells() # default cell index

   def search(self,         # Get the value associated with a key
              key):         # in the hash table, if any
      i = self.__find(key)  # Look for cell index matching key
      return (None if (i is None) or # If index not found,
              self.__table[i] is None or # item at i is empty or 
              self.__table[i][0] != key # it has another key, return
              else self.__table[i][1]) # None, else return item value

   __Deleted = (None, 'Deletion marker') # Unique value for deletions
   
   def __find(self,         # Find the hash table index for a key
              key,          # using open addressing probes.  Find
              deletedOK=False): # deleted cells if asked
      for i in self.__probe(self.hash(key), key, self.cells()):
         if (self.__table[i] is None or # If we find an empty cell or
             (self.__table[i] is HashTable.__Deleted and # a deleted
              deletedOK) or # cell when one is sought or the
             self.__table[i][0] == key): # 1st of tuple matches key,
            return i        # then return index
      return None           # If probe ends, the key was not found

   def insert(self,         # Insert or update the value associated
              key, value):  # with a given key
      i = self.__find(      # Look for cell index matching key or an
         key, deletedOK=True) # empty or deleted cell
      if i is None:         # If the probe sequence fails,
         raise Exception(   # then the hash table is full
            'Hash table probe sequence failed on insert')
      if (self.__table[i] is None or # If we found an empty cell, or
          self.__table[i] is HashTable.__Deleted): # a deleted cell
         self.__table[i] = ( # then insert the new item there
            key, value)     # as a key-value pair
         self.__nItems += 1 # and increment the item count
         if self.loadFactor() > self.__maxLoadFactor: # When load
            self.__growTable() # factor exceeds limit, grow table
         return True        # Return flag to indicate item inserted
                            
      if self.__table[i][0] == key: # If first of tuple matches key,
         self.__table[i] = (key, value) # then update item
         return False       # Return flag to indicate update

   def loadFactor(self):    # Get the load factor for the hash table
      return self.__nItems / len(self.__table)
         
   def __growTable(self):   # Grow the table to accommodate more items
      oldTable = self.__table # Save old table
      size = len(oldTable) * 2 + 1 # Make new table at least 2 times
      while not is_prime(size): # bigger and a prime number of cells
         size += 2          # Only consider odd sizes
      self.__table = [None] * size # Allocate new table
      self.__nItems = 0     # Note that it is empty
      for i in range(len(oldTable)): # Loop through old cells and
         if (oldTable[i] and # insert non-deleted items by re-hashing
             oldTable[i] is not HashTable.__Deleted):
            self.insert(*oldTable[i]) # Call with (key, value) tuple

   def delete(self,         # Delete an item identified by its key
              key,          # from the hash table. Raise an exception
              ignoreMissing=False): # if not ignoring missing keys
      i = self.__find(key)  # Look for cell index matching key
      if (i is None or      # If the probe sequence fails or
          self.__table[i] is None or # cell i is empty or 
          self.__table[i][0] != key): # it's not the item to delete,
         if ignoreMissing:  # then item was not found.  Ignore it
            return          # if so directed
         raise Exception(   # Otherwise raise an exception
            'Hash table does not contain key {} so cannot delete'
            .format(key))
      self.__table[i] = HashTable.__Deleted # Mark table cell deleted
      self.__nItems -= 1    # Reduce count of items
      
   def traverse(self):      # Traverse the key, value pairs in table
      for i in range(len(self.__table)): # Loop through all cells
         if (self.__table[i] and # For those that contain undeleted
             self.__table[i] is not HashTable.__Deleted): # items
            yield self.__table[i] # yield them to caller

   def __str__(self):       # Convert table to a string representaion
      N = len(self.__table)
      out = '<HashTable of {} items'.format(self.__nItems)
      show = 5              # Number of cells to show at either end
      for i in range(min(show, N)): # First cells up to show - 1
         out += '\n  {:4d}-'.format(i)
         if self.__table[i]:
            out += '{}: {}'.format(*self.__table[i])
      if N > 2 * show:
         out += '\n  ...'
      for i in range(max(N - show, show), N): # Last cells up to N - 1
         out += '\n  {:4d}-'.format(i)
         if self.__table[i]:
            out += '{}: {}'.format(*self.__table[i])
      out += ' >'
      return out

   def tableString(self):   # Show the keys of all table cells as
      return '[{}]'.format(','.join( # a string
         ' ' if cell is None else # Empty cells are spaces, deleted
         'ø' if cell is HashTable.__Deleted else # cells are the null
         repr(cell[0])      # Otherwise use the string of the key
         for cell in self.__table))

   def peek(self, i):       # Peek at contents of cell i
      return self.__table[i]
