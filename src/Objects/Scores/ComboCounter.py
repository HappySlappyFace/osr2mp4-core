from math import ceil

from Objects.abstracts import *


class ComboCounter(Images):
	def __init__(self, scorenumbers, width, height, gap, scale):
		self.height = height
		self.width = width
		self.score_images = scorenumbers.score_images
		self.score_images.append(scorenumbers.score_x)

		self.score_frames = []
		self.score_fadeout = []

		self.score_index = 0
		self.index_step = 1
		self.fadeout_index = 0

		self.combofadeout = 0
		self.combo = 0
		self.breaking = False
		self.adding = False
		self.animate = False

		self.gap = int(gap * scale)

		self.prepare_combo()

	def prepare_combo(self):
		for digit in range(len(self.score_images)):
			self.score_frames.append([])
			self.score_fadeout.append([])
			for x in range(100, 131, 3):
				self.score_images[digit].change_size(x/100, x/100)
				normal = self.score_images[digit].img
				self.score_frames[-1].append(normal)

			for x in range(180, 109, -7):
				self.score_images[digit].change_size(x/100, x/100)
				fadeout = super().newalpha(self.score_images[digit].img, (x/300))
				self.score_fadeout[-1].append(fadeout)

	def breakcombo(self):
		self.breaking = True
		self.adding = False
		self.animate = False
		self.combofadeout = 0

	def add_combo(self):
		if self.breaking:
			self.combo = 0
		if self.adding:
			self.combo = self.combofadeout
			self.score_index = 0
			self.index_step = 1
			self.animate = True

		self.breaking = False
		self.adding = True

		self.fadeout_index = 0
		self.combofadeout += 1

	def get_combo(self):
		return max(0, self.combofadeout-1)

	def set_combo(self, combo):
		self.combofadeout = combo
		self.combo = max(0, combo-1)

	def add_to_frame(self, background):
		if int(self.fadeout_index) == 10:
			self.combo = self.combofadeout
			self.score_index = 0
			self.index_step = 1
			self.fadeout_index = 0
			self.animate = True
			self.adding = False

		if self.breaking:
			self.combo = max(0, self.combo - 1)

		if int(self.score_index) == 10:
			self.index_step = -1

		if ceil(self.score_index) == 0 and self.animate and self.index_step == -1:
			self.animate = False

		if self.adding:
			x = 0
			y = self.height - self.score_fadeout[0][int(self.fadeout_index)].size[1]
			for digit in str(self.combofadeout):
				digit = int(digit)
				self.img = self.score_fadeout[digit][int(self.fadeout_index)]
				x += self.img.size[0] - self.gap
				x_offset = x - self.img.size[0]//2
				y_offset = y + self.img.size[1]//2
				super().add_to_frame(background, x_offset, y_offset)

			self.img = self.score_fadeout[10][int(self.fadeout_index)]
			x += self.img.size[0] - self.gap
			x_offset = x - self.img.size[0] // 2
			y_offset = y + self.img.size[1] // 2
			super().add_to_frame(background, x_offset, y_offset)

			self.fadeout_index += 1

		x = 0
		y = self.height - self.score_frames[0][int(self.score_index)].size[1]
		for digit in str(self.combo):
			digit = int(digit)
			self.img = self.score_frames[digit][int(self.score_index)]
			x += self.img.size[0] - self.gap
			x_offset = x - self.img.size[0]//2
			y_offset = y + self.img.size[1]//2
			super().add_to_frame(background, x_offset, y_offset)

		self.img = self.score_frames[10][int(self.score_index)]
		x += self.img.size[0] - self.gap
		x_offset = x - self.img.size[0] // 2
		y_offset = y + self.img.size[1] // 2
		super().add_to_frame(background, x_offset, y_offset)

		if self.animate:
			self.score_index += self.index_step