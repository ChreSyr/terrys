import pygame
from pygame.locals import *
import math
from Variables_pour_importer import Objet, Types, Bouton
from Variables_pour_importer import horloge, ouvrir_terrain, terrain_vierge, enregistrer_terrain, arrondir, IA_missile_besoin_tourner, get_sign
fps = 40
class Fenetre():
    def __init__(self):
        self.jouer = True
        self.open_window = True
        self.maping = False

class Terrain():
    def __init__(self, position_vert, position_rouge, position_bleu, fond_ecran):
        self.numero = "5"    #input("Quel terrain ?")
        self.position_vert = self.position_rouge = self.position_bleu = ""
        self.fond_ecran = fond_ecran
        self.contenu = []
        ouvrir_terrain(self)
"""
Classe qui cree l'objet terrain
"""

class Personnage(pygame.sprite.Sprite):

    def __init__(self,position,type,sprinter,fighter,tank,image_attak,image_explosion,image_piege,numero_manette,faiblesse,faible):
        pygame.sprite.Sprite.__init__(self)

        if type == "sprinter":
            self.image = sprinter
            self.rect = pygame.Rect(position[0],position[1],40,52)
            self.vitesse = 5
            self.vie = self.full_vie = 45
            self.attaque_speciale = "missile"
        elif type == "fighter":
            self.image = fighter
            self.rect = pygame.Rect(position[0],position[1],60,48)
            self.vitesse = 2.5
            self.vie = self.full_vie = 60
            self.attaque_speciale = "bombe"
        else:
            self.image = tank
            self.rect = pygame.Rect(position[0],position[1],56,60)
            self.vitesse = 2
            self.vie = self.full_vie = 100
            self.attaque_speciale = "glace"

        self.left, self.top = position[0], position[1]
        self.faible = faible
        self.faiblesse = faiblesse
        self.dy = self.dx = self.saut = self.temps_air = 0
        self.state = "STANDING"
        self.regarde = -1
        self.tomber = 0
        self.y_max = 0
        self.val_haut = 1
        self.acceleration = self.ralentissement = 1
        self.empoisonne = 0

        self.index_img = self.count = 0
        self.image = dict([(direction,[self.image.subsurface(x,y,self.rect.width,self.rect.height)for x in range(0,self.rect.width*4,self.rect.width)]) for direction,y in zip((-1,1),range(0,self.rect.height*2,self.rect.height))])
        self.direction = -1

        self.image_attak = [image_attak.subsurface(index,0,20,20)for index in range(0,80,20)]
        self.image_explosion = image_explosion
        self.image_piege = image_piege

        self.tirer_attak = self.temps_rechargement_attak = 0
        self.tirer_missile = self.temps_rechargement_missile = 0
        self.tirer_bombe = self.temps_rechargement_bombe = 0
        self.tirer_glace = self.temps_rechargement_glace = self.degel = 0
        self.tirer_piege = self.temps_rechargement_piege = 0

        groupe_pers.add(self)

    def move(self):

        #Effets blocs
        for bloc in groupe_bloc_effet:
            if self.rect.colliderect(bloc) and bloc.numero == "axel":
                self.acceleration = 2
                break
            else:
                self.acceleration = 1
            if self.rect.colliderect(bloc) and bloc.numero == "jump":
                if self.rect.left < bloc.rect.left:
                    diff = self.rect.right - bloc.rect.left
                else:
                    diff = bloc.rect.right - self.rect.left
                if diff > 7:
                    self.val_haut = 3
                    self.saut = 160000/(27*150**2)
                    self.state = "JUMPING"
                    self.temps_air = 0
                    if self.tomber:
                        self.tomber = 0
                    break

        #Rencontre piege
        for piege in groupe_piege:
            if self.rect.colliderect(piege.rect) and piege.vie > 0 and piege.lanceur != self:
                piege.vie = 0
                if piege.image == piege_vert:
                    self.empoisonne = 800
                elif piege.image == piege_rouge:
                    self.vie -= 5
                elif piege.image == piege_bleu:
                    self.ralentissement = 3.999

        if self.ralentissement > 1:
            self.ralentissement -= 0.003
            if not self.ralentissement > 3:
                self.ralentissement = 1

        if self.empoisonne:
            if self.empoisonne%100 == 0:
                self.vie -= 1
            self.empoisonne -= 1

        #Deplacement vertical
        if self.state == "STANDING":
            if self.joystick.get_axis(3) < -0.5:
                if self.tomber:
                    self.temps_air = self.tomber = 0
                self.saut = 160000/(27*100**2)
        elif self.saut == 0 and self.state == "JUMPING":
            if self.temps_air == 0:
                self.temps_air = 7.5
            self.saut = 160000/(27*85**2)
            self.tomber = 1

        if self.saut:
            self.jump()

        self.top += self.dy
        self.rect.top = self.top
        self.collision(0,self.dy)

        #Deplacement horizontal + Animation
        self.dx = round(self.joystick.get_axis(2)) * self.vitesse * self.acceleration / int(self.ralentissement)
        self.left += self.dx
        self.rect.left = self.left
        if self.dx:
            self.regarde = round(self.joystick.get_axis(2))
        else:
            self.index_img = 0
            self.count = 0

        temp = self.rect.copy()
        self.collision(self.dx,0)
        if self.rect.contains(temp):
            if round(self.joystick.get_axis(2)):
                self.direction = round(self.joystick.get_axis(2))
                self.count += 0.5 / (self.ralentissement *2)
                if not self.count < 4:
                    self.count = 0
                self.index_img = int(self.count)
            else: self.index_img = 0
        else: self.index_img = 0

        #Lancement attaque
        self.tirer_attak = 1 if math.sqrt(self.joystick.get_axis(0)**2 + self.joystick.get_axis(1)**2) > 0.9 else 0
        if self.temps_rechargement_attak == 0 and self.tirer_attak:
            Attak(self.rect.centerx,self.rect.centery,round(self.joystick.get_axis(0)*100),round(self.joystick.get_axis(1)*100),self.image_attak,self,self.image_explosion,self.faible)
            self.temps_rechargement_attak = 30
        elif self.temps_rechargement_attak != 0:
            self.temps_rechargement_attak -= 1

        #Lancement missile
        if self.attaque_speciale == "missile":
            self.tirer_missile = 1 if self.joystick.get_button(4) or self.joystick.get_button(5) else 0
            if self.temps_rechargement_missile == 0 and self.tirer_missile:
                Missile(self.rect.centerx,self.rect.centery,self.regarde,self)
                self.temps_rechargement_missile = 150
            elif self.temps_rechargement_missile != 0:
                self.temps_rechargement_missile -= 1

        #Lancement bombe
        if self.attaque_speciale == "bombe":
            self.tirer_bombe = 1 if self.joystick.get_button(4) or self.joystick.get_button(5) else 0
            if self.temps_rechargement_bombe == 0 and self.tirer_bombe:
                Bombe(self.rect.centerx,self.rect.centery,self, -1 if self.joystick.get_button(4) else 1)
                self.temps_rechargement_bombe = 300
            elif self.temps_rechargement_bombe != 0:
                self.temps_rechargement_bombe -= 1

        #Lancement rayon glace
        if self.attaque_speciale == "glace":
            self.tirer_glace = 1 if self.joystick.get_button(4) or self.joystick.get_button(5) else 0
            if self.temps_rechargement_glace == 0 and self.tirer_glace:
                Glace(self.rect.centerx, self.rect.centery, self)
                self.temps_rechargement_glace = 100
            elif self.temps_rechargement_glace != 0:
                self.temps_rechargement_glace -= 1

        #Lancement piege
        self.tirer_piege = 1 if self.joystick.get_button(6) or self.joystick.get_button(7) else 0
        if self.temps_rechargement_piege == 0 and self.tirer_piege:
            Piege(self.rect.centerx, self.rect.centery,self.image_piege,self)
            self.temps_rechargement_piege = 100
        elif self.temps_rechargement_piege != 0:
            self.temps_rechargement_piege -= 1

        #Detection etat
        self.statement()

        if self.state == "STANDING":
            if self.dy > 0:
                print(self.temps_air)
                self.dy = self.temps_air = self.saut = self.tomber = self.y_max = 0
                self.val_haut = 1



    def collision(self,dx,dy):
        for bloc in groupe_bloc:
            if self.rect.colliderect(bloc.rect):
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

        for bloc in groupe_bloc:
            if self.rect.colliderect(bloc.rect):
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
                y_chute = self.rect.bottom - self.y_max
                self.saut = 160000/(27*(0.5*y_chute)**2)
                self.temps_air = 0
                self.val_haut = 1
                self.rect.bottom += 1
                self.top = self.rect.top
                self.tomber = 0
                self.y_max = 0
            self.rect.bottom = mur.rect.top
            self.top = self.rect.top
        elif dy < 0:
            self.rect.top = mur.rect.bottom
            self.top = self.rect.top
            self.temps_air = 11/math.sqrt(3*self.saut)

    def jump(self):
            self.dy = (self.saut*self.temps_air**3/-5 + 20*self.temps_air)*self.val_haut
            self.temps_air += 0.125
            self.dy -= (self.saut*self.temps_air**3/-5 + 20*self.temps_air)*self.val_haut

            #Creation variable pour calculer la hauteur du saut
            if self.dy > 0 and not self.y_max:
                self.y_max = self.rect.bottom
                print(self.temps_air)

    def statement(self):
        collide = False
        temp = self.rect.copy()
        temp.top += 1
        for bloc in groupe_bloc:
            if temp.colliderect(bloc.rect) and not(self.state == "JUMPING" and bloc.numero == "slim" and self.saut < 50):
                self.state = "STANDING"
                collide = True
                break # pas besoin de regarder les autres murs
        if not collide:
            self.state = "JUMPING"
"""
Classe qui definit les personnages
"""

#_______________________________________________________________________________

#Fonction qui prends un screenshot
def screenshot():
    sub = ecran.subsurface(pygame.Rect(0,0,(len(terrain.contenu[0])-3)*30,(len(terrain.contenu)-3)*30))
    pygame.image.save(sub,"screenshot.png")

#Fonction qui sert a l'affichage dans la fenetre Maping
def affichage(carre):
    ecran.blit(terrain.fond_ecran, (0,0))
    for groupe in (groupe_bloc, groupe_bouton_bloc, groupe_bouton_maping):
        groupe.draw(ecran)
    ecran.blit(bloc_select, carre.topleft)
    for bloc in groupe_bloc_effet:
        ecran.blit(bloc.image.subsurface(0,0,30,30), (bloc.rect.left, bloc.rect.top))
    pygame.display.flip()

#Fonction qui permet de rajouter un bloc
def ajout(groupe_bloc,groupe_bloc_effet,case,coord_x,coord_y):
    if case == "bloc":
        groupe_bloc.add(Objet(coord_x,coord_y,30,30,bloc_image,"bloc"))
    elif case == "grnd":
        groupe_bloc.add(Objet(coord_x,coord_y,60,60,ground,"grnd"))
    elif case == "escR":
        groupe_bloc.add(Objet(coord_x,coord_y,15,15,stair_right,"escR"))
        groupe_bloc.add(Objet(coord_x,coord_y+15,30,15,slab_down,"escR"))
    elif case == "escL":
        groupe_bloc.add(Objet(coord_x+15,coord_y,15,15,stair_left,"escL"))
        groupe_bloc.add(Objet(coord_x,coord_y+15,30,15,slab_down,"escL"))
    elif case == "dalU":
        groupe_bloc.add(Objet(coord_x,coord_y,30,15,slab_up,"dalU"))
    elif case == "dalD":
        groupe_bloc.add(Objet(coord_x,coord_y+15,30,15,slab_down,"dalD"))
    elif case == "slim":
        groupe_bloc.add(Objet(coord_x,coord_y,30,30,trampo,"slim"))
    elif case == "jump":
        groupe_bloc_effet.add(Objet(coord_x,coord_y,30,30,jumper_image,"jump"))
    elif case == "axel":
        groupe_bloc_effet.add(Objet(coord_x,coord_y,30,30,accelerator_image,"axel"))
    return groupe_bloc,groupe_bloc_effet

#Fonction qui permet de sauvegarder les modifications apportees au terrain
def sauvegarder():

    sub = ecran.subsurface(pygame.Rect(0,0,(len(terrain.contenu[0])-2)*30,(len(terrain.contenu)-4)*30))
    pygame.image.save(sub,"Terrains/Terrain"+terrain.numero+".png")

    terrain.contenu = terrain_vierge(terrain.contenu)

    for groupe in (groupe_bloc, groupe_bloc_effet):
        for bloc in groupe:
            terrain.contenu[int(bloc.rect.top/30)+1][int(bloc.rect.left/30)+1] = bloc.numero

    #On enregistre le terrain.contenu
    enregistrer_terrain(terrain)

#Fonction qui vide tout les objets en dehors des blocs et des boutons.
def vide():
    for groupe in (groupe_pers, groupe_attak, groupe_missile, groupe_bombe, groupe_piege):
        for objet in groupe:
            groupe.remove(objet)

#Fonction qui initialise les personnages en fonction du nombre de joysticks
def start():
    vide()
    robot = Personnage((0,0), type.vert, vert_sprinter, vert_fighter, vert_tank, attak_vert, explosion_vert, piege_vert, None, "rouge", "bleu")

    global groupe_lignes, groupe_chute

    groupe_lignes = [ ((101, 34), (184, 34)) , ((185, 49), (199, 49)) , ((821, 49), (940, 49)) , ((200, 64), (289, 64)) , ((386, 124), (529, 124)) , ((551, 124), (754, 124)) , ((371, 139), (385, 139)) , ((755, 139), (769, 139)) , ((356, 154), (370, 154)) , ((341, 169), (355, 169)) , ((326, 184), (340, 184)) , ((311, 199), (325, 199)) , ((296, 214), (310, 214)) , ((161, 229), (295, 229)) , ((551, 304), (724, 304)) , ((725, 319), (739, 319)) , ((740, 334), (754, 334)) , ((755, 349), (769, 349)) , ((26, 394), (79, 394)) , ((176, 394), (244, 394)) , ((266, 394), (334, 394)) , ((161, 409), (175, 409)) , ((245, 409), (265, 409)) , ((335, 409), (349, 409)) , ((80, 424), (160, 424)) , ((350, 424), (940, 424)) ]

    # a l'aide du 1 de module fonctions a copier

    groupe_chute = []
    for i in 1, -1:
        for ligne in groupe_lignes:
            robot.rect.center = ligne[0]
            robot.rect.centerx -= i

            collide = False
            for bloc in groupe_bloc:
                if robot.rect.colliderect(bloc):
                    collide = True

            if collide == False:
                for ligne2 in groupe_lignes:
                    if ligne[0][0] - ligne2[1][0] == i:
                        if ligne[0][1] - ligne2[0][1] == -15:
                            groupe_chute.append([ligne, ligne2])
                    elif ligne[1][0] - ligne2[0][0] == i:
                        if ligne[0][1] - ligne2[0][1] == -15:
                            groupe_chute.append([ligne, ligne2])

    for chute1 in groupe_chute:
        restart = True
        while restart:
            restart = False
            for chute2 in groupe_chute:
                if chute1 != chute2:
                    if chute1[-1] == chute2[0]:
                        for i in range(1,len(chute2)):
                            chute1.append(chute2[i])
                        groupe_chute.remove(chute2)
                        restart = True
                    elif chute1[0] == chute2[-1]:
                        for i in range(1,len(chute2)):
                            chute1.insert(0,chute2[-i-1])
                        groupe_chute.remove(chute2)
                        restart = True
                    elif chute1[0] == chute2[0]:
                        for i in range(1,len(chute2)):
                            chute1.insert(0,chute2[i])
                        groupe_chute.remove(chute2)
                        restart = True
                # utile ?
                    elif chute1[-1] == chute2[-1]:
                        for i in range(1,len(chute2)):
                            chute1.append(chute2[-i-1])
                        groupe_chute.remove(chute2)
                        restart = True

#Fonction qui gere la fenetre Play
def PLAY():
    aff = True
    count_anim = 0
    if len(groupe_pers) == 0:
        start()

    while fenetre.jouer :
        for event in pygame.event.get():
            if event.type == QUIT:
                fenetre.jouer = False
                fenetre.open_window = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clic = pygame.Rect(arrondir(event.pos[0]),arrondir(event.pos[1]),30,30)
                for bouton in groupe_bouton_play:
                    if clic.colliderect(bouton):
                        if bouton.image == modifier_image:
                            fenetre.jouer = False
                            fenetre.maping = True
                        elif bouton.image == rejouer_image and len(groupe_pers) < 2:
                            start()

        if pygame.key.get_pressed()[pygame.K_SPACE]:
            start()
        if pygame.key.get_pressed()[pygame.K_f]:
            fenetre.jouer = False
            fenetre.maping = True

        ecran.blit(terrain.fond_ecran, (0,0))
        groupe_bloc.draw(ecran)

        if count_anim < 8.9:
            count_anim += 0.2
        else:
            count_anim = 0

        for bloc in groupe_bloc_effet:
            ecran.blit(bloc.image.subsurface(int(count_anim)*30,0,30,30), (bloc.rect.left, bloc.rect.top))

        for pers in groupe_pers:
            if pers.vie > 0:
                ecran.blit(pers.image[pers.direction][pers.index_img], pers.rect.topleft)
                couleur = (55 + 200 * abs( pers.vie/pers.full_vie -1 ), 255 - 200 * abs( pers.vie/pers.full_vie -1 ), 50)
                pygame.draw.rect(ecran, couleur, (pers.rect.left, pers.rect.top-10, pers.rect.width*pers.vie/pers.full_vie, 5))
                if pers.degel > 0:
                    ecran.blit(glacon_pers, (pers.rect.centerx - 32, pers.rect.centery - 32))
            else:
                groupe_pers.remove(pers)

        groupe_bouton_play.draw(ecran)
        for i in range(len(groupe_chute)):
            if aff == True:
                ecran.blit(terrain.fond_ecran, (0,0))
                groupe_bloc.draw(ecran)
                for bloc in groupe_bloc_effet:
                    ecran.blit(bloc.image.subsurface(0,0,30,30), (bloc.rect.left, bloc.rect.top))
                for line in groupe_chute[i]:
                    pygame.draw.line(ecran, (0,0,0), line[0], line[1])
                pygame.display.flip()
                pygame.time.wait(1000)
                print(len(groupe_chute[i]))
            else:
                for line in groupe_chute[i]:
                    pygame.draw.line(ecran, (0,0,0), line[0], line[1])

        aff = False

       # for line in groupe_lignes:
       #     pygame.draw.line(ecran, (0,0,0), line[0], line[1])

        pygame.display.flip()

        horloge.tick(fps)

        if pygame.key.get_pressed()[K_SPACE]:
            screenshot()

#Fonction qui gere la fenetre Maping
def MAPING(groupe_bloc,groupe_bloc_effet):

    image = bloc_image
    numero = "bloc"
    bloc_choisi = pygame.Rect(25,(len(terrain.contenu)-1)*30-125,40,40)
    affichage(bloc_choisi)

    while fenetre.maping:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                fenetre.maping = False
                fenetre.open_window = False
                sauvegarder()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                clic = pygame.Rect(arrondir(event.pos[0]),arrondir(event.pos[1]),30,30)

                if clic.colliderect(fen):
                    action =  0
                    for bloc in groupe_bloc:
                        if clic.colliderect(bloc):
                            groupe_bloc.remove(bloc)
                            action = 1
                    for bloc in groupe_bloc_effet:
                        if clic.colliderect(bloc):
                            groupe_bloc_effet.remove(bloc)
                            action = 1
                    if action == 0:
                        groupe_bloc,groupe_bloc_effet = ajout(groupe_bloc,groupe_bloc_effet,numero,arrondir(event.pos[0]),arrondir(event.pos[1]))
                else:
                    for bouton in groupe_bouton_bloc:
                        if clic.colliderect(bouton):
                            image = bouton.image
                            numero = bouton.numero
                            bloc_choisi.left = clic.left - 5
                    for bouton in groupe_bouton_maping:
                        if clic.colliderect(bouton):
                            if bouton == bouton_play:
                                sauvegarder()
                                fenetre.maping = False
                                fenetre.jouer = True

                affichage(bloc_choisi)

            elif pygame.key.get_pressed()[K_RETURN]:
                sauvegarder()
                fenetre.maping = False
                fenetre.jouer = True

            elif event.type == pygame.KEYDOWN and (event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT):
                bloc_choisi.left -= 60 if event.key == pygame.K_LEFT else -60
                decalage = False
                for bouton in groupe_bouton_bloc:
                    if bloc_choisi.colliderect(bouton):
                        image = bouton.image
                        numero = bouton.numero
                        affichage(bloc_choisi)
                        decalage = True
                        break
                if decalage == False:
                    bloc_choisi.left += 60 if event.key == pygame.K_LEFT else -60


        horloge.tick(fps)

        if pygame.key.get_pressed()[K_SPACE]:
            screenshot()

#___________________________________________________________________________________________________________________________________________________________________________


#Initialisation
pygame.init()

ecran = pygame.display.set_mode((0,0))
fond = pygame.image.load("Images/Fond ecran ciel.png").convert()
terrain = Terrain([18,15],[13,25],[0,8], fond)
ecran = pygame.display.set_mode((len(terrain.contenu[0])*30-60, len(terrain.contenu)*30-60))

fen = pygame.Rect(0,0,(len(terrain.contenu[0])-2)*30,(len(terrain.contenu)-6)*30)

#Chargement des images
game_icon = pygame.image.load("Images/Blocs/Bloc.png")
pygame.display.set_icon(game_icon)

bloc_image = pygame.image.load("Images/Blocs/bloc.png").convert().subsurface(0,0,30,30)
stair_left = bloc_image.subsurface(pygame.Rect(0,15,15,15))
stair_right = bloc_image.subsurface(pygame.Rect(0,0,15,15))
slab_down = bloc_image.subsurface(pygame.Rect(0,15,30,15))
slab_up = bloc_image.subsurface(pygame.Rect(0,0,30,15))
ground = pygame.image.load("Images/Blocs/ground.png").convert()
trampo = pygame.image.load("Images/Blocs/Bloc Rebondissant.png").convert()
jumper_image = pygame.image.load("Images/Blocs/JUMP.png").convert()
accelerator_image = pygame.image.load("Images/Blocs/AXEL.png").convert()
bloc_select = pygame.image.load("Images/Blocs/selection bloc.png").convert_alpha()

vert_sprinter = pygame.image.load("Images/Perso/vert sprinter.png").convert_alpha()
vert_fighter = pygame.image.load("Images/Perso/vert fighter.png").convert_alpha()
vert_tank = pygame.image.load("Images/Perso/vert tank.png").convert_alpha()
attak_vert = pygame.image.load("Images/Perso/vert attaque.png").convert_alpha()
explosion_vert = pygame.image.load("Images/Perso/vert explosion.png").convert_alpha()
piege_vert = pygame.image.load("Images/Perso/vert piege.png").convert_alpha()

rouge_sprinter = pygame.image.load("Images/Perso/rouge sprinter.png").convert_alpha()
rouge_fighter = pygame.image.load("Images/Perso/rouge fighter.png").convert_alpha()
rouge_tank = pygame.image.load("Images/Perso/rouge tank.png").convert_alpha()
attak_rouge = pygame.image.load("Images/Perso/rouge attaque.png").convert_alpha()
explosion_rouge = pygame.image.load("Images/Perso/rouge explosion.png").convert_alpha()
piege_rouge = pygame.image.load("Images/Perso/rouge piege.png").convert_alpha()

bleu_sprinter = pygame.image.load("Images/Perso/bleu sprinter.png").convert_alpha()
bleu_fighter = pygame.image.load("Images/Perso/bleu fighter.png").convert_alpha()
bleu_tank = pygame.image.load("Images/Perso/bleu tank.png").convert_alpha()
attak_bleu = pygame.image.load("Images/Perso/bleu attaque.png").convert_alpha()
explosion_bleu = pygame.image.load("Images/Perso/bleu explosion.png").convert_alpha()
piege_bleu = pygame.image.load("Images/Perso/bleu piege.png").convert_alpha()

missile_image = pygame.image.load("Images/missile.png").convert_alpha()
explosion_missile = pygame.image.load("Images/Explosion missile.png").convert_alpha()

bombe_image = pygame.image.load("Images/bombe.png").convert_alpha()
explosion_bombe = pygame.image.load("Images/Explosion bombe.png").convert_alpha()

explosion_glace = pygame.image.load("Images/Explosion glace.png").convert_alpha()
glacon_pers =  pygame.image.load("Images/Glacon pers.png").convert_alpha()
glacon_missile =  pygame.image.load("Images/Glacon missile.png").convert_alpha()

modifier_image = pygame.image.load("Images/Bouton modifier.png").convert()
jouer_image = pygame.image.load("Images/Bouton jouer.png").convert()
rejouer_image = pygame.image.load("Images/Bouton rejouer.png").convert()

#Creation des groupes
groupe_missile = pygame.sprite.Group()
groupe_bombe = pygame.sprite.Group()
groupe_attak = pygame.sprite.Group()
groupe_glace = pygame.sprite.Group()
groupe_piege = pygame.sprite.Group()
groupe_pers = pygame.sprite.Group()

groupe_bouton_bloc = pygame.sprite.Group()
groupe_bouton_maping = pygame.sprite.Group()
groupe_bouton_play = pygame.sprite.Group()

groupe_bloc_effet = pygame.sprite.Group()
groupe_bloc  = pygame.sprite.Group()

groupe_choose_pers = pygame.sprite.Group()

x_bloc = y_bloc = -30
for i in range(len(terrain.contenu)):
    for j in range(len(terrain.contenu[i])):
        groupe_bloc,groupe_bloc_effet = ajout(groupe_bloc,groupe_bloc_effet,terrain.contenu[i][j],x_bloc,y_bloc)
        x_bloc += 30
    y_bloc += 30
    x_bloc = -30

#Creation des boutons
bouton_bloc = Bouton(30*1,(len(terrain.contenu)-5)*30,30,30,bloc_image,"bloc",groupe_bouton_bloc)
bouton_stair_right1 = Bouton(30*3,(len(terrain.contenu)-5)*30,15,15,stair_right,"escR",groupe_bouton_bloc)
bouton_stair_right2 = Bouton(30*3,(len(terrain.contenu)-5)*30+15,30,15,slab_down,"escR",groupe_bouton_bloc)
bouton_stair_left1 = Bouton(30*5+15,(len(terrain.contenu)-5)*30,15,15,stair_left,"escL",groupe_bouton_bloc)
bouton_stair_left2 = Bouton(30*5,(len(terrain.contenu)-5)*30+15,30,15,slab_down,"escL",groupe_bouton_bloc)
bouton_slab_down = Bouton(30*7,(len(terrain.contenu)-5)*30+15,30,15,slab_down,"dalD",groupe_bouton_bloc)
bouton_slab_up = Bouton(30*9,(len(terrain.contenu)-5)*30,30,15,slab_up,"dalU",groupe_bouton_bloc)
bouton_trampo = Bouton(30*11,(len(terrain.contenu)-5)*30,30,30,trampo,"slim",groupe_bouton_bloc)
bouton_jumper = Bouton(30*13,(len(terrain.contenu)-5)*30,30,30,jumper_image.subsurface(pygame.Rect(0,0,30,30)),"jump",groupe_bouton_bloc)
bouton_accelerator = Bouton(30*15,(len(terrain.contenu)-5)*30,30,30,accelerator_image.subsurface(pygame.Rect(0,0,30,30)),"axel",groupe_bouton_bloc)

bouton_play = Bouton(30*27,(len(terrain.contenu)-5)*30,120,30,jouer_image,"joue",groupe_bouton_maping)

bouton_maping = Bouton(30*22,(len(terrain.contenu)-5)*30,120,30,modifier_image,"mapi",groupe_bouton_play)
bouton_rejouer = Bouton(30*27,(len(terrain.contenu)-5)*30,120,30,rejouer_image,"rejo",groupe_bouton_play)

#Initialisation des joysticks, de la fenetre et des types des personnages
nb_joysticks = pygame.joystick.get_count()
for i in range(nb_joysticks):
    mon_joystick = pygame.joystick.Joystick(i).init()

fenetre = Fenetre()
fenetre.jouer = True
type = Types("sprinter","sprinter","sprinter")

while fenetre.open_window:
    if fenetre.jouer:
        PLAY()
    if fenetre.maping:
        MAPING(groupe_bloc,groupe_bloc_effet,)

pygame.quit()