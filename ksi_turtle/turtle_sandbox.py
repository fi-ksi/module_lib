######### Replacement for turtle library ##########
# -*- coding: utf-8 -*-
import sys
import math

KSI_TURTLE_8kl = []

def KSI_WRITE_8kl(filename: str = None) -> str:
    answer_list = ["\n#KSI_META_OUTPUT_0a859a#"]
    for t in KSI_TURTLE_8kl:
        answer_list.append((" ".join(str(x) for x in t)))

    answer_str = "\n".join(answer_list)
    if filename is None:
        print(answer_str)
    else:
        with open(filename, "w") as f:
            f.write(answer_str)

    return answer_str



def done():
    pass

## taken from oficial source code
class Vec2D(tuple):
    """A 2 dimensional vector class, used as a helper class
    for implementing turtle graphics.
    May be useful for turtle graphics programs also.
    Derived from tuple, so a vector is a tuple!

    Provides (for a, b vectors, k number):
       a+b vector addition
       a-b vector subtraction
       a*b inner product
       k*a and a*k multiplication with scalar
       |a| absolute value of a
       a.rotate(angle) rotation
    """
    def __new__(cls, x, y):
        return tuple.__new__(cls, (x, y))
    def __add__(self, other):
        return Vec2D(self[0]+other[0], self[1]+other[1])
    def __mul__(self, other):
        if isinstance(other, Vec2D):
            return self[0]*other[0]+self[1]*other[1]
        return Vec2D(self[0]*other, self[1]*other)
    def __rmul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return Vec2D(self[0]*other, self[1]*other)
    def __sub__(self, other):
        return Vec2D(self[0]-other[0], self[1]-other[1])
    def __neg__(self):
        return Vec2D(-self[0], -self[1])
    def __abs__(self):
        return (self[0]**2 + self[1]**2)**0.5
    def rotate(self, angle):
        """rotate self counterclockwise by angle
        """
        perp = Vec2D(-self[1], self[0])
        angle = angle * math.pi / 180.0
        c, s = math.cos(angle), math.sin(angle)
        return Vec2D(self[0]*c+perp[0]*s, self[1]*c+perp[1]*s)
    def __getnewargs__(self):
        return (self[0], self[1])
    def __repr__(self):
        return "(%.2f,%.2f)" % self


class Turtle:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.dir = 0
        self.units = "d"
        self.mode = "s"
        self.pen = "d"

    def to_radians(self, units):
        if self.units == "d":
            return math.radians(units)
        return unit

    def to_degrees(self, unit):
        if self.units == "r":
            return math.degrees(unit)
        return unit

    def to_standard(self, angle):
        if self.mode == "s":
            return angle
        return angle - math.radians(90)

    def to_logo(self, angle):
        if self.mode == "m":
            return angle
        return angle + math.radians(90)

    def forward(self, step):
        self.x += step * math.sin(self.dir)
        self.y += step * math.cos(self.dir)
        KSI_TURTLE_8kl.append((self.x, self.y, self.dir, self.pen, "fd", step))

    def back(self, distance):
        self.forward(-distance)

    def right(self, angle):
        self.dir -= self.to_radians(angle)
        KSI_TURTLE_8kl.append((self.x, self.y, self.dir, self.pen, "rt", self.to_degrees(angle)))

    def left(self, angle):
        self.right(-angle)

    def goto(self, x, y=None):  # accepts either: tuple (x, y), or two parameters x and y
        if y is None:
            self.x = x[0]
            self.y = x[1]
        else:
            self.x = x
            self.y = y
        KSI_TURTLE_8kl.append((self.x, self.y, self.dir, self.pen, "goto", self.x, self.y))

    def setx(self, x):
        self.goto(x, self.y)

    def sety(self, y):
        self.goto(self.x, y)

    def setheading(self, angle):
        self.dir = self.to_standard(self.to_radians(angle))
        KSI_TURTLE_8kl.append((self.x, self.y, self.dir, self.pen, "seth", self.to_degrees(self.angle)))  # todo: self.angle doesn't exist

    def home(self):
        self.x = self.y = 0
        if self.mode == "s":
            self.dir = 0
        else:
            self.dir = 90
        KSI_TURTLE_8kl.append((self.x, self.y, self.dir, self.pen, "home"))

    def circle(self, radius, extent=None, steps=None):
        # ToDo
        pass

    def dot(self, size=None, *color):
        # ToDo
        pass

    def stamp(self):
        # ToDo
        pass

    def clearstamp(self, stamp_id):
        # ToDo
        pass

    def clearstamps(self, n=None):
        # ToDo
        pass

    def undo(self):
        tmp = KSI_TURTLE_8kl.pop()
        self.x = tmp[0]
        self.y = tmp[1]
        self.dir = tmp[2]
        self.pen = tmp[3]

    def speed(self, speed=None):
        pass

    def position(self):
        return Vec2D(self.x, self.y)

    def towards(self, x, y):
        # ToDo
        pass

    def xcor(self):
        return self.x

    def ycor(self):
        return self.y

    def heading(self):
        if self.mode == "s":
            if self.units == "d":
                return math.degrees(self.dir)
            return self.dir
        else:
            if self.units == "d":
                return math.degrees(self.dir) - 90
            return self.dir - math.radians(90)

    def distance(self, x, y=None):
        if y is None:
            y = x[1]
            x = x[0]
        dx = self.x - x
        dy = self.y - y
        return math.sqrt(dx*dx + dy*dy)

    def degrees(self):
        self.units = "d"

    def radians(self):
        self.units = "r"

    def pendown(self):
        self.pen = "d"
        KSI_TURTLE_8kl.append((self.x, self.y, self.dir, self.pen, "pendown"))

    def penup(self):
        self.pen = "u" 
        KSI_TURTLE_8kl.append((self.x, self.y, self.dir, self.pen, "penup"))

    def pensize(self, width=None):
        # ToDo
        pass

    def pen(self, pen=None, **pendict):
        # ToDo
        pass

    def isdown(self):
        return self.pen == "d"

    # aliases
    fd = forward
    bk = back
    backward = back
    rt = right
    lt = left
    setpos = goto
    setposition = goto
    seth = setheading
    pos = position
    pd = pendown
    down = pendown
    pu = penup
    up = penup
    width = pensize

######## End of turtle library remplacement #######