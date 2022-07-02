import displayio
from adafruit_matrixportal.matrix import Matrix
import adafruit_lis3dh
import board
import time
from adafruit_display_text.scrolling_label import ScrollingLabel
import terminalio
i2c = board.I2C()
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19)
lis3dh.range = adafruit_lis3dh.RANGE_2_G
matrix_width = 64
matrix_height = 32
matrix = Matrix(width=matrix_width, height=matrix_height, bit_depth=6)
display = matrix.display
marble_coords = [[2, 7], [3, 7], [3, 8], [3, 6], [4, 7]]
goal_coords = [[30,15],[29,15],[28,15],[29,16],[29,14]]
bitmap1 = displayio.Bitmap(32, 32, 3)
bitmap2 = displayio.Bitmap(32, 32, 3)
palette = displayio.Palette(4)
palette[0] = 0x000000 # BLANK BITS=
palette[1] = 0x3459eb # MARBLE - BLUE/GREEN
palette[2] = 0xeb34e5 # GOAL - GREEEN
palette[3] = 0x730dd9 # MAZE WALLS - BLUE

def color_bits(coord, index):
    x = int(coord[0])
    y = int(coord[1])
    if x > 31:
        x = x - 32
        bitmap2[x,y] = index
    else:
        bitmap1[x,y] = index
#BORDERS
for n in range(32): 
    bitmap1[n, 0] = 3
    bitmap1[n, 31] = 3
    bitmap1[0, n] = 3
    bitmap2[n, 0] = 3
    bitmap2[n, 31] = 3
    bitmap2[31, n] = 3

#MAZES

for n in range(20):
    color_bits([6, n+5], 3)
    color_bits([n+10, 20], 3)
    color_bits([n+6, 25], 3)
    color_bits([35, n+5],3)
    color_bits([40, n+5],3)

for n in range(5):
    color_bits([n+6, 5],3)
    color_bits([n+16, 5],3)
    color_bits([40, n+25],3)

for n in range(10):
    color_bits([11,n+5],3)
    color_bits([50,n+21],3)
    color_bits([15,n+5],3)
    color_bits([15,n+5],3)
    color_bits([n+20,10],3)
    color_bits([30,n+1],3)
    color_bits([n+26, 25], 3)
    color_bits([n+49, 20], 3)
    
for n in range(15):
    color_bits([20,n+5],3)
    color_bits([55,n+5],3)
    color_bits([n+40, 15], 3)
def Scroller():
    text="YOU WON THE MAZE GAME!"
    my_scrolling_label = ScrollingLabel(terminalio.FONT, text=text, max_characters=20, animate_time=1)
    my_scrolling_label.x = 0
    my_scrolling_label.y = 15
    display.show(my_scrolling_label)
    while True: 
        my_scrolling_label.update() 

def draw_goal(xd, yd, zd):
    for index, coord in enumerate(goal_coords):
        x = float(coord[0])
        y = float(coord[1])
        goal_coords[index] = [x, y]
        bitmap1[int(x), int(y)] = 2

def check_for_entities(coord, index):
    x = int(coord[0])
    y = int(coord[1])
    if x > 31:
        x = x - 32
        if bitmap2[x,y] == index:
            return True
        else:
            return False
    else:
        if bitmap1[x, y] == index:
            return True
        else:
            return False

def draw_ball(xd, yd, zd):
    global marble_coords
    temp_coords = [[], [], [], [], []]
    for index, coord in enumerate(marble_coords):
        x = float(coord[0]) + xd
        y = float(coord[1]) + yd
        if x < 1 or x > 63 or y < 1 or y > 31:
            return
        if check_for_entities([x, y], 3) == True:
            return
        if check_for_entities([x, y], 2) == True:
            time.sleep(.1)
            print("YOU WIN")
            Scroller()
        temp_coords[index] = [x, y]
    for coords in marble_coords:
        if check_for_entities(coords, 3) == False:
            color_bits(coords, 0)
    marble_coords = temp_coords
    for coord in temp_coords:
        color_bits(coord, 1)

image_grid = displayio.TileGrid(bitmap1, pixel_shader=palette,
                                     width=1, height=1,
                                     tile_height=32, tile_width=32,
                                     default_tile=0,
                                     x=0, y=0)
image_grid2 = displayio.TileGrid(bitmap2, pixel_shader=palette,
                                     width=1, height=1,
                                     tile_height=32, tile_width=32,
                                     default_tile=0,
                                     x=32, y=0)
group = displayio.Group()
group.append(image_grid)
group.append(image_grid2)
display.show(group)

while True:
    x, y, z = [value / adafruit_lis3dh.STANDARD_GRAVITY for value in lis3dh.acceleration]
    draw_ball(x, y, z)
    draw_goal(x, y, z)
    time.sleep(0.25)