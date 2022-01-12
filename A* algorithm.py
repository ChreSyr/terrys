#Author: Sean McKiernan (Mekire)
#Purpose: Exploring A* pathfinding and the feasability of using it for my enemies' AI in 'Cabbages and Kings'
#License: Free for everyone and anything (no warranty expressed or implied)
import sys,os,random,math

import pygame
from pygame.locals import *

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()

SCREENSIZE = (440,280)
SCREEN = pygame.display.set_mode(SCREENSIZE)

grid   = pygame.image.load("zgridsmall.png").convert_alpha()
arial  = pygame.font.SysFont("arial", 13, bold=True, italic=False)

Adjacents = []
Adjacents.append([(1,0),(-1,0),(0,1),(0,-1)])  #Rook (this is what I need for my 'Cabbages and Kings' game
Adjacents.append([(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]) #Queen (moves in all eight adjacent directions)
Adjacents.append([(1,-2),(1,2),(-1,-2),(-1,2),(2,1),(2,-1),(-2,1),(-2,-1)]) #Knight (figure it out)

class FindIt:
    def __init__(self):
        self.animate   = False #default to animation off (this gives a realistic result for time)
        self.altmethod = False #default to true A* (the alternate will often calculate faster but not necessarily be the most direct path)
        self.ADJind  = 0 #default to rook move
        self.clock   = pygame.time.Clock()
        self.init()
    def init(self):
        self.state  = "START"
        self.screen = SCREEN
        self.cell_size = (20,20)

        self.startcell   = None
        self.goalcell    = None
        self.currentcell = None
        self.barriers  = set()
        
        #sets two boundary rows as barriers (must be two thick to prevent knights cheating)
        for i in range(-1,23):
            self.barriers |= set(((i,-1),))
            self.barriers |= set(((i, 0),))
            self.barriers |= set(((i,13),))
            self.barriers |= set(((i,14),))
        for j in range(-1,15):
            self.barriers |= set(((-1,j),))
            self.barriers |= set((( 0,j),))
            self.barriers |= set(((21,j),))
            self.barriers |= set(((22,j),))

        self.addbarrier = False
        self.delbarrier = False
        
        self.solved     = False
##        self.solution   = set()
        self.solution   = [] #using a set is almost certainly faster but I want it to have an order.
        self.pathind    = 0
        self.nextcell   = None #used for alternate method

        self.timestart = 0.0
        self.timeend   = 0.0

        self.hx = {} #optimal estimate to goal
        self.gx = {} #cost from start to current position
        self.fx = {} #distance-plus-cost heuristic function

        self.closedset = set()
        self.openset   = set()
        self.came_from = {}

    def run_loop(self):
        self.target = pygame.mouse.get_pos()
        for click in pygame.event.get():
            if click.type == MOUSEBUTTONDOWN:
                hit = pygame.mouse.get_pressed()
                if hit[0]:
                    self.target = pygame.mouse.get_pos()
                    if (22 < self.target[0] < 420) and (22 < self.target[1] < 260):
                        if self.state == "START":
                            self.startcell = (self.target[0]//self.cell_size[0],self.target[1]//self.cell_size[1])
                            self.gx[self.startcell] = 0
                            self.closedset |= set((self.startcell,))
                            self.state = "GOAL"
                        elif self.state == "GOAL":
                            self.goalcell = (self.target[0]//self.cell_size[0],self.target[1]//self.cell_size[1])
                            self.state = "BARRIER"
                            self.hx[self.startcell] = self.get_dist(self.startcell,self.goalcell)
                        elif self.state == "BARRIER":
                            self.addbarrier = True
                    if self.state == "BARRIER":
                        if (10 < self.target[0] < 250) and (0 < self.target[1] < 17):
                            #start with mouse
                            self.state = "RUN"
                            self.currentcell = self.startcell
                            self.timestart = pygame.time.get_ticks()
                            self.get_openset()
                    if self.state == "DONE":
                        #restart/reset with mouse
                        if   (10 < self.target[0] < 140) and (0 < self.target[1] < 17):
                            self.init()
                        elif (142 < self.target[0] < 240) and (0 < self.target[1] < 17):
                            self.reset()
                    if self.state != "RUN":
                        #toggle animation on/off with mouse
                        if   (340 < self.target[0] < 420) and (0 < self.target[1] < 17):
                            self.animate = (False if self.animate else True)
                        #change move type w/ mouse
                        elif (335 < self.target[0] < 430) and (265 < self.target[1] < 280):
                            self.ADJind = ((self.ADJind + 1) if self.ADJind < 2 else 0)
                        #toggle between true A* and the alt-implementation w/ mouse
                        elif (222 < self.target[0] < 270) and (265 < self.target[1] < 280):
                            self.altmethod = (False if self.altmethod else True)
                            
                elif hit[2] and self.state == "BARRIER":
                    self.delbarrier = True
                    
            if click.type == pygame.MOUSEBUTTONUP:
                hit = pygame.mouse.get_pressed()
                if not hit[0]:
                    self.addbarrier  = False
                if not hit[2]:
                    self.delbarrier  = False

            if click.type == KEYDOWN:
                if click.key == K_RETURN:
                    #reset ket
                    self.init()
                if click.key == K_ESCAPE:
                    #insta quit
                    self.state = "QUIT"
                if self.state == "BARRIER" and click.key == K_SPACE:
                    #start key
                    self.state = "RUN"
                    self.currentcell = self.startcell
                    self.timestart = pygame.time.get_ticks()
                    self.get_openset()
                if click.key == K_d:
                    #turn animation on/off
                    self.animate = (False if self.animate else True)
                if self.state != "RUN":
                    if   click.key == K_1: self.ADJind = 0 #change to rook move
                    elif click.key == K_2: self.ADJind = 1 #change to queen move
                    elif click.key == K_3: self.ADJind = 2 #change to knight move
                    if click.key == K_LSHIFT:
                        #in a map sparse with obstacles the alternate method is almost always faster.
                        #in a more complex map the alternate method is often still faster but can be very indirect.
                        #the performance hit of using the true A* can be worth it.
                        self.altmethod = (False if self.altmethod else True)
                    if self.state == "DONE" and click.key == K_i:
                        #reset, but keep the initial state
                        self.reset()
                        
            if click.type == pygame.QUIT: self.state = "QUIT"

        if self.state == "BARRIER":
            #drawing/deleting barrier cell logic
            self.target = pygame.mouse.get_pos()
            if (22 < self.target[0] < 420) and (22 < self.target[1] < 260):
                if self.addbarrier:
                    if (self.target[0]//self.cell_size[0],self.target[1]//self.cell_size[1]) != self.goalcell:
                        self.barriers |= set(((self.target[0]//self.cell_size[0],self.target[1]//self.cell_size[1]),))
                elif self.delbarrier:
                    self.barriers -= set(((self.target[0]//self.cell_size[0],self.target[1]//self.cell_size[1]),))           

    def reset(self):
        #go back to the initial map state
        tempstart = self.startcell
        tempgoal  = self.goalcell
        tempbar   = self.barriers
        self.init()
        self.startcell = tempstart
        self.goalcell  = tempgoal
        self.barriers  = tempbar
        self.gx[self.startcell] = 0
        self.closedset |= set((self.startcell,))
        self.hx[self.startcell] = self.get_dist(self.startcell,self.goalcell)
        self.state = "BARRIER"
        
    def draw_em(self):
        for cell in self.barriers:
            self.screen.fill((255,255,255),((cell[0]*self.cell_size[0],cell[1]*self.cell_size[1]),self.cell_size))
        for cell in self.closedset:
            self.screen.fill((255,0,255),((cell[0]*self.cell_size[0],cell[1]*self.cell_size[1]),self.cell_size))
        if self.solved:
            for cell in self.solution:
                self.screen.fill((0,255,0),((cell[0]*self.cell_size[0],cell[1]*self.cell_size[1]),self.cell_size))
                self.screen.blit(arial.render(str(len(self.solution)-self.pathind),1,(0,0,0)),(cell[0]*self.cell_size[0]+5,cell[1]*self.cell_size[1]+3))
                self.pathind += 1
            self.pathind = 0
        if self.startcell:
            self.screen.fill((255,255,0),((self.startcell[0]*self.cell_size[0],self.startcell[1]*self.cell_size[1]),self.cell_size))
        if self.goalcell:
            self.screen.fill((0,0,255),((self.goalcell[0]*self.cell_size[0],self.goalcell[1]*self.cell_size[1]),self.cell_size))
            if self.solved:
                self.screen.blit(arial.render(str(len(self.solution)),1,(255,255,255)),(self.goalcell[0]*self.cell_size[0]+5,self.goalcell[1]*self.cell_size[1]+3))

    def get_dist(self,start,goal):
        #returns the distance between two cells
        if start and goal:
            if  self.ADJind == 0:
                #optimum path distance for orthoganal movement 'Rook'
                distance = abs(goal[0]-start[0])+abs(goal[1]-start[1])
            elif self.ADJind == 1:
                #optimum path distance for all 8 adjacent cell movement 'Queen'
                xdis = abs(goal[0]-start[0])
                ydis = abs(goal[1]-start[1])      
                distance = (xdis if xdis > ydis else ydis)
            else:
                #the 'true' distance from one point to another.
                #Useful if nothing is known about the true optimimum heuristic
                #Most effective in this implementation for the 'Knight' type movement
                distance = math.sqrt((goal[0]-start[0])**2+(goal[1]-start[1])**2)    
        else:
            distance = "endpoints not defined"
        return distance

    def get_neighbors(self):
        #get the tentative cells to be evaluated
        openset = set()
        for (i,j) in Adjacents[self.ADJind]:
            check = (self.currentcell[0]+i,self.currentcell[1]+j)
            if check not in self.barriers and check not in self.closedset:
                openset |= set((check,))
        return openset

    def get_openset(self):
        self.openset = self.get_neighbors()

    def get_path(self,cell):
        #anything recursive is slow >.<
        if cell in self.came_from:
##            self.solution |= set((cell,))  #probably faster than list
            self.solution.append(cell)###
            self.get_path(self.came_from[cell])     

    def evaluate(self):
        if self.openset and not self.solved:
            if self.nextcell and (self.altmethod or self.ADJind != 2):
                self.currentcell = self.nextcell
            if not self.altmethod or not self.nextcell:
                for cell in self.openset:
                    if cell not in self.came_from:
                        self.gx[cell] = 1
                        self.hx[cell] = self.get_dist(cell,self.goalcell)
                        self.fx[cell] = self.gx[cell]+self.hx[cell]
                        self.came_from[cell] = self.startcell
                    if self.currentcell not in self.openset:
                        self.currentcell = cell
                    elif self.fx[cell] < self.fx[self.currentcell]:
                        self.currentcell = cell
                    
            if self.currentcell == self.goalcell:
                self.get_path(self.currentcell)
                self.timeend = pygame.time.get_ticks()
                self.solved = True
            
            self.openset.discard(self.currentcell)
            self.closedset |= set((self.currentcell,))

            neighbors = self.get_neighbors()
            self.nextcell = None
            for cell in neighbors:
                tent_g = self.gx[self.currentcell]+1
                if cell not in self.openset:
                    self.openset |= set((cell,))
                    tent_better = True
                elif cell in self.gx and tent_g < self.gx[cell]:
                    tent_better = True
                else:
                    tent_better = False

                if tent_better:
                    self.came_from[cell] = self.currentcell
                    self.gx[cell] = tent_g
                    self.hx[cell] = self.get_dist(cell,self.goalcell)
                    self.fx[cell] = self.gx[cell]+self.hx[cell]
                    if not self.nextcell:
                        self.nextcell = cell
                    elif self.fx[cell]<self.fx[self.nextcell]:
                        self.nextcell = cell
                        
        elif self.solved:
            self.state = "DONE"
        else:
            #reached if no solution is found or possible.
            #Beware that searching for a solution when no solution is possible is very time consuming.
            self.timeend = pygame.time.get_ticks()
            self.state = "DONE"
                
    def update(self):
        if self.state == "RUN":
            self.evaluate()
            if self.animate:
                #for a true estimate of calculation time this must be off obviously
                self.draw_em()
                self.screen.blit(grid,(0,0))
                pygame.display.update()
                self.clock.tick(30)
        else:
            self.screen.fill((0))
            self.draw_em()
            self.screen.blit(grid,(0,0))
            if self.state == "START":
                self.screen.blit(arial.render("Place your start point:",1,(255,255,255)),(10,0))
            elif self.state == "GOAL":
                self.screen.blit(arial.render("Place your goal:",1,(255,255,255)),(10,0))
            elif self.state == "BARRIER":
                self.screen.blit(arial.render("Draw your walls or press spacebar to solve:",1,(255,255,255)),(10,0))
            elif self.state == "DONE":
                self.screen.blit(arial.render("Press 'Enter' to restart. Press 'i' to reset.",1,(255,255,255)),(10,0))
                if self.solved:
                    self.screen.blit(arial.render("Steps: "+str(len(self.solution)),1,(255,255,255)),(20,263))
                    self.screen.blit(arial.render("Time (ms): "+str(self.timeend-self.timestart),1,(255,255,255)),(100,263))
                else:
                    self.screen.blit(arial.render("No solution.",1,(255,255,255)),(20,263))
                    self.screen.blit(arial.render("Time (ms): "+str(self.timeend-self.timestart),1,(255,255,255)),(100,263))
            if self.animate:
                self.screen.blit(arial.render("Animation On",1,(255,255,255)),(340,0))
            else:
                self.screen.blit(arial.render("Animation Off",1,(255,255,255)),(340,0))
            if self.ADJind == 0:
                self.screen.blit(arial.render("Move type: Rook",1,(255,255,255)),(335,263))
            elif self.ADJind == 1:
                self.screen.blit(arial.render("Move type: Queen",1,(255,255,255)),(335,263))
            else:
                self.screen.blit(arial.render("Move type: Knight",1,(255,255,255)),(335,263))
            if not self.altmethod:
                self.screen.blit(arial.render("True A*",1,(255,255,255)),(225,263))
            else:
                self.screen.blit(arial.render("Alternate",1,(255,255,255)),(225,263))
            
            self.run_loop()
            pygame.display.update()

        if self.state == "QUIT":
            pygame.quit();sys.exit()
        
def main():
    Path.update()

#####
if __name__ == "__main__":
    Path = FindIt()
    while 1:
        main()
