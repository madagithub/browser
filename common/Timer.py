class Timer:
	def __init__(self, time, callback):
		self.timeLeft = time
		self.timePassed = 0
		self.callback = callback

	def tick(self, dt):
		self.timeLeft -= dt
		self.timePassed += dt
		if self.timeLeft <= 0:
			self.callback()

	def getSeconds(self):
		return self.timePassed