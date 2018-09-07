# TOBB ETU Lab Placement Tool

For assistants (like me:)), lab placement of student will be easier:)

Usage

1. Fill config.ini file properly
2. Run code with
```
python tobbetu_lab_placement_tool.py config.ini
```

 It uses selenium and chrome driver to fetch data from http://ubs.etu.edu.tr
 
 Places students into given lab section using greedy approach
 
 ```
 BİL 212
[('Çarşamba', 14), ('Çarşamba', 15)] --> 29
[('Çarşamba', 12), ('Çarşamba', 13)] --> 28
Garbage Slot Length: 0 --> []


Yey! No more student left to place \m/


Student list save in ../output/BİL 212_placement.csv
```
