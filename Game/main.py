from email.mime import image
from math import fabs
from pickle import TRUE
from turtle import speed, width
import pygame, sys, random
import pygame.locals as GAME_GLOBALS
import pygame.event as GAME_EVENTS
import pygame.time as GAME_TIME

pygame.init()
clock = pygame.time.Clock()

player_image = pygame.image.load("Game/recursos/dinosaurio.png")
title_image = pygame.image.load("Game/recursos/titulo.jpg")
game_over_image = pygame.image.load("Game/recursos/Fin_juego.jpg")

windowWidth = 400
windowHeight = 600

surface = pygame.display.set_mode((windowWidth, windowHeight)) # ventana principal para nuestro juego

pygame.display.set_caption('¡Déjate caer!')

# Definimos las variables para las pulsaciones de las teclas
leftDown = False
rightDown = False
# Definimos las variables que afectarán a nustra partida
gameStarted = False
gameEnded = False
gamePlatforms = []
platformSpeed = 4
platformDelay = 1200
lastPlatform = 0
platformsDroppedThrough = -1
dropping = False
# Establecemos los contadores a cero
gameBeganAt = 0
timer = 0
# Creamos un diccionario con todos los atributos del personaje principal
player = {
  "x" : windowWidth/1.5, #cambiar a 2
  "y" : 0,
  "height" : 20,
  "width" : 20,
  "vy" : 5,
  "direction": "left"
}

# Clase para mapear el sprite y sus propieades iniciales del dinosaurio
class Dino(pygame.sprite.Sprite):
  x = None
  y = None
  vy = 5
  leftDown = False
  rightDown = False
  dropping = False
  image = None
  speed = None
  height = None
  width = None
  dead = False
  platformsDroppedThrough = -1

  def __init__(self, x, y, s, h, w) -> None:
      pygame.sprite.Sprite.__init__(self)

      if Dino.image is None:
        Dino.image = pygame.image.load("Game/recursos/dinosaurio.png")

      self.x = x
      self.y = y
      self.speed = s
      self.height = h
      self.width = w    
      self.image = pygame.transform.scale(Dino.image, (h, w))
      self.rect = self.image.get_rect()
      self.rect.topleft = [x,y]
    

fuente = pygame.font.Font(None, 30)

#Poblacion inicial de dinos
dinos = []
dino = Dino(player["x"], player["y"], random.randint(2,9), random.randint(10,70), random.randint(10,70))
dino2 = Dino(player["x"]/1.1, player["y"], random.randint(2,9), random.randint(10,70), random.randint(10,70))
dino3 = Dino(player["x"]/1.2, player["y"], random.randint(2,9), random.randint(10,70), random.randint(10,70))
dino4 = Dino(player["x"]/1.3, player["y"], random.randint(2,9), random.randint(10,70), random.randint(10,70))
dino5 = Dino(player["x"]/1.4, player["y"], random.randint(2,9), random.randint(10,70), random.randint(10,70))
nuvosDinos = []

dinos.append(dino)
dinos.append(dino2)
dinos.append(dino3)
dinos.append(dino4)
dinos.append(dino5)


# Comenzamos a definir las funciones que formarán parte de nuestro juego

def drawPlayer(dinos):

  #Mostrar puntaje y dibujar los dinosaurios
  cont = 0
  for dino in dinos:
    dinoPuntaje = fuente.render('Dinosaurio puntaje: %d' % dino.platformsDroppedThrough , 0,(200, 60, 80))
    cont += 20
    if dino.dead != True:
      newDino = Dino(dino.x, dino.y, dino.speed, dino.height, dino.width)
      surface.blit(newDino.image, newDino.rect)
      surface.blit(dinoPuntaje, (0, cont))
 

  pygame.display.update()
 

def movePlayer(dinos):

  #Logica para que cada dinosaurio se mueva dependiendo sus valores iniciales
  for dino in dinos:

    global platformsDroppedThrough, dropping

    leftOfPlayerOnPlatform = True
    rightOfPlayerOnPlatform = True

    if surface.get_at((int(dino.x), int(dino.y + dino.height))) == (0,0,0,255):
      leftOfPlayerOnPlatform = False
      player["direction"] = "left"
      

    if surface.get_at((int(dino.x + dino.width), int(dino.y + dino.height))) == (0,0,0,255):
      rightOfPlayerOnPlatform = False
      player["direction"] = "right"

    if leftOfPlayerOnPlatform is False and rightOfPlayerOnPlatform is False and (dino.y + dino.height) + dino.vy < windowHeight:
      dino.y += dino.vy

      if dino.dropping is False:
        dino.dropping = True
        dino.platformsDroppedThrough += 1

    else :
      foundPlatformTop = False
      yOffset = 0
      dino.dropping = False

      while foundPlatformTop is False:

        if surface.get_at((int(dino.x),int( (dino.y + dino.height) - yOffset ))) == (0,0,0,255):
          dino.y -= yOffset
          foundPlatformTop = True
        elif (dino.y + dino.height) - yOffset > 0:
          yOffset += 1
        else :

          #gameOver()
          dino.dead = True
          break

    if dino.leftDown is True:
      if dino.x > 0 and dino.x - dino.speed > 0:
        dino.x -= dino.speed
      elif dino.x > 0 and dino.x - dino.speed < 0:
        dino.x = 0

    if dino.rightDown is True:
      if dino.x + dino.width < windowWidth and (dino.x + dino.width) + dino.speed < windowWidth:
        dino.x += dino.speed
      elif dino.x + dino.width < windowWidth and (dino.x + dino.width) + dino.speed > windowWidth:
        dino.x = windowWidth - dino.width

def createPlatform():

  global lastPlatform, platformDelay

  platformY = windowHeight
  gapPosition = random.randint(0, windowWidth - 70)

  gamePlatforms.append({"pos" : [0, platformY], "gap" : gapPosition})
  lastPlatform = GAME_TIME.get_ticks()

  #Aumentando la velocidad de las plataformas con el tiempo
  if platformDelay > 580:
    platformDelay -= 50

def movePlatforms():
  # print("Platforms")

  for idx, platform in enumerate(gamePlatforms):

    platform["pos"][1] -= platformSpeed

    if platform["pos"][1] < -10:
      gamePlatforms.pop(idx)

def drawPlatforms():

  for platform in gamePlatforms:

    pygame.draw.rect(surface, (255,255,255), (platform["pos"][0], platform["pos"][1], windowWidth, 10))
    pygame.draw.rect(surface, (0,0,0), (platform["gap"], platform["pos"][1], 70, 10) )


def gameOver():
  global gameStarted, gameEnded

  platformSpeed = 0
  gameStarted = False
  gameEnded = True

  
def restartGame():

  global gamePlatforms, player, gameBeganAt, platformsDroppedThrough, platformDelay

  gamePlatforms = []
  player["x"] = windowWidth / 2
  player["y"] = 0
  gameBeganAt = GAME_TIME.get_ticks()
  platformsDroppedThrough = -1
  platformDelay = 1200

def quitGame():
  pygame.quit()
  sys.exit()

# 'main' loop
while True:

  surface.fill((0,0,0))

  #Movimiento automatico de los dinos
  for i in range(len(gamePlatforms)):
    for dino in dinos:
      if gamePlatforms[i]['pos'][1] - dino.y == dino.height + 1: 
        print("En la plataforma: ", i + 1)
        print("Escape: ",gamePlatforms[i]['gap'])
        print("X: ", int(dino.x))
        dino.leftDown = False

        if int(dino.x) > gamePlatforms[i]['gap']:
          print("izquierda")
          dino.leftDown = True

        dino.rightDown = False
        if int(dino.x) < gamePlatforms[i]['gap']:
          dino.rightDown = True
          print("derecha")

  if len(gamePlatforms) > 0:
    print(gamePlatforms[-1])

  for event in GAME_EVENTS.get():

    if event.type == pygame.KEYDOWN:

      if event.key == pygame.K_LEFT:
        leftDown = True
      if event.key == pygame.K_RIGHT:
        rightDown = True
      if event.key == pygame.K_ESCAPE:
        quitGame()

    if event.type == pygame.KEYUP:
      if event.key == pygame.K_LEFT:
        leftDown = False
      if event.key == pygame.K_RIGHT:
        rightDown = False

      if event.key == pygame.K_SPACE:
        if gameStarted == False:
          restartGame()
          gameStarted = True

    if event.type == GAME_GLOBALS.QUIT:
      quitGame()

  if gameStarted is True:
    # Play game
    timer = GAME_TIME.get_ticks() - gameBeganAt

    movePlatforms()
    drawPlatforms()
    movePlayer(dinos)
    drawPlayer(dinos)

  elif gameEnded is True:
    # Draw game over screen
    surface.blit(game_over_image, (0, 150))

  else :
    # Welcome Screen
    surface.blit(title_image, (0, 150))

  if GAME_TIME.get_ticks() - lastPlatform > platformDelay:
    createPlatform()

  clock.tick(60)
  pygame.display.update()