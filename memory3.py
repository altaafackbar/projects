from uagame import Window
import pygame, time
from pygame.locals import *
import math, random

# User-defined functions

def main():

   window = Window('Tic Tac Toe', 500, 400)
   window.set_auto_update(False)   
   game = Game(window)
   game.play()
   window.close()

# User-defined classes
 
class Game:
   # An object in this class represents a complete game.

   def __init__(self, window):
      # Initialize a Game.
      # - self is the Game to initialize
      # - window is the uagame window object
      
      self.window = window
      Tile.set_window(window)
      self.bg_color = 'black'
      self.pause_time = 0.01 # smaller is faster game
      self.close_clicked = False
      self.continue_game = True
      self.hidden = 'image0.bmp'
      self.score = 0 
      self.board = []
      self.images = []
      self.make_list()    
      self.create_board()

      
   def make_list(self):
      for index in range(1, 9):
         image =('image' + str(index) + '.bmp')
         self.images.append(image)
      for i in range(0, 8):
         self.images.append(self.images[i])
      random.shuffle(self.images)  
    
      
   def create_board(self):
      # Create the game board.
      # - self is the Game whose board is created

      for row_index in range(0, 4):
         row = self.create_row(row_index)
         self.board.append(row)
         

      
   def create_row(self, row_index):
      # Create one row of the board
      # - self is the Game whose board row is being created
      # - row_index is the int index of the row starting at 0
      row = []
      width = self.window.get_width() // 5
      height = self.window.get_height() // 4
      y = row_index * height
      for col_index in range(0, 4):
         x = col_index * width
         tile = Tile(x, y, width, height, self.images.pop(), self.hidden)
         row.append(tile)

      return row

   def play(self):
      # Play the game until the player presses the close box.
      # - self is the Game that should be continued or not.

      while not self.close_clicked:  # until player clicks close box
         # play frame
         self.handle_event()          
         if self.continue_game:
            self.draw()
            self.update()
            self.decide_continue()
         #time.sleep(self.pause_time) # set game velocity by pausing

   def handle_event(self):
      # Handle each user event by changing the game state
      # appropriately.
      # - self is the Game whose events will be handled

      event = pygame.event.poll()
      if event.type == QUIT:
         self.close_clicked = True
      elif event.type == MOUSEBUTTONUP and self.continue_game:
         self.handle_mouse_up(event)
         
   def handle_mouse_up(self, event):
      # Respond to the player releasing the mouse button by
      # taking appropriate actions.
      # - self is the Game where the mouse up occurred.
      # - event is the pygame.event.Event object to handle
      
      for row in self.board:
         for tile in row:
            tile.select(event.pos)


      

   def draw(self):
      # Draw all game objects.
      # - self is the Game to draw
      
      self.window.clear()
      for row in self.board:
         for tile in row:
            tile.draw()
      self.draw_score()
      self.window.update()
      
   def draw_score(self):
      self.score = pygame.time.get_ticks() // 1000
      self.window.set_font_color('white')
      x = self.window.get_string_width(str(self.score))
      self.window.set_font_size(80)
      self.window.draw_string(str(self.score), 500 - x, 0)
      
      
   def update(self):
      # Update the game objects.
      # - self is the Game to update
      pass

   def decide_continue(self):
      # Check and remember if the game should continue
      # - self is the Game to check
      if len(Tile.matches) == 8:
         self.continue_game = False

   
class Tile:
   # An object in this class represents a Rectangular tile
   # that contains a string. A new tile contains an empty
   # string. A tile can be selected if the tile contains a
   # position. If an empty tile is selected its string can
   # be changed. If a non-empty tile is selected it will flash
   # the next time it is drawn. A tile can also be set to
   # flash forever. Two tiles are equal if they contain the
   # same non-empty string.


   # initialize the class attributes that are common to all tiles.
   window = None
   fg_color = pygame.Color('black')  # for drawing the border
   border_width = 3 # the pixel width of the tile border
   selected = []
   matches = []
   
   @classmethod
   def set_window(cls, window):
      # remember the window
      cls.window = window
   
   def __init__(self, x, y, width, height, image, hidden):
      # Initialize a tile to contain a ' '
      # - x is the int x coord of the upper left corner
      # - y is the int y coord of the upper left corner
      # - width is the int width of the tile
      # - height is the int height of the tile
      
      self.rectangle = pygame.Rect(x, y, width, height)
      self.hidden = hidden
      self.image = image
      self.reveal = False

         
   def draw(self):
      # Draw the tile on the surface
      # - self is the Tile
      myimage = pygame.image.load(self.image)
      hidden = pygame.image.load(self.hidden)
     
      if self.reveal == True:
         rect = Tile.window.get_surface().blit(myimage, self.rectangle)
         pygame.draw.rect(Tile.window.get_surface(), Tile.fg_color, rect, Tile.border_width)
         if self.image in Tile.matches:
            pass
         
         elif len(Tile.selected) == 0:
            time.sleep(0.45)     
            self.reveal = False           

         elif len(Tile.selected) == 2:
            if Tile.selected[0] == Tile.selected[1]:
               Tile.matches.append(self.image)
               Tile.selected.clear()
               
            elif Tile.selected[0] != Tile.selected[1]:
               Tile.selected.clear()
  
       
      else:
         h_rect = Tile.window.get_surface().blit(hidden, self.rectangle)
         pygame.draw.rect(Tile.window.get_surface(), Tile.fg_color, h_rect, Tile.border_width)         
            
      

      
   def select(self, mouse_position):
      # A position was selected. If the position is in the Tile
      # and the Tile is empty, then update the Tile content
      # - self is the Tile
      # - position is the selected location (tuple)
      # - new_content is the new str contents of the tile
      selected = []
      if self.rectangle.collidepoint(mouse_position) and self.reveal == False:
         self.reveal = True
         Tile.selected.append(self.image)
         
         

      


main()