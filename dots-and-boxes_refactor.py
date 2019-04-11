# Ryan Croke, 4-10-2019
"""
This is a refactor of some code I found on the internet sorry, no attribution :(
It is intended to be used to build a reinforcement learning algorithm
to master dots and boxes as has been done over and over for tic-tac-toe
"""
import tkinter as tk
from tkinter import font, messagebox
import sys
import numpy as np
 

class Player(object):
	"""
	The Player class stores the players name, and score and uses the tkinter
	StringVar to immediately update the gui
	"""
	def __init__(self, name, color="black"):
		self.score = 0
		self.players_display_score = tk.StringVar()
		self.name = name
		self.color = color

	def update(self):
		self.players_display_score.set(self.name + ": %d" % self.score)

class DotsAndBoxes(tk.Frame):
	def __init__(self, master, size_board=5):
		# assert size_board % 2 == 0,"cannot play game that could end in tie"
		self.TOL = 10
		self.CELLSIZE = 44
		self.OFFSET = 30
		self.CIRCLERAD = 2
		self.DOTOFFSET = self.OFFSET + self.CIRCLERAD
		self.NMBR_ROWS = size_board
		self.GAMEBOARD_SIZE = self.CELLSIZE*(self.NMBR_ROWS-1) + 2*self.OFFSET
		
		tk.Frame.__init__(self, master)

		self.display_font = tk.font.Font(self, name="display_font",
			                             family = "Times", weight="bold",
			                             size=36)
		self.canvas = tk.Canvas(self, height = self.GAMEBOARD_SIZE,
			                    width = self.GAMEBOARD_SIZE, bg="yellow")
		self.canvas.bind("<Button-1>", lambda e:self.click(e))
		self.canvas.grid(row=0,column=0)

		self.dots = [[self.create_circle(self.CELLSIZE*i+self.OFFSET, self.CELLSIZE*j+self.OFFSET,
			          self.CIRCLERAD) for j in range(self.NMBR_ROWS)] 
		              for i in range(self.NMBR_ROWS)]
		self.lines = []
		self.center_points = self.dots_center_coordinates()
		self.info_frame = tk.Frame(self)
		self.player_one = Player("Player 1", "blue")
		self.player_two = Player("Player 2", "red")

		self.info_frame.player_one = tk.Label(self.info_frame, textvariable = self.player_one.players_display_score)
		self.info_frame.player_one.grid()

		self.info_frame.player_two = tk.Label(self.info_frame, textvariable = self.player_two.players_display_score)
		self.info_frame.player_two.grid()

		self.turn = self.player_one
		self.update_players()
		self.info_frame.grid(row = 1, column = 0, sticky = 'N')
		self.grid()

	def create_circle(self, x, y, r):
		"""
		center coordinates, radius
		"""
		x0 = x - r
		y0 = y - r
		x1 = x + r
		y1 = y + r
		return self.canvas.create_oval(x0, y0, x1, y1, fill="black")

	def update_players(self):
		self.player_one.update()
		self.player_two.update()

	def dots_center_coordinates(self):
		center_points = []
		for i in range(self.NMBR_ROWS):
			center_points.append(self.CELLSIZE*i+self.OFFSET)
		return center_points

	def get_closest_coordinate(self, x, points_list):
		diffs = [abs(x - val) for val in points_list]
		return points_list[diffs.index(min(diffs))]


	def click(self, event):
		x,y = event.x, event.y
		orient = self.get_clicked_orientation_plane(x,y)

		if orient:
			if self.line_exists(x, y, orient):
				return

			line = self.create_line(x, y, orient)
			score = self.make_new_box(line)

			if score:
				self.turn.score += score
				self.turn.update()
				self.check_game_over()
			else:
				if self.turn.name == "Player 1":
					self.turn = self.player_two
				else:
					self.turn = self.player_one

			self.lines.append(line)

	def get_clicked_orientation_plane(self, x, y):

		limit_small = self.OFFSET - self.CIRCLERAD
		if (x < limit_small)  or (y < limit_small):
			return None

		limit_large = limit_small + (self.NMBR_ROWS-1)*self.CELLSIZE
		limit_large += 2*self.CIRCLERAD
		if (x > limit_large)  or (y > limit_large):
			return None

		# print("Raw:",x,y)
		# print("closest x:",self.get_closest_coordinate(x,self.center_points))
		# print("closest y:",self.get_closest_coordinate(y,self.center_points))
		# print("x diff:", x - self.get_closest_coordinate(x,self.center_points))
		# print("y diff:", y - self.get_closest_coordinate(y,self.center_points))

		dx = x - self.get_closest_coordinate(x,self.center_points)
		dy = y - self.get_closest_coordinate(y,self.center_points)

		x -= self.OFFSET
		y -= self.OFFSET
		dx = x - (x//self.CELLSIZE)*self.CELLSIZE
		dy = y - (y//self.CELLSIZE)*self.CELLSIZE

		if np.linalg.norm([dx,dy]) < np.sqrt(self.TOL):
			return None

		if abs(dx) < self.TOL:
			if abs(dy) < self.TOL:
				return None  # mouse in corner of box; ignore
			else:
				return 'VERTICAL'
		elif abs(dy) < self.TOL:
			return 'HORIZONTAL'
		else:
			return None

	def line_exists(self, x, y, orient):
		id_ = self.canvas.find_closest(x, y, halo=self.TOL)[0]
		if id_ in self.lines:
			return True
		else:
			return False

	def create_line(self, x, y, orient='HORIZONTAL'):
		startx = self.get_dot_coordinate_from_click(x)
		starty = self.get_dot_coordinate_from_click(y)

		if orient == 'HORIZONTAL':
			endx = startx + self.CELLSIZE
			endy = starty
		else:
			endx = startx
			endy = starty + self.CELLSIZE
		return self.canvas.create_line(startx,starty,endx,endy)

	def get_dot_coordinate_from_click(self, coordinate):
		dot_coordinate = self.CELLSIZE * ((coordinate-self.OFFSET)//self.CELLSIZE) 
		dot_coordinate = dot_coordinate + self.DOTOFFSET - self.CIRCLERAD
		return dot_coordinate

	def make_new_box(self, line):
		score = 0
		x0,y0,x1,y1 = self.canvas.coords(line)

		if x0 == x1:
			midx = x0
			midy = (y0+y1)/2
			pre = (x0 - self.CELLSIZE/2, midy)
			post = (x0 + self.CELLSIZE/2, midy)

		elif y0 == y1:
			midx = (x0 + x1)/2
			midy = y0
			pre = (midx, y0 - self.CELLSIZE/2)
			post = (midx, y0 + self.CELLSIZE/2)

		if len(self.find_lines(pre)) == 3:
			self.fill_in_square(pre)
			score += 1

		if len(self.find_lines(post)) == 3:
			self.fill_in_square(post)
			score += 1
		return score

	def find_lines(self, coords):
		x, y = coords
		if x < 0 or x > self.GAMEBOARD_SIZE:
			return []
		if y < 0 or y > self.GAMEBOARD_SIZE:
			return []

		lines = [x for x in self.canvas.find_enclosed(x-self.CELLSIZE,\
                                                      y-self.CELLSIZE,\
                                                      x+self.CELLSIZE,\
                                                      y+self.CELLSIZE)\
				if x in self.lines]
		return lines

	def fill_in_square(self, coords):
		"""
		Given the top left coordinate, fill in square with players color
		"""
		x, y = coords
		startx = self.get_dot_coordinate_from_click(x)
		starty = self.get_dot_coordinate_from_click(y)
		endx = startx + self.CELLSIZE
		endy = starty + self.CELLSIZE

		return self.canvas.create_rectangle(startx, starty, endx, endy,
			                                fill=self.turn.color)

	def check_game_over(self):
		total = self.player_one.score + self.player_two.score

		if total == (self.NMBR_ROWS-1) * (self.NMBR_ROWS-1):
			self.canvas.create_text(self.GAMEBOARD_SIZE/2, self.GAMEBOARD_SIZE/2,
				                    text="GAME OVER", font="display_font", fill="#888")

mainw = tk.Tk()
mainw.frm = DotsAndBoxes(mainw)
mainw.mainloop()