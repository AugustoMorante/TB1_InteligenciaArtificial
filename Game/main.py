from email.mime import image
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
  "x" : windowWidth / 2,
  "y" : 0,
  "height" : 20,
  "width" : 20,
  "vy" : 5
}

# Clase para mapear el sprite y la localizacion inicial del dinosaurio
class Dino(pygame.sprite.Sprite):
  image = None

  def __init__(self, location) -> None:
      pygame.sprite.Sprite.__init__(self)

      if Dino.image is None:
        Dino.image = pygame.image.load("Game/recursos/dinosaurio.png")
      
      self.image = pygame.transform.scale(Dino.image, (player["width"], player["height"]))
      self.rect = self.image.get_rect()
      self.rect.topleft = location
    
# Comenzamos a definir las funciones que formarán parte de nuestro juego

def drawPlayer():

  #pygame.draw.rect(surface, (255,128,0), (player["x"], player["y"], player["width"], player["height"]))

  #Inicializacion de la clase Dino
  dino = Dino([player["x"], player["y"]])
  surface.blit(dino.image, dino.rect)
  pygame.display.update()
 

def movePlayer():

  global platformsDroppedThrough, dropping

  leftOfPlayerOnPlatform = True
  rightOfPlayerOnPlatform = True

  if surface.get_at((int(player["x"]), int(player["y"] + player["height"]))) == (0,0,0,255):
    leftOfPlayerOnPlatform = False

  if surface.get_at((int(player["x"] + player["width"]), int(player["y"] + player["height"]))) == (0,0,0,255):
    rightOfPlayerOnPlatform = False

  if leftOfPlayerOnPlatform is False and rightOfPlayerOnPlatform is False and (player["y"] + player["height"]) + player["vy"] < windowHeight:
    player["y"] += player["vy"]

    if dropping is False:
      dropping = True
      platformsDroppedThrough += 1

  else :
    foundPlatformTop = False
    yOffset = 0
    dropping = False

    while foundPlatformTop is False:

      if surface.get_at((int(player["x"]),int( (player["y"] + player["height"]) - yOffset ))) == (0,0,0,255):
        player["y"] -= yOffset
        foundPlatformTop = True
      elif (player["y"] + player["height"]) - yOffset > 0:
        yOffset += 1
      else :

        gameOver()
        break

  if leftDown is True:
    if player["x"] > 0 and player["x"] - 5 > 0:
      player["x"] -= 5
    elif player["x"] > 0 and player["x"] - 5 < 0:
      player["x"] = 0

  if rightDown is True:
    if player["x"] + player["width"] < windowWidth and (player["x"] + player["width"]) + 5 < windowWidth:
      player["x"] += 5
    elif player["x"] + player["width"] < windowWidth and (player["x"] + player["width"]) + 5 > windowWidth:
      player["x"] = windowWidth - player["width"]

def createPlatform():

  global lastPlatform, platformDelay

  platformY = windowHeight
  gapPosition = random.randint(0, windowWidth - 40)

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
    pygame.draw.rect(surface, (0,0,0), (platform["gap"], platform["pos"][1], 40, 10) )


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

  for i in range(len(gamePlatforms)):
    if gamePlatforms[i]['pos'][1] - player["y"] == 21:
      print("En la plataforma: ", i + 1)
      print("Escape: ",gamePlatforms[i]['gap'])
      print("X: ", int(player["x"]))
      leftDown = False

      if int(player["x"]) > gamePlatforms[i]['gap']:
        print("izquierda")
        leftDown = True

      rightDown = False
      if int(player["x"]) < gamePlatforms[i]['gap']:
        rightDown = True
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
    movePlayer()
    drawPlayer()

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