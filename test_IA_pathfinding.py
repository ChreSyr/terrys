import pygame
import math
import random
from Variables_pour_importer import Objet, Types, Bouton
from Variables_pour_importer import horloge, arrondir, get_sign, trouve, distance_pnts

class Fenetre():
    def __init__(self):
        self.open_menu = False
        self.open_choose = False
        self.open_play = True
        self.open_maping = False
        self.open_window = True

        self.menu = Menu()
        self.play = Play()
        self.maping = Maping()
        self.choose = Choose()

        self.nb_joysticks = pygame.joystick.get_count()
        for i in range(self.nb_joysticks):
            pygame.joystick.Joystick(i).init()
"""
Classe qui permet de gerer la fenetre
"""

class Terrain():
    def __init__(self):
        self.numero = "5"    #input("Quel terrain ?")
        self.position_vert = self.position_rouge = self.position_bleu = ""
        self.contenu = []
        self.ouvrir_terrain()

        #Creation des groupes
        self.grp_missile = pygame.sprite.Group()
        self.grp_bombe = pygame.sprite.Group()
        self.grp_attak = pygame.sprite.Group()
        self.grp_glace = pygame.sprite.Group()
        self.grp_piege = pygame.sprite.Group()
        self.grp_pers = pygame.sprite.Group()

        self.grp_btn_bloc = pygame.sprite.Group()
        self.grp_btn_maping = pygame.sprite.Group()
        self.grp_btn_choose = pygame.sprite.Group()
        self.grp_btn_play = pygame.sprite.Group()
        self.grp_btn_menu = pygame.sprite.Group()
        self.grp_btn_resultats = pygame.sprite.Group()
        self.grp_btn_fen_quit = pygame.sprite.Group()

        self.grp_bloc = pygame.sprite.Group()
        self.grp_bloc_effet = pygame.sprite.Group()
        self.grp_bloc_pieg = pygame.sprite.Group()

        x_bloc = y_bloc = -30
        for i in range(len(self.contenu)):
            for j in range(len(self.contenu[i])):
                self.ajout(self.contenu[i][j],x_bloc,y_bloc)
                x_bloc += 30
            y_bloc += 30
            x_bloc = -30

        self.nb_survivants = 3

    #Fonction qui permet de rajouter un bloc
    def ajout(self,case,coord_x,coord_y):
        if case == "bloc":
            self.grp_bloc.add(Objet(coord_x,coord_y,30,30,im.bloc,"bloc"))
        elif case == "grnd":
            self.grp_bloc.add(Objet(coord_x,coord_y,30,30,im.ground,"grnd"))
        elif case == "escR":
            self.grp_bloc.add(Objet(coord_x,coord_y,15,15,im.stair_right,"escR"))
            self.grp_bloc.add(Objet(coord_x,coord_y+15,30,15,im.slab_down,"escR"))
        elif case == "escL":
            self.grp_bloc.add(Objet(coord_x+15,coord_y,15,15,im.stair_left,"escL"))
            self.grp_bloc.add(Objet(coord_x,coord_y+15,30,15,im.slab_down,"escL"))
        elif case == "dalU":
            self.grp_bloc.add(Objet(coord_x,coord_y,30,15,im.slab_up,"dalU"))
        elif case == "dalD":
            self.grp_bloc.add(Objet(coord_x,coord_y+15,30,15,im.slab_down,"dalD"))
        elif case == "slim":
            self.grp_bloc.add(Objet(coord_x,coord_y,30,30,im.trampo,"slim"))
        elif case == "jump":
            self.grp_bloc_effet.add(Objet(coord_x,coord_y,30,30,im.jumper,"jump"))
        elif case == "axel":
            self.grp_bloc_effet.add(Objet(coord_x,coord_y,30,30,im.accelerator,"axel"))
        elif case =="pieg":
            self.grp_bloc_pieg.add(Objet(coord_x,coord_y+22,30,4,im.poseur_piege_haut,"pieg"))
            self.grp_bloc.add(Objet(coord_x,coord_y+26,30,4,im.poseur_piege_bas,"pieg"))

    #Fonction qui permet de sauvegarder les modifications apportees au terrain
    def sauvegarder(self):

        #On vide le terrain
        i, j = len(self.contenu)-1, len(self.contenu[0])
        self.contenu = []
        for i in  range(i):
            self.contenu.append(["vide"]*j)

        #On le reremplit
        for groupe in (self.grp_bloc, self.grp_bloc_effet, self.grp_bloc_pieg):
            for bloc in groupe:
                self.contenu[int(bloc.rect.top/30)+1][int(bloc.rect.left/30)+1] = bloc.numero
        self.contenu.append([str(self.position_vert[0]), str(self.position_vert[1]), str(self.position_rouge[0]), str(self.position_rouge[1]), str(self.position_bleu[0]), str(self.position_bleu[1])])

        #On le met dans le format du fichier texte
        for i in range (len(self.contenu)):
            self.contenu[i] = "'".join(self.contenu[i])
        self.contenu = "\n".join(self.contenu)

        #On le met dans le fichier texte
        fichier_text = open("Terrains/Terrain"+self.numero+".txt","w")
        fichier_text.write(self.contenu)
        fichier_text.close()

        #On remet self.contenu dans la bonne forme
        self.ouvrir_terrain()

    def ouvrir_terrain(self):
        fichier_text = open("Terrains/Terrain"+self.numero+".txt","r")
        self.contenu = fichier_text.read()
        fichier_text.close()

        self.contenu = self.contenu.split("\n")
        for i in range (len(self.contenu)):
            self.contenu[i] = self.contenu[i].split("'")
        self.position_vert = [int(self.contenu[-1][0]), int(self.contenu[-1][1])]
        self.position_rouge = [int(self.contenu[-1][2]), int(self.contenu[-1][3])]
        self.position_bleu = [int(self.contenu[-1][4]), int(self.contenu[-1][5])]

    #Fonction qui prends un screenshot
    def screenshot(self, name):
        sub = ecran.subsurface(pygame.Rect(0,0,(len(self.contenu[0])-2)*30,(len(self.contenu)-3)*30))
        if name != "Screenshots/Screenshot":
            pygame.image.save(sub, name+".png")
        else:
            conteur = 0
            while conteur > -1:
                conteur += 1
                try:
                    a = pygame.image.load(name+str(conteur)+".png")
                except :
                    pygame.image.save(sub, name+str(conteur)+".png")
                    conteur = -1

"""
Classe qui cree l'objet terrain
"""

class Missile(pygame.sprite.Sprite):
    def __init__(self, centerx,centery, lanceur):
        pygame.sprite.Sprite.__init__(self)
        self.image = [im.missile.subsurface(index,0,24,24)for index in range(0,96,24)]
        self.lanceur = lanceur
        self.rect = pygame.Rect(0,0, 24, 24)
        self.rect.center = (arrondir(centerx)+15,arrondir(centery)+15)
        self.vie = 6
        self.index_img_explosion = 0
        self.degel = 0

        self.x = int(self.rect.centerx/30)
        self.y = int(self.rect.centery/30)
        self.dx = self.dy = 0
        self.act_listes = self.anc_listes = self.new_listes = self.chemin = []

        self.search_cible()
        if self.vie:
            ter.grp_missile.add(self)
        self.index_img = int(self.dx/2 +0.5) +2 if self.dx else int(self.dy/2 +0.5)

    #__________________________________________

    def move(self):

        if self.vie <= 0:
            self.index_img_explosion += 1
            if not self.index_img_explosion < 24.5:
                ter.grp_missile.remove(self)
        else:
            if self.degel:
                self.degel -= 1
            else:
                if self.cible.vie <= 0:
                    self.search_cible()

                if self.vie > 0:
                    if self.besoin_tourner(self.rect.centerx,self.rect.centery):
                        self.recherche_deplacement_vers_cible()

                    self.rect.centerx += self.dx*5
                    self.rect.centery += self.dy*5

                    for groupe in (ter.grp_pers, ter.grp_missile):
                        for objet in groupe:
                            if self.rect.colliderect(objet.rect) and objet != self.lanceur and objet != self and objet.vie > 0:
                                objet.vie -= 15
                                self.vie = 0
                                if groupe == ter.grp_pers:
                                    objet.temps_recharg_anim_degat = 20

                    for bloc in ter.grp_bloc:
                        if self.rect.colliderect(bloc.rect):
                            self.vie = 0

                    self.index_img = int(self.dx/2 +0.5) +2 if self.dx else int(self.dy/2 +0.5)

    def recherche_deplacement_vers_cible(self):
        test = Mis_Chemin([int(self.rect.centerx/30),int(self.rect.centery/30)],[int(self.cible.rect.centerx/30),int(self.cible.rect.centery/30)])
        if test.reussite:
            self.dx = test.prem_dep[0]
            self.dy = test.prem_dep[1]
            self.chemin = test.len_chemin
        else:
            self.x = int(self.rect.centerx/30)
            self.y = int(self.rect.centery/30)
            but = (int(self.cible.rect.centerx/30),int(self.cible.rect.centery/30))

            self.act_listes = [[(self.x, self.y)]]
            self.anc_listes = []
            self.chemin = []
            self.new_listes = []

            if but == (self.x, self.y):
                self.chemin =  [(self.x, self.y), (self.x, self.y)]

            while self.chemin == []:
                for liste in self.act_listes:
                    deplacements = []
                    for i in (1,0), (0,1), (-1,0), (0,-1):
                        if self.deplacement_possible( (liste[-1][0]+i[0], liste[-1][1]+i[1]) ):
                            deplacements.append(i)
                    deplacements_diagonale = []
                    for i in deplacements:
                        for j in deplacements:
                            if math.sqrt((i[0]+j[0])**2) == 1:
                                if self.deplacement_possible( (liste[-1][0]+i[0]+j[0], liste[-1][1]+i[1]+j[1]) ):
                                    ajout = True
                                    for vecteur in deplacements_diagonale:
                                        if (i[0]+j[0], i[1]+j[1]) == vecteur:
                                            ajout = False
                                    if ajout: deplacements_diagonale.append( (i[0]+j[0], i[1]+j[1]) )
                    for i in deplacements_diagonale:
                        deplacements.append(i)
                    for i in deplacements:
                        point = ( (liste[-1][0]+i[0], liste[-1][1]+i[1]) )
                        temp = []
                        for point2 in liste:
                            temp.append(point2)
                        temp.append(point)
                        self.new_listes.append(temp)

                        if point == but:
                            self.chemin = temp
                self.anc_listes = []
                for i in self.act_listes:
                    self.anc_listes.append(i)
                self.act_listes = []
                for i in self.new_listes:
                    self.act_listes.append(i)
                self.new_listes = []

                if self.act_listes == []:
                    self.chemin = [(self.x, self.y), (self.x, self.y)]
                    self.vie = 0

                #2 a copier

            self.dx = self.chemin[1][0]-self.x
            self.dy = self.chemin[1][1]-self.y

            #3 a copier

    def deplacement_possible(self, point):
        ajout = False
        case = ter.contenu[point[1]+1][point[0]+1]
        if case == "vide"or case == "axel" or case == "jump":
            ajout = True
            for listes in self.act_listes, self.anc_listes:
                for liste in listes:
                    if liste[-1] == point:
                        ajout = False
        return ajout

    def search_cible(self):
        cible = None
        distance_cible = 10000
        for pers in ter.grp_pers:
            if pers != self.lanceur and pers.vie > 0:
                self.cible = pers
                self.recherche_deplacement_vers_cible()
                if len(self.chemin) < distance_cible:
                    cible = pers
                    distance_cible = len(self.chemin)
        if cible != None:
            self.cible = cible
        else:
            self.vie = 0

    def besoin_tourner(self, x,y):
        return True if x == int(x/30)*30+15 and y == int(y/30)*30+15 else False

"""
Classe qui definit le missiles a tete chercheuse envoyes par les Sprinters
"""

class Mis_Chemin():
    def __init__(self,pos_dep,pos_arr):
        self.pos_arr = pos_arr
        self.pos_temp = pos_dep
        self.prem_dep = []
        self.reussite = "on sait pas"
        self.len_chemin = []

        while self.reussite == "on sait pas":
            self.len_chemin.append(1)
            self.dep = []
            self.dx = 1 if self.pos_arr[0] > self.pos_temp[0] else -1 if self.pos_arr[0] < self.pos_temp[0] else 0
            self.dy = 1 if self.pos_arr[1] > self.pos_temp[1] else -1 if self.pos_arr[1] < self.pos_temp[1] else 0
            for i in [self.dx,0],[0,self.dy]:
                if i != [0,0] and self.deplacement_possible(i):
                    self.dep.append(i)
            if self.dep == []:
                self.reussite = False
            elif len(self.dep) == 1:
                dep = self.dep[0]
                self.pos_temp[0] += dep[0]
                self.pos_temp[1] += dep[1]
            else:
                if self.deplacement_possible([self.dep[0][0],self.dep[1][1]]):
                    self.dep.append([self.dep[0][0],self.dep[1][1]])
                random.shuffle(self.dep)
                dep = self.dep[0]
                self.pos_temp[0] += dep[0]
                self.pos_temp[1] += dep[1]
            try:
                if self.prem_dep == []:
                    self.prem_dep = dep
            except UnboundLocalError:
                self.reussite = False
                self.prem_dep = (self.dx,self.dy)
            if self.pos_temp == self.pos_arr:
                self.reussite = True

    def deplacement_possible(self, dep):
        ajout = False
        case = ter.contenu[self.pos_temp[1]+dep[1]+1][self.pos_temp[0]+dep[0]+1]
        if case == "vide" or case == "axel" or case == "jump":
            ajout = True
        return ajout

class Bombe(pygame.sprite.Sprite):

    def __init__(self, centre_x, centre_y, lanceur, direction):
        pygame.sprite.Sprite.__init__(self)
        self.coord_lancement =[centre_x,centre_y]
        self.rect = pygame.Rect(centre_x - 10, centre_y - 10, 20, 20)
        self.image = im.bombe
        self.lanceur = lanceur

        self.index_img = self.count = self.index_img_explosion = 0
        self.count_traj = -1
        self.direction = direction
        self.vie = 1
        self.degel = 0

        ter.grp_bombe.add(self)

    def move(self):
        if self.vie <= 0:
            self.index_img_explosion += 0.3
            if not self.index_img_explosion < 8:
                ter.grp_bombe.remove(self)

        elif self.degel:
            self.degel -= 1

        else:
            self.count_traj += 1
            self.rect.centery = self.coord_lancement[1] - ( -self.count_traj**2 + 80*self.count_traj ) /60
            self.rect.centerx += self.direction*8

            explode = False
            for groupe in (ter.grp_pers, ter.grp_missile, ter.grp_bombe):
                for objet in groupe:
                    if self.rect.colliderect(objet.rect) and objet != self.lanceur and objet != self and objet.vie:
                        explode = True
                        break

            for bloc in ter.grp_bloc:
                if self.rect.colliderect(bloc.rect):
                    explode = True

            if explode:
                self.explosion()

    def explosion(self):
        self.vie = 0
        for groupe in (ter.grp_pers, ter.grp_attak, ter.grp_missile, ter.grp_bombe):
            for objet in groupe:
                distance = distance_pnts(objet.rect.center,self.rect.center)
                if distance < 210 and objet != self.lanceur and objet != self and objet.vie:
                    if groupe == ter.grp_bombe:
                        objet.explosion()
                    objet.vie -= (-distance*40) /210 +40
                    if groupe == ter.grp_pers:
                        objet.temps_recharg_anim_degat = 20

"""
Classe qui definit les bombes envoyees par les Fighters
"""

class Glace(pygame.sprite.Sprite):
    def __init__(self, centerx, centery, lanceur):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(centerx-192,centery-192,384,384)
        self.index_img = 0
        self.lanceur = lanceur

        for groupe in(ter.grp_pers, ter.grp_attak, ter.grp_missile, ter.grp_bombe):
            for objet in groupe:
                if objet != self.lanceur:
                    distance = distance_pnts(self.rect.center,objet.rect.center)
                    if distance < 192 and objet.vie > 0 and objet.degel == 0:
                        objet.degel = 300

        ter.grp_glace.add(self)
"""
Classe qui definit les rayons de congelation envoyes par les Tanks
"""

class Piege(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = pygame.Rect(x,y,30,48)
        self.vie = 1
        self.index_img = 0

        for grp in ter.grp_bloc, ter.grp_piege:
            for objet in grp:
                if self.rect.colliderect(objet.rect):
                    self.vie = 0

        if self.vie:
            ter.grp_piege.add(self)
"""
Classe qui definit les cristaux que laissent les personnages derriere eux
"""

class Attak(pygame.sprite.Sprite):

    def __init__(self, centre_x, centre_y, angle, image, lanceur, explosion, couleur):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = pygame.Rect(centre_x - 10, centre_y - 10, 20, 20)
        self.angle = math.radians(round(angle/30)*30)
        self.x, self.y = centre_x, centre_y
        self.lanceur = lanceur
        self.couleur = couleur
        self.explosion = explosion
        self.vie = 1
        self.index_img_explosion = 0

        self.index_img = self.count = 0
        self.degel = 0

        ter.grp_attak.add(self)

    def move(self, test = None):

        if self.vie <= 0:
            self.index_img_explosion += 0.3
            if not self.index_img_explosion < 8:
                ter.grp_attak.remove(self)

        elif self.degel:
            self.degel -= 1
        else:
            self.count += 0.1
            if self.count > 4:
                self.count = 0
            self.index_img = int(self.count)
            self.x += math.cos(self.angle)*7
            self.y += -math.sin(self.angle)*7
            self.rect.centerx = self.x
            self.rect.centery = self.y

            for groupe in(ter.grp_attak, ter.grp_missile):
                for objet in groupe:
                    if self.rect.colliderect(objet.rect) and objet != self.lanceur and objet != self and objet.vie > 0 and test == None:
                        self.vie = 0
                        objet.vie -= 3
                        self.rect.left += math.cos(self.angle)
                        self.rect.top += math.sin(self.angle)
            for pers in ter.grp_pers:
                if self.rect.colliderect(pers.rect) and pers != self.lanceur and pers.vie > 0:
                    self.vie = 0
                    if test == "test":
                        self.vie = -1
                    else:
                        pers.vie -= 3
                        pers.tps_recharg_anim_degat = 10
                        if pers.faiblesse == self.couleur:
                            pers.vie -= 7
            for bloc in ter.grp_bloc:
                if self.rect.colliderect(bloc.rect):
                    self.vie = 0
"""
Classe qui definit les petites attaques que chacun possede
"""

#COPIER LES ATTAQUES ICI

class IA(pygame.sprite.Sprite):

    def __init__(self,position,type,sprinter,fighter,tank,image_attak,image_explosion,faiblesse,couleur):
        pygame.sprite.Sprite.__init__(self)

        self.sprinter = sprinter
        self.fighter = fighter
        self.tank = tank
        self.gros = [pygame.image.load("Images/Perso/Gros/"+couleur+" sprinter.png"),
                     pygame.image.load("Images/Perso/Gros/"+couleur+" fighter.png"),
                     pygame.image.load("Images/Perso/Gros/"+couleur+" tank.png")]

        self.type = type
        if self.type == 0:
            self.image = self.sprinter
            self.rect = pygame.Rect(position[0],position[1],40,52)
            self.vitesse = 6
            self.vie = 45
            self.anim_degat = im.anim_degat_sprinter
            self.anim_ralenti = im.anim_ralenti_sprinter
            self.anim_poison = im.anim_poison_sprinter
        elif self.type == 1:
            self.image = self.fighter
            self.rect = pygame.Rect(position[0],position[1],60,48)
            self.vitesse = 3.5
            self.vie = 60
            self.tps_recharg_saut = 0
            self.anim_degat = im.anim_degat_fighter
            self.anim_ralenti = im.anim_ralenti_fighter
            self.anim_poison = im.anim_poison_fighter
        elif self.type == 2:
            self.image = self.tank
            self.rect = pygame.Rect(position[0],position[1],56,60)
            self.vitesse = 2.5
            self.vie = 100
            self.anim_degat = im.anim_degat_tank
            self.anim_ralenti = im.anim_ralenti_tank
            self.anim_poison = im.anim_poison_tank

        self.tps_recharg_changement_type = 0
        self.left, self.top = position[0], position[1]
        self.pos_init = position
        self.couleur = couleur
        self.faiblesse = faiblesse
        self.dy = self.dx = self.tps_en_air = self.y_max = self.effet_poison = 0
        self.state = "JUMPING"
        self.acceleration = self.effet_gel = 1
        self.force_saut = 0
        self.full_vie = self.vie
        self.tps_recharg_anim_degat = 0
        self.pers_valide = False
        self.fantome = False
        self.effet_rapide = 1
        self.resistance = 0
        self.anim_bouclier = 0
        self.tps_recharg_choix_type = 30
        self.cible = self.distance_cible = 0
        self.destination = self.line_dest = self.count_saut_ia = self.pnt_a_aller = 0
        self.chemin = []

        self.index_img = 0
        self.image = dict([(direction,[self.image.subsurface(x,y,self.rect.width,self.rect.height)for x in range(0,self.rect.width*4,self.rect.width)]) for direction,y in zip((-1,1),range(0,self.rect.height*2,self.rect.height))])
        self.direction = -1
        self.anim_degat = dict([(direction,[self.anim_degat.subsurface(x,y,self.rect.width,self.rect.height)for x in range(0,self.rect.width*4,self.rect.width)]) for direction,y in zip((-1,1),range(0,self.rect.height*2,self.rect.height))])
        self.anim_ralenti = dict([(direction,[self.anim_ralenti.subsurface(x,y,self.rect.width,self.rect.height)for x in range(0,self.rect.width*4,self.rect.width)]) for direction,y in zip((-1,1),range(0,self.rect.height*2,self.rect.height))])
        self.anim_poison = dict([(direction,[self.anim_poison.subsurface(x,y,self.rect.width,self.rect.height)for x in range(0,self.rect.width*4,self.rect.width)]) for direction,y in zip((-1,1),range(0,self.rect.height*2,self.rect.height))])

        self.image_attak = [image_attak.subsurface(index,0,20,20)for index in range(0,80,20)]
        self.image_explosion = image_explosion

        self.tirer_attak = self.tps_recharg_attak = 0
        self.tps_recharg_attak_spe = 0
        self.degel = 0
        self.mort = False
        self.animation = True
        self.indestructible = False

    def reinit(self):
        self.vie = self.full_vie
        self.rect.topleft = self.pos_init
        self.left, self.top = self.pos_init[0], self.pos_init[1]
        self.dy = self.dx = self.tps_en_air = self.y_max = self.effet_poison = self.force_saut = self.tps_recharg_anim_degat = self.tirer_attak = self.tps_recharg_attak = self.tirer_piege = self.tps_recharg_piege = self.degel = self.destination = self.line_dest = self.count_saut_ia = self.pnt_a_aller = 0
        self.chemin = []
        self.state = "JUMPING"
        self.acceleration = self.effet_gel = self.effet_rapide = 1
        self.direction = -1
        self.mort = self.cible = self.distance_cible = self.pers_valide = self.indestructible = False
        self.animation = True
        self.tps_recharg_choix_type = 30

    def changer_type(self):
        if self.type == 0:
            self.image = self.sprinter
            self.rect = pygame.Rect(self.rect.left,self.rect.top,40,52)
            self.vitesse = 6
            self.vie = 45
            self.anim_degat = im.anim_degat_sprinter
            self.anim_ralenti = im.anim_ralenti_sprinter
            self.anim_poison = im.anim_poison_sprinter
        elif self.type == 1:
            self.image = self.fighter
            self.rect = pygame.Rect(self.rect.left,self.rect.top,60,48)
            self.vitesse = 3.5
            self.vie = 60
            self.tps_recharg_saut = 0
            self.anim_degat = im.anim_degat_fighter
            self.anim_ralenti = im.anim_ralenti_fighter
            self.anim_poison = im.anim_poison_fighter
        elif self.type == 2:
            self.image = self.tank
            self.rect = pygame.Rect(self.rect.left,self.rect.top,56,60)
            self.vitesse = 2.5
            self.vie = 100
            self.anim_degat = im.anim_degat_tank
            self.anim_ralenti = im.anim_ralenti_tank
            self.anim_poison = im.anim_poison_tank
        self.full_vie = self.vie
        self.image = dict([(direction,[self.image.subsurface(x,y,self.rect.width,self.rect.height)for x in range(0,self.rect.width*4,self.rect.width)]) for direction,y in zip((-1,1),range(0,self.rect.height*2,self.rect.height))])
        self.anim_degat = dict([(direction,[self.anim_degat.subsurface(x,y,self.rect.width,self.rect.height)for x in range(0,self.rect.width*4,self.rect.width)]) for direction,y in zip((-1,1),range(0,self.rect.height*2,self.rect.height))])
        self.anim_ralenti = dict([(direction,[self.anim_ralenti.subsurface(x,y,self.rect.width,self.rect.height)for x in range(0,self.rect.width*4,self.rect.width)]) for direction,y in zip((-1,1),range(0,self.rect.height*2,self.rect.height))])
        self.anim_poison = dict([(direction,[self.anim_poison.subsurface(x,y,self.rect.width,self.rect.height)for x in range(0,self.rect.width*4,self.rect.width)]) for direction,y in zip((-1,1),range(0,self.rect.height*2,self.rect.height))])
        self.pers_valide = False
        self.tps_recharg_changement_type = 30

    def move(self, sauter=0, deplacer=0):

        if self.vie <= 0 and self.indestructible == False:
            if self.animation:
                if self.mort == False:
                    self.mort = True
                    self.tps_en_air = 0
                    self.force_saut = 40
                    ter.nb_survivants -= 1
                self.jump()
                self.top += self.dy
                self.rect.top = self.top
                if self.top > len(ter.contenu)*30:
                    self.animation = False

        elif self.degel:
            self.degel -= 1
        else:

            #Effets blocs
            for bloc in ter.grp_bloc_effet:
                if self.rect.colliderect(bloc) and bloc.numero == "axel" and not self.fantome:
                    self.acceleration = 2
                    break
                else:
                    self.acceleration = 1
                if self.rect.colliderect(bloc) and bloc.numero == "jump" and not self.fantome:
                    self.force_saut = 100
                    self.tps_en_air = 0
                    break

            #Rencontre piege
            for piege in ter.grp_piege:
                if self.rect.colliderect(piege.rect) and piege.vie > 0:
                    piege.vie = 0
                    if piege.image == im.piege_vert_bonus:
                        self.effet_rapide = 2.3
                    elif piege.image == im.piege_vert_malus:
                        self.effet_poison = 800
                    elif piege.image == im.piege_rouge_bonus:
                        self.vie += 10
                        if self.vie > self.full_vie:
                            self.vie = self.full_vie
                    elif piege.image == im.piege_rouge_malus:
                        self.vie -= 5
                        self.tps_recharg_anim_degat = 20
                    elif piege.image ==im.piege_bleu_bonus:
                        self.indestructible = self.vie
                        self.resistance = 1000
                    elif piege.image == im.piege_bleu_malus:
                        self.effet_gel = 3.3

            if self.effet_rapide > 1:
                self.effet_rapide -= 0.001
                if not self.effet_rapide > 2:
                    self.effet_rapide = 1

            if self.effet_gel > 1:
                self.effet_gel -= 0.001
                if not self.effet_gel > 3:
                    self.effet_gel = 1

            if self.effet_poison:
                if self.effet_poison%100 == 0:
                    self.vie -= 1
                    self.tps_recharg_anim_degat = 10
                self.effet_poison -= 1

            if self.resistance:
                self.resistance -= 1
                if self.resistance == 0:
                    self.indestructible = 0

            if self.anim_bouclier:
                self.anim_bouclier -= 1
            if not self.test_collision() or self.fantome:

                #Recherche dep a faire
                if self.type == 0:
                    dx = self.vitesse * self.acceleration * self.effet_rapide / int(self.effet_gel)

                    if self.pnt_a_aller:
                        if self.pnt_a_aller != -1:
                            if abs(self.pnt_a_aller[0] - self.rect.centerx) < dx:
                                self.rect.center = self.pnt_a_aller
                                self.pnt_a_aller = -1
                            else:
                                deplacer = get_sign(self.pnt_a_aller[0] - self.rect.centerx)
                        elif self.chemin and self.chemin[-1] != self.chemin[self.count_saut_ia+2]:
                            self.count_saut_ia += 1
                            sauter = self.chemin[self.count_saut_ia+1][0]
                            deplacer = self.chemin[self.count_saut_ia+1][1]
                        elif self.rect.center != self.middle_line(self.line_dest):
                            if self.find_lines(self.rect.center) == self.find_lines(self.line_dest[0]):
                                self.pnt_a_aller = self.middle_line(self.line_dest)
                            else:
                                self.pnt_a_aller = 0
                        else:
                            self.pnt_a_aller = 0

                    elif self.state == "STANDING":
                        self.count_saut_ia = self.destination = self.line_dest = self.pnt_a_aller = 0
                        self.chemin = []
                        lines = self.find_lines(self.rect.center)
                        self.line_dest = self.sprinter_find_way_dest()
                        if lines:
                            if lines.grp == self.destination.grp:
                                self.pnt_a_aller = self.middle_line(self.line_dest)
                            else:
                                for poss1 in self.find_grp_poss(lines.grp):
                                    if poss1[-1] == self.destination.grp:
                                        self.chemin.append([poss1])
                                    for poss2 in self.find_grp_poss(poss1[-1]):
                                        if poss2[-1] == self.destination.grp:
                                            self.chemin.append([poss1,poss2])
                                        for poss3 in self.find_grp_poss(poss2[-1]):
                                            if poss3[-1] == self.destination.grp:
                                                self.chemin.append([poss1,poss2,poss3])
                                            for poss4 in self.find_grp_poss(poss3[-1]):
                                                if poss4[-1] == self.destination.grp:
                                                    self.chemin.append([poss1,poss2,poss3,poss4])
                                #print(self.chemin)
                                tps_tot = 1000000
                                chemin = [0]
                                for grp_poss in self.chemin:
                                    tps_parcours = 0
                                    pos_arr = self.rect.center
                                    for poss in grp_poss:
                                        tps_parcours += abs(pos_arr[0] - poss[0][0])
                                        for i in range(len(poss)-3):
                                            tps_parcours += 1
                                        pos_arr = poss[1]
                                        for line in poss[-1]:
                                            if line == self.line_dest:
                                                tps_parcours += abs(pos_arr[0] - self.middle_line(self.line_dest)[0])
                                    if tps_parcours < tps_tot:
                                        tps_tot = tps_parcours
                                        chemin = grp_poss[0]
                                self.chemin = chemin
                                self.pnt_a_aller = self.chemin[0]

                #Check deplacement vertical sprinter
                if self.type == 0 and self.state == "STANDING" and sauter:
                        self.force_saut = 80

                #Check deplacement vertical fighter
                elif self.type == 1:
                    if sauter and self.tps_recharg_saut == 0:
                        self.tps_en_air = 0
                        self.force_saut = 65
                        self.tps_recharg_saut = 40

                    if self.tps_recharg_saut:
                        self.tps_recharg_saut -= 1

                #Check deplacement vertical tank
                elif self.type == 2 and sauter:
                    self.force_saut += 3

                #Deplacement horizontal + Animation
                if deplacer:
                    self.dx = deplacer * self.vitesse * self.acceleration * self.effet_rapide / int(self.effet_gel)
                    self.left += self.dx
                    self.rect.left = self.left
                    self.direction = deplacer

                    temp = self.rect.copy()
                    self.collision(self.dx,0)
                    if self.rect.contains(temp):
                        self.index_img += 0.5 / (self.effet_gel *2)
                        if not self.index_img < 4:
                            self.index_img = 0
                    else: self.index_img = 0

                else: self.index_img = 0

                #Deplacement vertical
                if self.force_saut or self.state == "JUMPING":
                    self.jump()
                    self.top += self.dy
                    self.rect.top = self.top
                    self.collision(0,self.dy)

            else:
                self.index_img = 0

            #Lancement attaque
            #self.IA_tirer_attak()

            #Lancement attaque speciale
            if False:                                    #A CHANGER
                if self.type == 0:
                    if self.tps_recharg_attak_spe == 0:
                        Missile(self.rect.centerx,self.rect.centery,self)
                        self.tps_recharg_attak_spe = 250
                if self.type == 2:
                    if self.tps_recharg_attak_spe == 0:
                        Glace(self.rect.centerx, self.rect.centery, self)
                        self.tps_recharg_attak_spe = 450

            #Changement etat special
            if self.type == 1:
                if False: self.fantome = True
                else:     self.fantome = False
                if False:                                    #A CHANGER
                    if self.tps_recharg_attak_spe == 0:
                        Bombe(self.rect.centerx, self.rect.centery, self, self.direction)
                        self.tps_recharg_attak_spe = 300

            if self.tps_recharg_attak_spe != 0:
                self.tps_recharg_attak_spe -= 1

            #Detection etat
            self.statement()

            if self.state == "STANDING" and self.dy > 0: #Si on vient de tomber, pas si on monte sur un bloc en montant
                self.dy = self.tps_en_air = self.force_saut = self.y_max = 0

            if self.tps_recharg_anim_degat:
                self.tps_recharg_anim_degat -= 1

        if self.indestructible != False:
            if self.vie != self.indestructible and self.resistance:
                self.anim_bouclier = 7
            self.vie = self.indestructible

    def collision(self,dx,dy):
        for bloc in ter.grp_bloc:
            if self.rect.colliderect(bloc.rect) and not (self.fantome and bloc.numero != "grnd"):
                if dx and self.state == "STANDING":
                    ecart = self.rect.bottom - bloc.rect.top
                    if ecart < 16:
                        self.rect.bottom -= ecart
                        self.top = self.rect.top
                        if self.test_collision():
                            self.rect.bottom += ecart
                            self.top = self.rect.top
                            self.bloquage(dx,dy,bloc)
                    else:
                        self.bloquage(dx,dy,bloc)
                else:
                    self.bloquage(dx,dy,bloc)

    def test_collision(self):

        for bloc in ter.grp_bloc:
            if self.rect.colliderect(bloc.rect):
                if not (self.fantome and bloc.numero == "grnd"):
                    return True ; break

    def bloquage(self,dx,dy,mur):
        if dx > 0:
            self.rect.right = mur.rect.left
            self.left = self.rect.left
        elif dx < 0:
            self.rect.left = mur.rect.right
            self.left = self.rect.left
        if dy > 0:
            if mur.numero == "slim" and self.state == "JUMPING":
                self.force_saut = dy*7-8
                self.tps_en_air = 0
                self.top = self.rect.top
                self.y_max = 0
            self.rect.bottom = mur.rect.top
            self.top = self.rect.top
        elif dy < 0:
            self.rect.top = mur.rect.bottom
            self.top = self.rect.top
            self.tps_en_air = 0
            self.force_saut = 0

    def jump(self):
        self.dy =  -10*self.tps_en_air**2 + self.tps_en_air *self.force_saut
        self.tps_en_air += 0.125
        self.dy -= -10*self.tps_en_air**2 + self.tps_en_air *self.force_saut

        if self.dy > 0 and not self.y_max:
            self.y_max = self.rect.bottom

    def statement(self):
        self.state = "JUMPING"
        list = []
        temp = self.rect.copy()
        temp.top += 1
        for bloc in ter.grp_bloc:
            if temp.colliderect(bloc.rect) and not(bloc.numero == "slim" and self.dy > 1) and not (self.fantome and bloc.numero != "grnd"):
                self.state = "STANDING"

    def IA_choisir_cible_attak(self,liste):
        self.distance_cible = 10000
        for cible in liste:
            distance_cible = distance_pnts(self.rect.center,cible.rect.center)
            if distance_cible < self.distance_cible:
                self.distance_cible = distance_cible
                self.cible = cible

    def IA_tirer_attak(self):
        liste = []
        for pers in ter.grp_pers:
            if pers != self and pers.vie > 0:
                liste.append(pers)
        for missile in ter.grp_missile:
            if missile.vie > 0 and missile.cible == self:
                liste.append(missile)
        self.IA_choisir_cible_attak(liste)

        if self.tps_recharg_attak:
            self.tps_recharg_attak -= 1
        else:
            while liste != []:
                dis_x = self.cible.rect.centerx-self.rect.centerx
                dis_y = self.cible.rect.centery-self.rect.centery
                hyp = math.sqrt(dis_x**2+dis_y**2)
                if hyp == 0: hyp = 1
                dx = dis_x/hyp
                dy = dis_y/hyp

                case_arrivee = (int(self.cible.rect.centerx/30),int(self.cible.rect.centery/30))

                x,y = self.rect.center
                while True:
                    x += dx*30
                    y += dy*30
                    if ter.contenu[int(y/30)+1][int(x/30)+1] != "vide" and ter.contenu[int(y/30)+1][int(x/30)+1] != "axel" and ter.contenu[int(y/30)+1][int(x/30)+1] != "jump":
                        tir = False
                        liste.remove(self.cible)
                        self.IA_choisir_cible_attak(liste)
                        break
                    elif (int(x/30),int(y/30)) == case_arrivee:
                        tir = True
                        liste = []
                        break
                if tir:
                    dis_x += random.randint(-30,30)
                    dis_y += random.randint(-30,30)
                    hyp = math.sqrt(dis_x**2 + dis_y**2)
                    if hyp == 0: hyp = 1
                    dx = dis_x/hyp
                    dy = dis_y/hyp
                    Attak(self.rect.centerx,self.rect.centery,dx,dy,self.image_attak,self,self.image_explosion,self.couleur)
                    self.tps_recharg_attak = 30


"""
Classe qui definit les ia
"""

class Personnage(pygame.sprite.Sprite):

    def __init__(self,position,type,sprinter,fighter,tank,image_attak,image_explosion,numero_manette,faiblesse,couleur):
        pygame.sprite.Sprite.__init__(self)

        self.sprinter = sprinter
        self.fighter = fighter
        self.tank = tank
        self.gros = [pygame.image.load("Images/Perso/Gros/"+couleur+" sprinter.png"),
                     pygame.image.load("Images/Perso/Gros/"+couleur+" fighter.png"),
                     pygame.image.load("Images/Perso/Gros/"+couleur+" tank.png")]

        self.type = type
        if self.type == 0:
            self.image = self.sprinter
            self.rect = pygame.Rect(position[0],position[1],40,52)
            self.vitesse = 6
            self.vie = 45
            self.anim_degat = im.anim_degat_sprinter
            self.anim_ralenti = im.anim_ralenti_sprinter
            self.anim_poison = im.anim_poison_sprinter
        elif self.type == 1:
            self.image = self.fighter
            self.rect = pygame.Rect(position[0],position[1],60,48)
            self.vitesse = 3.5
            self.vie = 60
            self.tps_recharg_saut = 0
            self.anim_degat = im.anim_degat_fighter
            self.anim_ralenti = im.anim_ralenti_fighter
            self.anim_poison = im.anim_poison_fighter
        elif self.type == 2:
            self.image = self.tank
            self.rect = pygame.Rect(position[0],position[1],56,60)
            self.vitesse = 2.5
            self.vie = 100
            self.anim_degat = im.anim_degat_tank
            self.anim_ralenti = im.anim_ralenti_tank
            self.anim_poison = im.anim_poison_tank

        self.tps_recharg_changement_type = 0
        self.left, self.top = position[0], position[1]
        self.pos_init = position
        self.couleur = couleur
        self.faiblesse = faiblesse
        self.dy = self.dx = self.tps_en_air = self.y_max = self.effet_poison = 0
        self.state = "STANDING"
        self.joystick = pygame.joystick.Joystick(numero_manette)
        self.acceleration = self.effet_gel = 1
        self.force_saut = 0
        self.full_vie = self.vie
        self.tps_recharg_anim_degat = 0
        self.pers_valide = False
        self.fantome = False
        self.effet_rapide = 1
        self.resistance = 0
        self.anim_bouclier = 0

        self.index_img = 0
        self.image = dict([(direction,[self.image.subsurface(x,y,self.rect.width,self.rect.height)for x in range(0,self.rect.width*4,self.rect.width)]) for direction,y in zip((-1,1),range(0,self.rect.height*2,self.rect.height))])
        self.direction = -1
        self.anim_degat = dict([(direction,[self.anim_degat.subsurface(x,y,self.rect.width,self.rect.height)for x in range(0,self.rect.width*4,self.rect.width)]) for direction,y in zip((-1,1),range(0,self.rect.height*2,self.rect.height))])
        self.anim_ralenti = dict([(direction,[self.anim_ralenti.subsurface(x,y,self.rect.width,self.rect.height)for x in range(0,self.rect.width*4,self.rect.width)]) for direction,y in zip((-1,1),range(0,self.rect.height*2,self.rect.height))])
        self.anim_poison = dict([(direction,[self.anim_poison.subsurface(x,y,self.rect.width,self.rect.height)for x in range(0,self.rect.width*4,self.rect.width)]) for direction,y in zip((-1,1),range(0,self.rect.height*2,self.rect.height))])

        self.image_attak = [image_attak.subsurface(index,0,20,20)for index in range(0,80,20)]
        self.image_explosion = image_explosion

        self.tirer_attak = self.tps_recharg_attak = 0
        self.tps_recharg_attak_spe = 0
        self.degel = 0
        self.mort = False
        self.animation = True
        self.indestructible = False

    def reinit(self):
        self.vie = self.full_vie
        self.rect.topleft = self.pos_init
        self.left, self.top = self.pos_init[0], self.pos_init[1]
        self.dy = self.dx = self.tps_en_air = self.y_max = self.effet_poison = self.force_saut = self.tps_recharg_anim_degat = self.tirer_attak = self.tps_recharg_attak = self.tirer_piege = self.tps_recharg_piege = self.degel = 0
        self.state = "STANDING"
        self.acceleration = self.effet_gel = self.effet_rapide = 1
        self.direction = -1
        self.mort = False
        self.animation = True
        self.pers_valide = False
        self.indestructible = False

    def changer_type(self):
        if self.type == 0:
            self.image = self.sprinter
            self.rect = pygame.Rect(self.rect.left,self.rect.top,40,52)
            self.vitesse = 6
            self.vie = 45
            self.anim_degat = im.anim_degat_sprinter
            self.anim_ralenti = im.anim_ralenti_sprinter
            self.anim_poison = im.anim_poison_sprinter
        elif self.type == 1:
            self.image = self.fighter
            self.rect = pygame.Rect(self.rect.left,self.rect.top,60,48)
            self.vitesse = 3.5
            self.vie = 60
            self.tps_recharg_saut = 0
            self.anim_degat = im.anim_degat_fighter
            self.anim_ralenti = im.anim_ralenti_fighter
            self.anim_poison = im.anim_poison_fighter
        elif self.type == 2:
            self.image = self.tank
            self.rect = pygame.Rect(self.rect.left,self.rect.top,56,60)
            self.vitesse = 2.5
            self.vie = 100
            self.anim_degat = im.anim_degat_tank
            self.anim_ralenti = im.anim_ralenti_tank
            self.anim_poison = im.anim_poison_tank
        self.full_vie = self.vie
        self.image = dict([(direction,[self.image.subsurface(x,y,self.rect.width,self.rect.height)for x in range(0,self.rect.width*4,self.rect.width)]) for direction,y in zip((-1,1),range(0,self.rect.height*2,self.rect.height))])
        self.anim_degat = dict([(direction,[self.anim_degat.subsurface(x,y,self.rect.width,self.rect.height)for x in range(0,self.rect.width*4,self.rect.width)]) for direction,y in zip((-1,1),range(0,self.rect.height*2,self.rect.height))])
        self.anim_ralenti = dict([(direction,[self.anim_ralenti.subsurface(x,y,self.rect.width,self.rect.height)for x in range(0,self.rect.width*4,self.rect.width)]) for direction,y in zip((-1,1),range(0,self.rect.height*2,self.rect.height))])
        self.anim_poison = dict([(direction,[self.anim_poison.subsurface(x,y,self.rect.width,self.rect.height)for x in range(0,self.rect.width*4,self.rect.width)]) for direction,y in zip((-1,1),range(0,self.rect.height*2,self.rect.height))])
        self.pers_valide = False
        self.tps_recharg_changement_type = 30

    def move(self):
        if self.vie <= 0 and self.indestructible == False:
            if self.animation:
                if self.mort == False:
                    self.mort = True
                    self.tps_en_air = 0
                    self.force_saut = 40
                    ter.nb_survivants -= 1
                self.jump()
                self.top += self.dy
                self.rect.top = self.top
                if self.top > len(ter.contenu)*30:
                    self.animation = False

        elif self.degel:
            self.degel -= 1
        else:

            #Effets blocs
            for bloc in ter.grp_bloc_effet:
                if self.rect.colliderect(bloc) and bloc.numero == "axel" and not self.fantome:
                    self.acceleration = 2
                    break
                else:
                    self.acceleration = 1
                if self.rect.colliderect(bloc) and bloc.numero == "jump" and not self.fantome:
                    self.force_saut = 100
                    self.tps_en_air = 0

                    break

            #Rencontre piege
            for piege in ter.grp_piege:
                if self.rect.colliderect(piege.rect) and piege.vie > 0:
                    piege.vie = 0
                    if piege.image == im.piege_vert_bonus:
                        self.effet_rapide = 2.3
                    elif piege.image == im.piege_vert_malus:
                        self.effet_poison = 800
                    elif piege.image == im.piege_rouge_bonus:
                        self.vie += 10
                        if self.vie > self.full_vie:
                            self.vie = self.full_vie
                    elif piege.image == im.piege_rouge_malus:
                        self.vie -= 5
                        self.tps_recharg_anim_degat = 20
                    elif piege.image ==im.piege_bleu_bonus:
                        self.indestructible = self.vie
                        self.resistance = 1000
                    elif piege.image == im.piege_bleu_malus:
                        self.effet_gel = 3.3

            if self.effet_rapide > 1:
                self.effet_rapide -= 0.001
                if not self.effet_rapide > 2:
                    self.effet_rapide = 1

            if self.effet_gel > 1:
                self.effet_gel -= 0.001
                if not self.effet_gel > 3:
                    self.effet_gel = 1

            if self.effet_poison:
                if self.effet_poison%100 == 0:
                    self.vie -= 1
                    self.tps_recharg_anim_degat = 10
                self.effet_poison -= 1

            if self.resistance:
                self.resistance -= 1
                if self.resistance == 0:
                    self.indestructible = 0

            if self.anim_bouclier:
                self.anim_bouclier -= 1

            if not self.test_collision() or self.fantome:

                #Check deplacement vertical sprinter
                if self.type == 0:
                    if self.state == "STANDING" and self.joystick.get_axis(3) < -0.4:
                        self.force_saut = 80

                #Check deplacement vertical fighter
                elif self.type == 1:
                    if self.joystick.get_axis(3) < -0.4 and self.tps_recharg_saut == 0:
                        self.tps_en_air = 0
                        self.force_saut = 65
                        self.tps_recharg_saut = 40

                    if self.tps_recharg_saut:
                        self.tps_recharg_saut -= 1

                #Check deplacement vertical tank
                if self.type == 2:
                    if self.joystick.get_axis(3) < -0.4:
                        self.force_saut += 3

                #Deplacement vertical
                if self.force_saut or self.state == "JUMPING":
                    self.jump()
                    self.top += self.dy
                    self.rect.top = self.top
                    self.collision(0,self.dy)

                #Deplacement horizontal + Animation
                if round(self.joystick.get_axis(2)):
                    self.dx = round(self.joystick.get_axis(2)) * self.vitesse * self.acceleration * self.effet_rapide / int(self.effet_gel)
                    self.left += self.dx
                    self.rect.left = self.left
                    self.direction = round(self.joystick.get_axis(2))

                    temp = self.rect.copy()
                    self.collision(self.dx,0)
                    if self.rect.contains(temp):
                        self.index_img += 0.5 / (self.effet_gel *2)
                        if not self.index_img < 4:
                            self.index_img = 0
                    else: self.index_img = 0

                else: self.index_img = 0
            else: self.index_img = 0

            #Lancement attaque
            if self.tps_recharg_attak == 0 and math.sqrt(self.joystick.get_axis(0)**2 + self.joystick.get_axis(1)**2) > 0.5:
                Attak(self.rect.centerx,self.rect.centery,-get_sign(self.joystick.get_axis(1))*int(math.degrees(math.acos(self.joystick.get_axis(0)))),self.image_attak,self,self.image_explosion,self.couleur)
                self.tps_recharg_attak = 30
            elif self.tps_recharg_attak != 0:
                self.tps_recharg_attak -= 1

            #Lancement attaque speciale
            if self.joystick.get_button(4):
                if self.type == 0:
                    if self.tps_recharg_attak_spe == 0:
                        Missile(self.rect.centerx,self.rect.centery,self)
                        self.tps_recharg_attak_spe = 14#250
                if self.type == 2:
                    if self.tps_recharg_attak_spe == 0:
                        Glace(self.rect.centerx, self.rect.centery, self)
                        self.tps_recharg_attak_spe = 450

            #Changement etat special
            if self.type == 1:
                if self.joystick.get_button(5): self.fantome = True
                else:                           self.fantome = False
                if self.joystick.get_button(4):
                    if self.tps_recharg_attak_spe == 0:
                        Bombe(self.rect.centerx, self.rect.centery, self, self.direction)
                        self.tps_recharg_attak_spe = 300

            if self.tps_recharg_attak_spe != 0:
                self.tps_recharg_attak_spe -= 1

            #Detection etat
            self.statement()

            if self.state == "STANDING" and self.dy > 0: #Si on vient de tomber, pas si on monte sur un bloc en montant
                self.dy = self.tps_en_air = self.force_saut = self.y_max = 0

            if self.tps_recharg_anim_degat:
                self.tps_recharg_anim_degat -= 1

        if self.indestructible != False:
            if self.vie != self.indestructible and self.resistance:
                self.anim_bouclier = 7
            self.vie = self.indestructible

    def collision(self,dx,dy):
        for bloc in ter.grp_bloc:
            if self.rect.colliderect(bloc.rect) and not (self.fantome and bloc.numero != "grnd"):
                if dx and self.state == "STANDING":
                    ecart = self.rect.bottom - bloc.rect.top
                    if ecart < 16:
                        self.rect.bottom -= ecart
                        self.top = self.rect.top
                        if self.test_collision():
                            self.rect.bottom += ecart
                            self.top = self.rect.top
                            self.bloquage(dx,dy,bloc)
                    else:
                        self.bloquage(dx,dy,bloc)
                else:
                    self.bloquage(dx,dy,bloc)

    def test_collision(self):

        for bloc in ter.grp_bloc:
            if self.rect.colliderect(bloc.rect):
                if not (self.fantome and bloc.numero == "grnd"):
                    return True ; break

    def bloquage(self,dx,dy,mur):
        if dx > 0:
            self.rect.right = mur.rect.left
            self.left = self.rect.left
        elif dx < 0:
            self.rect.left = mur.rect.right
            self.left = self.rect.left
        if dy > 0:
            if mur.numero == "slim" and self.state == "JUMPING":
                self.force_saut = dy*7-8
                self.tps_en_air = 0
                self.top = self.rect.top
                self.y_max = 0
            self.rect.bottom = mur.rect.top
            self.top = self.rect.top
        elif dy < 0:
            self.rect.top = mur.rect.bottom
            self.top = self.rect.top
            self.tps_en_air = 0
            self.force_saut = 0

    def jump(self):
        self.dy =  -10*self.tps_en_air**2 + self.tps_en_air *self.force_saut
        self.tps_en_air += 0.125
        self.dy -= -10*self.tps_en_air**2 + self.tps_en_air *self.force_saut

        if self.dy > 0 and not self.y_max:
            self.y_max = self.rect.bottom

    def statement(self):
        self.state = "JUMPING"
        list = []
        temp = self.rect.copy()
        temp.top += 1
        for bloc in ter.grp_bloc:
            if temp.colliderect(bloc.rect) and not(bloc.numero == "slim" and self.dy > 1 and self.joystick.get_axis(3) > -0.4) and not (self.fantome and bloc.numero != "grnd"):
                self.state = "STANDING"
"""
Classe qui definit les personnages
"""

class Menu():
    def __init__(self):
        Bouton(30*22+45,30,120,30,im.cadre_bouton,"MODIFIER",ter.grp_btn_menu)
        Bouton(30*27+45,30,120,30,im.cadre_bouton,"JOUER",ter.grp_btn_menu)

    def utiliser(self):
        bouton_select = "JOUER"

        while fen.open_menu:

            robot = Personnage((0,0), type.vert, im.vert_sprinter, im.vert_fighter, im.vert_tank, im.attak_vert, im.explosion_vert,0, "rouge", "bleu")
            groupe_lignes = [ ((836, 34), (919, 34)) , ((821, 49), (835, 49)) , ((71, 64), (259, 64)) , ((806, 64), (820, 64)) , ((791, 79), (805, 79)) , ((566, 94), (619, 94)) , ((776, 94), (790, 94)) , ((551, 109), (565, 109)) , ((761, 109), (775, 109)) , ((386, 124), (529, 124)) , ((620, 124), (760, 124)) , ((371, 139), (385, 139)) , ((356, 154), (370, 154)) , ((341, 169), (355, 169)) , ((326, 184), (340, 184)) , ((311, 199), (325, 199)) , ((296, 214), (310, 214)) , ((251, 229), (295, 229)) , ((566, 304), (724, 304)) , ((161, 319), (460, 319)) , ((551, 319), (565, 319)) , ((725, 319), (739, 319)) , ((740, 334), (754, 334)) , ((755, 349), (769, 349)) , ((26, 394), (94, 394)) , ((866, 394), (940, 394)) , ((95, 409), (109, 409)) , ((851, 409), (865, 409)) , ((110, 424), (220, 424)) , ((290, 424), (850, 424))]


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    fen.open_menu = False
                    fen.open_window = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    clic = pygame.Rect(arrondir(event.pos[0]),arrondir(event.pos[1]),30,30)
                    for bouton in ter.grp_btn_menu:
                        if clic.colliderect(bouton):
                            self.changer(bouton.numero)
            try:
                if vert.joystick.get_button(1) and bouton_select == "MODIFIER":
                    bouton_select = "JOUER"
                elif vert.joystick.get_button(3) and bouton_select == "JOUER":
                    bouton_select = "MODIFIER"
                if vert.joystick.get_button(0):
                    self.changer(bouton_select)
            except: None

            ecran.blit(im.fond_ground, (0,0))
            ter.grp_btn_menu.draw(ecran)
            for bouton in ter.grp_btn_menu:
                if bouton.numero == bouton_select:
                    ecran.blit(im.cadre_bouton_select, bouton.rect.topleft)
                ecran.blit(police30.render(bouton.numero, 1, (0,0,0)), (bouton.rect.left+12, bouton.rect.top+12))
            pygame.display.flip()
            horloge.tick(fps)

    def changer(self,fenetre):
        if fenetre == "MODIFIER":
            fen.open_menu = False
            fen.open_maping = True
        elif fenetre == "JOUER":
            fen.open_menu = False
            fen.open_choose = True

class Lines():
    def __init__(self,lines):
        self.grp = lines
        if lines[0][0][0] <= lines[-1][0][0]:
            self.pnt_left = lines[0][0] if lines[0][0][0] < lines[0][1][0] else lines[0][1]
            self.pnt_right = lines[-1][1] if lines[-1][0][0] < lines[-1][1][0] else lines[-1][0]
        else:
            self.pnt_right = lines[0][0] if lines[0][0][0] > lines[0][1][0] else lines[0][1]
            self.pnt_left = lines[-1][1] if lines[-1][0][0] > lines[-1][1][0] else lines[-1][0]
        self.line_top = ((10000, 10000), (10000, 10000))
        self.line_bottom = ((0,0), (0,0))
        self.line_left = ((10000, 10000), (10000, 10000))
        self.line_right = ((0,0), (0,0))
        for line in lines:
            if line[0][1] < self.line_top[0][1]:
                self.line_top = line
            if line[0][1] > self.line_bottom[0][1]:
                self.line_bottom = line
            if line[0][0] < self.line_left[0][0]:
                self.line_left = line
            if line[0][0] > self.line_right[0][0]:
                self.line_right = line

class Chutes():
    def __init__(self,grp):
        len_y = (len(ter.contenu)-5)*30
        len_x = (len(ter.contenu[0])-2)*30
        self.grp = []
        for lines in grp:
            self.grp.append(Lines(lines))
        self.lines_top_left = self.lines_top_right = self.lines_bottom_right = self.lines_bottom_left = 0
        conteur_top_left = conteur_bottom_right = 10000
        conteur_top_right = conteur_bottom_left = 10000
        for lines in self.grp:
            dis = math.sqrt( (len_x-lines.pnt_right[0])**2 + lines.line_top[0][1]**2 )
            if dis < conteur_top_right:
                conteur_top_right = dis
                self.lines_top_right = lines
            dis = math.sqrt( lines.pnt_left[0]**2 + lines.line_top[0][1]**2 )
            if dis < conteur_top_left:
                conteur_top_left = dis
                self.lines_top_left = lines
            dis = math.sqrt( (len_x-lines.pnt_right[0])**2 + (len_y-lines.line_bottom[0][1])**2 )
            if dis < conteur_bottom_right:
                conteur_bottom_right = dis
                self.lines_bottom_right = lines
            dis = math.sqrt( lines.pnt_left[0]**2 + (len_y-lines.line_bottom[0][1])**2 )
            if dis < conteur_bottom_left:
                conteur_bottom_left = dis
                self.lines_bottom_left = lines
        #6 a copier

class IA_chemin():
    def __init__(self,chemin):
        self.chemin = []
        for i in chemin:
            self.chemin.append(i)
        self.tps_en_air = 0
        self.top, self.left = 0,0
        self.force_saut = 0

class IA_terrain():
    def __init__(self):

        """self.liste_chemins = [
                            [
                            [(620, 124), (566, 94), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), [((566, 94), (619, 94)), ((551, 109), (565, 109))]],
                            [(620, 124), (404, 124), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), [((386, 124), (529, 124)), ((371, 139), (385, 139)), ((356, 154), (370, 154)), ((341, 169), (355, 169)), ((326, 184), (340, 184)), ((311, 199), (325, 199)), ((296, 214), (310, 214)), ((251, 229), (295, 229))]]
                            ],

                            [
                            [(919, 34), (937, 394), (0, 1), (0, 1), (0, 1), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), [((866, 394), (940, 394)), ((851, 409), (865, 409)), ((290, 424), (850, 424)), ((221, 420), (289, 420)), ((110, 424), (220, 424)), ((95, 409), (109, 409)), ((26, 394), (94, 394))]]
                            ],

                            [
                            [(551, 109), (491, 124), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), [((386, 124), (529, 124)), ((371, 139), (385, 139)), ((356, 154), (370, 154)), ((341, 169), (355, 169)), ((326, 184), (340, 184)), ((311, 199), (325, 199)), ((296, 214), (310, 214)), ((251, 229), (295, 229))]],
                            [(551, 109), (767, 109), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1),[((836, 34), (919, 34)), ((821, 49), (835, 49)), ((806, 64), (820, 64)), ((791, 79), (805, 79)), ((776, 94), (790, 94)), ((761, 109), (775, 109)), ((620, 124), (760, 124))]]
                            ],

                            [
                            [(619, 94), (760, 124), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), [((836, 34), (919, 34)), ((821, 49), (835, 49)), ((806, 64), (820, 64)), ((791, 79), (805, 79)), ((776, 94), (790, 94)), ((761, 109), (775, 109)), ((620, 124), (760, 124))]],
                            [(619, 94), (415, 124), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), [((386, 124), (529, 124)), ((371, 139), (385, 139)), ((356, 154), (370, 154)), ((341, 169), (355, 169)), ((326, 184), (340, 184)), ((311, 199), (325, 199)), ((296, 214), (310, 214)), ((251, 229), (295, 229))]]
                            ],

                            [
                            [(251, 229), (161, 319), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), [((161, 319), (460, 319))]],
                            [(251, 229), (53, 394), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), [((866, 394), (940, 394)), ((851, 409), (865, 409)), ((290, 424), (850, 424)), ((221, 420), (289, 420)), ((110, 424), (220, 424)), ((95, 409), (109, 409)), ((26, 394), (94, 394))]],
                            [(251, 229), (604, 304), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), [((755, 349), (769, 349)), ((740, 334), (754, 334)), ((725, 319), (739, 319)), ((566, 304), (724, 304)), ((551, 319), (565, 319))]]
                            ],

                            [
                            [(529, 124), (619, 94), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), [((566, 94), (619, 94)), ((551, 109), (565, 109))]],
                            [(529, 124), (610, 304), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), [((755, 349), (769, 349)), ((740, 334), (754, 334)), ((725, 319), (739, 319)), ((566, 304), (724, 304)), ((551, 319), (565, 319))]],
                            [(529, 124), (763, 109), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), [((836, 34), (919, 34)), ((821, 49), (835, 49)), ((806, 64), (820, 64)), ((791, 79), (805, 79)), ((776, 94), (790, 94)), ((761, 109), (775, 109)), ((620, 124), (760, 124))]],
                            [(529, 124), (187, 319), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), [((161, 319), (460, 319))] ,],
                            ],

                            [
                            [(551, 319), (845, 424), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), [((866, 394), (940, 394)), ((851, 409), (865, 409)), ((290, 424), (850, 424)), ((221, 420), (289, 420)), ((110, 424), (220, 424)), ((95, 409), (109, 409)), ((26, 394), (94, 394))]],
                            [(551, 319), (386, 124), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), [((386, 124), (529, 124)), ((371, 139), (385, 139)), ((356, 154), (370, 154)), ((341, 169), (355, 169)), ((326, 184), (340, 184)), ((311, 199), (325, 199)), ((296, 214), (310, 214)), ((251, 229), (295, 229))]],
                            [(551, 319), (164, 319), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (0, 0), (0, 0), [((161, 319), (460, 319))]]
                            ],

                            [
                            [(769, 349), (871, 394), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), [((866, 394), (940, 394)), ((851, 409), (865, 409)), ((290, 424), (850, 424)), ((221, 420), (289, 420)), ((110, 424), (220, 424)), ((95, 409), (109, 409)), ((26, 394), (94, 394))]],
                            [(769, 349), (386, 124), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), [((386, 124), (529, 124)), ((371, 139), (385, 139)), ((356, 154), (370, 154)), ((341, 169), (355, 169)), ((326, 184), (340, 184)), ((311, 199), (325, 199)), ((296, 214), (310, 214)), ((251, 229), (295, 229))]],
                            [(769, 349), (164, 319), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (0, 0), (0, 0), (0, 0), [((161, 319), (460, 319))]]
                            ],

                            [
                            [(26, 394), (250, 319), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), [((161, 319), (460, 319))]]
                            ],

                            [
                            [(940, 394), (616, 304), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), [((755, 349), (769, 349)), ((740, 334), (754, 334)), ((725, 319), (739, 319)), ((566, 304), (724, 304)), ((551, 319), (565, 319))]]
                            ],

                            [
                            [(71, 64), (29, 394), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), [((866, 394), (940, 394)), ((851, 409), (865, 409)), ((290, 424), (850, 424)), ((221, 420), (289, 420)), ((110, 424), (220, 424)), ((95, 409), (109, 409)), ((26, 394), (94, 394))]]
                            ],

                            [
                            [(259, 64), (385, 139), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 0), [((386, 124), (529, 124)), ((371, 139), (385, 139)), ((356, 154), (370, 154)), ((341, 169), (355, 169)), ((326, 184), (340, 184)), ((311, 199), (325, 199)), ((296, 214), (310, 214)), ((251, 229), (295, 229))]]
                            ],

                            [
                            [(161, 319), (29, 394), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), [((866, 394), (940, 394)), ((851, 409), (865, 409)), ((290, 424), (850, 424)), ((221, 420), (289, 420)), ((110, 424), (220, 424)), ((95, 409), (109, 409)), ((26, 394), (94, 394))]],
                            [(161, 319), (355, 169), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),[((386, 124), (529, 124)), ((371, 139), (385, 139)), ((356, 154), (370, 154)), ((341, 169), (355, 169)), ((326, 184), (340, 184)), ((311, 199), (325, 199)), ((296, 214), (310, 214)), ((251, 229), (295, 229))]]
                            ],
                            ]"""

        #5 a copier
        """self.robot = IA((0,0),0,im.vert_sprinter,im.vert_fighter,im.vert_tank,im.attak_vert,im.explosion_vert,"rouge","vert")
        self.act_listes = self.new_listes = self.chemins_finaux = []
        self.groupe_extremites = []
        self.liste_chemins = []
        self.recherche_deplacements_possibles()
        for grp_poss in self.liste_chemins:
            if grp_poss == []:
                self.liste_chemins.remove(grp_poss)
        
        lines_chemins = []
        for lines in groupe_chute.grp:
            lines_chemins.append( self.find_grp_poss(lines) )
        self.liste_chemins = lines_chemins

        liste_finale = []
        for grp_poss in self.liste_chemins:
            poss_liste = []
            for lines in groupe_chute.grp:
                liste = []
                for poss in grp_poss:
                    if self.find_lines(poss[1]) == lines:
                        liste.append(poss)
                if liste:
                    distance = 10000
                    for poss in liste:
                        if len(poss) < distance:
                            distance = len(poss)
                            poss_court = poss
                    poss_liste.append(poss_court)
            liste_finale.append(poss_liste)
        self.liste_chemins = liste_finale"""
        #print(liste_finale)
        self.liste_chemins = [[[(776, 94), (602, 94), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), [((566, 94), (619, 94)), ((551, 109), (565, 109))]],
                               [(650, 124), (404, 124), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), [((386, 124), (529, 124)), ((371, 139), (385, 139)), ((356, 154), (370, 154)), ((341, 169), (355, 169)), ((326, 184), (340, 184)), ((311, 199), (325, 199)), ((296, 214), (310, 214)), ((251, 229), (295, 229))]],
                               [(919, 34), (937, 394), (0, 1), (0, 1), (0, 1), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), [((866, 394), (940, 394)), ((851, 409), (865, 409)), ((290, 424), (850, 424)), ((221, 420), (289, 420)), ((110, 424), (220, 424)), ((95, 409), (109, 409)), ((26, 394), (94, 394))]],
                               [(761, 109), (164, 319), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (0, 0), (0, 0), [((161, 319), (460, 319))]]],
                              [[(619, 94), (760, 124), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), [((836, 34), (919, 34)), ((821, 49), (835, 49)), ((806, 64), (820, 64)), ((791, 79), (805, 79)), ((776, 94), (790, 94)), ((761, 109), (775, 109)), ((620, 124), (760, 124))]],
                               [(551, 109), (491, 124), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), [((386, 124), (529, 124)), ((371, 139), (385, 139)), ((356, 154), (370, 154)), ((341, 169), (355, 169)), ((326, 184), (340, 184)), ((311, 199), (325, 199)), ((296, 214), (310, 214)), ((251, 229), (295, 229))]]],
                              [[(529, 124), (763, 109), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), [((836, 34), (919, 34)), ((821, 49), (835, 49)), ((806, 64), (820, 64)), ((791, 79), (805, 79)), ((776, 94), (790, 94)), ((761, 109), (775, 109)), ((620, 124), (760, 124))]],
                               [(386, 124), (590, 94), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), [((566, 94), (619, 94)), ((551, 109), (565, 109))]],
                               [(529, 124), (610, 304), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), [((755, 349), (769, 349)), ((740, 334), (754, 334)), ((725, 319), (739, 319)), ((566, 304), (724, 304)), ((551, 319), (565, 319))]],
                               [(251, 229), (53, 394), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), [((866, 394), (940, 394)), ((851, 409), (865, 409)), ((290, 424), (850, 424)), ((221, 420), (289, 420)), ((110, 424), (220, 424)), ((95, 409), (109, 409)), ((26, 394), (94, 394))]],
                               [(386, 124), (212, 64), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), [((71, 64), (259, 64))]],
                               [(251, 229), (161, 319), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), [((161, 319), (460, 319))]]],
                              [[(551, 319), (386, 124), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), [((386, 124), (529, 124)), ((371, 139), (385, 139)), ((356, 154), (370, 154)), ((341, 169), (355, 169)), ((326, 184), (340, 184)), ((311, 199), (325, 199)), ((296, 214), (310, 214)), ((251, 229), (295, 229))]],
                               [(769, 349), (871, 394), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), [((866, 394), (940, 394)), ((851, 409), (865, 409)), ((290, 424), (850, 424)), ((221, 420), (289, 420)), ((110, 424), (220, 424)), ((95, 409), (109, 409)), ((26, 394), (94, 394))]],
                               [(551, 319), (164, 319), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (0, 0), (0, 0), [((161, 319), (460, 319))]]],
                              [[(560, 424), (386, 124), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), [((386, 124), (529, 124)), ((371, 139), (385, 139)), ((356, 154), (370, 154)), ((341, 169), (355, 169)), ((326, 184), (340, 184)), ((311, 199), (325, 199)), ((296, 214), (310, 214)), ((251, 229), (295, 229))]],
                               [(500, 424), (724, 304), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), [((755, 349), (769, 349)), ((740, 334), (754, 334)), ((725, 319), (739, 319)), ((566, 304), (724, 304)), ((551, 319), (565, 319))]],
                               [(109, 409), (250, 319), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), [((161, 319), (460, 319))]]],
                              [[(259, 64), (385, 139), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 0), [((386, 124), (529, 124)), ((371, 139), (385, 139)), ((356, 154), (370, 154)), ((341, 169), (355, 169)), ((326, 184), (340, 184)), ((311, 199), (325, 199)), ((296, 214), (310, 214)), ((251, 229), (295, 229))]],
                               [(71, 64), (29, 394), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), [((866, 394), (940, 394)), ((851, 409), (865, 409)), ((290, 424), (850, 424)), ((221, 420), (289, 420)), ((110, 424), (220, 424)), ((95, 409), (109, 409)), ((26, 394), (94, 394))]]],
                              [[(191, 319), (361, 154), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), [((386, 124), (529, 124)), ((371, 139), (385, 139)), ((356, 154), (370, 154)), ((341, 169), (355, 169)), ((326, 184), (340, 184)), ((311, 199), (325, 199)), ((296, 214), (310, 214)), ((251, 229), (295, 229))]],
                               [(161, 319), (29, 394), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), (0, -1), [((866, 394), (940, 394)), ((851, 409), (865, 409)), ((290, 424), (850, 424)), ((221, 420), (289, 420)), ((110, 424), (220, 424)), ((95, 409), (109, 409)), ((26, 394), (94, 394))]]]]


    def find_grp_poss(self,lines_orig):
        grp = []
        for grp_poss in self.liste_chemins:
            print(grp_poss)
            if self.find_lines(grp_poss[0][0]) == lines_orig:
                for i in grp_poss:
                    grp.append(i)
        return grp

    def find_lines(self,point):
        for lines in groupe_chute.grp:
            for line in lines.grp:
                if point[1] == line[0][1]:
                    if line[0][0] <= point[0] <= line[1][0]:
                        return lines
        return None

    def find_line(self,point):
        for lines in groupe_chute.grp:
            for line in lines.grp:
                if point[1] == line[0][1]:
                    if line[0][0] <= point[0] <= line[1][0]:
                        return line
        return None

    def recherche_deplacements_possibles(self):

        for lines in groupe_chute.grp:
            for line in lines.grp:
                liste = []
                for pnt_x in range(line[0][0],line[1][0],30):
                    liste.append((pnt_x,line[0][1]))
                liste.append(line[1])
                for pnt in line[0],line[1]:
                    for i in 1,-1:
                        temp = pygame.Rect(pnt[0]-20,pnt[1]-26,40,52)
                        temp.left += i
                        for bloc in ter.grp_bloc:
                            if temp.colliderect(bloc.rect):
                                liste.remove(pnt)
                                break
                self.groupe_extremites.append(liste)

        for pnts in self.groupe_extremites:
            for pnt in pnts:

                self.act_listes = [IA_chemin([])]
                self.chem_finaux = []
                self.new_listes = []

                for i in (0,-1), (0,1), (1,-1), (0,0), (1,1):

                    self.robot.rect.center = pnt
                    self.robot.left, self.robot.top = self.robot.rect.left,self.robot.rect.top
                    self.robot.tps_en_air = 0
                    self.move(self.robot,i[1],i[0]*80)

                    temp = IA_chemin([])
                    temp.chemin.append(i)
                    temp.left, temp.top = self.robot.left, self.robot.top
                    temp.tps_en_air = self.robot.tps_en_air
                    temp.force_saut = i[0]*80

                    if self.robot.state == "JUMPING":
                        self.new_listes.append(temp)

                self.act_listes = []
                for i in self.new_listes:
                    self.act_listes.append(i)
                self.new_listes = []

                if self.act_listes == []:
                        run = False

                run = True
                while run:

                    for liste in self.act_listes:

                        dep = [liste.chemin[-1],(0,0)] if liste.chemin[-1] != (0,0) else [(0,0)]
                        for i in dep:

                            self.robot.left, self.robot.top = liste.left,liste.top
                            self.robot.rect.topleft = self.robot.left,self.robot.top
                            self.robot.tps_en_air = liste.tps_en_air
                            self.robot.force_saut = liste.force_saut

                            self.move(self.robot,i[1],self.robot.force_saut)

                            temp = IA_chemin(liste.chemin)
                            temp.chemin.append(i)
                            temp.left, temp.top = self.robot.left, self.robot.top
                            temp.tps_en_air = self.robot.tps_en_air
                            temp.force_saut = self.robot.force_saut

                            if self.robot.state == "STANDING":
                                act_lines = self.find_lines(pnt)
                                for lines2 in groupe_chute.grp:
                                    if act_lines != lines2:
                                        for line2 in lines2.grp:
                                            if self.robot.rect.centery == line2[0][1]:
                                                if line2[0][0] <= self.robot.rect.centerx <= line2[1][0]:
                                                    ajout = True
                                                    for chemin in self.chem_finaux:
                                                        if chemin.chemin[-1] == lines2:
                                                            ajout = False
                                                    if ajout == True:
                                                        temp.chemin.append(lines2)
                                                        temp.chemin.insert(0,pnt)
                                                        temp.chemin.insert(1,self.robot.rect.center)
                                                        self.chem_finaux.append(temp)
                            elif self.robot.state == "JUMPING":
                                self.new_listes.append(temp)

                    self.act_listes = []
                    for i in self.new_listes:
                        self.act_listes.append(i)
                    self.new_listes = []

                    if self.act_listes == []:
                        run = False

                    ecran.blit(im.fond,(0,0))
                    ter.grp_bloc.draw(ecran)
                    for liste2 in self.act_listes:
                        pygame.draw.rect(ecran, (255,0,0), ((liste2.left,liste2.top), (40,52)))
                    pygame.draw.rect(ecran, (255,255,0), (pnt, (5,5)))
                    pygame.display.flip()


                self.liste_chemins.append(self.chem_finaux)

                """ecran.blit(im.fond,(0,0))
                ter.grp_bloc.draw(ecran)
                pygame.draw.rect(ecran, (255,255,0), (pnt, (5,5)))
                for chemins in self.chem_finaux:
                    for line in chemins.chemin[-1].grp:
                        pygame.draw.line(ecran, (255,255,0),line[0],line[1])
                pygame.display.flip()
                pygame.time.wait(1000)"""

    def move(self,pers,deplacer = 0, force_saut = 0):

        pers.dx = deplacer*6
        for bloc in ter.grp_bloc_effet:
            if pers.rect.colliderect(bloc) and bloc.numero == "axel":
                pers.dx += deplacer*6
                break
        pers.left += pers.dx
        self.bloquage(pers,pers.dx,0)

        self.statement(pers)

        pers.rect.topleft = pers.left,pers.top
        for bloc in ter.grp_bloc_effet:
            if pers.rect.colliderect(bloc) and bloc.numero == "jump":
                if deplacer:
                    pers.force_saut = 100
                    pers.tps_en_air = 0
                    break

        if pers.state == "JUMPING" or force_saut:

            pers.dy =  -10*pers.tps_en_air**2 + pers.tps_en_air *force_saut
            pers.tps_en_air += 0.125
            pers.dy -= -10*pers.tps_en_air**2 + pers.tps_en_air *force_saut

            pers.top += pers.dy
            self.bloquage(pers,0,pers.dy)

        self.statement(pers)

    def bloquage(self,pers,dx,dy):
        pers.rect.topleft = pers.left,pers.top
        for bloc in ter.grp_bloc:
            if pers.rect.colliderect(bloc.rect):
                if dx < 0:
                    pers.rect.left = bloc.rect.right
                elif dx > 0:
                    pers.rect.right = bloc.rect.left
                if dy < 0:
                    pers.rect.top = bloc.rect.bottom
                    pers.tps_en_air = 0
                    pers.force_saut = 0
                elif dy > 0:
                    pers.rect.bottom = bloc.rect.top
                pers.top = pers.rect.top
                pers.left = pers.rect.left

    def statement(self,pers):
        pers.state = "BLOQUED"
        if pers.test_collision() == None:
            pers.state = "JUMPING"
            pers.rect.top += 1
            if pers.test_collision() == True:
                pers.state = "STANDING"
            pers.rect.top -= 1
        for bloc in ter.grp_bloc_effet:
            if pers.rect.colliderect(bloc) and bloc.numero == "jump" and pers.dx == 0:
                pers.state = "BLOQUED"

#Fonction qui gere la fen Play
class Play():
    def __init__(self):
        Bouton(30*27+45,(len(ter.contenu)-5)*30+15,120,30,im.cadre_bouton,"QUITTER",ter.grp_btn_play)
        Bouton(320,365,120,30,im.cadre_bouton,"REJOUER",ter.grp_btn_resultats)
        Bouton(467,365,120,30,im.cadre_bouton,"MENU ",ter.grp_btn_resultats)
        Bouton(614,365,120,30,im.cadre_bouton,"OPTIONS",ter.grp_btn_resultats)
        Bouton(320,365,120,30,im.cadre_bouton,"ANNULER",ter.grp_btn_fen_quit)
        Bouton(467,365,120,30,im.cadre_bouton,"MENU ",ter.grp_btn_fen_quit)
        Bouton(614,365,120,30,im.cadre_bouton,"OPTIONS",ter.grp_btn_fen_quit)
        self.tps_recharg_chang_btn = 0
        self.count_anim_bloc_effet = 0
        self.btn_fin_select = "REJOUER"
        self.btn_pause_select = "ANNULER"
        self.open_fen_quit = False
        self.pause = False

    def utiliser(self):
        while fen.open_play :

            #Gerance des boutons
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    fen.open_play = False
                    fen.open_window = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    clic = pygame.Rect(arrondir(event.pos[0]),arrondir(event.pos[1]),30,30)
                    for bouton in ter.grp_btn_play:
                        if clic.colliderect(bouton):
                            if bouton.numero == "QUITTER":
                                self.open_fen_quit = self.pause = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == K_SPACE:
                        ter.screenshot("Screenshots/Screenshot")
            try:
                if vert.joystick.get_button(2):
                    self.open_fen_quit = self.pause = True
            except: None

            #Placement de pieges
            self.creation_piege()

            #Deplacements
            if self.pause == False:
                for groupe in (ter.grp_attak, ter.grp_bombe, ter.grp_missile, ter.grp_pers):
                    for objet in groupe:
                        objet.move()
                if self.count_anim_bloc_effet < 8.9: self.count_anim_bloc_effet += 0.2
                else:                                self.count_anim_bloc_effet = 0

            #Affichage
            ecran.blit(im.fond, (0,0))
            ter.grp_bloc.draw(ecran)
            ter.grp_bloc_pieg.draw(ecran)

            for bloc in ter.grp_bloc_effet:
                ecran.blit(bloc.image.subsurface(int(self.count_anim_bloc_effet)*30,0,30,30), (bloc.rect.left, bloc.rect.top))

            for piege in ter.grp_piege:
                if piege.vie <= 0:
                    piege.index_img += 0.3
                    if piege.index_img > 4.7:
                        ter.grp_piege.remove(piege)
                ecran.blit(piege.image.subsurface(48*int(piege.index_img),0,48,48), (piege.rect.left-9,piege.rect.top))

            for pers in ter.grp_pers:
                ecran.blit(pers.image[pers.direction][int(pers.index_img)], pers.rect.topleft)
                if pers.tps_recharg_anim_degat:
                    ecran.blit(pers.anim_degat[pers.direction][int(pers.index_img)], pers.rect.topleft)
                if pers.effet_gel > 1:
                    ecran.blit(pers.anim_ralenti[pers.direction][int(pers.index_img)], pers.rect.topleft)
                if pers.effet_poison and not pers.tps_recharg_anim_degat:
                    ecran.blit(pers.anim_poison[pers.direction][int(pers.index_img)], pers.rect.topleft)
                if pers.degel > 0:
                    ecran.blit(im.glacon_pers, (pers.rect.centerx - 32, pers.rect.centery - 32))
                if pers.vie <= 0:
                    pers.vie = 0
                else:
                    couleur = (55 + 200 * abs( pers.vie/pers.full_vie -1 ), 255 - 200 * abs( pers.vie/pers.full_vie -1 ), 50)
                    haut = pers.rect.top - 10 if pers.rect.top - 10 >= 0 else 0
                    pygame.draw.rect(ecran, couleur, (pers.rect.left, haut, pers.rect.width*pers.vie/pers.full_vie, 5))
                if pers.anim_bouclier:
                    ecran.blit(im.bouclier[pers.anim_bouclier],(pers.rect.left,pers.rect.top))

            for attak in ter.grp_attak:
                if attak.vie > 0:
                    ecran.blit(attak.image[attak.index_img], attak.rect.topleft)
                    if attak.degel > 0:
                        ecran.blit(im.glacon_attak, (attak.rect.centerx - 16, attak.rect.centery - 16))
                else:
                    ecran.blit(attak.explosion.subsurface(int(attak.index_img_explosion)*37,0,37,37), (attak.rect.centerx-37/2, attak.rect.centery-37/2))

            for missile in ter.grp_missile:
                if missile.vie > 0:
                    ecran.blit(missile.image[missile.index_img], missile.rect.topleft)
                    if missile.degel > 0:
                        ecran.blit(im.glacon_attak, (missile.rect.centerx - 16, missile.rect.centery - 16))
                else:
                    ecran.blit(im.explosion_missile.subsurface(int(missile.index_img_explosion)*64,0,64,64), (missile.rect.centerx-32,missile.rect.centery-32))

            for bombe in ter.grp_bombe:
                if bombe.vie > 0:
                    ecran.blit(bombe.image, bombe.rect.topleft)
                    if bombe.degel > 0:
                        ecran.blit(im.glacon_attak, (bombe.rect.centerx - 16, bombe.rect.centery - 16))
                else:
                    ecran.blit(im.explosion_bombe.subsurface(int(bombe.index_img_explosion)*256,0,256,256), ((bombe.rect.centerx-128,bombe.rect.centery-128)))

            for glace in ter.grp_glace:
                glace.index_img += 0.3 if 5 < glace.index_img < 10 else 0.2
                ter.grp_glace.remove(glace) if not glace.index_img < 19 else ecran.blit(im.explosion_glace.subsurface(int(glace.index_img)*384,0,384,384), glace.rect.topleft)

            ter.grp_btn_play.draw(ecran)
            for bouton in ter.grp_btn_play:
                ecran.blit(police30.render(bouton.numero, 1, (0,0,0)), (bouton.rect.left+12, bouton.rect.top+12))

            if ter.nb_survivants == 1:
                for pers in ter.grp_pers:
                    if not pers.mort:
                        pers.indestructible = pers.vie
                        self.resultats(pers.gros[pers.type])

            if self.open_fen_quit:
                self.fen_quit()

            pygame.display.flip()

            horloge.tick(fps)

    #Fonction qui initialise les personnages en fonction du nombre de joysticks
    def start(self):
        global vert, rouge, bleu
        for groupe in (ter.grp_pers, ter.grp_attak, ter.grp_missile, ter.grp_bombe, ter.grp_piege):
            for objet in groupe:
                groupe.remove(objet)

        global ia_ter, groupe_chute

        groupe_chute = Chutes([[ ((836, 34), (919, 34)) , ((821, 49), (835, 49)) , ((806, 64), (820, 64)) , ((791, 79), (805, 79)) , ((776, 94), (790, 94)) , ((761, 109), (775, 109)) , ((620, 124), (760, 124)) ,],[ ((566, 94), (619, 94)) , ((551, 109), (565, 109)) ,],[ ((386, 124), (529, 124)) , ((371, 139), (385, 139)) , ((356, 154), (370, 154)) , ((341, 169), (355, 169)) , ((326, 184), (340, 184)) , ((311, 199), (325, 199)) , ((296, 214), (310, 214)) , ((251, 229), (295, 229)) ,],[ ((755, 349), (769, 349)) , ((740, 334), (754, 334)) , ((725, 319), (739, 319)) , ((566, 304), (724, 304)) , ((551, 319), (565, 319)) ,],[ ((866, 394), (940, 394)) , ((851, 409), (865, 409)) , ((290, 424), (850, 424)) , ((221, 420), (289, 420)) , ((110, 424), (220, 424)) , ((95, 409), (109, 409)) , ((26, 394), (94, 394)) ,],[ ((71, 64), (259, 64)) ,],[ ((161, 319), (460, 319)) ,]])

        # a l'aide du 1 de module fonctions a copier

        ia_ter = IA_terrain()

        if fen.nb_joysticks > 0:
            vert = Personnage(ter.position_vert,type.vert,im.vert_sprinter,im.vert_fighter,im.vert_tank,im.attak_vert,im.explosion_vert,0,"rouge","vert")
        else:
            vert = IA(ter.position_vert,type.vert,im.vert_sprinter,im.vert_fighter,im.vert_tank,im.attak_vert,im.explosion_vert,"rouge","vert")
        if fen.nb_joysticks > 1:
            rouge = Personnage(ter.position_rouge,type.rouge,im.rouge_sprinter,im.rouge_fighter,im.rouge_tank,im.attak_rouge,im.explosion_rouge,0,"bleu","rouge")
        else:
            rouge = IA(ter.position_rouge,type.rouge,im.rouge_sprinter,im.rouge_fighter,im.rouge_tank,im.attak_rouge,im.explosion_rouge,"bleu","rouge")
        if fen.nb_joysticks > 2:
            bleu = Personnage(ter.position_bleu,type.bleu,im.bleu_sprinter,im.bleu_fighter,im.bleu_tank,im.attak_bleu,im.explosion_bleu,0,"vert","bleu")
        else:
            bleu = IA(ter.position_bleu,type.bleu,im.bleu_sprinter,im.bleu_fighter,im.bleu_tank,im.attak_bleu,im.explosion_bleu,"vert","bleu")
        ter.grp_pers.add(vert)
        ter.grp_pers.add(rouge)
        ter.grp_pers.add(bleu)

    #Fonction qui ouvre une fenetre a la fin d'une partie pour dire qui a gagne
    def resultats(self,gagnant):

        ecran.blit(im.cadre_resultats,(250,100))
        ter.grp_btn_resultats.draw(ecran)
        for btn in ter.grp_btn_resultats:
            if btn.numero == self.btn_fin_select:
                ecran.blit(im.cadre_bouton_select, btn.rect.topleft)
            ecran.blit(police30.render(btn.numero, 1, (0,0,0)), (btn.rect.left+12, btn.rect.top+12))
        ecran.blit(gagnant, (300, 150))
        ecran.blit(police50.render("WINNER !", 1, (0,0,0)), (470, 120))

        try:
            if self.tps_recharg_chang_btn == 0:
                if vert.joystick.get_button(1):
                    self.tps_recharg_chang_btn = 10
                    if self.btn_fin_select == "REJOUER":
                        self.btn_fin_select = "MENU "
                    elif self.btn_fin_select == "MENU ":
                        self.btn_fin_select = "OPTIONS"
                elif vert.joystick.get_button(3):
                    self.tps_recharg_chang_btn = 10
                    if self.btn_fin_select == "OPTIONS":
                        self.btn_fin_select = "MENU "
                    elif self.btn_fin_select == "MENU ":
                        self.btn_fin_select = "REJOUER"
            else: self.tps_recharg_chang_btn -= 1
            if vert.joystick.get_button(0):
                self.changer(self.btn_fin_select)
        except:None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                fen.open_play = False
                fen.open_window = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clic = pygame.Rect(arrondir(event.pos[0]),arrondir(event.pos[1]),30,30)
                for btn in ter.grp_btn_resultats:
                    if clic.colliderect(btn.rect):
                        self.tps_recharg_chang_btn = 0
                        self.changer(btn.numero)

    def fen_quit(self):
        ecran.blit(im.cadre_resultats,(250,100))
        ecran.blit(police50.render("ATTENTION", 1, (0,0,0)), (370, 120))
        ecran.blit(police30.render("Vous etes sur le point de quitter la partie", 1, (0,0,0)), (270, 180))
        ecran.blit(police30.render("en cours. Etes-vous sur de continuer ?", 1, (0,0,0)), (270, 205))
        ter.grp_btn_fen_quit.draw(ecran)
        for btn in ter.grp_btn_fen_quit:
            if btn.numero == self.btn_pause_select:
                ecran.blit(im.cadre_bouton_select,btn.rect.topleft)
            ecran.blit(police30.render(btn.numero, 1, (0,0,0)), (btn.rect.left+12, btn.rect.top+12))

        try:
            if self.tps_recharg_chang_btn == 0:
                if vert.joystick.get_button(1):
                    self.tps_recharg_chang_btn = 10
                    if self.btn_pause_select == "ANNULER":
                        self.btn_pause_select = "MENU "
                    elif self.btn_pause_select == "MENU ":
                        self.btn_pause_select = "OPTIONS"
                elif vert.joystick.get_button(3):
                    self.tps_recharg_chang_btn = 10
                    if self.btn_pause_select == "OPTIONS":
                        self.btn_pause_select = "MENU "
                    elif self.btn_pause_select == "MENU ":
                        self.btn_pause_select = "ANNULER"
            else: self.tps_recharg_chang_btn -= 1
            if vert.joystick.get_button(0):
                self.changer(self.btn_pause_select)
        except: None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                fen.open_play = False
                fen.open_window = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clic = pygame.Rect(arrondir(event.pos[0]),arrondir(event.pos[1]),30,30)
                for btn in ter.grp_btn_fen_quit:
                    if clic.colliderect(btn.rect):
                        self.changer(btn.numero)

    def changer(self,fenetre):
        ter.nb_survivants = 3
        self.btn_fin_select = "REJOUER"
        self.btn_pause_select = "ANNULER"
        self.open_fen_quit = self.pause = False
        if fenetre == "MENU ":
            fen.open_play = False
            fen.open_menu = True
        elif fenetre == "OPTIONS":
            fen.open_play = False
            fen.open_choose = True
        if fenetre != "ANNULER":
            for groupe in (ter.grp_attak, ter.grp_missile, ter.grp_bombe, ter.grp_piege):
                for objet in groupe:
                    groupe.remove(objet)
            for pers in ter.grp_pers:
                pers.reinit()

    def creation_piege(self):
        for poseur in ter.grp_bloc_pieg:
            if random.randrange(0,1000) == 0:
                Piege(poseur.rect.left,poseur.rect.top-48,random.choice((im.piege_vert_bonus,im.piege_vert_malus,im.piege_rouge_bonus,im.piege_rouge_malus,im.piege_bleu_bonus,im.piege_bleu_malus)))

#Fonction qui gere la fen open_maping
class Maping():
    def __init__(self):
        Bouton(30*27+45,(len(ter.contenu)-5)*30+15,120,30,im.cadre_bouton,"MENU ",ter.grp_btn_maping)
        Bouton(30*1,(len(ter.contenu)-5)*30,30,30,im.bloc,"bloc",ter.grp_btn_bloc)
        Bouton(30*3,(len(ter.contenu)-5)*30,15,15,im.stair_right,"escR",ter.grp_btn_bloc)
        Bouton(30*3,(len(ter.contenu)-5)*30+15,30,15,im.slab_down,"escR",ter.grp_btn_bloc)
        Bouton(30*5+15,(len(ter.contenu)-5)*30,15,15,im.stair_left,"escL",ter.grp_btn_bloc)
        Bouton(30*5,(len(ter.contenu)-5)*30+15,30,15,im.slab_down,"escL",ter.grp_btn_bloc)
        Bouton(30*7,(len(ter.contenu)-5)*30+15,30,15,im.slab_down,"dalD",ter.grp_btn_bloc)
        Bouton(30*9,(len(ter.contenu)-5)*30,30,15,im.slab_up,"dalU",ter.grp_btn_bloc)
        Bouton(30*11,(len(ter.contenu)-5)*30,30,30,im.trampo,"slim",ter.grp_btn_bloc)
        Bouton(30*13,(len(ter.contenu)-5)*30,30,30,im.jumper.subsurface(pygame.Rect(0,0,30,30)),"jump",ter.grp_btn_bloc)
        Bouton(30*15,(len(ter.contenu)-5)*30,30,30,im.accelerator.subsurface(pygame.Rect(0,0,30,30)),"axel",ter.grp_btn_bloc)
        Bouton(30*17,(len(ter.contenu)-5)*30+22,30,30,im.poseur_piege,"pieg",ter.grp_btn_bloc)

    def utiliser(self):

        image = im.bloc
        numero = "bloc"
        bloc_choisi = pygame.Rect(25,(len(ter.contenu)-1)*30-125,40,40)
        operation = None

        while fen.open_maping:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    fen.open_maping = False
                    fen.open_window = False
                    ter.screenshot("Terrains/Terrain"+ter.numero)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    clic = pygame.Rect(arrondir(event.pos[0]), arrondir(event.pos[1]), 30, 30)
                    if 0 < event.pos[0] < (len(ter.contenu[0])-2)*30 and 0 < event.pos[1] < (len(ter.contenu)-6)*30:
                        operation = "ajout" if ter.contenu[int(event.pos[1]/30)+1][int(event.pos[0]/30)+1] == "vide" else "retrait"
                        if operation == "retrait":
                            for grp in ter.grp_bloc, ter.grp_bloc_effet, ter.grp_bloc_pieg:
                                for bloc in grp:
                                    if bloc.rect.colliderect(clic):
                                        grp.remove(bloc)
                        if operation == "ajout" and ter.contenu[int(event.pos[1]/30)+1][int(event.pos[0]/30)+1] == "vide":
                            ter.ajout(numero,arrondir(event.pos[0]),arrondir(event.pos[1]))
                        ter.sauvegarder()
                    else:
                        for bouton in ter.grp_btn_bloc:
                            if bouton.rect.colliderect(clic):
                                image = bouton.image
                                numero = bouton.numero
                                bloc_choisi.left = clic.left - 5
                        for bouton in ter.grp_btn_maping:
                            if bouton.rect.colliderect(clic):
                                ter.screenshot("Terrains/Terrain"+ter.numero)
                                fen.open_maping = False
                                fen.open_menu = True
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    operation = None

                if operation:
                    new_clic = pygame.Rect(arrondir(event.pos[0]), arrondir(event.pos[1]), 30, 30)
                    if new_clic != clic:
                        if operation == "retrait":
                            for grp in ter.grp_bloc, ter.grp_bloc_effet, ter.grp_bloc_pieg:
                                for bloc in grp:
                                    if bloc.rect.colliderect(new_clic):
                                        grp.remove(bloc)
                        if operation == "ajout" and ter.contenu[int(event.pos[1]/30)+1][int(event.pos[0]/30)+1] == "vide":
                            ter.ajout(numero,arrondir(event.pos[0]),arrondir(event.pos[1]))
                        ter.sauvegarder()
                    clic = new_clic

                elif event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT):
                        bloc_choisi.left -= 60 if event.key == pygame.K_LEFT else -60
                        decalage = False
                        for bouton in ter.grp_btn_bloc:
                            if bloc_choisi.colliderect(bouton):
                                image = bouton.image
                                numero = bouton.numero
                                decalage = True
                                break
                        if decalage == False:
                            bloc_choisi.left += 60 if event.key == pygame.K_LEFT else -60

                    elif event.key == K_SPACE:
                        ter.screenshot("Screenshots/Screenshot")
                    elif event.key == K_RETURN:
                        ter.screenshot("Terrains/Terrain"+ter.numero)
                        fen.open_maping = False
                        fen.open_play = True
                try:
                    if vert.joystick.get_button(0):
                        fen.open_maping = False
                        fen.open_menu = True
                except: None

                ecran.blit(im.fond, (0,0))
                ter.grp_bloc.draw(ecran)
                ter.grp_bloc_pieg.draw(ecran)
                for bloc in ter.grp_bloc_effet:
                    ecran.blit(bloc.image.subsurface(0,0,30,30), (bloc.rect.left, bloc.rect.top))
                ecran.blit(im.cadre_bloc, bloc_choisi.topleft)
                ter.grp_btn_bloc.draw(ecran)
                ter.grp_btn_maping.draw(ecran)
                for bouton in ter.grp_btn_maping:
                    ecran.blit(police30.render(bouton.numero, 1, (0,0,0)), (bouton.rect.left+12, bouton.rect.top+12))
                try:
                    clic = pygame.Rect(arrondir(event.pos[0]),arrondir(event.pos[1]),30,30)
                    for bouton in ter.grp_btn_bloc:
                        if clic.colliderect(bouton.rect):
                            ecran.blit(im.bloc_vise, (arrondir(event.pos[0]), arrondir(event.pos[1])))
                    if event.pos[1] < (len(ter.contenu)-6)*30:
                        ecran.blit(im.bloc_vise, (arrondir(event.pos[0]), arrondir(event.pos[1])))
                except AttributeError: None
                pygame.display.flip()

            horloge.tick(fps)

#Fonction qui gere la fen open_choose_type
class Choose():
    def __init__(self):
        Bouton(30*22+45,30,120,30,im.cadre_bouton,"MENU ",ter.grp_btn_choose)
        Bouton(30*27+45,30,120,30,im.cadre_bouton,"JOUER",ter.grp_btn_choose)

    def utiliser(self):

        while fen.open_choose:

            for i in ter.grp_pers:
                try:
                    if i.tps_recharg_changement_type == 0:
                        if i.joystick.get_axis(2) > 0.5:
                            i.type += 1
                            if i.type > 2:
                                i.type = 0
                            i.changer_type()
                        elif i.joystick.get_axis(2) < -0.5:
                            i.type -= 1
                            if i.type < 0:
                                i.type = 2
                            i.changer_type()
                    else: i.tps_recharg_changement_type -= 1
                    if i.joystick.get_button(8):
                        i.pers_valide = True

                except AttributeError:
                    if i.tps_recharg_choix_type:
                        i.tps_recharg_choix_type -= 1
                    elif random.randint(0,10) == 10:
                        i.type = random.randrange(0,3)
                        i.changer_type()
                        i.pers_valide = True
                    if not i.pers_valide:
                        i.type += 1
                        if i.type > 2:
                            i.type = 0
                        i.changer_type()

            ecran.blit(im.fond_ground, (0,0))
            ter.grp_btn_choose.draw(ecran)
            for bouton in ter.grp_btn_choose:
                ecran.blit(police30.render(bouton.numero, 1, (0,0,0)), (bouton.rect.left+12, bouton.rect.top+12))

            i = 0
            for pers in vert,rouge,bleu:
                ecran.blit(im.cadre_pers, (80+i,100))
                ecran.blit(pers.gros[pers.type], (160-pers.rect.width+i,180-pers.rect.height))
                if pers.pers_valide:
                    ecran.blit(im.validation,(180+i,210))
                ecran.blit(im.cadre_stat, (135+i,278))
                ecran.blit(im.cadre_stat, (135+i,318))
                ecran.blit(im.coeur, (95+i,280))
                ecran.blit(im.eclair, (95+i,320))
                pygame.draw.rect(ecran, (255,255,0), (137+i, 280, 81*pers.vie/100, 30))
                pygame.draw.rect(ecran, (255,255,0), (137+i, 320, 81*pers.vitesse/6, 30))
                if pers.type == 0:
                    ecran.blit(im.gros_missiile, (100+i,360))
                    ecran.blit(police30.render("Missile", 1, (0,0,0)), (95+i,450))
                elif pers.type == 1:
                    ecran.blit(im.gros_bombe, (100+i,360))
                    ecran.blit(police30.render("Bombe", 1, (0,0,0)), (95+i,450))
                elif pers.type == 2:
                    ecran.blit(im.gros_exp_glace, (100+i,360))
                    ecran.blit(police30.render("Glace", 1, (0,0,0)), (95+i,450))
                i += 200

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    fen.open_choose = False
                    fen.open_window = False

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    clic = pygame.Rect(event.pos[0],event.pos[1],1,1)
                    for bouton in ter.grp_btn_choose:
                        if clic.colliderect(bouton.rect):
                            if bouton.numero == "MENU ":
                                fen.open_choose = False
                                fen.open_menu = True
                                for pers in ter.grp_pers:
                                    pers.reinit()
                            elif bouton.numero == "JOUER":
                                fen.open_choose = False
                                fen.open_play = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == K_SPACE:
                        ter.screenshot("Screenshots/Screenshot")
                    elif event.key == K_RETURN:
                        fen.open_choose = False
                        fen.open_play = True

            if vert.pers_valide and rouge.pers_valide and bleu.pers_valide:
                fen.open_choose = False
                fen.open_play = True
                pygame.time.wait(1000)

        type.vert = vert.type
        type.rouge = rouge.type
        type.bleu = bleu.type

#___________________________________________________________________________________________________________________________________________________________________________

#Initialisation
pygame.init()

ecran = pygame.display.set_mode((0,0))
from Variables_pour_importer import Images
im = Images()
ter = Terrain()
ecran = pygame.display.set_mode((len(ter.contenu[0])*30-60, len(ter.contenu)*30-60))
fps = 100

police30 = pygame.font.Font(None, 30)
police50 = pygame.font.Font(None, 50)


fen = Fenetre()
type = Types(0,0,0)
fen.play.start()

while fen.open_window:
    if fen.open_menu:
        fen.menu.utiliser()
    if fen.open_play:
        fen.play.utiliser()
    if fen.open_maping:
        fen.maping.utiliser()
    if fen.open_choose:
        fen.choose.utiliser()

pygame.quit()