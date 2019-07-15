import pygame
from pygame.locals import *

import time

import platform

if platform.system() == 'Linux':
	import evdev
	from evdev import InputDevice, categorize, ecodes

from threading import Thread

from common.Config import Config
from common.Button import Button
from common.Timer import Timer

CONFIG_FILENAME = 'assets/config/config.json'
MAGNIFIER_BUTTON_POSITION = (42, 857)
IDLE_TIME = 300

from ft5406 import Touchscreen, TS_PRESS, TS_RELEASE, TS_MOVE

class Leonardo:
	def __init__(self):
		self.touchPos = (0,0)

	def start(self):
		self.idleTimer = Timer(IDLE_TIME, self.onIdle)
		self.blitCursor = True
		self.isMagnifying = False
		self.config = Config(CONFIG_FILENAME)

		self.touchScreenBounds = (self.config.getTouchScreenMaxX(), self.config.getTouchScreenMaxY())

		pygame.mixer.pre_init(44100, -16, 1, 512)
		pygame.init()
		pygame.mouse.set_visible(False)

		self.screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
		self.zoomRenderSurface = pygame.Surface(self.config.getMagnifierSize()).convert_alpha()
		self.cursor = pygame.image.load('assets/images/cursor.png').convert_alpha()
		self.magnifier = pygame.image.load('assets/images/magnifier.png').convert_alpha()
		self.magnifierPosition = (0,0)
		self.dragStartPos = None

		if self.config.isTouch():
			print("Loading touch screen...")
			self.setupTouchScreen()

		self.totalImagesNum = 21
		self.currIndex = 0
		self.loadImage()

		self.buttons = []

		self.prevButton = Button(self.screen, pygame.Rect(70, 1080 // 2 - 102 // 2, 56, 102), 
			pygame.image.load('assets/images/left_regular.png'), pygame.image.load('assets/images/left_selected.png'), 
			None, None, None, None, self.onPrevClick)
		self.buttons.append(self.prevButton)

		self.nextButton = Button(self.screen, pygame.Rect(1760, 1080 // 2 - 102 // 2, 56, 102), 
			pygame.image.load('assets/images/right_regular.png'), pygame.image.load('assets/images/right_selected.png'), 
			None, None, None, None, self.onNextClick)
		self.buttons.append(self.nextButton)

		self.magnifierOff = pygame.image.load('assets/images/magnifier_off.png')
		self.magnifierOn = pygame.image.load('assets/images/magnifier_on.png')
		self.magnifierButton = self.magnifierOff

		self.loop()

	def setupTouchScreen(self):
		self.device = evdev.InputDevice(self.config.getTouchDevice())
		self.readTouchThread = Thread(target=self.readTouch, args=())
		self.readTouchThread.daemon = True
		self.readTouchThread.start()

	def readTouch(self):
		print('THREAD UP!!!!')

		try:
			currX = 0
			currY = 0

			coordinatesChanged = 0

			isUp = False
			isDown = False

			# TODO: Change to read_one and alow thread to exit when marked
			for event in self.device.read_loop():
				if event.type == ecodes.SYN_REPORT:
					pos = (int(currX * 1920 / self.touchScreenBounds[0]), int(currY * 1080 / self.touchScreenBounds[1]))
					if isUp:
						print("UP!", pos)
						self.onMouseUp(pos)
					elif isDown:
						print("DOWN!", pos)
						self.onMouseDown(pos)
					else:
						self.touchPos = pos

					isUp = False
					isDown = False

				if event.type == ecodes.EV_KEY:
					keyEvent = categorize(event)
					if keyEvent.keycode[0] == 'BTN_LEFT' or keyEvent.keycode == 'BTN_TOUCH':
						if keyEvent.keystate == keyEvent.key_up:
							isUp = True
						elif keyEvent.keystate == keyEvent.key_down:
							isDown = True
				elif event.type == ecodes.EV_ABS:
					absEvent = categorize(event)

					if absEvent.event.code == 0:
						currX = absEvent.event.value
					elif absEvent.event.code == 1:
						currY = absEvent.event.value
		except e:
			print(str(e))

	def onIdle(self):
		self.isMagnifying = False
		self.updateMagnifierButton()
		self.currIndex = 0
		self.loadImage()

	def loadImage(self):
		self.currImage = pygame.image.load('assets/images/' + str(self.currIndex + 1) + '.png').convert()
		self.currZoomImage = pygame.image.load('assets/images/' + str(self.currIndex + 1) + '-big.png').convert()
		self.zoomFactor = self.currZoomImage.get_width() / self.currImage.get_width()

	def onNextClick(self):
		self.idleTimer = Timer(IDLE_TIME, self.onIdle)
		self.currIndex = (self.currIndex + 1) % self.totalImagesNum
		self.loadImage()

	def onPrevClick(self):
		self.idleTimer = Timer(IDLE_TIME, self.onIdle)
		self.currIndex = (self.currIndex - 1) % self.totalImagesNum
		self.loadImage()

	def toggleMagnifier(self):
		self.idleTimer = Timer(IDLE_TIME, self.onIdle)
		self.isMagnifying = not self.isMagnifying
		self.updateMagnifierButton()
	
	def updateMagnifierButton(self):
		self.magnifierButton = self.magnifierOn if self.isMagnifying else self.magnifierOff

	def onMouseDown(self, pos):
		for button in self.buttons:
			button.onMouseDown(pos)

		if Rect(MAGNIFIER_BUTTON_POSITION[0], MAGNIFIER_BUTTON_POSITION[1], self.magnifierButton.get_width(), self.magnifierButton.get_height()).collidepoint(pos):
			self.toggleMagnifier()

		if Rect(self.magnifierPosition[0], self.magnifierPosition[1], self.magnifier.get_width(), self.magnifier.get_height()).collidepoint(pos):
			self.idleTimer = Timer(IDLE_TIME, self.onIdle)
			self.dragStartPos = pos
			self.magnifierStartPos = self.magnifierPosition

	def onMouseUp(self, pos):
		for button in self.buttons:
			button.onMouseUp(pos)

		self.dragStartPos = None

	def onMouseMove(self, pos):
		if self.dragStartPos is not None:
			self.idleTimer = Timer(IDLE_TIME, self.onIdle)
			self.magnifierPosition = (pos[0] - self.dragStartPos[0] + self.magnifierStartPos[0], pos[1] - self.dragStartPos[1] + self.magnifierStartPos[1])

	def draw(self, dt):
		self.screen.blit(self.currImage, (0, 0))

		if self.isMagnifying:
			magnifierCenterPos = self.config.getMagnifierImageCenterPos()
			magnifierMidPos = (self.magnifierPosition[0] + magnifierCenterPos[0], self.magnifierPosition[1] + magnifierCenterPos[1])
			midZoomPos = (magnifierMidPos[0] * self.zoomFactor, magnifierMidPos[1] * self.zoomFactor)
			magnifierSize = self.config.getMagnifierSize()

			self.zoomRenderSurface.blit(self.currZoomImage, 
				(0, 0),
				Rect(midZoomPos[0] - magnifierSize[0] // 2, midZoomPos[1] - magnifierSize[1] // 2, magnifierSize[0], magnifierSize[1]))

			transparent = pygame.Color(0,0,0,0)
			for i in range(125):
				for j in range(125 - i):
					self.zoomRenderSurface.set_at((i,j), transparent)
					self.zoomRenderSurface.set_at((magnifierSize[0] - i,j), transparent)
					self.zoomRenderSurface.set_at((i,magnifierSize[1] - j), transparent)
					self.zoomRenderSurface.set_at((magnifierSize[0] - i,magnifierSize[1] - j), transparent)

			self.screen.blit(self.zoomRenderSurface, 
				(self.magnifierPosition[0] + magnifierCenterPos[0] - magnifierSize[0] // 2, self.magnifierPosition[1] + magnifierCenterPos[1] - magnifierSize[1] // 2))

			self.screen.blit(self.magnifier, self.magnifierPosition)

		for button in self.buttons:
			button.draw()

		self.screen.blit(self.magnifierButton, MAGNIFIER_BUTTON_POSITION)

	def loop(self):
		isGameRunning = True
		clock = pygame.time.Clock()
		lastTime = pygame.time.get_ticks()
		font = pygame.font.Font(None, 30)

		while isGameRunning:
			for event in pygame.event.get():
				if event.type == MOUSEBUTTONDOWN:
					if not self.config.isTouch():
						self.onMouseDown(event.pos)
				elif event.type == MOUSEBUTTONUP:
					if not self.config.isTouch():
						self.onMouseUp(event.pos)
				elif event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						isGameRunning = False

			if not self.config.isTouch():
				self.onMouseMove(pygame.mouse.get_pos())
			else:
				pos = self.touchPos
				self.onMouseMove(pos)

			self.screen.fill([0,0,0])
			currTime = pygame.time.get_ticks()
			dt = currTime - lastTime
			lastTime = currTime

			self.draw(dt / 1000)
			self.idleTimer.tick(dt / 1000)

			if not self.config.isTouch() and self.blitCursor:
				self.screen.blit(self.cursor, (pygame.mouse.get_pos()))

			fps = font.render(str(int(clock.get_fps())), True, Color('white'))
			self.screen.blit(fps, (50, 50))

			pygame.display.flip()
			clock.tick(60)

		pygame.quit()

if __name__ == '__main__':
	Leonardo().start()
