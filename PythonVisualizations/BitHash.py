
import random

# setup a list of random 64-bit values to be used by BitHash
__bits = [0] * (64*1024)
__rnd = random.Random()

# seed the generator to produce repeatable results
__rnd.seed("BitHash random numbers") 

# fill the list
for i in range(64*1024): 
    __bits[i] = __rnd.getrandbits(64)

def BitHash(s, h = 0):
    for c in s: 
        h  = (((h << 1) | (h >> 63)) ^ __bits[ord(c)]) 
        h &= 0xffffffffffffffff
    return h

# this function causes subsequent calls to BitHash to be
# based on a new set of random numbers. This is useful
# in the event that client code needs a new hash function,
# for example, for Cuckoo Hashing. 
def ResetBitHash():
    global __bits
    for i in range(64*1024): 
        __bits[i] = __rnd.getrandbits(64)   


def __main():
    # use BitHash to get two hash values for each of a bunch of strings
    # and print them out.
    v1 = BitHash("foo");  v2 = BitHash("foo", v1);  print(v1, v2)
    v1 = BitHash("bar");  v2 = BitHash("bar", v1);  print(v1, v2)
    v1 = BitHash("baz");  v2 = BitHash("baz", v1);  print(v1, v2)
    v1 = BitHash("blat"); v2 = BitHash("blat", v1); print(v1, v2)
    
    # now reset BitHash so that it is effectively 
    # a new hash function, and print out the hash values
    # for the same words.
    print("\nresetting BitHash to new hash function\n")
    ResetBitHash()
    
    v1 = BitHash("foo");  v2 = BitHash("foo", v1);  print(v1, v2)
    v1 = BitHash("bar");  v2 = BitHash("bar", v1);  print(v1, v2)
    v1 = BitHash("baz");  v2 = BitHash("baz", v1);  print(v1, v2)
    v1 = BitHash("blat"); v2 = BitHash("blat", v1); print(v1, v2)

    # now reset BitHash again so that it is effectively 
    # yet another hash function, and print out the hash values
    # for the same words.
    print("\nresetting BitHash to yet another hash function\n")
    ResetBitHash()
    
    v1 = BitHash("foo");  v2 = BitHash("foo", v1);  print(v1, v2)
    v1 = BitHash("bar");  v2 = BitHash("bar", v1);  print(v1, v2)
    v1 = BitHash("baz");  v2 = BitHash("baz", v1);  print(v1, v2)
    v1 = BitHash("blat"); v2 = BitHash("blat", v1); print(v1, v2)

    
                        
if __name__ == '__main__':
    __main()       
                
                       

