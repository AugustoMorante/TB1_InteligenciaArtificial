from email.mime import image
from math import fabs
from operator import ge
from pickle import TRUE
from turtle import speed, width
import pygame, sys, random
import pygame.locals as GAME_GLOBALS
import pygame.event as GAME_EVENTS
import pygame.time as GAME_TIME
import numpy as np
import random


#Inicializar pygame y asignar los recursos base
pygame.init()
clock = pygame.time.Clock()
soundtrack = pygame.mixer.Sound("Game/recursos/soundtrack.wav")
title_image = pygame.image.load("Game/recursos/titulo.jpg")
game_over_image = pygame.image.load("Game/recursos/Fin_juego.jpg")

#Tamano del canvas
windowWidth = 400
windowHeight = 600

surface = pygame.display.set_mode((windowWidth, windowHeight)) # ventana principal para nuestro juego

pygame.display.set_caption('DINO GAME')

# Definimos las variables que afectarán a nustra partida
gameStarted = False
gameEnded = False
gamePlatforms = []
platformSpeed = 4
platformDelay = 1200
lastPlatform = 0
# Establecemos los contadores a cero
gameBeganAt = 0
timer = 0
# Creamos un diccionario par el posicionamiento inicial de dinos
player = {
  "x" : windowWidth/1.5,
  "y" : 0
}

#Algoritmo Genético
class DNA:
    def __init__(self, target, mutation_rate, n_individuals, n_selection, n_generations, verbose = True):
        self.target = target
        self.mutation_rate = mutation_rate
        self.n_individuals = n_individuals
        self.n_selection = n_selection
        self.n_generations = n_generations
        self.verbose = verbose


    def create_individual(self, min = 0, max = 9):
        return [np.random.randint(min, max) for _ in range(len(self.target))]

    def create_population(self):
        return [self.create_individual() for _ in range(self.n_individuals)]

    def fitness(self, individual):
        fitness = 0

        for i in range(len(individual)):
            if individual[i] == self.target[i]:
                fitness += 1
        
        return fitness
    
    def selection(self, population):

        scores = [(self.fitness(i), i) for i in population]
        scores = [i[1] for i in sorted(scores)]

        return scores[len(scores)-self.n_selection:]
    
    def reproduction(self, population, selected):        
        point = 0
        father = []

        for i in range(len(population)):
            point = np.random.randint(1, len(self.target) - 1)
            father = random.sample(selected, 2)

            population[i][:point] = father[0][:point]
            population[i][point:] = father[1][point:]
        
        return population
    
    def mutation(self, population):
        
        for i in range(len(population)):
            if random.random() <= self.mutation_rate:
                point = np.random.randint(len(self.target))
                new_value = np.random.randint(0, 9)

                while new_value == population[i][point]:
                    new_value = np.random.randint(0, 9)
                
                population[i][point] = new_value
            return population
    
    def run_geneticalgo(self):
        population = self.create_population()
        populationList = []

        for i in range(self.n_generations):

            '''if self.verbose:
                print('__')
                print('Generacion: ', i)
                print('Poblacion', population)
                print()'''

            temp = population[0][0]
            populationList.append(temp)
            selected = self.selection(population)
            population = self.reproduction(population, selected)
            population = self.mutation(population)

        return populationList

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
  path = None
  color = None
  platformsDroppedThrough = -1

  def __init__(self, x, y, s, h, w, path, color) -> None:
      pygame.sprite.Sprite.__init__(self)     

      self.x = x
      self.y = y
      self.speed = s
      self.height = h
      self.width = w
      self.path = path    
      self.image = pygame.transform.scale(pygame.image.load(path), (h, w))
      self.color = color
      self.rect = self.image.get_rect()
      self.rect.topleft = [x,y]    

fuente = pygame.font.Font(None, 30)


#Aplicacion del algoritmo genetico
#El valor óptimo de la velocidad que se quiere llegar
target = [9,0,0]
model = DNA(target = target,mutation_rate = 0.2,n_individuals = 25,n_selection = 10,n_generations = 10,verbose=True)
genetico = model.run_geneticalgo()

print(" ")
print('Con el algoritmo genético las velocidades varían:')
print(" ")
print('1° Generacion - Velocidad dinosaurio naranja: ', genetico[0])
print('2° Generacion - Velocidad dinosaurio azul: ', genetico[1]) 
print('3° Generacion - Velocidad dinosaurio celeste: ', genetico[2]) 
print('4° Generacion - Velocidad dinosaurio rojo: ', genetico[3]) 
print('5° Generacion - Velocidad dinosaurio amarillo: ', genetico[4]) 


#Poblacion inicial de dinos (la velocidad es dada pro el algoritmo genetico, alto y ancho se genera de manera random)
dinos = []
dino = Dino(player["x"], player["y"], genetico[0], random.randint(10,70), random.randint(10,70), "Game/recursos/dinosaurio.png", (255, 127, 39))
dino2 = Dino(player["x"]/1.1, player["y"], genetico[1], random.randint(10,70), random.randint(10,70), "Game/recursos/dinosaurio2.png", (63, 72, 204))
dino3 = Dino(player["x"]/1.2, player["y"], genetico[2], random.randint(10,70), random.randint(10,70), "Game/recursos/dinosaurio3.png", (0, 168, 243))
dino4 = Dino(player["x"]/1.3, player["y"], genetico[3], random.randint(10,70), random.randint(10,70), "Game/recursos/dinosaurio4.png", (136, 0, 27))
dino5 = Dino(player["x"]/1.4, player["y"], genetico[4], random.randint(10,70), random.randint(10,70), "Game/recursos/dinosaurio5.png", (255, 202, 24))

dinos.append(dino)
dinos.append(dino2)
dinos.append(dino3)
dinos.append(dino4)
dinos.append(dino5)


# Comenzamos a definir las funciones que formarán parte de nuestro juego
def drawDinos(dinos):

  #Mostrar puntaje y dibujar los dinosaurios
  cont = 0
  for dino in dinos:
    dinoPuntaje = fuente.render('Dinosaurio puntaje: %d' % dino.platformsDroppedThrough , 0, dino.color)
    cont += 20
    if dino.dead != True:
      newDino = Dino(dino.x, dino.y, dino.speed, dino.height, dino.width, dino.path, dino.color)
      surface.blit(newDino.image, newDino.rect)
      surface.blit(dinoPuntaje, (0, cont))
 

  pygame.display.update()
 

def moveDinos(dinos):

  #Logica para que cada dinosaurio se mueva dependiendo sus valores iniciales
  for dino in dinos:

    global platformsDroppedThrough, dropping

    leftOfPlayerOnPlatform = True
    rightOfPlayerOnPlatform = True

    if surface.get_at((int(dino.x), int(dino.y + dino.height))) == (0,0,0,255):
      leftOfPlayerOnPlatform = False
      player["direction"] = "left"      

    #Casos en el que esta linea da un "Index out of range" en otro caso el algoritmo corre sin problemas
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


#Crear las plataformas
def createPlatform():

  global lastPlatform, platformDelay

  platformY = windowHeight
  gapPosition = random.randint(0, windowWidth - 70)

  gamePlatforms.append({"pos" : [0, platformY], "gap" : gapPosition})
  lastPlatform = GAME_TIME.get_ticks()

  #Aumentando la velocidad de las plataformas con el tiempo
  if platformDelay > 580:
    platformDelay -= 50


#Movimiento de las plataformas
def movePlatforms():

  for idx, platform in enumerate(gamePlatforms):

    platform["pos"][1] -= platformSpeed

    if platform["pos"][1] < -10:
      gamePlatforms.pop(idx)


#Dibujar las plataformas
def drawPlatforms():

  for platform in gamePlatforms:

    pygame.draw.rect(surface, (255,255,255), (platform["pos"][0], platform["pos"][1], windowWidth, 10))
    pygame.draw.rect(surface, (0,0,0), (platform["gap"], platform["pos"][1], 70, 10) )


def gameOver():
  global gameStarted, gameEnded
 
  gameStarted = False
  gameEnded = True

  
def restartGame():

  soundtrack.play()
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
        dino.leftDown = False

        if int(dino.x) > gamePlatforms[i]['gap']:
          dino.leftDown = True

        dino.rightDown = False
        if int(dino.x) < gamePlatforms[i]['gap']:
          dino.rightDown = True

  for event in GAME_EVENTS.get():

    if event.type == pygame.KEYDOWN:

      if event.key == pygame.K_SPACE:
        if gameStarted == False:
          restartGame()
          gameStarted = True

    if event.type == GAME_GLOBALS.QUIT:
      quitGame()

  if gameStarted is True:
    #Empezar el juego
    timer = GAME_TIME.get_ticks() - gameBeganAt

    movePlatforms()
    drawPlatforms()
    moveDinos(dinos)
    drawDinos(dinos)

  elif gameEnded is True:
    #Patanalla de juego finalizado
    surface.blit(game_over_image, (0, 150))

  else :
    #Pantalla de bienvenida
    surface.blit(title_image, (0, 150))

  if GAME_TIME.get_ticks() - lastPlatform > platformDelay:
    createPlatform()

  clock.tick(60)
  pygame.display.update()