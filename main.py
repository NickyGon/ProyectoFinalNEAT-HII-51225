# -*- coding: utf-8 -*-
"""
Created on Fri Jun 24 12:03:21 2022

@author: Nicole
"""

import pygame
import os
import random
import neat
import math


pygame.init()

win_height = 400
win_width = 800
win = pygame.display.set_mode((win_width, win_height))

# Tomando y escalando la imagen del estado estático
imstationary = pygame.image.load(os.path.join("Assets/Player", "standing.png"))
stationary = pygame.transform.scale(imstationary,(120,120))
# Tomando y escalando las imagenes de caminar a la izquierda
left = [None]*9
for picIndex in range(1,9):
    imleft=pygame.image.load(os.path.join("Assets/Player", "L" + str(picIndex) + ".png"))
    left[picIndex-1] = pygame.transform.scale(imleft,(120,120))
    picIndex+=1
# Tomando y escalando las imagenes de caminar a la derecha
right = [None]*9
for picIndex in range(1,9):
    imright=pygame.image.load(os.path.join("Assets/Player", "R" + str(picIndex) + ".png"))
    right[picIndex-1] = pygame.transform.scale(imright,(120,120))
    picIndex+=1
# Tomando y escalando la imagen de la bomba
imbomb = pygame.image.load(os.path.join("Assets/FallingObject", "Bomb.png"))
bomb = pygame.transform.scale(imbomb,(50,50))
imfruit = pygame.image.load(os.path.join("Assets/FallingObject", "Fruta.png"))
fruit = pygame.transform.scale(imfruit,(50,50))
imground = pygame.image.load(os.path.join("Assets/Landscape", "ground.png"))
groundd = pygame.transform.scale(imground,(800,200))
rect = groundd.get_rect()
imbg = pygame.image.load(os.path.join("Assets/Landscape", "bg.png"))

class FallObject:
     def __init__(self, x, y,kind):
        self.x = x
        self.y = y
        self.vely = 15
        self.caught= False
        self.kind= kind # 0=Bomba / 1=Moneda
        # El hitbox nos ayuda a detectar el impacto del objeto
        self.hitbox = (self.x, self.y, 45, 45)
        # count para el conteo de cooldown y stp para activarlo
        self.count = 0
        self.stp= False
    
    #Detectar si el objeto cae al suelo y actuar con el cooldown (tiempo de permanencia)
     def move(self):
        self.cooldown()
        self.hit()
     def catch(self):
         self.caught=True
       
    #Mantener el objeto en el suelo por un tiempo
     def cooldown(self): 
        if self.count >= 5:
            self.count = 0
        elif self.count > 0:
            self.count += 1

        
     def draw(self, win):
        self.hitbox = (self.x, self.y, 45, 45)
        pygame.draw.rect(win, (0,0,0), self.hitbox, 1)
        if(self.kind==0):
            win.blit(bomb, (self.x, self.y))
        else:
            win.blit(fruit, (self.x, self.y))
     
    #Caer constantemente al suelo una vez invocado
     def update(self):
        self.move() 
    
    #Si llega a caer al suelo, detenerse unos segundos antes de desaparecer
     def hit(self):
        if (self.hitbox[1]>ground.y):
            if (not self.stp):
                self.stp= True
                self.count = 1
            if (self.count==0 and self.caught==False and self.stp==True):
                fallobject.remove(self)
        else:
             self.y+=self.vely
 


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.cooldownSta=0
        self.inmov=False
        self.velx = 15.5
        self.face_right = False
        self.face_left = False
        self.stepIndex = 0
        self.hitbox = (self.x, self.y, 110, 110)
        self.points=0
        self.where=0
        self.candy=0

        
    def collide(self):  
        for ob in fallobject:
            if (ob.hitbox[1]+ob.hitbox[3] >self.hitbox[1] and ((ob.hitbox[0]<self.hitbox[0]+self.hitbox[3]) and (ob.hitbox[0]+ob.hitbox[2]>self.hitbox[0]))):
                ob.caught=True
                
    def statcool(self):
       if self.inmov==True:
            self.cooldownSta += 1
   
        
            
    def update(self):
        self.move_player()
        
    def move_player(self):
       
        self.statcool()
        self.collide()
        if self.where==1 and self.x <= win_width-92:
            self.inmov=False
            self.x += self.velx
            self.face_right = True
            self.face_left = False
        elif self.where==-1 and self.x >= 0:
            self.inmov=False
            self.x -= self.velx
            self.face_right = False
            self.face_left = True
        else:
            self.face_right = False
            self.face_left = False
            self.stepIndex = 0
            self.inmov=True
            
    def draw(self, win):
        self.hitbox = (self.x, self.y, 110, 110)
        pygame.draw.rect(win, (0,0,0), self.hitbox, 1)
        if self.stepIndex >=32:
            self.stepIndex = 0
        if self.face_left:
            win.blit(left[self.stepIndex//4], (self.x, self.y))
            self.stepIndex += 1
        elif self.face_right:
            win.blit(right[self.stepIndex//4], (self.x, self.y))
            self.stepIndex += 1
        else:
             win.blit(stationary, (self.x,self.y))

class Ground:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hitbox = (self.x, self.y, 800, 200)
        
    def draw(self, win):
        pygame.draw.rect(win, (0,0,255), self.hitbox, 1)
        win.blit(groundd, (self.x,self.y))



def remove(index):
    players.pop(index)
    genomas.pop(index)
    redneuro.pop(index)   

def distance(pos_xa, pos_ya,pos_xb,pos_yb):
    dx = pos_xa-pos_xb
    dy = pos_ya-pos_yb
    return math.sqrt(dx**2+dy**2)

def eval_genomas(genomes, config):
    global ground,player,players,fallobject,genomas,redneuro
    
    ground=Ground(0,300)
    players=[]
    fallobject = []
    genomas=[]
    redneuro=[]
    
    for genoma_id, genoma in genomes:
        players.append(Player(400, 230))
        genomas.append(genoma)
        red=neat.nn.FeedForwardNetwork.create(genoma, config)
        redneuro.append(red)
        genoma.fitness = 0
    
    
    def draw_game():
        win.fill((0, 0, 0))
        win.blit(imbg, (0,0))
        ground.draw(win)
        for player in players:
            player.draw(win)
        for ob in fallobject:
            ob.draw(win)
        font = pygame.font.Font('freesansbold.ttf', 32)
        text_1 = font.render(f'Jugadores Vivos:  {str(len(players))}', True, (0,206,209))
        text_2 = font.render(f'Generacion:  {pop.generation+1}', True, (0,206,209))
        win.blit(text_1, (390, 20))
        win.blit(text_2, (390,40))
        pygame.time.delay(30)
        pygame.display.update()
    
    run = True
    while run:
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
        for play in players:
            play.update()
             
        if len(players)==0:
            break
        
        if len(fallobject)==0:
                random_x = random.randint(50,win_width-50)
                random_type = random.randint(0,1)
                fallob = FallObject(random_x, 0, random_type)
                #fallob = FallObject(random_x, 0, 0)
                fallobject.append(fallob)
                

        for ob in fallobject:
            ob.update()
            
            for i,play in enumerate(players):
                genomas[i].fitness += 1
                if play.inmov==True and play.cooldownSta>=20:
                        genomas[i].fitness -= 10
                        remove(i)
                if ob.caught:
                    if ob in fallobject: fallobject.remove(ob)
                    #genomas[i].fitness -= 1
                    #remove(i)
                    if ob.kind==0:
                        genomas[i].fitness -= (play.candy * 10)
                        remove(i)
                    if ob.kind==1 and play.inmov==False:
                        play.candy=+1
                        genomas[i].fitness = genomas[i].fitness*play.candy
                        
                
                    
                       
                    
        for i,play in enumerate(players):
            output = redneuro[i].activate((play.hitbox[0], distance(play.hitbox[0], play.hitbox[1],ob.hitbox[0]+ob.hitbox[2],ob.hitbox[1]+ob.hitbox[3]),ob.kind,ob.hitbox[1]+ob.hitbox[3]>=play.hitbox[1]))
           
           # <=0.5 (Alejarse) 0.5>(Ir)

            if (output[0] <= 0 or output[1] > 0):
                    play.where=-1
            if (output[1] <= 0 or output[0]>0):
                    play.where=1
            
    
        draw_game()




#Configurando el algoritmo NEAT para el juego
def run(config_path):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    bestgen=pop.run(eval_genomas, 10)
    print(bestgen)

    
   
    

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)