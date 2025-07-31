from utils.graphics import *
from math import cos, sin, radians, sqrt
from random import randrange
from time import time
from utils.buttons import RectangularButton

def main():
	game = CannonballGame()
	game.play()

class CannonballGame:
	def __init__(self):

		# window
		self.background_color = "black"
		self.foreground_color = "white"
		self.win = GraphWin("Cannonball Game", 1300, 800)
		self.win.setBackground(self.background_color)
		self.win.setCoords(-15,-10,115,70)

		# grid
		self.grid = Grid(self.win, origin=Point(0,0), length=105, height=55, tick_interval=10, tick_size=4, color=self.foreground_color)

		# instructions
		self._createInstructions()

		# launch arrow
		self.arrow = LaunchArrow(self.win, magnitude=20, color=self.foreground_color)

		# shots in motion
		self.shots = []
		self.shot_radius = 1 
		self.shot_color = self.foreground_color
		self.frame_rate = 20

		# ammunition bar
		self.ammo = VerticalAmmoBar(self.win, xpos=-10, num_shots=10, ammo_radius=1, ammo_spacing=3, ammo_color=self.foreground_color)

		# target
		self.target = Target(self.win, radius=4, ring_scores=[40,30,20,10], ring_colors=["green", "yellow", "orange", "red4"])

		# timer (for moving target)
		self.start_time = time()
		self.current_time = self.start_time
		self.timer_delay = 4
		
		# score
		self.score = Score(self.win, center=Point(50,55), font_size=28, color="yellow")

		# goal prompt
		self.goal = 100
		self.prompt = Text(Point(50,63), f"Get to {self.goal} points!")
		self.prompt.setSize(20)
		self.prompt.setTextColor(self.foreground_color)
		self.prompt.draw(self.win)

		# legend
		self._createLegend()

		# outcome of game
		self.outcome = Text(Point(50,40), "")
		self.outcome.setSize(36)

	def _createInstructions(self):
		s1 = "\u2190 \u2192  Control Power"
		s2 = "\u2191 \u2193 Control Angle"
		s3 = "Press 'F' to Fire"

		instructions = [
			Text(Point(100,65), f"{s1:<20}"), 
			Text(Point(100,62), f"{s2:<20}"),
			Text(Point(100,59), f"{s3:<20}"),]

		for inst in instructions:
			inst.setSize(16)
			inst.setTextColor(self.foreground_color)
			inst.draw(self.win)

	def _createLegend(self):
		sqs = [
		Rectangle(Point(96,53), Point(98, 55)),
		Rectangle(Point(96,50), Point(98, 52)),
		Rectangle(Point(96,47), Point(98, 49)),
		Rectangle(Point(96,44), Point(98, 46)),]

		for i in range(len(sqs)):
			sqs[i].setFill(self.target.getRingColors()[i])
			sqs[i].setOutline(self.foreground_color)
			sqs[i].draw(self.win)

		labels = [
				Text(Point(102,54),""),
				Text(Point(102,51),""),
				Text(Point(102,48),""),
				Text(Point(102,45),""),
				]
		for i in range(len(labels)):
			labels[i].setText(f"{f"{self.target.getRingScores()[i]} pts":<10}")
			labels[i].setTextColor(self.foreground_color)
			labels[i].draw(self.win)


	def play(self):

		while True:
			# Moves target on timer
			self.current_time = time()
			if (self.current_time - self.start_time) > self.timer_delay:
				self.start_time = self.current_time
				self.target.newTarget() 

			self._checkHits() 	# Checks for hits and updates score

			# Checks for commands 
			key = self.win.checkKey()
			if key:
				if key in ["Right", "Left", "Up", "Down"]:	# Adjust launch arrow
					self.arrow.adjustArrow(key)				
				if key in ['f', 'F']:						# Fire
					self.ammo.useUp()						
					a,v = self.arrow.getSpecs()				
					shot = Cannonball(self.win, a, v, height=0, time_step=0.05, radius=self.shot_radius, color=self.shot_color)
					self.shots.append(shot) 				


			self._updateShots() 					# Updates shot animations
			update(self.frame_rate) 				# Update/frame rate

			if (self.ammo.getShotsLeft() == 0):		# Exits when ammo runs out
				break

		while self.shots:		# Finishes rest of shot animations
			self._checkHits()
			self._updateShots()
			update(self.frame_rate)

		self._showOutcome()		# Shows outcome of game
	
		# Play again
		play_again = RectangularButton(self.win, center=Point(50,30), width=10, height=5, label="Play Again", 
			background_color="blue4", outline_color=self.foreground_color, label_color=self.foreground_color)
		while True:
			pt = self.win.getMouse()
			if play_again.clicked(pt):
				play_again.undraw()
				self.outcome.undraw()
				break

		self._resetGame()
		self.play()

	def _updateShots(self):
		# Updates live shots and their positions
		# Once shot is out of play, the shot value is added to the total score

		alive = []
		for shot in self.shots:
			shot.update()
			if (0 <= shot.getX() < 100) and (0 <= shot.getY()):
				alive.append(shot)
			else:
				self.score.scorePoints(shot.getScore())
				shot.undraw()
		self.shots = alive

	def _checkHits(self):
		# Passes shot hitbox points to target to check for hits
		# Shot score and color get updated based on rings hit (highest value ring)

		for shot in self.shots:
			pts = shot.getHitbox()
			for pt in pts:
				hit = self.target.hit(pt)
				if hit:
					shot.addHit(hit)

			shot_hits = shot.getObjectsHit()

			for ring in self.target.getRings():
				if ring.getName() in shot_hits:
					shot.setColor(ring.getColor())
					shot.setScore(ring.getScore())
					break

	def _showOutcome(self):
		# Shows outcome of game

		if self.score.getScore() >= self.goal:
			self.outcome.setTextColor("green")
			self.outcome.setText("You Win!")
		else:
			self.outcome.setTextColor("red4")
			self.outcome.setText("You Lose!")

		self.outcome.draw(self.win)

	def _resetGame(self):
		self.score.setScore(0) # Reset score
		self.ammo.reset() 	   # Reset ammo
		self.win.checkKey()    # Clear key presses		

class Grid:
	def __init__(self, win, origin, length, height, tick_interval, tick_size, color):
		# axes and axis labels
		self.win = win
		ox = origin.getX()
		oy = origin.getY()
		x_axis = Line(origin, Point(ox+length,oy))
		y_axis = Line(origin, Point(ox,oy+height))
		x_axis.setArrow("last")
		y_axis.setArrow("last")
		x_axis.setFill(color)
		y_axis.setFill(color)
		x_axis.draw(self.win)
		y_axis.draw(self.win)

		# ticks and tick labels
		x = ox
		while x < ox+length:
			tick = Line(Point(x,oy-tick_size/2), Point(x,oy+tick_size/2))
			label = Text(Point(x,oy-tick_size), f"{x:.0f}")
			tick.setFill(color)
			label.setFill(color)
			tick.draw(self.win)
			label.draw(self.win)
			x += tick_interval

		y = oy
		while y < oy+height:
			tick = Line(Point(ox-tick_size/2,y), Point(ox+tick_size/2,y))
			label = Text(Point(ox-tick_size, y), f"{y:.0f}")
			tick.setFill(color)
			label.setFill(color)
			tick.draw(self.win)
			label.draw(self.win)
			y += tick_interval



class Cannonball:
	# Cannonball projectile; keeps track of the score of the shot

	def __init__(self, win, angle, velocity, height, time_step, radius, color):
		self.win = win

		# kinematics initialization
		x = 0
		y = height
		theta = radians(angle)
		self.xvel = velocity * cos(theta)
		self.yvel = velocity * sin(theta)
		self.time_step = time_step	# time interval between updates

		# marker
		self.radius = radius
		self.color = color
		self.circ = Circle(Point(x,y), self.radius)
		self.circ.setFill(color)
		self.circ.draw(self.win)

		# hitbox
		ll = Point(x-self.radius, y-self.radius)
		ul = Point(x-self.radius, y+self.radius)
		ur = Point(x+self.radius, y+self.radius)
		lr = Point(x+self.radius, y-self.radius)
		self.hitbox = [ur, lr, ll, ul]

		# all objects the shot hits
		self.objects_hit = set()

		# points scored by the shot
		self.score = 0
	
	def update(self):
		# Moves projectile through one time_step
		dx = self.xvel * self.time_step
		endvel = self.yvel - 9.8 * self.time_step
		avgvel = 0.5 * (self.yvel + endvel)
		dy = avgvel * self.time_step
		self.yvel = endvel

		self.circ.move(dx,dy)

		for pt in self.hitbox:
			pt.move(dx,dy)

	def getHitbox(self):
		return self.hitbox

	def getX(self):
		return self.circ.getCenter().getX()

	def getY(self):
		return self.circ.getCenter().getY()

	def undraw(self):
		self.circ.undraw()

	def setColor(self, color):
		self.color = color
		self.circ.setFill(self.color)

	def addHit(self, obj):
		self.objects_hit.add(obj)

	def getObjectsHit(self):
		return self.objects_hit

	def setScore(self, score):
		self.score = score

	def getScore(self):
		return self.score


class Target:
	# Moving target

	def __init__(self, win, radius, ring_scores, ring_colors):
		self.win = win
		self.ring_colors = ring_colors
		self.ring_scores = ring_scores
		self.rings = []
		dummy = Point(0,0)
		num_rings = len(ring_scores)
		for i in range(num_rings):
			ring = TargetRing(center=dummy, radius=(i+1)*(radius/num_rings), num=i+1, score=ring_scores[i], color=ring_colors[i])
			self.rings.append(ring)
		self.newTarget()
		for ring in self.rings:
			ring.draw(self.win)

	def _move(self, dx, dy):
		for ring in self.rings:
			ring.move(dx,dy)

	def getCenter(self):
		return self.rings[0].getCenter()

	def getRings(self):
		return self.rings

	def getRingColors(self):
		return self.ring_colors

	def getRingScores(self):
		return self.ring_scores

	def newTarget(self):
		# Moves the target to a new random position
		x = randrange(50, 90)
		y = randrange(10, 45)
		dx = x - self.getCenter().getX()
		dy = y - self.getCenter().getY()
		self._move(dx,dy)

	def hit(self, pt):
		# Returns which ring a pt hits
		tc = self.getCenter()
		cx = tc.getX()
		cy = tc.getY()
		x = pt.getX()
		y = pt.getY()
		dist = sqrt((x-cx)**2 + (y-cy)**2)
		for ring in self.rings:
			if dist<ring.getRadius():
				return ring.getName()		
		return ""

class TargetRing:
	# Single ring of the target
	def __init__(self, center, radius, num, score, color):
		self.num = num
		self.radius = radius
		self.color = color
		self.name = "Ring" + str(num)
		self.score = score 
		self.circ = Circle(center, self.radius)
		self.circ.setOutline(color)

	def draw(self, win):
		self.circ.draw(win)

	def move(self, dx, dy):
		self.circ.move(dx,dy)

	def getCenter(self):
		return self.circ.getCenter()

	def getRadius(self):
		return self.radius

	def getName(self):
		return self.name

	def getScore(self):
		return self.score

	def getColor(self):
		return self.color


class VerticalAmmoBar:
	# Represents how many shots player has left

	def __init__(self, win, xpos, num_shots, ammo_radius, ammo_spacing, ammo_color):
		self.win = win
		self.balls = []
		self.xpos = xpos
		self.num_shots = num_shots
		self.ammo_radius = ammo_radius
		self.ammo_spacing = ammo_spacing
		self.ammo_color = ammo_color
		

		for y in range(self.ammo_spacing, self.num_shots*self.ammo_spacing, self.ammo_spacing):
			circ = Circle(Point(self.xpos,y), self.ammo_radius)
			circ.setFill(self.ammo_color)
			circ.draw(self.win)
			self.balls.append(circ)

	def useUp(self):
		# Uses up a single ammunition

		if len(self.balls) > 0:
			self.balls[-1].undraw()
			self.balls.pop()

	def getShotsLeft(self):
		return len(self.balls)

	def reset(self):
		# Resets ammo back to initial num_shots
		for y in range(self.ammo_spacing, self.num_shots*self.ammo_spacing, self.ammo_spacing):
			circ = Circle(Point(self.xpos,y), self.ammo_radius)
			circ.setFill(self.ammo_color)
			circ.draw(self.win)
			self.balls.append(circ)



class LaunchArrow:
	# An arrow which represents the kinematic specification for the shot

	def __init__(self, win, magnitude, color):
		self.win = win
		self.delta_mag = 1			# magnitude step size
		self.delta_ang = 5			# angle step size
		self.max_mag = magnitude	# max magnitude bound
		self.max_ang = 90			# max angle bound (degrees)
		self.ratio_magtovel = 1/2	# ratio between arrow magnitude and shot velocity 

		# initial arrow
		self.magnitude = magnitude/2
		self.angle = 45
		self.marker = Line(Point(0,0), Point(0,0))
		self.marker.setFill(color)
		self.marker.draw(self.win)
		self._redraw()

	def adjustArrow(self, key):
		# Adjusts arrow based on key pressed
		self._updateSpecs(key)
		self._redraw()

	def _updateSpecs(self, key):
		# Changes arrow specs by step size each key press (within bounds)
		if key == "Right":
			if self.magnitude < self.max_mag-self.delta_mag:
				self.magnitude += self.delta_mag
		elif key == "Left":
			if self.magnitude > self.delta_mag:
				self.magnitude -= self.delta_mag
		elif key == "Up":
			if self.angle < self.max_ang - self.delta_ang:
				self.angle += self.delta_ang
		elif key == "Down":
			if self.angle > self.delta_ang:
				self.angle -= self.delta_ang	

	def _redraw(self):
		# Updates arrow marker 
		self.marker.undraw()
		theta = radians(self.angle)
		self.marker = Line(Point(0,0), Point(self.magnitude*cos(theta),self.magnitude*sin(theta)))
		self.marker.setArrow("last")
		self.marker.setFill("white")
		self.marker.draw(self.win)

	def getSpecs(self):
		# Gets angle and velocity specification
		a = self.angle
		v = self.magnitude/self.ratio_magtovel
		return a,v


class Score:
	def __init__(self, win, center, font_size, color):
		self.win = win
		self.score = 0
		self.score_display = Text(center, str(self.score))
		self.score_display.setSize(font_size)
		self.score_display.setTextColor(color)
		self.score_display.draw(self.win)

	def scorePoints(self, points):
		self.score += points
		self.score_display.setText(str(self.score))

	def setScore(self, score):
		self.score = score
		self.score_display.setText(str(self.score))

	def getScore(self):
		return self.score

if __name__ == "__main__":
	main()