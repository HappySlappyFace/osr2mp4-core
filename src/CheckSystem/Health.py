MULTIPLIER = {0: -1, 50: 0.05, 100: 0.01, 300: 1}


def health_increase_for(hitresult):
	default_max_health_increase = 0.05
	return MULTIPLIER[hitresult] * default_max_health_increase


def diffcultyrange(difficulty, mini, mid, maxi):
	if difficulty > 5:
		return mid + (maxi - mid) * (difficulty - 5) / 5
	if difficulty < 5:
		return mid - (mid - mini) * (5 - difficulty) / 5

	return mid


def sign(a):
	if a >= 0:
		return 1
	else:
		return -1


class HealthProcessor:
	def __init__(self, beatmap, drainrate=None):
		self.minimum_health_error = 0.01
		self.min_health_target = 0.95
		self.mid_health_target = 0.70
		self.max_health_target = 0.30
		self.beatmap = beatmap.hitobjects
		self.drain_starttime = beatmap.start_time
		self.drain_endtime = beatmap.end_time
		self.breakperiods = beatmap.breakperiods[:-1]
		self.target_min_health = diffcultyrange(beatmap.diff["HPDrainRate"], self.min_health_target, self.mid_health_target, self.max_health_target)
		self.drain_rate = 1
		self.health_value = 1
		self.increase_step = health_increase_for(300)
		if drainrate is None:
			self.drain_rate = self.compute_drainrate()
		else:
			self.drain_rate = drainrate

	def compute_drainrate(self):
		if len(self.beatmap) == 0:
			return 0

		adjustment = 1
		result = 1

		while adjustment > 0:
			currentHealth = 1
			lowestHealth = 1
			currentbreak = -1

			for i in range(len(self.beatmap)):
				currentTime = self.beatmap[i]["time"]
				lastTime = self.beatmap[i - 1]["time"] if i > 0 else self.drain_starttime

				if len(self.breakperiods) > 0:
					while currentbreak + 1 < len(self.breakperiods) and self.breakperiods[currentbreak + 1]["End"] < currentTime:
						currentbreak += 1

					if currentbreak >= 0:
						lastTime = max(lastTime, self.breakperiods[currentbreak]["End"])

				currentHealth -= (self.beatmap[i]["time"] - lastTime) * result
				lowestHealth = min(lowestHealth, currentHealth)
				step = self.increase_step * (1 + 0.05 * int("new combo" in self.beatmap[i]["type"]))

				currentHealth = min(1, currentHealth + step)

				if lowestHealth < 0:
					break

			if abs(lowestHealth - self.target_min_health) <= self.minimum_health_error:
				break

			adjustment *= 2
			result += 1.0 / adjustment * sign(lowestHealth - self.target_min_health)

		return result

	def drainhp(self, cur_time, last_time, in_break):
		if in_break:
			return

		cur_time = max(self.drain_starttime, min(self.drain_endtime, cur_time))
		last_time = max(self.drain_starttime, min(self.drain_endtime, last_time))
		self.health_value -= self.drain_rate * (cur_time - last_time)

	def updatehp(self, hitresult, obj_type):
		h = health_increase_for(hitresult) * (1 + 0.05 * int("type" in obj_type))
		self.health_value = min(1, self.health_value + h)