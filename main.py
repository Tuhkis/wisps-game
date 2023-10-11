import pygame, math, random, json, sys
pygame.init()
pygame.font.init()

# Basic setup
pygame.display.set_caption('WISPS - GAME')
win = pygame.display.set_mode((720, 720), pygame.SCALED + pygame.RESIZABLE)
clock = pygame.time.Clock()

cam = [0, 0, 0]

WAVE = 0

# A text drawing method
def write(text, size=32, wave=0, offset=0, colour=(44, 44, 44)):
	font = pygame.font.SysFont('freesanbold.ttf', size)
	text1 = font.render(str(text), True, colour)
	win.blit(text1, (win.get_width() / 2 - text1.get_width() / 2 - cam[0], win.get_height() / 2 - text1.get_height() / 2 - cam[1] + math.sin(wave * 5) * 32 + offset))

class Particles_emitter:
	# "fire" particles are set as default
	def __init__(self, path="data/particles/fire.json"):
		# Emitter position
		self.pos = [0, 0]
		self.particles = []

		# Goes through the particle JSON file and parses it into data
		ijson = open(path)
		data = ijson.read()
		ijson.close()
		data = json.loads(data)

		self.colour = (data['colour'][0], data['colour'][1], data['colour'][2])
		self.initial_velocity = data['initial_velocity']
		self.velocity_randomness = data['velocity_randomness']
		self.radius = data['radius']
		self.gravity = data['gravity']
		self.shrink = data['shrink']
		self.lifetime = data['lifetime']
		self.tone_variance = data['tone_variance']
		self.glow = data['glow']
	def spawn_particle(self):
		# Does magic to spawn a new particle
		# 0 = x, 1 = y, 2 = radius, 3 = acc, 4 = colour, 5 = age
		darkness = max(random.randrange(self.tone_variance, 11), 1) / 10
		vel = self.initial_velocity.copy()
		vel[0] *= random.randrange(self.velocity_randomness[0][0], self.velocity_randomness[0][1])
		vel[1] *= random.randrange(self.velocity_randomness[1][0], self.velocity_randomness[1][1])
		self.particles.append([self.pos[0], self.pos[1], random.randrange(self.radius, int(self.radius * 1.5)), vel, (self.colour[0] * darkness, self.colour[1] * darkness, self.colour[2] * darkness), 0])
	def draw(self, surf=win):
		# Draws every particle
		for p in self.particles:
			if self.glow:
				pygame.draw.circle(bloomSurf, (p[4][0] / 1.15, p[4][1] / 1.15, p[4][2] / 1.15), (p[0] - cam[0], p[1] - cam[1]), p[2] * 1.5)
			
			pygame.draw.circle(surf, p[4], (p[0] - cam[0], p[1] - cam[1]), p[2])
	def update(self, delta):
		# Goes through the particles and does magic
		for p in self.particles:
			p[0] += p[3][0] * delta
			p[1] += p[3][1] * delta
			p[3][1] += self.gravity[1] * delta
			p[3][0] += self.gravity[0] * delta
			p[2] -= (self.shrink * (random.randrange(0, 35) / 10)) * delta
			p[5] += 1 * delta

			if p[0] > win.get_width() - p[2]:
				p[0] = win.get_width() - p[2]
				p[3][0] *= -0.5
			if p[0] < 0 + p[2]:
				p[0] = 0 + p[2]
				p[3][0] *= -0.5

			if p[1] > win.get_height() - p[2]:
				p[1] = win.get_height() - p[2]
				p[3][1] *= -0.5
			if p[1] < 0 + p[2]:
				p[1] = 0 + p[2]
				p[3][1] *= -0.5

			if p[5] >= self.lifetime + random.randrange(0, 35) / 10:
				self.particles.remove(p)

class Point:
	def __init__(self, pos):
		self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
		self.lifetime = 0
	def draw(self):
		pygame.draw.circle(win, (250, 70, 70), (self.hitbox.x + 8 - cam[0], self.hitbox.y + 8 - cam[1]), 8)
	def update(self, dt, player, points, particles, pointsint):
		self.lifetime += 1 * dt
		if self.lifetime > 4:
			self.lifetime = 4
		if player.hitbox.colliderect(self.hitbox):
			explosion_particles = Particles_emitter('data/particles/explosion.json')
			explosion_particles.pos = [self.hitbox.x, self.hitbox.y]
			for i in range(32):
				explosion_particles.spawn_particle()
			particles.append(explosion_particles)
			points.append(Point([random.randrange(0, 690), random.randrange(0, 690)]))
			pointsint[0] += 6 - int(self.lifetime)
			cam[2] += 10
			points.remove(self)

class Player:
	def __init__(self):
		self.hitbox = pygame.Rect(0, 0, 35, 35)
		self.vel = [0, 2]
		self.speed = 600
		self.trail = Particles_emitter('data/particles/trail.json')
		self.end_game = False;
	def draw(self):
		self.trail.draw()
		
		#pygame.draw.rect(win, (255, 25, 25), self.hitbox)
	def update(self, dt):
		self.vel[1] += 100 * dt

		keys = pygame.key.get_pressed()
		if keys[pygame.K_d]:
			self.vel[0] += self.speed * dt
		if keys[pygame.K_a]:
			self.vel[0] += -self.speed * dt
		if keys[pygame.K_w]:
			self.vel[1] += -self.speed * dt
		if keys[pygame.K_s]:
			self.vel[1] += self.speed * dt

		if keys[pygame.K_SPACE] and self.end_game:
			GAME = Game()
			GAME.tick()

		self.hitbox.x += self.vel[0] * dt
		self.hitbox.y += self.vel[1] * dt

		if self.hitbox.x < 0:
			self.hitbox.x = 0
			self.vel[0] *= -0.7
		if self.hitbox.x > win.get_width() - self.hitbox.width:
			self.hitbox.x = win.get_width() - self.hitbox.width
			self.vel[0] *= -0.7
		if self.hitbox.y < 0:
			self.hitbox.y = 0
			self.vel[1] *= -0.7
		if self.hitbox.y > win.get_height() - self.hitbox.height:
			self.hitbox.y = win.get_height() - self.hitbox.height
			self.vel[1] *= -0.7

		self.trail.update(dt)
		self.trail.pos = [self.hitbox.x + self.hitbox.width / 2, self.hitbox.y + self.hitbox.height / 2]
		self.trail.spawn_particle()

bloomSurf = pygame.Surface((win.get_width(), win.get_height()), pygame.SRCALPHA)

class Menu:
	def __init__(self):
		pass
	def tick(self):
		global WAVE
		RUNNING = True
		while RUNNING:
			dt = clock.tick(60) / 1000
			WAVE += 1 * dt
			for e in pygame.event.get():
				if e.type == pygame.QUIT:
					RUNNING = False
					pygame.quit()
					sys.exit()
					break
			keys = pygame.key.get_pressed()
			if keys[pygame.K_SPACE]:
				GAME = Game()
				GAME.tick()
			win.fill((30, 30, 30))
			write('PRESS SPACE', 125, WAVE)
			write('YOU HAVE 30s', 75, WAVE, 127)
			pygame.display.update()


class Game:
	def __init__(self):
		self.timer = 30
	def tick(self):
		global WAVE
		pointsint = [0]
		RUNNING = True
		player = Player()
		points = [Point([400, 400])]
		particles = []
		while RUNNING:
			dt = clock.tick(60) / 1000
			WAVE += 1 * dt
			for e in pygame.event.get():
				if e.type == pygame.QUIT:
					RUNNING = False
					pygame.quit()
					sys.exit()
					break
			# Update methods
			player.update(dt)
			for p in points:
				p.update(dt, player, points, particles, pointsint)
			for p in particles:
				p.update(dt)
				if p.particles == []:
					particles.remove(p)
			# Move Camera
			if cam[2] < 0:
				cam[2] = 0
			cam[0] = math.sin(cam[2] * 5) * (7 * (cam[2] / 5))
			cam[1] = math.sin(cam[2] * 6) * (7 * (cam[2] / 5))
			cam[2] -= 10 * dt
			# Drawing methods
			win.fill((30, 30, 30))
			bloomSurf.fill(pygame.Color(0, 0, 0, 0))
			if self.timer < 6:
				write(str(pointsint[0]), 500, WAVE / 3, 0, (122, 122, 122))
			else:
				write(str(pointsint[0]), 500)

			if self.timer < 6:
				write(str(int(self.timer)) + 's', 75, WAVE / 3, 150, (122, 122, 122))
			else:
				write(str(int(self.timer)) + 's', 75, 0, 150)
				WAVE = 0
			for p in points:
				p.draw()
			for p in particles:
				p.draw()
			player.draw()
			win.blit(bloomSurf, (0, 0), None, pygame.BLEND_RGB_ADD)
			pygame.draw.circle(win,(200, 170, 235), (player.hitbox.x + player.hitbox.width / 2 - cam[0], player.hitbox.y + player.hitbox.width / 2 - cam[1]), player.hitbox.width / 2)
			self.timer -= 1 * dt
			if self.timer < 0:
				points = []
				player.end_game = True;
				write('Restart with space.', 75, 0, 200, (200, 240, 255))
				# GAME = Menu()
				# GAME.tick()
			# Update screen
			pygame.display.update()


GAME = Menu()
def game():
	global bloomSurf
	GAME.tick()
	
game()
pygame.quit()
