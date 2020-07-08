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

Find int in array*:find button disabled and sort continued: find button disabled 
and sort continued

Find int not in array*:find button disabled and sort continued: find button disabled
and sort continued

Sort after find int in array: items sorted: items sorted

Sort after find int not in array: items sorted: items sorted

Find int in sorted array: int found: int found 

Find int not in sorted array: int not found: int not found 

Find int with leading 0('s) (i.e. 0007) in array*: find button disabled and sort
continued: find button disabled and sort continued

Find int with leading 0('s) (i.e. 020) not in array*: find button disabled and 
sort continued: find button disabled and sort continued

Find int with more than 2 digits*: find button disabled and sort continued: 
find button disabled and sort continued

Find non-ints*: unable to type, sort continued: unable to type, sort continued



Category 5: Insert 

Insert int less than the highest int in array*: insert button disabled and sort
continued: insert button disabled and sort continued 

Insert int greater than the highest int in array*: insert button disabled and
sort continued: insert button disabled and sort continued

Insert int into sorted array: int inserted: int inserted

Sort after insert: items sorted: items sorted

Insert int with leading 0('s) (i.e. 0018)*: insert button disabled and sort 
continued: insert button disabled and sort continued

Insert int with more than 2 digits*: insert button disabled and sort continued: 
insert button disabled and sort continued 

Insert non-ints*: unable to type, sort continued: unable to type, sort continued



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

Delete Rightmost before Bubble sort: items sorted: items sorted

Delete Rightmost after Bubble sort: deleted rightmost item: deleted rightmost item


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

Find int in array*: find button disabled and sort continued: find button disabled
and sort continued

Find int not in array*: find button disabled and sort continued: find button
disabled and sort continued

Sort after find int in array: items sorted: items sorted

Sort after find int not in array: items sorted: items sorted

Find int in sorted array: int found: int found 

Find int not in sorted array: int not found: int not found 

Find int with leading 0('s) (i.e. 0021) in array*: find button disabled and sort
continued: find button disabled and sort continued

Find int with leading 0('s) (i.e. 0001) not in array*: find button disabled and
sort continued: find button disabled and sort continued

Find int with more than 2 digits*: find button disabled and sort continued: find
button disabled and sort continued

Find non-ints*: unable to type, sort continued: unable to type, sort continued 



Category 5: Insert

Insert int less than the highest int in array*: insert button disabled and sort
continued: insert button disabled and sort continued 

Insert int greater than the highest int in array*: insert button disabled and sort
continued: insert button disabled and sort continued

Insert int into sorted array: int inserted: int inserted

Sort after insert: items sorted: items sorted

Insert int with leading 0('s) (i.e. 0003)*: insert button disabled and sort 
continued: insert button disabled and sort continued

Insert int with more than 2 digits*: insert button disabled and sort continued:
insert button disabled and sort continued

Insert non-ints*: unable to type, sort continued: unable to type, sort continued 



Category 6: Speed Switches 

Middle speed: sort occurs at intermediate speed, items sorted: sort occurs at 
intermediate speed, items sorted

Slow speed: sort occurs slowly, items sorted: sort occurs slowly, items sorted

Fast speed: sort occurs fast, items sorted: sort occurs fast, items sorted 



Category 7: Pause/Play/Stop/Delete Rightmost buttons

Pause: sort paused: sort paused

Play: sort begins from point it was paused: sort begins from point it was paused

Stop: sort stopped: sort stopped  

Delete Rightmost before Selection sort: items sorted: items sorted

Delete Rightmost after Selection sort: deleted rightmost item: deleted rightmost item


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

Find int in array*: find button disabled and sort continued: find button disabled
and sort continued

Find int not in array*: find button disabled and sort continued: find button 
disabled and sort continued

Sort after find int in array: items sorted: items sorted 

Sort after find int not in array: items sorted: items sorted

Find int in sorted array: int found: int found 

Find int not in sorted array: int not found: int not found 

Find int with leading 0('s) (i.e. 0014) in array*: find button disabled and sort
continued: find button disabled and sort continued

Find int with leading 0('s) (i.e. 0012) not in array*: find button disabled and 
sort continued: find button disabled and sort continued

Find int with more than 2 digits*: find button disabled and sort continued: find
button disabled and sort continued

Find non-ints*: unable to type, sort continued: unable to type, sort continued 



Category 5: Insert 

Insert int less than the highest int in array*: insert button disabled and sort
continued: insert button disabled and sort continued 

Insert int greater than the highest int in array*: insert button disabled and sort
continued: insert button disabled and sort continued

Insert int into sorted array: int inserted: int inserted

Sort after insert: items sorted: items sorted

Insert int with leading 0('s) (i.e. 0007)*: insert button disabled and sort 
continued: insert button disabled and sort continued 

Insert int with more than 2 digits*: insert button disabled and sort continued: 
insert button disabled and sort continued 

Insert non-ints*: unable to type, sort continued: unable to type, sort continued



Category 6: Speed Switches

Middle speed: sort occurs at intermediate speed, items sorted: sort occurs at 
intermediate speed, items sorted

Slow speed: sort occurs slowly, items sorted: sort occurs slowly, items sorted 

Fast speed: sort occurs fast, items sorted: sort occurs fast, items sorted 



Category 7: Pause/Play/Stop/Delete Rightmost 

Pause: sort paused: sort paused

Play: sort begins from point it was paused: sort begins from point it was paused

Stop: sort stopped: sort stopped and array is altered**

Delete Rightmost before Insertion sort: items sorted: items sorted

Delete Rightmost after Insertion sort: deleted rightmost item: deleted rightmost item


*clicked on during Bubble/Selection/Insertion sort

**During Insertion sort the int stored as temp needs to be re-inserted into its 
correct position in the array, so specific ints in the array shift over to the 
right one by one to make room for it. 

When stop is clicked during a shift, the int being shifted which currently appears
as a duplicate in the array, remains a duplicate in the array. The int stored as
temp remains above the array and will dissapear when another animation is started.

If stop is clicked at a moment when an int is shifting and one of the duplicates
is in a position in between boxes, the duplicate gets stuck in that position and
will stay there during any subsequent animations.



'''