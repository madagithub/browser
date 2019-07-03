import pygame
from pygame.locals import *

from common.Utilities import Utilities

class Button:
	def __init__(self, screen, rect, image, tappedImage, text, color, selectedColor, font, onClickCallback):
		self.screen = screen
		self.rect = rect
		self.image = image
		self.tappedImage = tappedImage
		self.color = color
		self.selectedColor = selectedColor
		self.visible = True

		self.createText(text, font)

		self.onClickCallback = onClickCallback
		self.isMouseDownOnButton = False

	def createText(self, text, font):
		if text is not None:
			self.textBox = font.render(text, True, self.color)
			self.selectedTextBox = font.render(text, True, self.selectedColor)
		else:
			self.textBox = None

	def draw(self):
		if self.visible:
			self.screen.blit(self.tappedImage if self.isMouseDownOnButton else self.image, (self.rect.left, self.rect.top))

			if self.textBox is not None:
				Utilities.drawTextOnCenter(self.screen, self.selectedTextBox if self.isMouseDownOnButton else self.textBox, self.rect.center)

	def onMouseDown(self, position):
		if self.visible:
			self.isMouseDownOnButton = self.rect.collidepoint(position)

	def onMouseUp(self, position):
		if self.visible:
			if self.rect.collidepoint(position) and self.isMouseDownOnButton:
				self.onClickCallback()

			self.isMouseDownOnButton = False

