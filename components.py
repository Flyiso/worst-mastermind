import random
import cv2
import numpy as np

# TO MAKE SURE WORKS:
# Spinner       -
# SpinnerButton -
# Colors        OK! :)
# GameStatus    OK! :)
# GuessGrid     OK! :)
movement = 5
slowdown = 0.95
print(movement)
while movement > 0.1 and movement < 5.5:
    movement = movement*slowdown
    print(movement)


class Spinner:
    """"
    Spinner object, containing one section that
    randomizes a value from a decided
    dict of options, and animates this randomization.
    and one section containing a
    button that control the spinner object.
    """
    def __init__(self, idx: int, colors: dict, texture_size) -> None:
        self.colors = colors
        self.current = self.colors[0]
        # how many percent of field dot is passed- start at middle/50%
        self.current_percentile = 50
        # img to map to is square, with width(smallest since portrait layout)
        self.screen_width, self.screen_height = \
            texture_size[0], texture_size[0]
        self.idx = idx
        # dimensions/locations currently assumes
        # top left corner of screen as origin.
        self.top, self.bottom, \
            self.leftmost, self.rightmost = self.get_dimensions()
        self.button = SpinnerButton(self)
        self.locked = self.button.is_locked
        self.is_spinning = False
        # randomize individual slow-down speed for spinner
        self.field_resistance = random.choice([0.950, 0.955, 0.960,
                                               0.965, 0.970, 0.975,
                                               0.980, 0.985, 0.990, 0.995])
        # move 5 'spaces' per time unit
        self.movement = 50

    def get_dimensions(self) -> list:
        top = ((self.screen_width / 78) * 37)
        bottom = ((self.screen_width / 78) * 58)
        leftmost = ((self.screen_width / 78) * (14 + (self.idx * 13)))
        rightmost = ((self.screen_width / 78) * ((14 + 11) + (self.idx * 13)))
        return top, bottom, leftmost, rightmost

    def update_spinner(self):
        """
        updates the individual spinner with new values for current color,
        current colors location and current movement.e
        """
        # image of size of spinner field
        if self.is_locked:
            # just keep current image and value & return
            pass
        # update with randomized new color and animation for it
        np.zeros(round((self.screen_width/78)*13),
                 round((self.screen_width/78)*21), 3)

        # set updated index and location
        # idx x.50: current color is perfectly aligned to middle of field.
        self.idx = (self.idx+self.movement) % (len(self.colors.keys()))
        self.current_color, self.current_value = list(
            self.colors.items())[int(self.idx)]

        # movement counts in percentiles-  percent of dot is pass/time unit
        self.movement = self.movement * 0.75
        # stop movement if threshold is reached
        if self.movement < 0.001:
            self.movement = 0

        # Get the new frame:
        spinner_frame = self.draw_spinner()
        return spinner_frame

    def draw_spinner(self):
        """
        Draws an image for the current values of spinner
        """
        # temporary/not static later on?
        n_colors = 5
        # create image to display visible and partly visible dots.
        upd_frame = np.zeros(round((self.screen_width/78)*13),
                             round((self.screen_width/78)*(13*n_colors)), 3)
        loc_modifier = self.idx-int(self.idx)
        circle_radius = round((upd_frame.shape[0]/2)*0.8)

        # NOTE: frame status is represented by decimal value-
        #       int(nr) is index of color currently the 'in the middle/active'
        #       decimal represents the location- .5 == perfectly in middle
        #       the frame to draw on fit 5 dot'spaces' total.

        center_w = round(upd_frame.shape[0]/2)
        draw_colors = self.get_color_codes_listed(5)
        for n in range(0, n_colors):
            center_h = round((((upd_frame.shape[1]/5) * n) +
                              (upd_frame.shape[1]/5)) * loc_modifier)
            cv2.circle(upd_frame,
                       (center_w, center_h), circle_radius,
                       draw_colors[n], -1)

        # continue to draw surrounding-decide size of each + amount to display.
        return upd_frame

    def get_color_codes_listed(self, nr_colors: int) -> list:
        """
        Return a list (length nr_colors), of color codes to draw.

        :param nr_colors: int, odd value. how many colors to add to list.
        :return: list of color codes, middle one is active color.
        """
        rnge = nr_colors // 2
        colors = self.colors.values()[int(self.idx)-rnge:int(self.idx)+(rnge+1)]
        # get the colors and add to list
        return colors


class SpinnerButton():
    def __init__(self, spinner) -> None:
        self.is_locked = False
        self.spinner = spinner
        self.center_width = (sum([self.spinner.leftmost,
                                  self.spinner.rightmost]))/2
        self.center_h_unpressed, \
            self.center_h_pressed = self.get_center_heights()
        self.radius_vertical, self.radius_horizontal = self.get_radius()

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
    self.active_colors: dict item of x key-value pairs representing
                        colors active in game
    self.correct_sequence: 2d list of [name(str), value_rgb(tuple)]
    """

    def __init__(self, n_colors: int = 5,
                 sequence_length: int = 4) -> None:
        """
        Determine active color in game, randomize the win sequence.
        """
        self.color_options = {'red': (255, 0, 0), 'orange': (255, 128, 0),
                              'yellow': (255, 255, 0), 'lime': (128, 255, 0),
                              'green': (0, 255, 0), 'turquoise': (0, 255, 255),
                              'teal': (0, 128, 255), 'blue': (0, 0, 255),
                              'purple': (127, 0, 255),
                              'magenta': (255, 0, 255), 'pink': (255, 0, 127)}
        self.n_colors, self.sequence_length, = \
            self.check_input(n_colors, sequence_length,)
        self.active_colors = self.get_active_colors(self.color_options,
                                                    self.n_colors)
        self.correct_sequence = self.get_game_sequence()

    def check_input(self, n_colors, sequence_length):
        """
        method to confirm valid input values and resets problematic ones.

        :param n_colors: int-how many different active colors in game
        :param sequence_length: int-how many guesses per round
        (currently only 4 is supported)
        :output: n_colors, sequence_length - as valid data
        types and within valid ranges
        """
        # make sure value is int and in range.
        if not isinstance(n_colors, int):
            n_colors = 5
        elif n_colors < 2 or n_colors > len(self.color_options.items()):
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
            color_name, color_value = random.choice(list(
                self.active_colors.items()))
            correct.append([color_name, color_value])
        return correct

    @staticmethod
    def get_active_colors(color_options, n_colors: int = 5,) -> dict:
        """
        Create dictionary of n_colors different colors color_name:color_rgb

        :param n_colors: default = 5. int in range 2-11
        the number of colors active in game.
        :output: dictionary of the color items active
        """
        colors_chosen = {}
        for _ in range(n_colors):
            color_name, color_value = random.choice(list(
                color_options.items()))
            colors_chosen[color_name] = color_value
            del color_options[color_name]
        return colors_chosen


class GameStatus:
    def __init__(self, correct: list) -> None:
        """
        Initialize the game status tool-
        compare_to_sequence method evaluates guess compared
        to the correct sequence.

        :param correct: list of dict items, length 4, each item consist
        of a name and a color value(rgb)
        """
        self.guesses = []
        self.game_won = False
        self.correct_sequence = correct

    def compare_to_sequence(self, guessed_sequence):
        """
        Compare guess made with the correct sequence. create list of 1 and 0,
        where 1 is correct place and color, and 2 is correct color, not place.

        :param guessed_sequence: list 2D, each item consist
        of name_str, color_tuple_rgb
        :return: 2D list. of inner lists- fist-list of guess
        (name_str,color_tuple_rgb), then-evaluation
        """
        results = []
        temp_corr = self.correct_sequence.copy()
        for idx, (correct, guess) in enumerate(zip(self.correct_sequence,
                                                   guessed_sequence)):
            if correct == guess:
                if idx in results:
                    remove_idx = results.index(idx)
                    results.remove(remove_idx)
                results.append('x')
                if guess in temp_corr:
                    temp_corr.remove(guess)

            elif guess in temp_corr:
                results.append(idx)
                temp_corr.remove(guess)
        results = [1 if itm == 'x' else 0 for itm in results]
        results.sort()
        self.guesses.append([guessed_sequence, results])
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
        self.fontScale = min(self.square_size, self.square_size)/(25/1)

    def draw_grid(self, guesses: list) -> np.ndarray:
        """
        draw guesses and evaluations of them on the grid.
        """
        self.num_rows = round(max([self.screen_height // self.square_size + 1,
                                   len(guesses)+self.num_columns]))
        self.screen_height = round((self.num_rows*self.square_size) +
                                   (self.padding*2))
        img = np.zeros(
            (max([self.screen_height, round(len(guesses)*self.square_size)]),
             self.screen_width, 3),
            dtype=np.uint8)
        for row in range(self.num_rows+1):
            cv2.line(img,
                     (0+self.padding,
                      round((row*self.square_size)+self.padding)),
                     (round(self.square_size*self.num_columns)+self.padding,
                      round((row*self.square_size)+self.padding)),
                     (255, 255, 255), 1)
            for col in range(self.num_columns+1):
                cv2.line(img,
                         (round((col*self.square_size)+self.padding),
                          0+self.padding),
                         (round((col*self.square_size)+self.padding),
                          round(self.screen_height-self.padding)),
                         (255, 255, 255), 1)

        img = self.draw_guesses(img, guesses)
        return img

    def draw_guesses(self, img, guesses):
        for row in range(self.num_rows):
            cv2.putText(img, str(row+1),
                        (round(0+(self.padding*1.3)),
                         round(((row+1)*self.square_size)+(self.padding*0.5))),
                        1, self.fontScale, (255, 255, 255), 2, cv2.LINE_AA)
            if len(guesses) <= row:
                continue
            for col in range(1, self.num_columns-1):
                center = (
                    round((self.padding +
                           (self.square_size*(col+1)))-self.square_size/2),
                    round((self.padding +
                           (self.square_size*(row+1)))-self.square_size/2)
                          )
                cv2.circle(img, center, round((self.square_size / 2) * 0.75),
                           guesses[row][0][col-1][1][::-1], -1)

            center = (round(((self.square_size*self.num_columns) +
                             self.padding)-(self.square_size/2)),
                      round((((row+1)*self.square_size) +
                             self.padding)-self.square_size/2))
            center_fourths = [(center[0]-(self.square_size/4),
                               center[1]-(self.square_size/4)),
                              (center[0]+(self.square_size/4),
                               center[1]-(self.square_size/4)),
                              (center[0]-(self.square_size/4),
                               center[1]+(self.square_size/4)),
                              (center[0]+(self.square_size/4),
                               center[1]+(self.square_size/4))
                              ]
            for idx, location in enumerate(center_fourths):
                color_bgr = (0, 0, 255)
                if (len(guesses[row][1])-1) >= idx:
                    color_bgr = (255*abs(guesses[row][1][idx]-1),
                                 255*guesses[row][1][idx],
                                 0)
                cv2.circle(img, (round(location[0]), round(location[1])),
                           round((self.square_size/4)*0.6), color_bgr, -1)
        return img


mock_guess = [[[['red', (255, 0, 0)], ['blue', (0, 0, 255)],
                ['green', (0, 255, 0)], ['blue', (0, 0, 255)]],
               [1, 0, 0]],
              [[['blue', (0, 0, 255)], ['blue', (0, 0, 255)],
                ['red', (255, 0, 0)], ['blue', (0, 0, 255)]],
               [0]],
              [[['green', (0, 255, 0)], ['red', (255, 0, 0)],
                ['green', (0, 255, 0)], ['blue', (0, 0, 255)]],
               [1, 1, 1]],
              [[['red', (255, 0, 0)], ['blue', (0, 0, 255)],
                ['green', (0, 255, 0)], ['blue', (0, 0, 255)]],
               [1, 0, 0]],
              [[['blue', (0, 0, 255)], ['blue', (0, 0, 255)],
                ['blue', (0, 0, 255)], ['blue', (0, 0, 255)]],
               []],
              [[['green', (0, 255, 0)], ['red', (255, 0, 0)],
               ['green', (0, 255, 0)], ['red', (255, 0, 0)]],
              [1, 1, 1, 1]],
              [[['red', (255, 0, 0)], ['blue', (0, 0, 255)],
                ['green', (0, 255, 0)], ['blue', (0, 0, 255)]],
               [1, 0, 0]],
              [[['blue', (0, 0, 255)], ['blue', (0, 0, 255)],
                ['red', (255, 0, 0)], ['blue', (0, 0, 255)]],
               [0]],
              [[['green', (0, 255, 0)], ['red', (255, 0, 0)],
                ['green', (0, 255, 0)], ['blue', (0, 0, 255)]],
               [1, 1, 1]],
              [[['red', (255, 0, 0)], ['blue', (0, 0, 255)],
                ['green', (0, 255, 0)], ['blue', (0, 0, 255)]],
               [1, 0, 0]],
              [[['blue', (0, 0, 255)], ['blue', (0, 0, 255)],
                ['blue', (0, 0, 255)], ['blue', (0, 0, 255)]],
               []],
              [[['green', (0, 255, 0)], ['red', (255, 0, 0)],
               ['green', (0, 255, 0)], ['red', (255, 0, 0)]],
              [1, 1, 1, 1]],
              [[['red', (255, 0, 0)], ['blue', (0, 0, 255)],
                ['green', (0, 255, 0)], ['blue', (0, 0, 255)]],
               [1, 0, 0]],
              [[['blue', (0, 0, 255)], ['blue', (0, 0, 255)],
                ['red', (255, 0, 0)], ['blue', (0, 0, 255)]],
               [0]],
              [[['green', (0, 255, 0)], ['red', (255, 0, 0)],
                ['green', (0, 255, 0)], ['blue', (0, 0, 255)]],
               [1, 1, 1]],
              [[['red', (255, 0, 0)], ['blue', (0, 0, 255)],
                ['green', (0, 255, 0)], ['blue', (0, 0, 255)]],
               [1, 0, 0]],
              [[['blue', (0, 0, 255)], ['blue', (0, 0, 255)],
                ['blue', (0, 0, 255)], ['blue', (0, 0, 255)]],
               []],
              [[['green', (0, 255, 0)], ['red', (255, 0, 0)],
               ['green', (0, 255, 0)], ['red', (255, 0, 0)]],
              [1, 1, 1, 1]]]
# grid_class = GuessGrid([350, 900])
# mock_grid = grid_class.draw_grid(mock_guess)
'''
ORDER TO DRAW EVERYTHING:
0. guesses made/guess_grid
1. background
2. slider_arm
3. current_colors/spinners
4. machine/foreground img
5  slider_button
6. buttons(first kivy buttons to link to event then img on top?)


while spinners are spinning: draw 3-5
when guess is made/lever moved draw 2-5
lever all way down = start spinners(and check buttons), wait til stopped,
compare to win sequence

when game is run:
1. get active colors & correct sequence
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
            if guess is correct- display something, let user choose to restart
            (and start at step 1 if they do)

TODO animation for slider
TODO animation for spinner
TODO button drawing
TODO spinner/random(?) logic
TODO connect to kivy

TODO: Make testable on computer: while keeping proportions for phone devices.
(use screen_h/2 as width?)

Notes:
app will consist of 2 'main' sections-

first- a grid in the background, displaying a grid specifying
the users guesses, and the feedback to those guesses.
this field is, apart from being scrollable, not interactive.
since this field is, to a degree drawn/displayed under
the other section of the app, it also need to draw a few more rows on the
grid than guessed, to allow the user to see
their last guess without problem. it should also automatically make
the users last guess visible (once the user makes
a guess- meaning, when the lever is drawn,
and wheels have stopped spinning, in the section 2 of the app)

second- the interactive section of the app-
this section displays the machine, the current colors, buttons to 'lock'
colors and a leaver to randomize unlocked colors
and make a guess from the result. This field is not scrollable.


layout/app-widget-design-plan:
1.main app-all of screen- draw background here- do not adjust proportions on
background, but put it at bottom of
the field, and match the with of the image to the with of the devices screen
2.guesses-field- somewhat overlap(or underlay to be precise)
the main widget of the game. this has the same size as screen, and is
scrollable- n of fields drawn =
    max([
        (n of guesses_made)
        (n of fields that fit in device height(size of fields has ratio 1:1,
        and is dictated by width(1/6 of width)) -6 )
        ])
    + 6 blank rows

This makes the seventh last row the one to display, but also,
makes scrolling as long as possible a working method for
centering on most interesting row.

the columns in this field represent:
1. guess number
2. color_guess 1
3. color_guess 2
4. color_guess 3
5. color_guess 4
6. guess evaluation/ displaying one symbol
when a color is present in correct sequence,
   and one color when both color and location is correct.
'''
