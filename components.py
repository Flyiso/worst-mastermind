import random
import cv2
import numpy as np


class Spinner():
    def __init__(self, idx: int, colors: list, texture_size) -> None:
        self.colors = colors
        self.cuttent = self.colors[0]
        self.screen_width, self.screen_height = texture_size[:2]
        self.idx = idx
        # dimentions/locations currently assumes
        # top left corner of screen as origin.
        self.top, self.bottom,\
            self.leftmost, self.rightmost = self.get_dimentions()
        self.button = SpinnerButton(self)
        self.locked = self.button.is_locked
        self.is_spinnig = False

    def get_dimentions(self) -> list:
        top = (self.screen_height-self.screen_width + ((self.screen_width / 78) * 37))
        bottom = (self.screen_height-self.screen_width + ((self.screen_width / 78) * 58))
        leftmost = ((self.screen_width / 78) * (14 + (self.idx * 13)))
        rightmost = ((self.screen_width / 78) * ((14 + 11) + (self.idx * 13)))
        return top, bottom, leftmost, rightmost
    
    def draw_spinner(self):
        pass


class SpinnerButton():
    def __init__(self, spinner) -> None:
        self.is_locked = False
        self.spinner = spinner
        self.center_width = (sum([self.spinner.leftmost,
                                  self.spinner.rifghtmost]))/2
        self.center_h_unpressed,\
            self.center_h_pressed = self.get_center_heights()
        self.radus_vertical, self.radius_horizontal = self.get_radius()

    def get_center_heights(self):
        unpressed = (self.spinner.screen_height - self.spinner.screen_width +
        ((self.spinner.screen_width / 78) * 63))
        pressed = (self.spinner.screen_height-self.spinner.screen_width +
        ((self.spinner.screen_width / 78) * 64))
        return unpressed, pressed

    def get_radius(self):
        r_width = ((self.spinner.screen_width/78) * 3.5)
        r_height = (self.spinner.screen_width/78)
        return r_height, r_width

    def draw_button(self):
        pass

    def press_button(self):
        if self.is_locked:
            self.is_locked = False
            return
        self.is_locked = True

class Colors:
    """
    Manage colors in game-
    Class to set the colors active and the sequence to win.
    self.active_colors: dict item of x key-value pairs reprecenting
                        colors active in game
    self.correct_sequence: 2d list of [name(str), value_rgb(tuple)]
    """
    color_options = {'red':(255,0,0), 'orange':(255,128,0),
                     'yellow':(255,255,0), 'lime':(128,255,0),
                     'green':(0,255,0), 'turquoise':(0, 255, 255), 
                     'blue':(0,128,255), 'deepblue':(0,0,255),
                     'purple':(127,0,255), 'magenta':(255,0,255),
                     'pink':(255, 0, 127)}

    def __init__(self, n_colors: int = 5,
                 sequence_length: int = 4) -> None:
        """
        Determine active color in game, randomize the win sequence.
        """
        self.sequence_length, self.n_colors = self.check_input(sequence_length, n_colors)
        self.active_colors = self.get_active_colors(self.color_options, self.n_colors)
        self.correct_sequence = self.get_game_sequence()
    
    def check_input(self, n_colors, sequence_length):
        """
        method to confirm valid input values and resets problmatic ones.

        :param n_colors: int-how many different active colors in game
        :param sequence_length: int-how many guesses per round(currently only 4 is supported)
        :output: n_colors, sequence_length - as valid data types and within valid ranges
        """
        # make sure value is int and in range.
        if not isinstance(n_colors, int):
            n_colors = 5
        elif n_colors < 2 or n_colors > len(self.color_options):
            n_colors = 5
        
        # Current layout only support sequence length of 4
        if not isinstance(sequence_length, int):
            sequence_length = 4
        elif sequence_length != 4:
            sequence_length = 4

        return n_colors, sequence_length
    
    def get_game_sequence(self) -> list:
        """
        Get 4 random colors form the ones active in game.

        :return: list(2d) of list items[name, color_code_rgb]
        """
        correct = []
        for _ in range(self.sequence_length):
            color_name, color_value = random.choice(list(self.active_colors.items()))
            correct.append([color_name, color_value])
        return correct
    
    @staticmethod
    def get_active_colors(color_options, n_colors: int = 5,) -> dict:
        """
        Create dictionary of n_colors different colors color_name:color_rgb

        :param n_colors: default = 5. int in range 2-11 the number of colors active in game.
        :output: dictionary of the color items active
        """
        colors_choosen = {}
        for _ in range(n_colors):
            color_name, color_value = random.choice(list(color_options.items()))
            colors_choosen[color_name] = color_value
            del color_options[color_name]
        return colors_choosen

class GameStatus:
    def __init__(self, correct: list) -> None:
        """
        Initalize the game status tool- compare_to_sequence method evaluates guess compared
        to the correct sequence.

        :param correct: list of dict items, length 4, each item concist of a name and a color value(rgb)
        """
        self.guesses = []
        self.game_won = False
        self.correct_sequence = correct

    def compare_to_sequence(self, guessed_sequence):
        """
        Compare guess made with the correct sequence. create list of 1 and 0,
        where 1 is correct place and color, and 2 is correct color, not place.

        :param guessed_sequence: list 2D, each item concist of name_str, color_tuple_rgb
        :return: 2D list. of inner lists- fist-list of guess(name_str,color_tuple_rgb), then-evaluation
        """
        results = [0]
        temp_corr = self.correct_sequence
        for correct, guess in zip (self.correct_sequence,
                                   guessed_sequence):
            if correct == guess:
                results.append(1)
                temp_corr.remove(guess)
            elif guess in temp_corr:
                results.append(0)
                temp_corr.remove(guess)
        results.sort()
        self.guesses.append([guess, results])
        if sum(results) == len(self.correct_sequence):
            self.game_won = True
        return self.guesses


class GuessGrid:
    """
    Draws grid / background displaying the users guesses
    This should be a scrollable field.
    """
    def __init__(self, texture_size):
        self.num_columns = 6
        self.screen_width, self.screen_height = texture_size[:2]
        self.square_size = (self.screen_width*0.94) // self.num_columns
        self.padding = round(self.screen_width*0.03)
        self.fontScale = min(self.square_size,self.square_size)/(25/1)

    def draw_grid(self, guesses: list) -> np.ndarray:
        """
        draw guesses and evaluations of them on the grid.
        """
        self.num_rows = round(max([self.screen_height // self.square_size + 1,
                                   len(guesses)+self.num_columns]))
        img = np.zeros(
            (max([self.screen_height, round(len(guesses)*self.square_size)]),
            self.screen_width, 3),
            dtype=np.uint8)
        for row in range(self.num_rows+1):
            cv2.line(img,
                        (0+self.padding, round((row*self.square_size)+self.padding)),
                        (round(self.square_size*self.num_columns)+self.padding, round((row*self.square_size)+self.padding)),
                        (255, 255, 255), 1)
            for col in range(self.num_columns+1):
                cv2.line(img,
                         (round((col*self.square_size)+self.padding), 0+self.padding),
                         (round((col*self.square_size)+self.padding), self.screen_height+self.padding), 
                         (255, 255, 255), 1)
                
        img = self.draw_guesses(img, guesses)
        return img
        

    def draw_guesses(self, img, guesses):
        for row in range(self.num_rows):
            cv2.putText(img, str(row+1), (0, round(row+1*self.square_size)),
                        round(self.fontScale), cv2.FONT_HERSHEY_SIMPLEX,
                        (255, 255, 255), 2, cv2.LINE_AA)
            if len(guesses) <= row:
                continue # or continue? break? 
            for col in range(1, self.num_columns-1):
                center = (
                    round((self.padding + (self.square_size*(col+1)))-self.square_size/2),
                    round((self.padding + (self.square_size*(row+1)))-self.square_size/2)
                          )
                cv2.circle(img, center, round((self.square_size / 2) * 0.95),
                           guesses[row][0][col-1][1][::-1], -1)

            center = (round(((self.square_size*self.num_columns)+self.padding)-(self.square_size/2)),
                      round((((row+1)*self.square_size)+self.padding)-self.square_size/2))
            center_fourths = [(center[0]-(self.square_size/4), center[1]-(self.square_size/4)),
                              (center[0]+(self.square_size/4), center[1]-(self.square_size/4)),
                              (center[0]-(self.square_size/4), center[1]+(self.square_size/4)),
                              (center[0]+(self.square_size/4), center[1]+(self.square_size/4))
                                                    ]
            for idx, location in enumerate(center_fourths):
                color_bgr = (0, 0, 255)
                print('....')
                print(guesses[row][1])
                if (len(guesses[row][1])-1) >= idx:
                    print(guesses[row][1][idx])
                    color_bgr = (255*abs(guesses[row][1][idx]-1), 255*guesses[row][1][idx], 0)
                print(color_bgr)
                cv2.circle(img, (round(location[0]), round(location[1])),
                           round((self.square_size/4)*0.9), color_bgr, -1)
        return img

mock_correct = [['green', (0, 255, 0)], ['red', (255, 0, 0)], ['green', (0, 255, 0)], ['red', (255, 0, 0)]]

mock_guess = [[[['red',(255, 0, 0)],['blue',(0, 0, 255)],
                ['green',(0, 255, 0)],['blue',(0, 0, 255)]],
               [1,0,0]],
              [[['blue',(0, 0, 255)],['blue',(0, 0, 255)],
                ['red',(255, 0, 0)],['blue',(0, 0, 255)]],
               [0]],
              [[['green', (0, 255, 0)], ['red', (255, 0, 0)],
                ['green',(0, 255, 0)],['blue',(0, 0, 255)]],
               [1,1,1]],
              [[['red',(255, 0, 0)],['blue',(0, 0, 255)],
                ['green',(0, 255, 0)],['blue',(0, 0, 255)]],
               [1,0,0]],
              [[['blue',(0, 0, 255)], ['blue',(0, 0, 255)],
                ['blue',(0, 0, 255)], ['blue',(0, 0, 255)]],
               []],
              [[['green', (0, 255, 0)], ['red', (255, 0, 0)],
               ['green', (0, 255, 0)], ['red', (255, 0, 0)]],
              [1, 1, 1, 1]]]
grid_class = GuessGrid([350, 900])
mock_grid = grid_class.draw_grid(mock_guess)
cv2.imwrite('mock_grid.png', mock_grid)
'''
ORDER TO DRAW EVERYTHING:
0. guesses made/guess_grid
1. background
2. slider_arm
3. current_colors/spinners
4. machine/forground img
5  slider_button
6. buttons(first kivy buttons to link to event then img on top?)


while spinners are spinning: draw 3-5
when guess is made/lever moved draw 2-5
lever all way down = start spinners(and check buttons), wait til stopped, compare to win sequence

when game is run:
1. get active collors & correct sequence
2. draw frame
-loop-
    if button_press:
        set button & spinner values
        re-draw 4, 6
    if slider is pulled:
        re-draw 2, 4, 5
    if slider is released(but not at 100):
        re-draw 2, 4, 5 until it reaches value of 0
    if slider reaches 100%
        start spinner values, re-draw 2-6 while spinning and lever resets
        when stopped, check guess
        re-draw everything, update guess grid with last guess
            if guess is correct- display something, let user choose to restart(and start at step 1 if they do)


TODO animation for slider
TODO animation for spinner
TODO button drawing 
TODO spinner/random(?) logic
TODO connect to kivy

TODO: Make testable on computer: while keeping porportions for phone devices. (use screen_h/2 as width?)

Notes:
app will consist of 2 'main' sections-

first- a grid in the bacground, displaying a grid specifying the users guesses, and the feedback to those guesses.
this field is, apart from being scrollable, not interactive. since this field is, to a degree drawn/displayed under
the other sectoion of the app, it also need to draw a few more rows on the grid than guessed, to allow the user to see
their last guess without problem. it should also automatically make the users last guess visible (once the user makes
a guess- meaning, when the lever is drawn, and weels have stopped spinning, in the section 2 of the app)

second- the interactive section of the app-
this section displays the machine, the current colors, buttons to 'lock' colors and a leaver to randomize unloced colors
and make a guess from the result. This field is not scrollable. 


layout/app-widget-design-plan:
1.main app-all of screen- draw background here- do not adjust proportions on background, but put it at bottom of
the field, and match the with of the image to the with of the devices screen
2.guesses-field- somewhat overlap(or underlap to be precice) the main widget of the game. this has the same size as screen, and is
scrollable- n of fields drawn =  
    max([
        (n of guesses_made)
        (n of fields that fit in device heigth(size of fields has ratio 1:1, and is dictated by width(1/6 of width)) -6 )
        ])
    + 6 blank rows

This makes the seventh last row the one to display, but also, makes scrolling as long as possible a working method for
centering on most interesting row.

the columns in this field represent:
1. guess number
2. color_guess 1
3. color_guess 2
4. color_guess 3
5. color_guess 4
6. guess evaluation/ displaing one symbol when a color is present in correct sequence,
   and one collor when both color and location is correct.
'''