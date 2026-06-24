import pygame
import sys
import math
from modules.player import Player
from modules.geometry import Rect

WIDTH, HEIGHT = 800, 600

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

player = Player(WIDTH // 2, HEIGHT // 2, 0, 3, 3)

walls = [
	Rect(250, 150, 0, 100, 100)
]

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()

	keys = pygame.key.get_pressed()

	player.update(keys)

	screen.fill((20, 20, 20))

	for wall in walls:
		wall.draw(screen)

	player.draw(screen)

	pygame.display.flip()
	clock.tick(60)