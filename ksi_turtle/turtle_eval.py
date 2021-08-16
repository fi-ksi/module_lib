import sys
from turtle import Turtle, getcanvas, resetscreen, screensize
from PIL import Image, ImageOps

MIN_ALPHA_DELTA = 100


def load_image(name):
    #im = Image.open(name + '.png')
    # NOTE: PIL umi pracovat primo s EPS
    im = Image.open(name)
    alpha = im.split()[-1]
    values = alpha.load()
    width, height = im.size
    return values, width, height

def store_current_image(name):
    canvas = getcanvas()
    canvas.postscript(file=name, width=1150, x=-1150/2, height=700, y=-700/2)
    #eps_to_png(name)

def store_image(turtle, drawing_function, name, color=None):
    resetscreen()
    screensize(800, 600)
    turtle.hideturtle()
    turtle.speed(0)
    turtle.pensize(3)
    if color:
        turtle.pencolor(color)
    drawing_function(turtle)
    store_current_image(name)



def combine_images(front, back, result):
    f = Image.open(front)
    b = Image.open(back)
    b.paste(f, (0, 0), ImageOps.invert(f.split()[-1]))
    b.save(result)

def interpret_turtle(file, turtle):
    turtle.speed(0)
    if not isinstance(file, list):
        f = open(file, "r")
        lines = f.readlines()
        f.close()
    else:
        lines = file

    for line in lines:
        s = line.split(" ")
        if s[4] == "fd":
            turtle.fd(float(s[5]))
        elif s[4] == "rt":
            turtle.rt(float(s[5]))
        elif s[4] == "goto":
            turtle.goto(float(s[5]), float(s[6]))
        elif s[4] == "seth":
            turtle.goto(float(s[5]), float(s[6]))
        elif s[4] == "home":
            turtle.home()
        elif s[4] == "pendown":
            turtle.pendown()
        elif s[4] == "penup":
            turtle.penup()

def compare_solutions(student, solution):
    values1, width1, height1 = load_image(student)
    values2, width2, height2 = load_image(solution)
    assert width1 == width2 and height1 == height2, 'Obrazky nejsou stejne velke!'
    difference = 0
    for x in range(width1):
        for y in range(height1):
            key = (x, y)
            value1 = values1[key]
            value2 = values2[key]
            delta = abs(value1 - value2)
            if delta >= MIN_ALPHA_DELTA:
                difference += 1
    return difference
