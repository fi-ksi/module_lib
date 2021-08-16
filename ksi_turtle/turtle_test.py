#!/usr/bin/env python3
from typing import Optional

from .turtle_sandbox import Turtle, KSI_WRITE_8kl

turtle_txt = 'tmp/a.txt'
eps_file = 'tmp/student.eps'
png_file: Optional[str] = 'tmp/student.png'  # this conversion requires ghostscript binary. If you want to skip this step, set this variable to None.


j = Turtle()
j.fd(100)
j.right(90)
j.fd(100)
# j.write(turtle_txt)
KSI_WRITE_8kl(turtle_txt)

from .turtle_eval import *
from turtle import Turtle, turtles, getcanvas
a = Turtle()
interpret_turtle(turtle_txt, a)
canvas = getcanvas()
canvas.postscript(file=eps_file)

if png_file:
    convert_eps_to_png(eps_file, png_file)
