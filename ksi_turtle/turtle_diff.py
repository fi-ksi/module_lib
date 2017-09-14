"""
Evaluation script for turtle tasks.
Requires Pillow library (pip install Pillow) for working with images.
"""

from turtle import Turtle, getcanvas, resetscreen
from PIL import Image

# nastaveni
STUDENT_FILE_NAME = '/tmp/student.eps'
CORRECT_SOLUTION_FILE_NAME = 'correct-solution'
CORRECT_SOLUTION_COLOR_FILE_NAME = 'correct-solution-color'

# jak moc musi byt pixely alespon rozdilne, aby byl zapocitan rozdil
MIN_ALPHA_DELTA = 100
# kolik pixelu muze byt ruznych, aby byly obrazky povazovane za stejne
MAX_DIFFERENCE = 50


#def eps_to_png(name):
#    eps_name = name + '.eps'
#    png_name = name + '.png'
#    call(["convert", eps_name, png_name])

def load_image(name):
    #im = Image.open(name + '.png')
    # NOTE: PIL umi pracovat primo s EPS
    im = Image.open(name)
    alpha = im.split()[-1]
    values = alpha.load()
    width, height = im.size
    return values, width, height



# NOTE: pre_evaluation by stacilo spustit jen jednou (pred vsemi vyhodnocenimi)
def pre_evaluation():
    julie = Turtle()
    # vzorove reseni cerne
    store_image(julie, draw_solution, name=CORRECT_SOLUTION_FILE_NAME)
    # vzorove reseni cervene
    store_image(julie, draw_solution, name=CORRECT_SOLUTION_COLOR_FILE_NAME, color='#cc2233')


def compare_solutions():
    values1, width1, height1 = load_image(CORRECT_SOLUTION_FILE_NAME)
    values2, width2, height2 = load_image(STUDENT_FILE_NAME)
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



def main():
    # uloz vzorove reseni (cervene a cerne)
    pre_evaluation()
    ## zkonvertuj resitelovo reseni do  png
    #eps_to_png(STUDENT_FILE_NAME)
    # porovnej resitelovo reseni a vzorove reseni
    difference = compare_solutions()
    print(difference)
    if difference > MAX_DIFFERENCE:
        print('NOK')
    else:
        print('OK')