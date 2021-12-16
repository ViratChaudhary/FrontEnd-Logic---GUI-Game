'''
CSSE1001 Assignment 3 
Semester 2, 2020
'''
import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
from tkinter import filedialog

__author__ = "{{Virat Chaudhary}} ({{s4641144}})"
__email__ = "v.chaudhary@uqconnect.edu.au"
__date__ = "30 October 2020"

GAME_LEVELS = {
    # dungeon layout: max moves allowed
    "game1.txt": 7,
    "game2.txt": 12,
    "game3.txt": 19,
}

PLAYER = "O"
KEY = "K"
DOOR = "D"
WALL = "#"
MOVE_INCREASE = "M"
SPACE = " "

DIRECTIONS = {
    "W": (-1, 0),
    "S": (1, 0),
    "D": (0, 1),
    "A": (0, -1)
}

INVESTIGATE = "I"
QUIT = "Q"
HELP = "H"

VALID_ACTIONS = [INVESTIGATE, QUIT, HELP, *DIRECTIONS.keys()]

HELP_MESSAGE = f"Here is a list of valid actions: {VALID_ACTIONS}"

INVALID = "That's invalid."

WIN_TEXT = "You have won the game with your strength and honour!"

LOSE_TEST = "You have lost all your strength and honour."
LOSE_TEXT = "You have lost all your strength and honour."

TASK_ONE = 1
TASK_TWO = 2

def load_game(filename):
    """Create a 2D array of string representing the dungeon to display.
    
    Parameters:
        filename (str): A string representing the name of the level.

    Returns:
        (list<list<str>>): A 2D array of strings representing the 
            dungeon.
    """
    dungeon_layout = []

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            dungeon_layout.append(list(line))

    return dungeon_layout


class Entity:
    """ """

    _id = "Entity"

    def __init__(self):
        """
        Something the player can interact with
        """
        self._collidable = True

    def get_id(self):
        """ """
        return self._id

    def set_collide(self, collidable):
        """ """
        self._collidable = collidable

    def can_collide(self):
        """ """
        return self._collidable

    def __str__(self):
        return f"{self.__class__.__name__}({self._id!r})"

    def __repr__(self):
        return str(self)


class Wall(Entity):
    """ """

    _id = WALL
    
    def __init__(self):
        """ """
        super().__init__()
        self.set_collide(False)


class Item(Entity):
    """ """
    def on_hit(self, game):
        """ """
        raise NotImplementedError


class Key(Item):
    """ """

    _id = KEY

    def on_hit(self, game):
        """ """
        player = game.get_player()
        player.add_item(self)
        game.get_game_information().pop(player.get_position())


class MoveIncrease(Item):
    """ """

    _id = MOVE_INCREASE

    def __init__(self, moves=5):
        """ """
        super().__init__()
        self._moves = moves

    def on_hit(self, game):
        """ """
        player = game.get_player()
        player.change_move_count(self._moves)
        game.get_game_information().pop(player.get_position())


class Door(Entity):
    """ """
    _id = DOOR

    def on_hit(self, game):
        """ """
        player = game.get_player()
        for item in player.get_inventory():
            if item.get_id() == KEY:
                game.set_win(True)
                game.get_game_information().pop(player.get_position())
                return

        print("You don't have the key!")


class Player(Entity):
    """ """

    _id = PLAYER

    def __init__(self, move_count):
        """ """
        super().__init__()
        self._move_count = move_count
        self._inventory = []
        self._position = None

    def set_position(self, position):
        """ """
        self._position = position

    def get_position(self):
        """ """
        return self._position

    def change_move_count(self, number):
        """
        Parameters:
            number (int): number to be added to move count
        """
        self._move_count += number

    def moves_remaining(self):
        """ """
        return self._move_count

    def add_item(self, item):
        """
        Adds item (Item) to inventory
        """
        self._inventory.append(item)

    def get_inventory(self):
        """ """
        return self._inventory


class GameLogic:
    def __init__(self, dungeon_name):
        """ """
        self._dungeon = load_game(dungeon_name)
        self._dungeon_size = len(self._dungeon)
        self._player = Player(GAME_LEVELS[dungeon_name])
        self._game_information = self.init_game_information()
        self._win = False

    def get_positions(self, entity):
        """ """
        positions = []
        for row, line in enumerate(self._dungeon):
            for col, char in enumerate(line):
                if char == entity:
                    positions.append((row, col))

        return positions

    def init_game_information(self):
        """ """
        player_pos = self.get_positions(PLAYER)[0]
        key_position = self.get_positions(KEY)[0]
        door_position = self.get_positions(DOOR)[0]
        wall_positions = self.get_positions(WALL)
        move_increase_positions = self.get_positions(MOVE_INCREASE)
        
        self._player.set_position(player_pos)

        information = {
            key_position: Key(),
            door_position: Door(),
        }

        for wall in wall_positions:
            information[wall] = Wall()

        for move_increase in move_increase_positions:
            information[move_increase] = MoveIncrease()

        return information

    def get_player(self):
        """ """
        return self._player

    def get_entity(self, position):
        """ """
        return self._game_information.get(position)

    def get_entity_in_direction(self, direction):
        """ """
        new_position = self.new_position(direction)
        return self.get_entity(new_position)

    def get_game_information(self):
        """ """
        return self._game_information

    def get_dungeon_size(self):
        """ """
        return self._dungeon_size

    def move_player(self, direction):
        """ """
        new_pos = self.new_position(direction)
        self.get_player().set_position(new_pos)

    def collision_check(self, direction):
        """
        Check to see if a player can travel in a given direction
        Parameters:
            direction (str): a direction for the player to travel in.

        Returns:
            (bool): False if the player can travel in that direction without colliding otherwise True.
        """
        new_pos = self.new_position(direction)
        entity = self.get_entity(new_pos)
        if entity is not None and not entity.can_collide():
            return True
        
        return not (0 <= new_pos[0] < self._dungeon_size and 0 <= new_pos[1] < self._dungeon_size)

    def new_position(self, direction):
        """ """
        x, y = self.get_player().get_position()
        dx, dy = DIRECTIONS[direction]
        return x + dx, y + dy

    def check_game_over(self):
        """ """
        return self.get_player().moves_remaining() <= 0

    def set_win(self, win):
        """ """
        self._win = win

    def won(self):
        """ """
        return self._win


class AbstractGrid(tk.Canvas):
    def __init__(self, master, rows, cols, width, height, **kwargs):
        """
        Constructor: AbstractGrid

        Parameters:
            master: The tk window
            rows (int): Number of rows in the canvas
            cols (int): Number of columns in the canvas
            width (int): width of the canvas in pixels
            height (int): height of the canvas in pixels 
            **kwargs: tk.Canvas valid parameters 
        """
        super().__init__(master, width=width, height=height, **kwargs)

        self._master = master
        self._rows = rows
        self._cols = cols
        self._width = width
        self._height = height

        self._row_length = self._height // self._rows
        self._col_length = self._width // self._cols

    def get_bbox(self, position):
        """
        find the corner coordinates for the rectangle

        Parameters:
            position (tuple): the row col position for the rectangle

        Returns:
            (tuple): the 4 corner coordinates of the rectangle in pixel coordinates
        """
        row, col = position

        x1 = self._col_length * col
        x2 = self._col_length * (col + 1)
        y1 = self._row_length * row
        y2 = self._row_length * (row + 1)

        return (x1, y1, x2, y2)

    def pixel_to_position(self, pixel):
        """
        find the row col position for the pixel coordinates given
        
        Parameters:
            pixel (tuple): the pixel coordinates 

        Returns:
            (tuple): the row col position for the given pixel coordinates
        """
        x, y = pixel

        col_pos = x // self._col_length
        row_pos = y // self._row_length

        return (row_pos, col_pos)
    
    def get_position_center(self, position):
        """
        find the pixel coordinates of the center of the rectangle for the given row col rectangle position
        
        Parameters:
            position (tuple): the row col position for the rectangle

        Returns:
            (tuple): the center pixel coordinates of the given rectangle
        """
        row, col = position

        x_coord = (col * self._col_length) + (self._col_length / 2)
        y_coord = (row * self._row_length) + (self._row_length / 2)
        
        return (x_coord, y_coord)

    def annotate_position(self, position, text):
        """
        annotates a position on the canvas given the position and the text needing to be annotated

        Parameters:
            position (tuple): the row col position that needs to be annotated
            text (str): the text that needs to be placed at the given position
        """
        x, y = self.get_position_center(position)
        self.create_text(x, y, text=text)
        
class DungeonMap(AbstractGrid):
    def __init__(self, master, size, width=600, **kwargs):
        """
        Constructor: DungeonMap

        Parameters:
            master: The tk window
            size (int): the rows and columns needed for the grid
            width (int): width of the grid in pixels 
            **kwargs: AbstractGrid valid parameters 
        """
        super().__init__(master, size, size, width=width, height=width, bg='light gray')

        self._width = width
        self._master = master
        self._size = size

        self.fills = {
            PLAYER: 'green',
            WALL: 'gray',
            KEY: 'yellow',
            MOVE_INCREASE: 'orange',
            DOOR: 'red'
        }

        self.annotations = {
            PLAYER: 'Ibis',
            KEY: 'Trash',
            MOVE_INCREASE: 'Banana',
            DOOR: 'Nest', 
            WALL: ''
        }

    def draw_square(self, position, entity):
        """
        draws a single square of the grid given the position at which to draw and the entity the fills the position
        
        Parameters:
            position (tuple): the row col position for the entity
            entity: the entity that is placed at the given position
        """
        self.create_rectangle(self.get_bbox(position), fill=self.fills.get(entity.get_id()))
        self.annotate_position(position, self.annotations.get(entity.get_id()))

    def draw_player(self, position):
        """
        draws the player on the grid given the position

        Parameters:
            position (tuple): the row col position of the player
        """
        self.create_rectangle(self.get_bbox(position), fill=self.fills.get(PLAYER))
        self.annotate_position(position, self.annotations.get(PLAYER))

    def draw_grid(self, dungeon, player_position):
        """
        draws the entire grid filling all positions with the entities and player for displaying

        Parameters:
            dungeon (dict): the game dictionary with keys as row col positions and values as the entities
            player_position (tuple): the row col position of the player on the grid
        """
        for position, entity in dungeon.items():
            self.draw_square(position, entity)

        self.draw_player(player_position)

class AdvancedDungeonMap(DungeonMap):
    def __init__(self, master, size, width=600, **kwargs):
        """
        Constructor: AdvancedDungeonMap

        Parameters:
            master: The tk window
            size (int): the rows and columns needed for the grid
            width (int): width of the grid in pixels 
            **kwargs: DungeonMap valid parameters 
        """
        super().__init__(master, size, width=width, **kwargs)

        self._master = master
        self._size = size
        self._width = width

        self._images = {
            PLAYER: self.load_image('player.png'),
            KEY: self.load_image('key.png'),
            MOVE_INCREASE: self.load_image('moveIncrease.png'),
            DOOR: self.load_image('door.png'), 
            WALL: self.load_image('wall.png'),
            'Grass': self.load_image('empty.png')
        }

    def load_image(self, path):
        """
        loads and resizes the image dependant on the grid dimensions given the image file name

        Parameters:
            path (str): file name of the image that needs to be loaded

        Returns:
            (PhotoImage): the image that had been loaded
        """
        picture = Image.open(path)
        picture = picture.resize((self._row_length, self._col_length))
        self.picture = ImageTk.PhotoImage(picture)

        return self.picture
        
    def draw_square(self, position, entity):
        """
        draws a single square of the grid given the position at which to draw and the entity the fills the position
        this method overwrites draw_square from DungeonMap class
        
        Parameters:
            position (tuple): the row col position for the entity
            entity: the entity that is placed at the given position
        """
        x, y = self.get_position_center(position)
        self.create_image(x, y, image=self._images.get(entity.get_id()))

    def draw_player(self, position):
        """
        draws the player on the grid given the position
        this method overwrites draw_player from DungeonMap class

        Parameters:
            position (tuple): the row col position of the player
        """
        x, y = self.get_position_center(position)
        self.create_image(x, y, image=self._images.get(PLAYER))

    def draw_grid(self, dungeon, player_position):
        """
        draws the entire grid filling all positions with the entities and player for displaying including the grass background
        this method overwrites draw_grid from DungeonMap class

        Parameters:
            dungeon (dict): the game dictionary with keys as row col positions and values as the entities
            player_position (tuple): the row col position of the player on the grid
        """
        for x in range(self._rows):
            for y in range(self._cols):
                position = (x, y)
                x_pos, y_pos = self.get_position_center(position)
                self.create_image(x_pos, y_pos, image=self._images.get('Grass'))

        super().draw_grid(dungeon, player_position)
                
class KeyPad(AbstractGrid):
    def __init__(self, master, width=200, height=100, **kwargs):
        """
        Constructor: KeyPad

        Parameters:
            master: The tk window
            width (int): width of the keypad in pixels 
            height (int): height of the keypad in pixels
            **kwargs: AbstractGrid valid parameters 
        """
        super().__init__(master, rows=2, cols=3, width=width, height=height, **kwargs)

        self._master = master
        self._width = width
        self._height = height

        self._key_dict = {(0, 1): 'W', (1, 0): 'A', (1, 1): 'S', (1, 2): 'D'}

        for key, val in self._key_dict.items():
            kp_x1, kp_y1, kp_x2, kp_y2 = self.get_bbox(key)
            self.create_rectangle(kp_x1, kp_y1, kp_x2, kp_y2, fill='dark gray')

            if val == 'W':
                self.annotate_position(key, 'N')
            elif val == 'A':
                self.annotate_position(key, 'W')
            elif val == 'S':
                self.annotate_position(key, 'S')
            elif val == 'D':
                self.annotate_position(key, 'E')

    def pixel_to_direction(self, pixel):
        """
        gets the direction in WASD dependant on the pixel coordinates of the keypad

        Parameters:
            pixel (tuple): pixel coordinates of the keypad

        Returns:
            (str): the direction string as 'W', 'A', 'S' or 'D' for the given pixel position
        """
        row_col_pos = self.pixel_to_position(pixel)

        for key, val in self._key_dict.items():
            if row_col_pos == key:
                return val
            
class StatusBar(tk.Frame):
    def __init__(self, master, **kwargs):
        """
        Constructor: StatusBar

        Parameters:
            master: The tk window
            **kwargs: tk.Frame valid parameters 
        """
        super().__init__(master, **kwargs)

        self._master = master

        # BUTTONS FRAME
        buttons_frame = tk.Frame(self)
        buttons_frame.pack(side=tk.LEFT)

        self.new_game_button = tk.Button(buttons_frame, text='New Game')
        self.quit_game_button = tk.Button(buttons_frame, text='Quit')
        self.quit_game_button.pack(side=tk.BOTTOM, pady=5, padx=75)    
        self.new_game_button.pack(side=tk.BOTTOM, pady=5, padx=75)

        # TIME FRAMES
        time_frame = tk.Frame(self)
        time_frame.pack(side=tk.LEFT)

        time_pic_frame = tk.Frame(time_frame)
        time_pic_frame.pack(side=tk.LEFT)

        time_text_frame = tk.Frame(time_frame)
        time_text_frame.pack(side=tk.LEFT)

        clock_image = Image.open('clock.png')
        clock_image = clock_image.resize((40, 40))
        self.clock_picture = ImageTk.PhotoImage(clock_image)

        clock_label = tk.Label(time_pic_frame, image=self.clock_picture)
        clock_label.pack()

        time_elapsed_label = tk.Label(time_frame, text='Time elapsed')
        self.timer_label = tk.Label(time_frame, text='0m 0s')

        self.timer_label.pack(side=tk.BOTTOM)
        time_elapsed_label.pack(side=tk.BOTTOM)

        # MOVES FRAMES
        moves_frame = tk.Frame(self)
        moves_frame.pack(side=tk.LEFT, padx=75)

        moves_pic_frame = tk.Frame(moves_frame)
        moves_pic_frame.pack(side=tk.LEFT)

        moves_text_frame = tk.Frame(moves_frame)
        moves_text_frame.pack(side=tk.LEFT)

        lightning_image = Image.open('lightning.png')
        lightning_image = lightning_image.resize((40, 40))
        self.lightning_picture = ImageTk.PhotoImage(lightning_image)
    
        lightning_label = tk.Label(moves_pic_frame, image=self.lightning_picture)
        lightning_label.pack()

        moves_left_label = tk.Label(moves_text_frame, text='Moves left')
        self.moves_remaining_label = tk.Label(moves_text_frame, text='')

        self.moves_remaining_label.pack(side=tk.BOTTOM)
        moves_left_label.pack(side=tk.BOTTOM)
        
    def set_new_game_button(self, new_game):
        """
        configurates the new game button to allow for it run the new_game function in gameapp when clicked

        Parameters:
            new_game (function): the new_game function defined in gameapp
        """
        self.new_game_button.config(command=new_game)

    def set_quit_game_button(self, quit_game):
        """
        configurates the quit button to allow for it run the quit_game function in gameapp when clicked

        Parameters:
            quit_game (function): the quit_game function defined in gameapp
        """
        self.quit_game_button.config(command=quit_game)

    def show_moves_remaining(self, moves):
        """
        configurates the moves remaining label to show the updated moves remaining

        Parameters:
            moves (int): the moves remaining in the game
        """
        self.moves_remaining_label.config(text='{} moves remaining'.format(moves)) 

    def get_time_label(self):
        """
        Returns:
            the time label defined in the __init__
        """
        return self.timer_label

    def show_time(self, minutes, seconds):
        """
        configurates the time label to show the updated time

        Parameters:
            minutes (int): the minutes elapsed in the current game
            seconds (int): the seconds elapsed in the current game
        """
        self.get_time_label().config(text='{}m {}s'.format(minutes, seconds))

class GameApp:
    def __init__(self, master, task=TASK_TWO, dungeon_name='game2.txt'):
        """
        Constructor: GameApp

        Parameters:
            master: The tk window
            task: constant defined to check task 1 and task 2
            dungeon_name (string): game text file
        """

        self._task = task
        self._dungeon_name = dungeon_name
        self._master = master

        self._master.title('Key Cave Adventure Game')

        self._model = GameLogic(dungeon_name)

        # Key Cave Adventure Game Label Banner
        self._label_banner = tk.Label(master, text='Key Cave Adventure Game', bg='light green', relief='raised', font=('Courier', 20))
        self._label_banner.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        # initiate and show status bar with its features if task 2
        if self._task == TASK_TWO:
            self.time_seconds = 0
            self.time_minutes = 0
            self.score = 0
            self._status_bar = StatusBar(self._master)
            self._status_bar.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH)
            self._status_bar.set_new_game_button(self.new_game)
            self._status_bar.set_quit_game_button(self.quit_game)
            self._status_bar.show_moves_remaining(self._model.get_player().moves_remaining())
            self._status_bar.show_time(self.time_minutes, self.time_seconds)
            self._status_bar.get_time_label().after(1000, self.update_time)

        # initiate and show menubar with filemenu if task 2
        if self._task == TASK_TWO:
            self.menubar = tk.Menu(self._master)
            self._master.config(menu=self.menubar)

            filemenu = tk.Menu(self.menubar)
            self.menubar.add_cascade(label='File', menu=filemenu)
            filemenu.add_command(label='Save Game', command=self.save_game)
            filemenu.add_command(label='Load Game', command=self.load_game_file)
            filemenu.add_command(label='New Game', command=self.new_game)
            filemenu.add_command(label='Quit', command=self.quit_game)

        # show standard dungeon map if task 1
        if self._task == TASK_ONE:
            self._get_dungeon = DungeonMap(self._master, self._model._dungeon_size)
        
        # show advanced dungeon map if task 2
        if self._task == TASK_TWO:
            self._get_dungeon = AdvancedDungeonMap(self._master, self._model._dungeon_size)

        self._get_dungeon.draw_grid(self._model.get_game_information(), self._model.get_player().get_position())
        self._get_dungeon.pack(side=tk.LEFT)
        
        self._get_keypad = KeyPad(self._master)
        self._get_keypad.pack(side=tk.LEFT)

        # bind the move keys and the left click for moving the player
        self._get_keypad.bind('<Button-1>', self.click)
        self._master.bind('w', self.keyboard_press)
        self._master.bind('a', self.keyboard_press)
        self._master.bind('s', self.keyboard_press)
        self._master.bind('d', self.keyboard_press)

    def click(self, event):
        """
        - handles calculating the direction the player needs to move depending on where the click was made
        - the direction is then passed to the play function to handle player movement logic if not none

        Parameters:
            event: the event initiated when the user clicks on the keypad
        """
        direction = self._get_keypad.pixel_to_direction((event.x, event.y))
        if direction: 
            self.play(direction)
            
    def keyboard_press(self, event):
        """
        - handles calculating the direction the player needs to move depending on the key pressed
        - the direction is the n passed to the play function to handle player movement logic

        Parameters:
            event: the event initiated when the user presses a valid key
        """
        key_pressed = event.keysym
        for key, val in DIRECTIONS.items():
            if key_pressed.upper() == key:
                direction = key
                self.play(direction)
                
    def redraw(self):
        """
        - handles deleting the current grid and drawing a new grid everytime the player moves
        - handles changing the movecount everytime the player moves
        """
        self._get_dungeon.delete(tk.ALL)
        self._get_dungeon.draw_grid(self._model.get_game_information(), self._model.get_player().get_position())

        self._model.get_player().change_move_count(-1)

        # if task 2, then the status bar is also updated with the new moves remaining figure
        if self._task == TASK_TWO:
            self._status_bar.show_moves_remaining(self._model.get_player().moves_remaining())

    def play(self, direction):
        """
        - handles checking if there are valid moves remaining for the player to move
        - hanldes checking if the player can move in the given direction using collision check
        - redraws the grid if valid collision check and checks for game win condition

        Parameters:
            direction (str): the direction the player needs to move in 'W', 'A', 'S' or 'D'
        """

        if self._model.get_player().moves_remaining() != 0:
        
            if not self._model.collision_check(direction):
                self._model.move_player(direction)
                entity = self._model.get_entity(self._model.get_player().get_position())
                
                if entity is not None:
                    entity.on_hit(self._model)

            self.redraw()
            self._master.update()

            self.check_game_win()
    
    def check_game_win(self):

        # checks if the game is won and displays the appropriate messagebox dependant on what task is defined
        if self._model.won():
            if self._task == TASK_ONE:
                tk.messagebox.showinfo(title='Game Won', message=WIN_TEXT)
                self._master.destroy()

            # if task 2, when the game is won, the score is show and request is made to the user to play again
            elif self._task == TASK_TWO:
                self.win_message = 'You have finished the level with the score of {}. \n\nWould you like to play again?'.format(self.score)

                if tk.messagebox.askyesno(title='You Won!', message=self.win_message):
                    self.new_game()
                else:
                    self._master.destroy()

        # checks for the lose condition and displays the appropriate messagebox dependant on what task is defined
        if self._model.get_player().moves_remaining() == 0:
            if self._task == TASK_ONE:
                tk.messagebox.showinfo(title='Game Lost', message=LOSE_TEXT)
                self._master.destroy()

            # if task 2. when the game is lost, a request is made to play again
            elif self._task == TASK_TWO:
                self.lose_message = '{} \n\nWould you like to play again?'.format(LOSE_TEXT)

                if tk.messagebox.askyesno(title='You Lost', message=self.lose_message):
                    self.new_game()
                else:
                    self._master.destroy()

    def new_game(self):
        """
        resets the game completely by:
            - instantiating gamelogic again with the default game dictionary based on the game text file
            - resetting moves remaining the the default moves remaining at the start of the game
            - resetting the time and score of the game to 0. 
        """

        self._model = GameLogic(self._dungeon_name)

        self._get_dungeon.delete(tk.ALL)
        self._get_dungeon.draw_grid(self._model.get_game_information(), self._model.get_player().get_position())

        self._status_bar.show_moves_remaining(self._model.get_player().moves_remaining())

        self.time_seconds = 0
        self.time_minutes = 0
        self.score = 0
        self._status_bar.show_time(self.time_minutes, self.time_seconds)
    
    def quit_game(self):
        # asks the user if they want to quit using a messagebox
        if tk.messagebox.askyesno(title='Quit', message='Are you sure you would like to quit the game?'):
            self._master.destroy()

    def update_time(self):
        # updates time by incrementing score and seconds, and checking if minutes need to be incremented.
        self.time_seconds += 1
        self.score += 1
        
        if self.time_seconds == 60:
            self.time_minutes += 1
            self.time_seconds = 0

        # shows the updated time 
        self._status_bar.show_time(self.time_minutes, self.time_seconds)
        self._status_bar.get_time_label().after(1000, self.update_time)

    def save_game(self):
        """
        writes a txt file and saves it to the computer with relevant details on how to load the game again from the filemenu   
        """

        self._file = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text Files', '*.txt')], title='Save Game File')
        if self._file:
            with open(self._file, 'w') as f:

                # writes the dungeon game text file
                print(self._dungeon_name, file=f)

                # writes the seconds, minutes and score the player was on at the time of saving
                print(self.time_seconds, file=f)
                print(self.time_minutes, file=f)
                print(self.score, file=f)

                # writes the moves remaining the player was on at the time of saving
                print(self._model.get_player().moves_remaining(), file=f) 

                # writes the player position on the grid at the time of saving
                self.x_pos, self.y_pos = self._model.get_player().get_position()
                print(self.x_pos, self.y_pos, file=f) 
                
                # writes the number of elements in the player inventory at the time of saving
                print(len(self._model.get_player().get_inventory()), file=f)

                # checks if the move increase has been obtained by the player or not and writes the answer in text boolean form
                self.move_increase_exists = False
                for key, val in self._model.get_game_information().items():
                    if isinstance(val, MoveIncrease):
                        self.move_increase_exists = True
                print(self.move_increase_exists, file=f)

                # checks if the door is present in the game and writes the answer in text boolean form
                self.door_exists = False
                for key, val in self._model.get_game_information().items():
                    if isinstance(val, Door):
                        self.door_exists = True
                print(self.door_exists, file=f)

    def load_game_file(self):
        """
        - loads a game from the filemenu given a txt file from the computer with details of a saved game
        - errors with the txt file are handles before loading the new game, this is done by using a dummy game logic:
            the dummy game logic is assigned to the primary game logic of self._model if and only if there are no errors present in the load file,
            otherwise the current game the user is on continutes after showing a message of the error the load file ran into
        """
        self._text_file = filedialog.askopenfilename(defaultextension='.txt', filetypes=[('Text Files', '*.txt')], title='Open Saved Game File')
        if self._text_file:
            with open(self._text_file, 'r') as f:

                # checks for incorrect length of lines to load the game (incomplete or excessive information in the txt file that was manually added)
                self.content = f.readlines()
                self.all_lines = [i.strip() for i in self.content]
                if len(self.all_lines) < 9:
                    tk.messagebox.showinfo(title='Invalid Load Game File', message='Insufficient data in load file to display game.')
                    return
                elif len(self.all_lines) > 9:
                    tk.messagebox.showinfo(title='Invalid Load Game File', message='Excessive data in load file to display game.')
                    return

                # checks for incorrect game txt file (altering the game txt file ie. game2.txt changes to game2abcd.txt)
                try:
                    dungeon_name = self.all_lines[0]
                    dummy_model = GameLogic(dungeon_name)
                except FileNotFoundError:
                    tk.messagebox.showinfo(title='Invalid Dungeon Entry', message='The dungeon text file is invalid.')
                    return

                # checks for incorrect time and score which cannot be converted back into integer type from string
                try:
                    txt_seconds = self.all_lines[1]
                    txt_minutes = self.all_lines[2]
                    txt_score = self.all_lines[3]

                    test_seconds = int(txt_seconds)
                    test_minutes = int(txt_minutes)
                    test_score = int(txt_score)
                except ValueError:
                    tk.messagebox.showinfo(title='Invalid Time Entry', message='The value for time and/or score cannot be converted to integer.')
                    return
                
                # checks for incorrect moves remaining value which cannot be converted back into integer type from string
                try:
                    moves_left = self.all_lines[4]
                    dummy_model.get_player()._move_count = int(moves_left)
                except ValueError:
                    tk.messagebox.showinfo(title='Invalid Move Increase Entry', message='The value for move increase cannot be converted to integer.')
                    return

                # checks for incorrect player position which cannot be converted to a tuple from string
                try:
                    player_position = self.all_lines[5]
                    player_position = (int(player_position[0]), int(player_position[2]))
                except ValueError:
                    tk.messagebox.showinfo(title='Invalid Player position Entry', message='The value for player position cannot be converted to position tuple.')
                    return
                
                # checks for incorrect value for inventory items that cannot be converted to integer from string
                try:
                    inventory = self.all_lines[6]
                    if int(inventory) > 0:
                        dummy_model.get_player().add_item(Key())
                        for key, val in dummy_model.get_game_information().items():
                            if isinstance(val, Key):
                                key_position = key
                        dummy_model.get_game_information().pop(key_position)
                except ValueError:
                    tk.messagebox.showinfo(title='Invalid Inventory', message='The value for player inventory is incorrect')
                    return

                # checks for manipulations of move increase boolean text value which would make it invalid to identify if move increase exists or not
                move_inc = self.all_lines[7]
                if move_inc == 'False':
                    for key, val in dummy_model.get_game_information().items():
                        if isinstance(val, MoveIncrease):
                            move_increase_position = key
                    dummy_model.get_game_information().pop(move_increase_position)
                elif move_inc != 'True':
                    tk.messagebox.showinfo(title='Invalid Move Increase Boolean', message='The value for move increase exists is incorrect.')
                    return

                # checks for manipulations of door boolean text value which would make it invalid to identify if door exists or not
                door = self.all_lines[8]
                if door == 'False':
                    for key, val in dummy_model.get_game_information().items():
                        if isinstance(val, Door):
                            door = key
                    dummy_model.get_game_information().pop(door)
                elif door != 'True':
                    tk.messagebox.showinfo(title='Invalid Door Boolean', message='The value for door exists is incorrect.')
                    return

                # assigns all dummy variables to the primary variables used in self._model to redraw the game and show the appropriate status bar
                self.time_seconds = test_seconds
                self.time_minutes = test_minutes
                self.score = test_score
                self._model = dummy_model

                # shows the time and moves remaining in the status bar and sets the player position to the given in the load file
                self._status_bar.show_time(self.time_minutes, self.time_seconds)
                self._status_bar.show_moves_remaining(self._model.get_player().moves_remaining())    
                self._model.get_player().set_position(player_position)

                # deletes the dungeon grid and draws a new grid with the information from the load file
                self._get_dungeon.delete(tk.ALL)
                self._get_dungeon.draw_grid(self._model.get_game_information(), self._model.get_player().get_position())
                                
def main():
    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
