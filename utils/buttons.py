from utils.graphics import *

class RectangularButton:
	def __init__(self, win, center, width, height, label, background_color="black", outline_color="white", label_color="white"):
		# Creates a rectangular button with specified position, dimensions, and label 
		self.win = win

		cx, cy = center.getX(), center.getY()
		self.xmin, self.xmax = cx - width/2, cx + width/2
		self.ymin, self.ymax = cy - height/2, cy + height/2

		self.rect = Rectangle(Point(self.xmin, self.ymin), Point(self.xmax, self.ymax))
		self.rect.setFill(background_color)
		self.rect.setOutline(outline_color)

		self.display_text = Text(center, label)
		self.display_text.setTextColor(label_color)

		self.rect.draw(self.win)
		self.display_text.draw(self.win)

	def clicked(self, pt):
		# returns True if button is clicked
		return (self.xmin < pt.getX() < self.xmax) and (self.ymin < pt.getY() < self.ymax)

	def getLabel(self):
		return self.display_text.getText()

	def setColor(self, color):
		self.rect.setFill(color)

	def setTextColor(self, color):
		self.display_text.setTextColor(color)

	def undraw(self):
		self.rect.undraw()
		self.display_text.undraw()