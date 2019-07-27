import json

class Config:

	def __init__(self, filename):
		with open(filename) as file:
			self.config = json.load(file)

	def isTouch(self):
		return self.config['touch']

	def setTouch(self, value):
		self.config['touch'] = value

	def getTouchDevicePartialName(self):
		return self.config['touchDeviceName']

	def getTouchScreenMaxX(self):
		return self.config['touchMaxX']

	def getTouchScreenMaxY(self):
		return self.config['touchMaxY']

	def getMagnifierImageCenterPos(self):
		return (self.config['magnifierImageCenterX'], self.config['magnifierImageCenterY'])

	def getMagnifierInitialPosition(self):
		return (self.config['magnifierInitialPositionX'], self.config['magnifierInitialPositionY'])

	def getMagnifierSize(self):
		return (self.config['magnifierWidth'], self.config['magnifierHeight'])

	def showFPS(self):
		return (self.config['showFPS'])
