import random

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
    def __init__(self, n_colors) -> None:
        self.active_colors = self.get_active_colors(n_colors)
        self.correct_sequence = self.get_game_sequence()
    
    def get_game_sequence(self):
        correct = []
        for _ in range(4):
            correct.append(random.choice(self.active_colors))
        return correct
    
    @staticmethod
    def get_active_colors(n_colors):
        color_options = {'red':(255,0,0), 'orange':(255,128,0),
                         'yellow':(255,255,0), 'lime':(128,255,0),
                         'green':(0,255,0), 'turquoise':(0, 255, 255), 
                         'blue':(0,128,255), 'deepblue':(0,0,255),
                         'purple':(127,0,255), 'magenta':(255,0,255),
                         'pink':(255, 0, 127)}
        colors_choosen = []
        for color in range(n_colors):
            color = random.choice(color_options)
            del color_options[color]
            colors_choosen.append(color)
        return colors_choosen

class GameStatus:
    def __init__(self) -> None:
        self.guesses = []
        self.game_won = False

    def compare_to_sequence(self, correct_sequence, guessed_sequence):
        results = [0]
        temp_corr = correct_sequence
        for correct, guess in zip (correct_sequence,
                                   guessed_sequence):
            if correct == guess:
                results.append(1)
                temp_corr.remove(guess)
            elif guess in temp_corr:
                results.append(0)
                temp_corr.remove(guess)
        results.sort()
        self.guesses.append([guess, results])
        if sum(results) == len(correct_sequence):
            self.game_won = True


class GuessGrid:
    """
    Draws grid/background displaying the users guesses
    This should be a scrollable field.
    """
    def __init__(self, texture_size):
        pass

    def draw_grid(self):
        pass
    
    def draw_guesses(self, new_guess):
        pass


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

'''