from turtle_sandbox import Turtle

j = Turtle()
j.fd(100)
j.right(90)
j.fd(100)
j.write("a.txt")

from turtle_eval import *
from turtle import Turtle, turtles, getcanvas
a = Turtle()
interpret_turtle("a.txt", a)
canvas = getcanvas()
canvas.postscript(file='student.eps')