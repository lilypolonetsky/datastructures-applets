'''
End-user tests for Simple Sorting:

Tested:Expected Result:Result

################################################################################
Tests for Bubble sort:
Category 1: Array Size 
Empty array (size 0): no sort occurred: no sort occurred 
Single array (size 1): no sort occurred: no sort occurred  
Default array (size 10): items sorted: items sorted 
Smaller array (size 5): items sorted: items sorted 
Larger array (size 15): items sorted: items sorted 

Category 2: Sorted Array
Sorted array: sort attempted (no swaps): sort attempted (no swaps)

Category 3: Duplicates 
Array with duplicate and unique ints: stable sort (the preceding int does not 
get passed over/swapped with its succeeding duplicate): stable sort
Array with the same int: sort attempted (no swaps): sort attempted (no swaps)
Array only with duplicates: stable sort: stable sort 

Category 4: Find 
Find int in array*: sort stopped, int found: sort stopped, int found
Find int not in array*: sort stopped, int not found: sort stopped, int not found 
Sort after find int in array*: items sorted: (sort starts from beginning), 
items sorted
Sort after find int not in array*: items sorted: (sort starts from beginning) 
items sorted
Find int in sorted array: int found: int found 
Find int not in sorted array: int not found: int not found 
Find int with leading 0('s) (i.e. 0007) in array*: sort stopped, int found: sort 
stopped, int found
Find int with leading 0('s) (i.e. 020) not in array*: sort stopped, int not found:
sort stopped, int not found
Find int with more than 2 digits*: error message, sort continues: error message,
sort continues
Find non-ints*: unable to type, sort continues: unable to type, sort continues

Category 5: Insert 
Insert int less than the highest int in array*: int inserted, sort stopped: int 
inserted, sort stopped**
Insert int greater than the highest int in array*: int inserted, sort stopped: 
int inserted, sort stopped**
Sort after insert: items sorted: items sorted
Insert int with leading 0('s) (i.e. 0018)*: int inserted, sort stopped: int 
inserted, sort stopped
Insert int with more than 2 digits*: error message, sort continues: error message, 
sort continues 
Insert non-ints*: unable to type, sort continues: unable to type, sort continues 

Category 6: Speed Switches
Middle speed: sort occurs at intermediate speed, items sorted: sort occurs at 
intermediate speed, items sorted
Slow speed: sort occurs slowly, items sorted: sort occurs slowly, items sorted
Fast speed: sort occurs fast, items sorted: sort occurs fast, items sorted

Category 7: Pause/Play/Stop/Delete Rightmost buttons 
Pause: sort paused: sort paused
Play: sort begins from point it was paused: sort begins from point it was 
paused
Stop: sort stopped: sort stopped 
Delete Rightmost (applied before/after Bubble sort): sort works/items sorted: 
sort works/items sorted

 
**if insert occured when the Bubble sort was up to a pair that needed to be 
swapped (i.e. 28 followed by 8), the insert took place followed by the swapping 
of the two ints and then the sort stopped. Otherwise, if the sort was interrupted 
at a pair that didn't need to be swapped, the insert took place and sort stopped

################################################################################
Tests for Selection sort:
Category 1: Array Size 
Empty array: no sort occurred: no sort occurred 
Single array: no sort occurred: no sort occurred 
Default array (size 10): items sorted: items sorted 
Smaller array (size 5): items sorted: items sorted 
Larger array (size 15): items sorted: items sorted 

Category 2: Sorted Array
Sorted array: sort attempted (no swaps): sort attempted (no swaps) 

Category 3: Duplicates
Array with duplicate and unique ints: unstable sort (the preceding int can be 
passed over/swapped with its succeeding duplicate in the array): unstable sort 
Array with the same int: sort attempted (no swaps): sort attempted (no swaps)
Array only with duplicates: unstable sort: unstable sort 

Category 4: Find 
Find int in array*: sort stopped, int found: sort stopped, int found 
Find int not in array*: sort stopped, int not found: sort stopped, int not found
Sort after find int in array*: items sorted: (sort starts from beginning), 
items sorted
Sort after find int not in array*: items sorted: (sort starts from beginning),  
items sorted
Find int in sorted array: int found: int found 
Find int not in sorted array: int not found: int not found 
Find int with leading 0('s) (i.e. 0021) in array*: sort stopped, int found: sort
stopped, int found
Find int with leading 0('s) (i.e. 0001) not in array*: sort stopped, int not found:
sort stopped, int not found 
Find int with more than 2 digits*: error message, sort continues: error message, 
sort continues 
Find non-ints*: unable to type, sort continues: unable to type, sort continues 

Category 5: Insert
Insert int less than the highest int in array*: sort stopped, int inserted: sort
stopped, int inserted 
Insert int greater than the highest int in array*: sort stopped, int inserted:
sort stopped, int inserted **Exception in Tkinter callback, IndexError: list index
out of range) 
Sort after insert: items sorted: items sorted
Insert int with leading 0('s) (i.e. 0003)*: sort stopped, int inserted: sort 
stopped, int inserted **IndexError: list index out of range
Insert int with more than 2 digits*: error message, sort continues: error 
message, sort continues
Insert non-ints*: unable to type, sort continues: unable to type, sort continues 

Category 6: Speed Switches 
Middle speed: sort occurs at intermediate speed, items sorted: sort occurs at 
intermediate speed, items sorted
Slow speed: sort occurs slowly, items sorted: sort occurs slowly, items sorted 
**screen froze
Fast speed: sort occurs fast, items sorted: sort occurs fast, items sorted 

Category 7: Pause/Play/Stop/Delete Rightmost buttons
Pause: sort paused: sort paused
Play: sort begins from point it was paused: sort begins from point it was paused
Stop: sort stopped: sort stopped  
Delete Rightmost (applied before/after Selection sort): sort works/items sorted:
sort works/items sorted

**Errors

################################################################################
Tests for Insertion sort:
Category 1: Array Size 
Empty array: no sort occurred: no sort occurred
Single array: no sort occurred: no sort occurred
Default array (size 10): items sorted: items sorted  
Smaller array (size 5): items sorted: items sorted 
Larger array (size 15): items sorted: items sorted

Category 2: Sorted array
Sorted array: sort attempted (no swaps): sort attempted (no swaps) 

Category 3: Duplicates
Array with duplicate and unique ints: stable sort: stable sort   
Array with the same int: sort attempted (no swaps): sort attempted (no swaps)
Array only with duplicates: stable sort: stable sort 

Category 4: Find
Find int in array*: sort stopped, int found: sort stopped**, int found
Find int not in array*: sort stopped, int not found: sort stopped, int not found
Sort after find int in array*: items sorted: (sort starts from beginning), items 
sorted 
Sort after find int not in array*: items sorted: (sort starts from beginning),  
items NOT sorted**
Find int in sorted array: int found: int found 
Find int not in sorted array: int not found: int not found 
Find int with leading 0('s) (i.e. 0014) in array*: sort stopped, int found: sort
stopped, int found
Find int with leading 0('s) (i.e. 0012) not in array*: sort stopped, int not found:
sort stopped, int not found 
Find int with more than 2 digits*: error message, sort continues: error message, 
sort continues 
Find non-ints*: unable to type, sort continues: unable to type, sort continues 

Category 5: Insert 
Insert int less than the highest int in array*: sort stopped, int inserted: sort
stopped, int inserted 
Insert int greater than the highest int in array*: sort stopped, int inserted:
sort stopped, int inserted **Exception in Tkinter callback
Sort after insert: items sorted: items sorted
Insert int with leading 0('s) (i.e. 0007)*: sort stopped, int inserted: sort 
stopped, int inserted **duplication of an int in array
Insert int with more than 2 digits*: error message, sort continues: error 
message, sort continues
Insert non-ints*: unable to type, sort continues: unable to type, sort continues 

Category 6: Speed Switches
Middle speed: sort occurs at intermediate speed, items sorted: sort occurs at 
intermediate speed, items sorted
Slow speed: sort occurs slowly, items sorted: sort occurs slowly, items sorted 
Fast speed: sort occurs fast, items sorted: sort occurs fast, items sorted 

Category 7: Pause/Play/Stop/Delete Rightmost 
Pause: sort paused: sort paused
Play: sort begins from point it was paused: sort begins from point it was paused
Stop: sort stopped: sort stopped  
Delete Rightmost (applied before/after Insertion sort): sort works/items sorted:
sort works/items sorted


**When the sort was interrupted by doing a find, an int was frozen out of its 
slot and the sort continued for a bit, the int was found and sort stopped. The 
int that was frozen out of its slot moved above the array and stayed there. 
Exception in Tkinter callback. In another case, when interrupting the sort with 
a find, the first element in the array disapears and when you do the sort again
it doesn't sort the array completely. 


*clicked on during Bubble/Selection/Insertion sort
'''