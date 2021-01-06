## Table of contents
* [General Info](#general-info)

## General Info

  This is the second challenge for GHGSat.
  It's a single python file which uses openCV to crop a ROI and detects matching points in them
  - to install dependencies :
  ``` pip freeze -r requirements ```
  - to run :
  ``` make run ```
  - or :
  ``` python ex2.py <path_to_img0> <path_to_img1> ```

  - to run the unittests:
  ``` make test ```
  - Sadly, I run out of time before getting cross compilation working.
  Since I chose to work with Python, I would have either assumed that the target machine has python and the appropriate dependencies (opencv, numpy), or make it use pip freeze.
  If not, I would have used Cpython to compile the program and link it statically with Python and its dependencies.
