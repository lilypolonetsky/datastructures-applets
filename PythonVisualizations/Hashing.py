import sys
import random

def encode_letter(letter):  # Encode letters a thru z as 1 thru 26
   letter = letter.lower()  # Treat uppercase as lower case
   if 'a' <= letter and letter <= 'z':
      return ord(letter) - ord('a') + 1
   return 0                 # Spaces and everything else are 0

def encode_word(word):      # Encode a word with the sum of its
   return sum(encode_letter(l) for l in word) # letter codes

def unique_encode_word_loop(word): # Encode a word uniquely using
   total = 0                # a loop to sum the letter codes times
   for i in range(len(word)): # a power of 27 based on their position
      total += encode_letter(word[i]) * 27 ** (len(word) - 1 - i)
   return total

def unique_encode_word(word): # Encode a word uniquely (abbreviated)
   return sum(encode_letter(word[i]) * 27 ** (len(word) - 1 - i)
              for i in range(len(word)))

def hashString1(key):       # Use Horner's method to hash a string
   total = 0                # Sum contribution of all characters
   for i in range(len(key) - 1, -1, -1): # Go in reverse order
      total = total * 256 + ord(key[i]) # Multiply by base, add char i
   return total             # Return sum

def hashString2(key):       # Use Horner's method to hash a string
   total = 0                # Sum contribution of all characters
   for i in range(len(key)): # Go in forward order
      total = (total << 8) + ord(key[i]) # Shift to mult., add char i
   return total             # Return sum

def hashString3(key, size): # Use Horner's method to hash a string
   total = 0                # Sum without overflowing
   for i in range(len(key)): # Go in forward order, shift, add char i
      total = ((total << 8) + ord(key[i])) % size # and use modulo
   return total             # Return sum

# Set up an empty array of random 64-bit values to be used by bitHash
# There will be a 64 bit field for every Unicode character
__maxUnicode = 0x10FFFF
__bitArray = [0] * (__maxUnicode + 1)
__64bits = (1 << 64) - 1
__16bits = (1 << 16) - 1

# Seed the random number generator to produce repeatable results
# random.seed("bitHash random numbers") 

for i in range(len(__bitArray)): # Fill the bit array with random
    __bitArray[i] = random.getrandbits(64) # 64-bit sequences

def bitHash(key, h=0):      # Hash an arbitrary key into 64 bits
   if isinstance(key, str): # by rotating and xor'ing bits
      for c in key:         # Exclusive-or rotated hash with bits
         h = (((h << 1) | (h >> 63)) ^ # from string character
               __bitArray[ord(c)]) & __64bits # keeping 64 bits
   elif isinstance(key, int): # Exclusive-or bits of integers
      h = (((h << 1) | (h >> 63)) ^ # by hashing 16-bit fields 
           __bitArray[key & __16bits])
      if key > __16bits:    # If there are more bits, recursively
         h = bitHash(key >> 16, h) # combine them
   elif key is True:        # Hash True and False like 1 and 0
      h = __bitArray[1]
   elif key is False:
      h = __bitArray[0]
   elif isinstance(key, (list, tuple)): # For sequences, apply
      for elem in key:      # the hashing over the whole sequence
         h = bitHash(elem, h)
   return h

#__bigPrime = 412670427844921037470771 # 79 bits = 0x5762e8a1d752ba9cbc33
#__highBits = __bigPrime >> 64
__bigPrime = 1111111111111111111 # 60 bits = 0xf6b75ab2bc471c7
__salt = 777767777 # Another prime

def multiplicativeHash(key, h=0): # Hash an arbitrary key into 64 bits
   if isinstance(key, str): # by rotating and xor'ing bits
      for c in key:         # Exclusive-or rotated hash with bits
         h = (((h << 1) | (h >> 63)) ^ # from string character times
               (__bigPrime * ord(c) + __salt) # prime plus bits
              & __64bits)   # keeping 64 bits
   elif isinstance(key, int): # Exclusive-or bits of integers
      h = (((h << 1) | (h >> 63)) ^ # after multiplying with a big
           (__bigPrime * key + __salt)) # prime and adding bits
   elif key in (True, False):  # Hash True and False like 1 and 2
      h = (((h << 1) | (h >> 63)) ^
           (__bigPrime * (1 if key else 2) + __salt))
   elif isinstance(key, (list, tuple, set)): # For sequences, apply
      for elem in key:      # the hashing over the whole sequence
         h = multiplicativeHash(elem, h)
   return h

def is_prime(N):            # Determine if an integer is prime
   if N < 2 or (N > 2 and N % 2 == 0): # If N is small or even
      return False          # then it's not prime
   # The upper bound of possible factors is the square root of N
   top = int(pow(N, 0.5) + 1)
   factor = 3               # Start factor testing at 3
   while factor < top:      # While there are more factors to check,
      if N % factor == 0:   # test if factor divides N evenly
         return False       # If so, then N is not prime
      factor += 2           # Otherwise check next odd factor
            
   return True              # No factors found, so N is prime

def quadraticProbeCoverage(maxArraySize=555, minArraySize=5, step=1):
   """Determine number of array cells visited by quadratic probing
   for every array size within a range.
   Returns a 3-tuple for each array size: (size, ratio_visited, is_prime)
   """
   return [(size, len({i ** 2 % size for i in range(5 * size)}) / size,
            is_prime(size))
           for size in range(minArraySize, maxArraySize + 1, step)]
