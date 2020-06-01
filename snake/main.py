import curses
import random
import time

class Screen:
    COLOR_APPLE = 1
    COLOR_LOST = 2
    def __init__(self):
        self.__stdscr = curses.initscr()
        self.__height = curses.LINES - 2
        self.__width = curses.COLS - 2
        self.__stdscr.nodelay(True)
        self.__snake_body = []
        self.__apple = None
        curses.noecho()
        self.__stdscr.keypad(True)
        self.__score = 0
        self.__lost_message = False
        curses.start_color()
        curses.init_pair(Screen.COLOR_APPLE, curses.COLOR_RED, curses.COLOR_BLACK)        
        curses.init_pair(Screen.COLOR_LOST, curses.COLOR_RED, curses.COLOR_BLACK)        

    def get_size(self):
        return (self.__width, self.__height)

    def refresh(self):
        self.__stdscr.erase()
        self.__draw_board()
        for i in range(len(self.__snake_body)):
            self.__stdscr.addch(self.__snake_body[i][1], self.__snake_body[i][0], 'O')
        if self.__apple is not None:
            self.__stdscr.addch(self.__apple[1], self.__apple[0], '*', curses.color_pair(Screen.COLOR_APPLE) )
        self.__stdscr.addstr(0, 0, f'Score: {self.__score:3} ', curses.A_REVERSE)
        if self.__lost_message:
            self.__stdscr.addstr(int(self.__height / 2), int(self.__width / 2) - 9, ' Y O U   L O S T ', curses.color_pair(Screen.COLOR_LOST) | curses.A_REVERSE)
        self.__stdscr.refresh()

    def draw_snake(self, body):
        self.__snake_body = body.copy()  

    def draw_apple(self, apple):
        self.__apple = apple

    def show_score(self, score):
        self.__score = score

    def getch(self):
        return self.__stdscr.getch(self.__height, self.__width)

    def lost_message(self):
        self.__lost_message = True

    def __draw_board(self):
        for x in range(0, self.__width+1):
            self.__stdscr.addch(0, x, '-')
            self.__stdscr.addch(self.__height, x, '-')
        for y in range(0, self.__height+1):
            self.__stdscr.addch(y, 0, '|')
            self.__stdscr.addch(y, self.__width, '|')

class Snake:
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

    STATUS_CONTINUE = 0
    STATUS_SUCCESS = 1
    STATUS_COLLISION = 2

    def __init__(self, screen, snake_size=5):
        self.__screen = screen
        screen_size = screen.get_size()
        head = (int(screen_size[0] / 2), int(screen_size[1] / 2))
        self.__body = []
        for i in range(snake_size):
            self.__body.append((head[0], head[1] + i))
        self.__direction = Snake.UP
        self.place_apple()
        self.__score = 0
        self.__delay = 0.3

    def change_direction(self, direction):
        self.__direction = direction
        self.__grow()

    def get_delay(self):
        return self.__delay

    def move(self):
        head = self.__body[0]
        if self.__direction == Snake.UP:
            head = (head[0], head[1] - 1)
        elif self.__direction == Snake.DOWN:
            head = (head[0], head[1] + 1)
        elif self.__direction == Snake.LEFT:
            head = (head[0] - 1, head[1])
        elif self.__direction == Snake.RIGHT:
            head = (head[0] + 1, head[1])
        else:
            print(f'Invalid direction: { self.__direction }')

        for i in range(len(self.__body) - 1, 0, -1):
            self.__body[i] = self.__body[i - 1]
        self.__body[0] = head

    def __grow(self):
        self.__body.append((0, 0))        

    def has_collided(self):
        result = False
        head_x, head_y = self.__body[0]
        columns, rows = self.__screen.get_size()
        if head_x <= 0 or head_x >= columns:
            return True
        if head_y <= 0 or head_y >= rows:
            return True
        for i in range(1, len(self.__body)):
            if self.__body[0] == self.__body[i]:
                return True

    def has_eaten_apple(self):
        return self.__body[0] == self.__apple

    def place_apple(self):
        apple_placed_ok = False
        screen_size = screen.get_size()
        while not apple_placed_ok:
            self.__apple = (random.randint(1, screen_size[0]-1), random.randint(1, screen_size[1]-1))
            if self.__valid_apple_position():
                apple_placed_ok = True

    def draw(self):
        self.__screen.draw_snake(self.__body)
        self.__screen.draw_apple(self.__apple)
        self.__screen.show_score(self.__score)

    def tick(self):
        self.move()
        if self.has_collided():
            return False
        if self.has_eaten_apple():
            self.__score += 1
            self.__grow()
            self.place_apple()
            self.__delay = self.__delay * 0.9
        self.draw()
        return True

    def __valid_apple_position(self):
        for i in range(len(self.__body)):
            if self.__body[i] == self.__apple:
                return False
        return True
        
    

screen = Screen()
snake = Snake(screen)
lost = False
while True:
    screen.refresh()
    time.sleep(snake.get_delay())
    ch = screen.getch()
    if ch == ord(' '):
        break
    if not lost:
        if ch == curses.KEY_LEFT:
            snake.change_direction(Snake.LEFT)
        elif ch == curses.KEY_UP:
            snake.change_direction(Snake.UP)
        elif ch == curses.KEY_DOWN:
            snake.change_direction(Snake.DOWN)
        elif ch == curses.KEY_RIGHT:
            snake.change_direction(Snake.RIGHT)
        else:
            pass
        if not snake.tick():
            screen.lost_message()
            lost = True
