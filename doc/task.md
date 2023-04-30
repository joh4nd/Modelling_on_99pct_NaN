# Rebel Rescue

## The Problem
Due to an imminent super-nova, we need to extract our rebels from the affected region of
space-time! Unfortunately, we need to know their space-time positions for 1000 galactic
time units for the space-time extractor to properly lock on to them…

**Your Mission:** Using *only* their publicly broadcasted messages, please provide us with the
(x,y,z,uncertainty) of *each* of our rebels for *all* times from 1-1000.

**Given:** 10 previous (similar) rebel travel patterns, and the corresponding “truth” information
for you to build your algorithm/model.

## Assignment Content

**out/** 
 - 10 previous travel patterns in similar space-time 
   - 00??_truth.txt: full information on space-time contents, and rebel movements
   - 00??_public.txt: only the publicly available messages emitted by rebels
   - The “real” assignment contents:
     - assignment_public.txt : only the publicly available messages emitted by rebels
   - A sample solution for 0001_{public,truth}.txt
     - sample_answer.txt
     
**python/**
 - Some helper scripts and notebooks to help in parsing, and grade your submission

## The World

- The Universe:
  - Dimensions: 1000 x 1000 x 1000
  - Stars: ~4000, some as part of star clusters, some isolated
- The Time:
  - All data is for times between 0-1000, in Galactic Standard Time Units
- The Rebels:
  - ~30 present at any given time 
  - Travel in rebel teams aboard star-ships travelling between the stars
- Public Messages:
  - Our rebels occasionally emit one of three types of messages which we hope to use to ﬁnd
their positions

## The Rebels

Rebels travel aboard (un-named) ships with their teammates between the stars, and star
clusters. Rebels never enter or leave the universe, and do not change, or otherwise leave
ships. All rebel names are *unique* for this exercise.

Rebel team movements are *not completely* random...which is a hint...

### Rebel Types:
- Three "ﬂavours" of rebel. Each ﬂavour emits a different type of public message:
  - **NEA:** Emits the name of the closest star (stars unfortunately have un-imaginative names)
  - **COT:** Emits the name of a co-traveller (somebody on board the same ship)
  - **LOC:** Emits their current location (with some unknown resolution)

## The Solution

Make a text ﬁle (see out/sample_answer.txt) with the following contents (space
separated between columns):

```<time> <rebel> <x> <y> <z> <uncertainty>```

Do this for every rebel, for every time (you can omit entries where you feel you do not have enough information)

## The Helpers

We've supplied a few notebooks and scripts to help you parse the output, and visualize the truth
information. You should not need to make your own .txt parser, but may want to change how the
dataframes are laid out. You are not forced to use anything we provide :)

- python/ directory
  - rebel_decode.py : The muscle power behind the notebooks. Feel free to extend or alter.
  - truth_plotter.ipynb : Start here. Gives some feeling behind the truth data, and some
dataframes to play around with. Reads *_truth.txt ﬁles as input
  - public_plotter.ipynb : Parses the public rebel broadcasts and returns some dataframes
you can use. Also plots the location of the LOC ﬂavour of leaks for simple inspection as an example.
Reads *_public.txt ﬁles as input.
  - grade_assignment.ipynb : reads your solution, along with the truth file and provides a score. Very slow.
    - If not using notebooks, you can also just call grade_assignment() directly in rebel_decode.py


## Grading

Submit your .txt file answer as outlined above, along with your code you used to make the
model/algorithm. You may also provide another small file with comments or explanations.

More points for more accurate answers

More points for more precise answers

While not part of the scored solution, some interesting items in case you want to look at
other things (and may help in constructing your scored assignment):
- How many ships are there in the graded assignment?
- List all passengers of each ship in the graded assignment
- What type of leaks are most common?
- Are public message leak rates independent of time/position?
  - If not, can you determine the analytical function that govern the rates?
- We said rebel movements are not completely random. Is this true?

## Requirements
 - Using the python utility script: python3, pandas, scipy, numpy
 - (Optional) Using the jupyter notebooks: jupyterlab and plotly extension (plotly.com/python/getting-started/#jupyterlab-support)

Otherwise, feel free to use any language, tools, or frameworks you feel comfortable with.