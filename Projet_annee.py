import pygame
from pygame.locals import *
import math
import random
from Variables_pour_importer import Objet, Types, Bouton
from Variables_pour_importer import horloge, arrondir, get_sign, trouve


class Fenetre():
    def __init__(self):
        self.open_menu = True
        self.open_choose = False
        self.open_play = False
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


class Terrain:
    def __init__(self):
        self.numero = "5"  # input("Quel terrain ?")
        self.position_vert = self.position_rouge = self.position_bleu = ""
        self.contenu = []
        self.ouvrir_terrain()

        # Creation des groupes
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
                self.ajout(self.contenu[i][j], x_bloc, y_bloc)
                x_bloc += 30
            y_bloc += 30
            x_bloc = -30

        self.nb_survivants = 3

    # Fonction qui permet de rajouter un bloc
    def ajout(self, case, coord_x, coord_y):
        if case == "bloc":
            self.grp_bloc.add(Objet(coord_x, coord_y, 30, 30, im.bloc, "bloc"))
        elif case == "grnd":
            self.grp_bloc.add(Objet(coord_x, coord_y, 30, 30, im.ground, "grnd"))
        elif case == "escR":
            self.grp_bloc.add(Objet(coord_x, coord_y, 15, 15, im.stair_right, "escR"))
            self.grp_bloc.add(Objet(coord_x, coord_y + 15, 30, 15, im.slab_down, "escR"))
        elif case == "escL":
            self.grp_bloc.add(Objet(coord_x + 15, coord_y, 15, 15, im.stair_left, "escL"))
            self.grp_bloc.add(Objet(coord_x, coord_y + 15, 30, 15, im.slab_down, "escL"))
        elif case == "dalU":
            self.grp_bloc.add(Objet(coord_x, coord_y, 30, 15, im.slab_up, "dalU"))
        elif case == "dalD":
            self.grp_bloc.add(Objet(coord_x, coord_y + 15, 30, 15, im.slab_down, "dalD"))
        elif case == "slim":
            self.grp_bloc.add(Objet(coord_x, coord_y, 30, 30, im.trampo, "slim"))
        elif case == "jump":
            self.grp_bloc_effet.add(Objet(coord_x, coord_y, 30, 30, im.jumper, "jump"))
        elif case == "axel":
            self.grp_bloc_effet.add(Objet(coord_x, coord_y, 30, 30, im.accelerator, "axel"))
        elif case == "pieg":
            self.grp_bloc_pieg.add(Objet(coord_x, coord_y + 22, 30, 4, im.poseur_piege_haut, "pieg"))
            self.grp_bloc.add(Objet(coord_x, coord_y + 26, 30, 4, im.poseur_piege_bas, "pieg"))

    # Fonction qui permet de sauvegarder les modifications apportees au terrain
    def sauvegarder(self):

        # On vide le terrain
        i, j = len(self.contenu) - 1, len(self.contenu[0])
        self.contenu = []
        for i in range(i):
            self.contenu.append(["vide"] * j)

        # On le reremplit
        for groupe in (self.grp_bloc, self.grp_bloc_effet, self.grp_bloc_pieg):
            for bloc in groupe:
                self.contenu[int(bloc.rect.top / 30) + 1][int(bloc.rect.left / 30) + 1] = bloc.numero
        self.contenu.append([str(self.position_vert[0]), str(self.position_vert[1]), str(self.position_rouge[0]),
                             str(self.position_rouge[1]), str(self.position_bleu[0]), str(self.position_bleu[1])])

        # On le met dans le format du fichier texte
        for i in range(len(self.contenu)):
            self.contenu[i] = "'".join(self.contenu[i])
        self.contenu = "\n".join(self.contenu)

        # On le met dans le fichier texte
        fichier_text = open("Terrains/Terrain" + self.numero + ".txt", "w")
        fichier_text.write(self.contenu)
        fichier_text.close()

        # On remet self.contenu dans la bonne forme
        self.ouvrir_terrain()

    def ouvrir_terrain(self):
        fichier_text = open("Terrains/Terrain" + self.numero + ".txt", "r")
        self.contenu = fichier_text.read()
        fichier_text.close()

        self.contenu = self.contenu.split("\n")
        for i in range(len(self.contenu)):
            self.contenu[i] = self.contenu[i].split("'")
        self.position_vert = [int(self.contenu[-1][0]), int(self.contenu[-1][1])]
        self.position_rouge = [int(self.contenu[-1][2]), int(self.contenu[-1][3])]
        self.position_bleu = [int(self.contenu[-1][4]), int(self.contenu[-1][5])]

    # Fonction qui prends un screenshot
    def screenshot(self, name):
        sub = ecran.subsurface(pygame.Rect(0, 0, (len(self.contenu[0]) - 2) * 30, (len(self.contenu) - 3) * 30))
        if name != "screenshots/screenshot":
            pygame.image.save(sub, name + ".png")
        else:
            conteur = 0
            while conteur > -1:
                conteur += 1
                try:
                    a = pygame.image.load(name + str(conteur) + ".png")
                except:
                    pygame.image.save(sub, name + str(conteur) + ".png")
                    conteur = -1


"""
Classe qui cree l'objet terrain
"""


class Missile(pygame.sprite.Sprite):
    def __init__(self, centerx, centery, lanceur):
        pygame.sprite.Sprite.__init__(self)
        self.image = [im.missile.subsurface(index, 0, 24, 24) for index in range(0, 96, 24)]
        self.lanceur = lanceur
        self.rect = pygame.Rect(0, 0, 24, 24)
        self.rect.center = (arrondir(centerx) + 15, arrondir(centery) + 15)
        self.vie = 6
        self.index_img_explosion = 0
        self.degel = 0

        self.x = int(self.rect.centerx / 30)
        self.y = int(self.rect.centery / 30)
        self.dx = self.dy = 0
        self.act_listes = self.anc_listes = self.new_listes = self.chemin = []

        self.search_cible()
        self.index_img = int(self.dx / 2 + 0.5) + 2 if self.dx else int(self.dy / 2 + 0.5)

    def move(self):

        if not self.vie > 0:
            self.index_img_explosion += 1
            if not self.index_img_explosion < 24.5:
                ter.grp_missile.remove(self)
        else:
            if self.degel:
                self.degel -= 1
            else:
                if self.cible.mort or not self.cible:
                    self.search_cible()
                    if not self.cible:
                        self.vie = 0

                if self.vie > 0:
                    if self.besoin_tourner(self.rect.centerx, self.rect.centery):
                        self.recherche_deplacement_vers_cible()

                    self.rect.centerx += self.dx * 5
                    self.rect.centery += self.dy * 5

                    for groupe in (ter.grp_pers, ter.grp_missile):
                        for objet in groupe:
                            if self.rect.colliderect(
                                    objet.rect) and objet != self.lanceur and objet != self and objet.vie > 0:
                                objet.vie -= 15
                                self.vie = 0
                                if groupe == ter.grp_pers:
                                    objet.temps_recharg_anim_degat = 20

                    for bloc in ter.grp_bloc:
                        if self.rect.colliderect(bloc.rect):
                            self.vie = 0

                    self.index_img = int(self.dx / 2 + 0.5) + 2 if self.dx else int(self.dy / 2 + 0.5)

    def recherche_deplacement_vers_cible(self):
        self.x = int(self.rect.centerx / 30)
        self.y = int(self.rect.centery / 30)
        but = (int(self.cible.rect.centerx / 30), int(self.cible.rect.centery / 30))

        self.act_listes = [[(self.x, self.y)]]
        self.anc_listes = []
        self.chemin = []
        self.new_listes = []

        if but == (self.x, self.y):
            self.chemin = [(self.x, self.y), (self.x, self.y)]

        while self.chemin == []:
            for liste1 in self.act_listes:
                deplacements = []
                for i in (1, 0), (0, 1), (-1, 0), (0, -1):
                    if self.deplacement_possible((liste1[-1][0] + i[0], liste1[-1][1] + i[1])):
                        deplacements.append(i)
                deplacements_diagonale = []
                for i in deplacements:
                    for j in deplacements:
                        if math.sqrt((i[0] + j[0]) ** 2) == 1:
                            if self.deplacement_possible((liste1[-1][0] + i[0] + j[0], liste1[-1][1] + i[1] + j[1])):
                                ajout = True
                                for vecteur in deplacements_diagonale:
                                    if (i[0] + j[0], i[1] + j[1]) == vecteur:
                                        ajout = False
                                if ajout: deplacements_diagonale.append((i[0] + j[0], i[1] + j[1]))
                for i in deplacements_diagonale:
                    deplacements.append(i)
                for i in deplacements:
                    point = ((liste1[-1][0] + i[0], liste1[-1][1] + i[1]))
                    temp = []
                    for point2 in liste1:
                        temp.append(point2)
                    temp.append(point)
                    if point == but:
                        self.chemin = temp
                    self.new_listes.append(temp)

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

                # 2 aÃ‚Â  copier

        self.dx = self.chemin[1][0] - self.x
        self.dy = self.chemin[1][1] - self.y

        # 3 aÃ‚Â  copier

    def deplacement_possible(self, point):
        ajout = False
        case = ter.contenu[point[1] + 1][point[0] + 1]
        if case == "vide" or case == "axel" or case == "jump":
            ajout = True
            for listes in self.act_listes, self.anc_listes:
                for liste in listes:
                    if liste[-1] == point:
                        ajout = False
        return ajout

    def search_cible(self):
        list = []
        for pers in ter.grp_pers:
            if pers != self.lanceur and pers.vie > 0:
                self.cible = pers
                self.recherche_deplacement_vers_cible()
                if self.vie:
                    list.append((pers, len(self.chemin)))
        if list:
            if len(list) == 2:
                self.cible = list[0][0] if list[0][1] < list[1][1] else list[1][0]
            else:
                self.cible = list[0][0]
            ter.grp_missile.add(self)
            self.vie = 6

    def besoin_tourner(self, x, y):
        return True if x == int(x / 30) * 30 + 15 and y == int(y / 30) * 30 + 15 else False


"""
Classe qui definit le missiles a tete chercheuse envoyes par les Sprinters
"""


class Bombe(pygame.sprite.Sprite):
    def __init__(self, centre_x, centre_y, lanceur, direction):
        pygame.sprite.Sprite.__init__(self)
        self.coord_lancement = [centre_x, centre_y]
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
            self.rect.centery = self.coord_lancement[1] - (-self.count_traj ** 2 + 80 * self.count_traj) / 60
            self.rect.centerx += self.direction * 8

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
                distance = math.sqrt(
                    (objet.rect.centerx - self.rect.centerx) ** 2 + (objet.rect.centery - self.rect.centery) ** 2)
                if distance < 210 and objet != self.lanceur and objet != self and objet.vie:
                    if groupe == ter.grp_bombe:
                        objet.explosion()
                    objet.vie -= (-distance * 40) / 210 + 40
                    if groupe == ter.grp_pers:
                        objet.temps_recharg_anim_degat = 20


"""
Classe qui definit les bombes envoyees par les Fighters
"""


class Glace(pygame.sprite.Sprite):
    def __init__(self, centerx, centery, lanceur):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(centerx - 192, centery - 192, 384, 384)
        self.index_img = 0
        self.lanceur = lanceur

        for groupe in (ter.grp_pers, ter.grp_attak, ter.grp_missile, ter.grp_bombe):
            for objet in groupe:
                if objet != self.lanceur:
                    distance = math.sqrt(
                        (self.rect.centerx - objet.rect.centerx) ** 2 + (self.rect.centery - objet.rect.centery) ** 2)
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
        self.rect = pygame.Rect(x, y, 30, 48)
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
    def __init__(self, centre_x, centre_y, deplacement_x, deplacement_y, image, lanceur, explosion, couleur):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = pygame.Rect(centre_x - 10, centre_y - 10, 20, 20)
        self.deplacement_x = deplacement_x
        self.deplacement_y = deplacement_y
        self.x, self.y = centre_x, centre_y
        self.lanceur = lanceur
        self.couleur = couleur
        self.explosion = explosion
        self.vie = 1
        self.index_img_explosion = 0

        self.index_img = self.count = 0
        self.degel = 0

        ter.grp_attak.add(self)

    def move(self, test=None):

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
            self.x += self.deplacement_x * 7
            self.y += self.deplacement_y * 7
            self.rect.centerx = self.x
            self.rect.centery = self.y

            for groupe in (ter.grp_attak, ter.grp_missile):
                for objet in groupe:
                    if self.rect.colliderect(
                            objet.rect) and objet != self.lanceur and objet != self and objet.vie > 0 and test == None:
                        self.vie = 0
                        objet.vie -= 3
                        self.rect.left += self.deplacement_x
                        self.rect.top += self.deplacement_y
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


# COPIER LES ATTAQUES ICI

class IA(pygame.sprite.Sprite):
    def __init__(self, position, type, sprinter, fighter, tank, image_attak, image_explosion, faiblesse, couleur):
        pygame.sprite.Sprite.__init__(self)

        self.sprinter = sprinter
        self.fighter = fighter
        self.tank = tank
        self.gros = [pygame.image.load("Images/Perso/Gros/" + couleur + " sprinter.png"),
                     pygame.image.load("Images/Perso/Gros/" + couleur + " fighter.png"),
                     pygame.image.load("Images/Perso/Gros/" + couleur + " tank.png")]

        self.type = type
        if self.type == 0:
            self.image = self.sprinter
            self.rect = pygame.Rect(position[0], position[1], 40, 52)
            self.vitesse = 6
            self.vie = 45
            self.anim_degat = im.anim_degat_sprinter
            self.anim_ralenti = im.anim_ralenti_sprinter
            self.anim_poison = im.anim_poison_sprinter
        elif self.type == 1:
            self.image = self.fighter
            self.rect = pygame.Rect(position[0], position[1], 60, 48)
            self.vitesse = 2.5
            self.vie = 60
            self.tps_recharg_saut = 0
            self.anim_degat = im.anim_degat_fighter
            self.anim_ralenti = im.anim_ralenti_fighter
            self.anim_poison = im.anim_poison_fighter
        elif self.type == 2:
            self.image = self.tank
            self.rect = pygame.Rect(position[0], position[1], 56, 60)
            self.vitesse = 2
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
        self.acceleration = self.effet_gel = 1
        self.force_saut = 0
        self.full_vie = self.vie
        self.tps_recharg_anim_degat = 0
        self.pers_valide = False
        self.fantome = False
        self.effet_rapide = 1
        self.resistance = 0
        self.anim_bouclier = 0
        self.sauter = 0
        self.deplacer = 0
        self.tps_recharg_choix_type = 30
        self.cible = False

        self.index_img = 0
        self.image = dict([(direction, [self.image.subsurface(x, y, self.rect.width, self.rect.height) for x in
                                        range(0, self.rect.width * 4, self.rect.width)]) for direction, y in
                           zip((-1, 1), range(0, self.rect.height * 2, self.rect.height))])
        self.direction = -1
        self.anim_degat = dict([(direction,
                                 [self.anim_degat.subsurface(x, y, self.rect.width, self.rect.height) for x in
                                  range(0, self.rect.width * 4, self.rect.width)]) for direction, y in
                                zip((-1, 1), range(0, self.rect.height * 2, self.rect.height))])
        self.anim_ralenti = dict([(direction,
                                   [self.anim_ralenti.subsurface(x, y, self.rect.width, self.rect.height) for x in
                                    range(0, self.rect.width * 4, self.rect.width)]) for direction, y in
                                  zip((-1, 1), range(0, self.rect.height * 2, self.rect.height))])
        self.anim_poison = dict([(direction,
                                  [self.anim_poison.subsurface(x, y, self.rect.width, self.rect.height) for x in
                                   range(0, self.rect.width * 4, self.rect.width)]) for direction, y in
                                 zip((-1, 1), range(0, self.rect.height * 2, self.rect.height))])

        self.image_attak = [image_attak.subsurface(index, 0, 20, 20) for index in range(0, 80, 20)]
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
        self.dy = self.dx = self.tps_en_air = self.y_max = self.effet_poison = self.force_saut = self.tps_recharg_anim_degat = self.tirer_attak = self.tps_recharg_attak = self.tirer_piege = self.tps_recharg_piege = self.degel = self.sauter = self.deplacer = 0
        self.state = "STANDING"
        self.acceleration = self.effet_gel = self.effet_rapide = 1
        self.direction = -1
        self.mort = self.cible = self.pers_valide = self.indestructible = False
        self.animation = True
        self.tps_recharg_choix_type = 30

    def changer_type(self):
        if self.type == 0:
            self.image = self.sprinter
            self.rect = pygame.Rect(self.rect.left, self.rect.top, 40, 52)
            self.vitesse = 6
            self.vie = 45
            self.anim_degat = im.anim_degat_sprinter
            self.anim_ralenti = im.anim_ralenti_sprinter
            self.anim_poison = im.anim_poison_sprinter
        elif self.type == 1:
            self.image = self.fighter
            self.rect = pygame.Rect(self.rect.left, self.rect.top, 60, 48)
            self.vitesse = 2.5
            self.vie = 60
            self.tps_recharg_saut = 0
            self.anim_degat = im.anim_degat_fighter
            self.anim_ralenti = im.anim_ralenti_fighter
            self.anim_poison = im.anim_poison_fighter
        elif self.type == 2:
            self.image = self.tank
            self.rect = pygame.Rect(self.rect.left, self.rect.top, 56, 60)
            self.vitesse = 2
            self.vie = 100
            self.anim_degat = im.anim_degat_tank
            self.anim_ralenti = im.anim_ralenti_tank
            self.anim_poison = im.anim_poison_tank
        self.full_vie = self.vie
        self.image = dict([(direction, [self.image.subsurface(x, y, self.rect.width, self.rect.height) for x in
                                        range(0, self.rect.width * 4, self.rect.width)]) for direction, y in
                           zip((-1, 1), range(0, self.rect.height * 2, self.rect.height))])
        self.anim_degat = dict([(direction,
                                 [self.anim_degat.subsurface(x, y, self.rect.width, self.rect.height) for x in
                                  range(0, self.rect.width * 4, self.rect.width)]) for direction, y in
                                zip((-1, 1), range(0, self.rect.height * 2, self.rect.height))])
        self.anim_ralenti = dict([(direction,
                                   [self.anim_ralenti.subsurface(x, y, self.rect.width, self.rect.height) for x in
                                    range(0, self.rect.width * 4, self.rect.width)]) for direction, y in
                                  zip((-1, 1), range(0, self.rect.height * 2, self.rect.height))])
        self.anim_poison = dict([(direction,
                                  [self.anim_poison.subsurface(x, y, self.rect.width, self.rect.height) for x in
                                   range(0, self.rect.width * 4, self.rect.width)]) for direction, y in
                                 zip((-1, 1), range(0, self.rect.height * 2, self.rect.height))])
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
                if self.top > len(ter.contenu) * 30:
                    self.animation = False

        elif self.degel:
            self.degel -= 1
        else:

            # Effets blocs
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

            # Rencontre piege
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
                    elif piege.image == im.piege_bleu_bonus:
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
                if self.effet_poison % 100 == 0:
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

                self.IA_choisir_cible()

                # Check deplacement vertical sprinter
                if self.type == 0 and self.state == "STANDING" and self.sauter:
                    self.force_saut = 80

                # Check deplacement vertical fighter
                elif self.type == 1:
                    if self.sauter and self.tps_recharg_saut == 0:
                        self.tps_en_air = 0
                        self.force_saut = 65
                        self.tps_recharg_saut = 40

                    if self.tps_recharg_saut:
                        self.tps_recharg_saut -= 1

                # Check deplacement vertical tank
                elif self.type == 2 and self.sauter:
                    self.force_saut += 3

                # Deplacement vertical
                if self.force_saut or self.state == "JUMPING":
                    self.jump()
                    self.top += self.dy
                    self.rect.top = self.top
                    self.collision(0, self.dy)

                # Deplacement horizontal + Animation
                if self.deplacer:
                    self.dx = self.deplacer * self.vitesse * self.acceleration * self.effet_rapide / int(self.effet_gel)
                    self.left += self.dx
                    self.rect.left = self.left
                    self.direction = self.deplacer

                    temp = self.rect.copy()
                    self.collision(self.dx, 0)
                    if self.rect.contains(temp):
                        self.index_img += 0.5 / (self.effet_gel * 2)
                        if not self.index_img < 4:
                            self.index_img = 0
                    else:
                        self.index_img = 0

                else:
                    self.index_img = 0
            else:
                self.index_img = 0

            # Lancement attaque
            self.IA_tirer_attak()

            # Lancement attaque speciale
            if False:  # Â§Â§Â§Â§Â§Â§Â§ A CHANGER Â§Â§Â§Â§Â§Â§Â§
                if self.type == 0:
                    if self.tps_recharg_attak_spe == 0:
                        Missile(self.rect.centerx, self.rect.centery, self)
                        self.tps_recharg_attak_spe = 14  # 250
                if self.type == 2:
                    if self.tps_recharg_attak_spe == 0:
                        Glace(self.rect.centerx, self.rect.centery, self)
                        self.tps_recharg_attak_spe = 450

            # Changement etat special
            if self.type == 1:
                if False:
                    self.fantome = True
                else:
                    self.fantome = False
                if False:  # Â§Â§Â§Â§Â§Â§Â§ A CHANGER Â§Â§Â§Â§Â§Â§Â§
                    if self.tps_recharg_attak_spe == 0:
                        Bombe(self.rect.centerx, self.rect.centery, self, self.direction)
                        self.tps_recharg_attak_spe = 300

            if self.tps_recharg_attak_spe != 0:
                self.tps_recharg_attak_spe -= 1

            # Detection etat
            self.statement()

            if self.state == "STANDING" and self.dy > 0:  # Si on vient de tomber, pas si on monte sur un bloc en montant
                self.dy = self.tps_en_air = self.force_saut = self.y_max = 0

            if self.tps_recharg_anim_degat:
                self.tps_recharg_anim_degat -= 1

        if self.indestructible != False:
            if self.vie != self.indestructible and self.resistance:
                self.anim_bouclier = 7
            self.vie = self.indestructible

    def IA_sauter_sprinter(self):
        if self.state == "STANDING":
            None

    def collision(self, dx, dy):
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
                            self.bloquage(dx, dy, bloc)
                    else:
                        self.bloquage(dx, dy, bloc)
                else:
                    self.bloquage(dx, dy, bloc)

    def test_collision(self):

        for bloc in ter.grp_bloc:
            if self.rect.colliderect(bloc.rect):
                if not (self.fantome and bloc.numero == "grnd"):
                    return True;
                    break

    def bloquage(self, dx, dy, mur):
        if dx > 0:
            self.rect.right = mur.rect.left
            self.left = self.rect.left
        elif dx < 0:
            self.rect.left = mur.rect.right
            self.left = self.rect.left
        if dy > 0:
            if mur.numero == "slim" and self.state == "JUMPING":
                self.force_saut = dy * 7 - 8
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
        self.dy = -10 * self.tps_en_air ** 2 + self.tps_en_air * self.force_saut
        self.tps_en_air += 0.125
        self.dy -= -10 * self.tps_en_air ** 2 + self.tps_en_air * self.force_saut

        # Creation variable pour calculer la hauteur du saut
        if self.dy > 0 and not self.y_max:
            self.y_max = self.rect.bottom

    def statement(self):
        self.state = "JUMPING"
        list = []
        temp = self.rect.copy()
        temp.top += 1
        for bloc in ter.grp_bloc:
            if temp.colliderect(bloc.rect) and not (bloc.numero == "slim" and self.dy > 1 and self.sauter) and not (
                self.fantome and bloc.numero != "grnd"):
                self.state = "STANDING"

    def IA_choisir_cible(self):
        list1 = []
        # list2 = []
        for pers in ter.grp_pers:
            if pers != self and pers.vie > 0:
                list1.append(pers.rect.center)
                # list2.append(pers.type)
        if len(list1) == 0:
            self.cible = False
        elif len(list1) == 1:
            self.cible = list1[0]
        else:
            self.cible = list1[0] if math.sqrt(
                (list1[0][0] - self.rect.centerx) ** 2 + (list1[0][1] - self.rect.centery) ** 2) < math.sqrt(
                (list1[1][0] - self.rect.centerx) ** 2 + (list1[1][1] - self.rect.centery) ** 2) else list1[1]

    def IA_tirer_attak(self):
        if self.tps_recharg_attak:
            self.tps_recharg_attak -= 1
        else:
            for pers in ter.grp_pers:
                if pers != self and pers.mort == False and self.tps_recharg_attak == 0:

                    dis_x = pers.rect.centerx - self.rect.centerx
                    dis_y = pers.rect.centery - self.rect.centery
                    hyp = math.sqrt(dis_x ** 2 + dis_y ** 2)
                    dx = dis_x / hyp
                    dy = dis_y / hyp

                    case_arrivee = (int(pers.rect.centerx / 30), int(pers.rect.centery / 30))

                    x, y = self.rect.center
                    while True:
                        x += dx
                        y += dy
                        if ter.contenu[int(y / 30) + 1][int(x / 30) + 1] != "vide":
                            tir = False
                            break
                        elif (int(x / 30), int(y / 30)) == case_arrivee:
                            tir = True
                            break
                    if tir:
                        dis_x += random.randint(-15, 15)
                        dis_y += random.randint(-15, 15)
                        hyp = math.sqrt(dis_x ** 2 + dis_y ** 2)
                        dx = dis_x / hyp
                        dy = dis_y / hyp
                        Attak(self.rect.centerx, self.rect.centery, dx, dy, self.image_attak, self,
                              self.image_explosion, self.couleur)
                        self.tps_recharg_attak = 30


"""
Classe qui definit les ia
"""


class Personnage(pygame.sprite.Sprite):
    def __init__(self, position, type, sprinter, fighter, tank, image_attak, image_explosion, numero_manette, faiblesse,
                 couleur):
        pygame.sprite.Sprite.__init__(self)

        self.sprinter = sprinter
        self.fighter = fighter
        self.tank = tank
        self.gros = [pygame.image.load("Images/Perso/Gros/" + couleur + " sprinter.png"),
                     pygame.image.load("Images/Perso/Gros/" + couleur + " fighter.png"),
                     pygame.image.load("Images/Perso/Gros/" + couleur + " tank.png")]

        self.type = type
        if self.type == 0:
            self.image = self.sprinter
            self.rect = pygame.Rect(position[0], position[1], 40, 52)
            self.vitesse = 6
            self.vie = 45
            self.anim_degat = im.anim_degat_sprinter
            self.anim_ralenti = im.anim_ralenti_sprinter
            self.anim_poison = im.anim_poison_sprinter
        elif self.type == 1:
            self.image = self.fighter
            self.rect = pygame.Rect(position[0], position[1], 60, 48)
            self.vitesse = 2.5
            self.vie = 60
            self.tps_recharg_saut = 0
            self.anim_degat = im.anim_degat_fighter
            self.anim_ralenti = im.anim_ralenti_fighter
            self.anim_poison = im.anim_poison_fighter
        elif self.type == 2:
            self.image = self.tank
            self.rect = pygame.Rect(position[0], position[1], 56, 60)
            self.vitesse = 2
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
        self.image = dict([(direction, [self.image.subsurface(x, y, self.rect.width, self.rect.height) for x in
                                        range(0, self.rect.width * 4, self.rect.width)]) for direction, y in
                           zip((-1, 1), range(0, self.rect.height * 2, self.rect.height))])
        self.direction = -1
        self.anim_degat = dict([(direction,
                                 [self.anim_degat.subsurface(x, y, self.rect.width, self.rect.height) for x in
                                  range(0, self.rect.width * 4, self.rect.width)]) for direction, y in
                                zip((-1, 1), range(0, self.rect.height * 2, self.rect.height))])
        self.anim_ralenti = dict([(direction,
                                   [self.anim_ralenti.subsurface(x, y, self.rect.width, self.rect.height) for x in
                                    range(0, self.rect.width * 4, self.rect.width)]) for direction, y in
                                  zip((-1, 1), range(0, self.rect.height * 2, self.rect.height))])
        self.anim_poison = dict([(direction,
                                  [self.anim_poison.subsurface(x, y, self.rect.width, self.rect.height) for x in
                                   range(0, self.rect.width * 4, self.rect.width)]) for direction, y in
                                 zip((-1, 1), range(0, self.rect.height * 2, self.rect.height))])

        self.image_attak = [image_attak.subsurface(index, 0, 20, 20) for index in range(0, 80, 20)]
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
            self.rect = pygame.Rect(self.rect.left, self.rect.top, 40, 52)
            self.vitesse = 6
            self.vie = 45
            self.anim_degat = im.anim_degat_sprinter
            self.anim_ralenti = im.anim_ralenti_sprinter
            self.anim_poison = im.anim_poison_sprinter
        elif self.type == 1:
            self.image = self.fighter
            self.rect = pygame.Rect(self.rect.left, self.rect.top, 60, 48)
            self.vitesse = 2.5
            self.vie = 60
            self.tps_recharg_saut = 0
            self.anim_degat = im.anim_degat_fighter
            self.anim_ralenti = im.anim_ralenti_fighter
            self.anim_poison = im.anim_poison_fighter
        elif self.type == 2:
            self.image = self.tank
            self.rect = pygame.Rect(self.rect.left, self.rect.top, 56, 60)
            self.vitesse = 2
            self.vie = 100
            self.anim_degat = im.anim_degat_tank
            self.anim_ralenti = im.anim_ralenti_tank
            self.anim_poison = im.anim_poison_tank
        self.full_vie = self.vie
        self.image = dict([(direction, [self.image.subsurface(x, y, self.rect.width, self.rect.height) for x in
                                        range(0, self.rect.width * 4, self.rect.width)]) for direction, y in
                           zip((-1, 1), range(0, self.rect.height * 2, self.rect.height))])
        self.anim_degat = dict([(direction,
                                 [self.anim_degat.subsurface(x, y, self.rect.width, self.rect.height) for x in
                                  range(0, self.rect.width * 4, self.rect.width)]) for direction, y in
                                zip((-1, 1), range(0, self.rect.height * 2, self.rect.height))])
        self.anim_ralenti = dict([(direction,
                                   [self.anim_ralenti.subsurface(x, y, self.rect.width, self.rect.height) for x in
                                    range(0, self.rect.width * 4, self.rect.width)]) for direction, y in
                                  zip((-1, 1), range(0, self.rect.height * 2, self.rect.height))])
        self.anim_poison = dict([(direction,
                                  [self.anim_poison.subsurface(x, y, self.rect.width, self.rect.height) for x in
                                   range(0, self.rect.width * 4, self.rect.width)]) for direction, y in
                                 zip((-1, 1), range(0, self.rect.height * 2, self.rect.height))])
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
                if self.top > len(ter.contenu) * 30:
                    self.animation = False

        elif self.degel:
            self.degel -= 1
        else:

            # Effets blocs
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

            # Rencontre piege
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
                    elif piege.image == im.piege_bleu_bonus:
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
                if self.effet_poison % 100 == 0:
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

                # Check deplacement vertical sprinter
                if self.type == 0:
                    if self.state == "STANDING" and self.joystick.get_axis(3) < -0.4:
                        self.force_saut = 80

                # Check deplacement vertical fighter
                elif self.type == 1:
                    if self.joystick.get_axis(3) < -0.4 and self.tps_recharg_saut == 0:
                        self.tps_en_air = 0
                        self.force_saut = 65
                        self.tps_recharg_saut = 40

                    if self.tps_recharg_saut:
                        self.tps_recharg_saut -= 1

                # Check deplacement vertical tank
                if self.type == 2:
                    if self.joystick.get_axis(3) < -0.4:
                        self.force_saut += 3

                # Deplacement vertical
                if self.force_saut or self.state == "JUMPING":
                    self.jump()
                    self.top += self.dy
                    self.rect.top = self.top
                    self.collision(0, self.dy)

                # Deplacement horizontal + Animation
                if round(self.joystick.get_axis(2)):
                    self.dx = round(
                        self.joystick.get_axis(2)) * self.vitesse * self.acceleration * self.effet_rapide / int(
                        self.effet_gel)
                    self.left += self.dx
                    self.rect.left = self.left
                    self.direction = round(self.joystick.get_axis(2))

                    temp = self.rect.copy()
                    self.collision(self.dx, 0)
                    if self.rect.contains(temp):
                        self.index_img += 0.5 / (self.effet_gel * 2)
                        if not self.index_img < 4:
                            self.index_img = 0
                    else:
                        self.index_img = 0

                else:
                    self.index_img = 0
            else:
                self.index_img = 0

            # Lancement attaque
            if self.tps_recharg_attak == 0 and math.sqrt(
                                    self.joystick.get_axis(0) ** 2 + self.joystick.get_axis(1) ** 2) > 0.5:
                Attak(self.rect.centerx, self.rect.centery, self.joystick.get_axis(0), self.joystick.get_axis(1),
                      self.image_attak, self, self.image_explosion, self.couleur)
                self.tps_recharg_attak = 30
            elif self.tps_recharg_attak != 0:
                self.tps_recharg_attak -= 1

            # Lancement attaque speciale
            if self.joystick.get_button(4):
                if self.type == 0:
                    if self.tps_recharg_attak_spe == 0:
                        Missile(self.rect.centerx, self.rect.centery, self)
                        self.tps_recharg_attak_spe = 14  # 250
                if self.type == 2:
                    if self.tps_recharg_attak_spe == 0:
                        Glace(self.rect.centerx, self.rect.centery, self)
                        self.tps_recharg_attak_spe = 450

            # Changement etat special
            if self.type == 1:
                if self.joystick.get_button(5):
                    self.fantome = True
                else:
                    self.fantome = False
                if self.joystick.get_button(4):
                    if self.tps_recharg_attak_spe == 0:
                        Bombe(self.rect.centerx, self.rect.centery, self, self.direction)
                        self.tps_recharg_attak_spe = 300

            if self.tps_recharg_attak_spe != 0:
                self.tps_recharg_attak_spe -= 1

            # Detection etat
            self.statement()

            if self.state == "STANDING" and self.dy > 0:  # Si on vient de tomber, pas si on monte sur un bloc en montant
                self.dy = self.tps_en_air = self.force_saut = self.y_max = 0

            if self.tps_recharg_anim_degat:
                self.tps_recharg_anim_degat -= 1

        if self.indestructible != False:
            if self.vie != self.indestructible and self.resistance:
                self.anim_bouclier = 7
            self.vie = self.indestructible

    def collision(self, dx, dy):
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
                            self.bloquage(dx, dy, bloc)
                    else:
                        self.bloquage(dx, dy, bloc)
                else:
                    self.bloquage(dx, dy, bloc)

    def test_collision(self):

        for bloc in ter.grp_bloc:
            if self.rect.colliderect(bloc.rect):
                if not (self.fantome and bloc.numero == "grnd"):
                    return True;
                    break

    def bloquage(self, dx, dy, mur):
        if dx > 0:
            self.rect.right = mur.rect.left
            self.left = self.rect.left
        elif dx < 0:
            self.rect.left = mur.rect.right
            self.left = self.rect.left
        if dy > 0:
            if mur.numero == "slim" and self.state == "JUMPING":
                self.force_saut = dy * 7 - 8
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
        self.dy = -10 * self.tps_en_air ** 2 + self.tps_en_air * self.force_saut
        self.tps_en_air += 0.125
        self.dy -= -10 * self.tps_en_air ** 2 + self.tps_en_air * self.force_saut

        # Creation variable pour calculer la hauteur du saut
        if self.dy > 0 and not self.y_max:
            self.y_max = self.rect.bottom

    def statement(self):
        self.state = "JUMPING"
        list = []
        temp = self.rect.copy()
        temp.top += 1
        for bloc in ter.grp_bloc:
            if temp.colliderect(bloc.rect) and not (
                        bloc.numero == "slim" and self.dy > 1 and self.joystick.get_axis(3) > -0.4) and not (
                self.fantome and bloc.numero != "grnd"):
                self.state = "STANDING"


"""
Classe qui definit les personnages
"""


class Menu():
    def __init__(self):
        Bouton(30 * 22 + 45, 30, 120, 30, im.cadre_bouton, "MODIFIER", ter.grp_btn_menu)
        Bouton(30 * 27 + 45, 30, 120, 30, im.cadre_bouton, "JOUER", ter.grp_btn_menu)

    def utiliser(self):
        bouton_select = "JOUER"

        while fen.open_menu:

            # robot = Personnage((0,0), type.vert, im.vert_sprinter, im.vert_fighter, im.vert_tank, im.attak_vert, im.explosion_vert,0, "rouge", "bleu")
            groupe_lignes = [((836, 34), (919, 34)), ((821, 49), (835, 49)), ((71, 64), (259, 64)),
                             ((806, 64), (820, 64)), ((791, 79), (805, 79)), ((566, 94), (619, 94)),
                             ((776, 94), (790, 94)), ((551, 109), (565, 109)), ((761, 109), (775, 109)),
                             ((386, 124), (529, 124)), ((620, 124), (760, 124)), ((371, 139), (385, 139)),
                             ((356, 154), (370, 154)), ((341, 169), (355, 169)), ((326, 184), (340, 184)),
                             ((311, 199), (325, 199)), ((296, 214), (310, 214)), ((251, 229), (295, 229)),
                             ((566, 304), (724, 304)), ((161, 319), (460, 319)), ((551, 319), (565, 319)),
                             ((725, 319), (739, 319)), ((740, 334), (754, 334)), ((755, 349), (769, 349)),
                             ((26, 394), (94, 394)), ((866, 394), (940, 394)), ((95, 409), (109, 409)),
                             ((851, 409), (865, 409)), ((110, 424), (220, 424)), ((290, 424), (850, 424))]

            for event in pygame.event.get():
                if event.type == QUIT:
                    fen.open_menu = False
                    fen.open_window = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    clic = pygame.Rect(arrondir(event.pos[0]), arrondir(event.pos[1]), 30, 30)
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
            except:
                None

            ecran.blit(im.fond_ground, (0, 0))
            ter.grp_btn_menu.draw(ecran)
            for bouton in ter.grp_btn_menu:
                if bouton.numero == bouton_select:
                    ecran.blit(im.cadre_bouton_select, bouton.rect.topleft)
                ecran.blit(police30.render(bouton.numero, 1, (0, 0, 0)), (bouton.rect.left + 12, bouton.rect.top + 12))
            pygame.display.flip()
            horloge.tick(fps)

    def changer(self, fenetre):
        if fenetre == "MODIFIER":
            fen.open_menu = False
            fen.open_maping = True
        elif fenetre == "JOUER":
            fen.open_menu = False
            fen.open_choose = True


# Fonction qui gere la fen Play
class Play():
    def __init__(self):
        Bouton(30 * 27 + 45, (len(ter.contenu) - 5) * 30 + 15, 120, 30, im.cadre_bouton, "QUITTER", ter.grp_btn_play)
        Bouton(320, 365, 120, 30, im.cadre_bouton, "REJOUER", ter.grp_btn_resultats)
        Bouton(467, 365, 120, 30, im.cadre_bouton, "MENU ", ter.grp_btn_resultats)
        Bouton(614, 365, 120, 30, im.cadre_bouton, "OPTIONS", ter.grp_btn_resultats)
        Bouton(320, 365, 120, 30, im.cadre_bouton, "ANNULER", ter.grp_btn_fen_quit)
        Bouton(467, 365, 120, 30, im.cadre_bouton, "MENU ", ter.grp_btn_fen_quit)
        Bouton(614, 365, 120, 30, im.cadre_bouton, "OPTIONS", ter.grp_btn_fen_quit)
        self.tps_recharg_chang_btn = 0
        self.count_anim_bloc_effet = 0
        self.btn_fin_select = "REJOUER"
        self.btn_pause_select = "ANNULER"
        self.open_fen_quit = False
        self.pause = False

    def utiliser(self):
        while fen.open_play:

            # Gerance des boutons
            for event in pygame.event.get():
                if event.type == QUIT:
                    fen.open_play = False
                    fen.open_window = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    clic = pygame.Rect(arrondir(event.pos[0]), arrondir(event.pos[1]), 30, 30)
                    for bouton in ter.grp_btn_play:
                        if clic.colliderect(bouton):
                            if bouton.numero == "QUITTER":
                                self.open_fen_quit = self.pause = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == K_SPACE:
                        ter.screenshot("screenshots/screenshot")
            try:
                if vert.joystick.get_button(2):
                    self.open_fen_quit = self.pause = True
            except:
                None

            # Placement de pieges
            self.creation_piege()  # Â§Â§Â§Â§Â§Â§Â§Â§Â§Â§Â§Â§Â§Â§Â§Â§Â§Â§Â§Â§

            # Deplacements
            if self.pause == False:
                for groupe in (ter.grp_attak, ter.grp_bombe, ter.grp_missile, ter.grp_pers):
                    for objet in groupe:
                        objet.move()
                if self.count_anim_bloc_effet < 8.9:
                    self.count_anim_bloc_effet += 0.2
                else:
                    self.count_anim_bloc_effet = 0

            # Affichage
            ecran.blit(im.fond, (0, 0))
            ter.grp_bloc.draw(ecran)
            ter.grp_bloc_pieg.draw(ecran)

            for bloc in ter.grp_bloc_effet:
                ecran.blit(bloc.image.subsurface(int(self.count_anim_bloc_effet) * 30, 0, 30, 30),
                           (bloc.rect.left, bloc.rect.top))

            for piege in ter.grp_piege:
                if piege.vie <= 0:
                    piege.index_img += 0.3
                    if piege.index_img > 4.7:
                        ter.grp_piege.remove(piege)
                ecran.blit(piege.image.subsurface(48 * int(piege.index_img), 0, 48, 48),
                           (piege.rect.left - 9, piege.rect.top))

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
                    couleur = (
                    55 + 200 * abs(pers.vie / pers.full_vie - 1), 255 - 200 * abs(pers.vie / pers.full_vie - 1), 50)
                    pygame.draw.rect(ecran, couleur, (
                    pers.rect.left, pers.rect.top - 10, pers.rect.width * pers.vie / pers.full_vie, 5))
                if pers.anim_bouclier:
                    ecran.blit(im.bouclier[pers.anim_bouclier], (pers.rect.left, pers.rect.top))

            for attak in ter.grp_attak:
                if attak.vie > 0:
                    ecran.blit(attak.image[attak.index_img], attak.rect.topleft)
                    if attak.degel > 0:
                        ecran.blit(im.glacon_attak, (attak.rect.centerx - 16, attak.rect.centery - 16))
                else:
                    ecran.blit(attak.explosion.subsurface(int(attak.index_img_explosion) * 37, 0, 37, 37),
                               (attak.rect.centerx - 37 / 2, attak.rect.centery - 37 / 2))

            for missile in ter.grp_missile:
                if missile.vie > 0:
                    ecran.blit(missile.image[missile.index_img], missile.rect.topleft)
                    if missile.degel > 0:
                        ecran.blit(im.glacon_attak, (missile.rect.centerx - 16, missile.rect.centery - 16))
                else:
                    ecran.blit(im.explosion_missile.subsurface(int(missile.index_img_explosion) * 64, 0, 64, 64),
                               (missile.rect.centerx - 32, missile.rect.centery - 32))

            for bombe in ter.grp_bombe:
                if bombe.vie > 0:
                    ecran.blit(bombe.image, bombe.rect.topleft)
                    if bombe.degel > 0:
                        ecran.blit(im.glacon_attak, (bombe.rect.centerx - 16, bombe.rect.centery - 16))
                else:
                    ecran.blit(im.explosion_bombe.subsurface(int(bombe.index_img_explosion) * 256, 0, 256, 256),
                               ((bombe.rect.centerx - 128, bombe.rect.centery - 128)))

            for glace in ter.grp_glace:
                glace.index_img += 0.3 if 5 < glace.index_img < 10 else 0.2
                ter.grp_glace.remove(glace) if not glace.index_img < 19 else ecran.blit(
                    im.explosion_glace.subsurface(int(glace.index_img) * 384, 0, 384, 384), glace.rect.topleft)

            ter.grp_btn_play.draw(ecran)
            for bouton in ter.grp_btn_play:
                ecran.blit(police30.render(bouton.numero, 1, (0, 0, 0)), (bouton.rect.left + 12, bouton.rect.top + 12))

            if ter.nb_survivants == 1:
                for pers in ter.grp_pers:
                    if not pers.mort:
                        pers.indestructible = pers.vie
                        self.resultats(pers.gros[pers.type])

            if self.open_fen_quit:
                self.fen_quit()

            pygame.display.flip()

            horloge.tick(fps)

    # Fonction qui initialise les personnages en fonction du nombre de joysticks
    def start(self):
        global vert, rouge, bleu
        for groupe in (ter.grp_pers, ter.grp_attak, ter.grp_missile, ter.grp_bombe, ter.grp_piege):
            for objet in groupe:
                groupe.remove(objet)

        if fen.nb_joysticks > 0:
            print(fen.nb_joysticks)
            vert = Personnage(ter.position_vert, type.vert, im.vert_sprinter, im.vert_fighter, im.vert_tank,
                              im.attak_vert, im.explosion_vert, 0, "rouge", "vert")
        else:
            vert = IA(ter.position_vert, type.vert, im.vert_sprinter, im.vert_fighter, im.vert_tank, im.attak_vert,
                      im.explosion_vert, "rouge", "vert")
        if fen.nb_joysticks > 1:
            rouge = Personnage(ter.position_rouge, type.rouge, im.rouge_sprinter, im.rouge_fighter, im.rouge_tank,
                               im.attak_rouge, im.explosion_rouge, 0, "bleu", "rouge")
        else:
            rouge = IA(ter.position_rouge, type.rouge, im.rouge_sprinter, im.rouge_fighter, im.rouge_tank,
                       im.attak_rouge, im.explosion_rouge, "bleu", "rouge")
        if fen.nb_joysticks > 2:
            bleu = Personnage(ter.position_bleu, type.bleu, im.bleu_sprinter, im.bleu_fighter, im.bleu_tank,
                              im.attak_bleu, im.explosion_bleu, 0, "vert", "bleu")
        else:
            bleu = IA(ter.position_bleu, type.bleu, im.bleu_sprinter, im.bleu_fighter, im.bleu_tank, im.attak_bleu,
                      im.explosion_bleu, "vert", "bleu")
        ter.grp_pers.add(vert)
        ter.grp_pers.add(rouge)
        ter.grp_pers.add(bleu)

    # Fonction qui ouvre une fenetre a la fin d'une partie pour dire qui a gagne
    def resultats(self, gagnant):

        ecran.blit(im.cadre_resultats, (250, 100))
        ter.grp_btn_resultats.draw(ecran)
        for btn in ter.grp_btn_resultats:
            if btn.numero == self.btn_fin_select:
                ecran.blit(im.cadre_bouton_select, btn.rect.topleft)
            ecran.blit(police30.render(btn.numero, 1, (0, 0, 0)), (btn.rect.left + 12, btn.rect.top + 12))
        ecran.blit(gagnant, (300, 150))
        ecran.blit(police50.render("WINNER !", 1, (0, 0, 0)), (470, 120))

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
            else:
                self.tps_recharg_chang_btn -= 1
            if vert.joystick.get_button(0):
                self.changer(self.btn_fin_select)
        except:
            None
        for event in pygame.event.get():
            if event.type == QUIT:
                fen.open_play = False
                fen.open_window = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clic = pygame.Rect(arrondir(event.pos[0]), arrondir(event.pos[1]), 30, 30)
                for btn in ter.grp_btn_resultats:
                    if clic.colliderect(btn.rect):
                        self.tps_recharg_chang_btn = 0
                        self.changer(btn.numero)

    def fen_quit(self):
        ecran.blit(im.cadre_resultats, (250, 100))
        ecran.blit(police50.render("ATTENTION", 1, (0, 0, 0)), (370, 120))
        ecran.blit(police30.render("Vous etes sur le point de quitter la partie", 1, (0, 0, 0)), (270, 180))
        ecran.blit(police30.render("en cours. Etes-vous sur de continuer ?", 1, (0, 0, 0)), (270, 205))
        ter.grp_btn_fen_quit.draw(ecran)
        for btn in ter.grp_btn_fen_quit:
            if btn.numero == self.btn_pause_select:
                ecran.blit(im.cadre_bouton_select, btn.rect.topleft)
            ecran.blit(police30.render(btn.numero, 1, (0, 0, 0)), (btn.rect.left + 12, btn.rect.top + 12))

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
            else:
                self.tps_recharg_chang_btn -= 1
            if vert.joystick.get_button(0):
                self.changer(self.btn_pause_select)
        except:
            None
        for event in pygame.event.get():
            if event.type == QUIT:
                fen.open_play = False
                fen.open_window = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clic = pygame.Rect(arrondir(event.pos[0]), arrondir(event.pos[1]), 30, 30)
                for btn in ter.grp_btn_fen_quit:
                    if clic.colliderect(btn.rect):
                        self.changer(btn.numero)

    def changer(self, fenetre):
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
            if random.randrange(0, 1000) == 0:
                Piege(poseur.rect.left, poseur.rect.top - 48, random.choice((im.piege_vert_bonus, im.piege_vert_malus,
                                                                             im.piege_rouge_bonus, im.piege_rouge_malus,
                                                                             im.piege_bleu_bonus, im.piege_bleu_malus)))


# Fonction qui gere la fen open_maping
class Maping():
    def __init__(self):
        Bouton(30 * 27 + 45, (len(ter.contenu) - 5) * 30 + 15, 120, 30, im.cadre_bouton, "MENU ", ter.grp_btn_maping)
        Bouton(30 * 1, (len(ter.contenu) - 5) * 30, 30, 30, im.bloc, "bloc", ter.grp_btn_bloc)
        Bouton(30 * 3, (len(ter.contenu) - 5) * 30, 15, 15, im.stair_right, "escR", ter.grp_btn_bloc)
        Bouton(30 * 3, (len(ter.contenu) - 5) * 30 + 15, 30, 15, im.slab_down, "escR", ter.grp_btn_bloc)
        Bouton(30 * 5 + 15, (len(ter.contenu) - 5) * 30, 15, 15, im.stair_left, "escL", ter.grp_btn_bloc)
        Bouton(30 * 5, (len(ter.contenu) - 5) * 30 + 15, 30, 15, im.slab_down, "escL", ter.grp_btn_bloc)
        Bouton(30 * 7, (len(ter.contenu) - 5) * 30 + 15, 30, 15, im.slab_down, "dalD", ter.grp_btn_bloc)
        Bouton(30 * 9, (len(ter.contenu) - 5) * 30, 30, 15, im.slab_up, "dalU", ter.grp_btn_bloc)
        Bouton(30 * 11, (len(ter.contenu) - 5) * 30, 30, 30, im.trampo, "slim", ter.grp_btn_bloc)
        Bouton(30 * 13, (len(ter.contenu) - 5) * 30, 30, 30, im.jumper.subsurface(pygame.Rect(0, 0, 30, 30)), "jump",
               ter.grp_btn_bloc)
        Bouton(30 * 15, (len(ter.contenu) - 5) * 30, 30, 30, im.accelerator.subsurface(pygame.Rect(0, 0, 30, 30)),
               "axel", ter.grp_btn_bloc)
        Bouton(30 * 17, (len(ter.contenu) - 5) * 30 + 22, 30, 30, im.poseur_piege, "pieg", ter.grp_btn_bloc)

    def utiliser(self):

        image = im.bloc
        numero = "bloc"
        bloc_choisi = pygame.Rect(25, (len(ter.contenu) - 1) * 30 - 125, 40, 40)
        operation = None

        while fen.open_maping:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    fen.open_maping = False
                    fen.open_window = False
                    ter.screenshot("Terrains/Terrain" + ter.numero)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    clic = pygame.Rect(arrondir(event.pos[0]), arrondir(event.pos[1]), 30, 30)
                    if 0 < event.pos[0] < (len(ter.contenu[0]) - 2) * 30 and 0 < event.pos[1] < (
                        len(ter.contenu) - 6) * 30:
                        operation = "ajout" if ter.contenu[int(event.pos[1] / 30) + 1][
                                                   int(event.pos[0] / 30) + 1] == "vide" else "retrait"
                        if operation == "retrait":
                            for grp in ter.grp_bloc, ter.grp_bloc_effet, ter.grp_bloc_pieg:
                                for bloc in grp:
                                    if bloc.rect.colliderect(clic):
                                        grp.remove(bloc)
                        if operation == "ajout" and ter.contenu[int(event.pos[1] / 30) + 1][
                                    int(event.pos[0] / 30) + 1] == "vide":
                            ter.ajout(numero, arrondir(event.pos[0]), arrondir(event.pos[1]))
                        ter.sauvegarder()
                    else:
                        for bouton in ter.grp_btn_bloc:
                            if bouton.rect.colliderect(clic):
                                image = bouton.image
                                numero = bouton.numero
                                bloc_choisi.left = clic.left - 5
                        for bouton in ter.grp_btn_maping:
                            if bouton.rect.colliderect(clic):
                                ter.screenshot("Terrains/Terrain" + ter.numero)
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
                        if operation == "ajout" and ter.contenu[int(event.pos[1] / 30) + 1][
                                    int(event.pos[0] / 30) + 1] == "vide":
                            ter.ajout(numero, arrondir(event.pos[0]), arrondir(event.pos[1]))
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
                        ter.screenshot("screenshots/screenshot")
                    elif event.key == K_RETURN:
                        ter.screenshot("Terrains/Terrain" + ter.numero)
                        fen.open_maping = False
                        fen.open_play = True
                try:
                    if vert.joystick.get_button(0):
                        fen.open_maping = False
                        fen.open_menu = True
                except:
                    None

                ecran.blit(im.fond, (0, 0))
                ter.grp_bloc.draw(ecran)
                ter.grp_bloc_pieg.draw(ecran)
                for bloc in ter.grp_bloc_effet:
                    ecran.blit(bloc.image.subsurface(0, 0, 30, 30), (bloc.rect.left, bloc.rect.top))
                ecran.blit(im.cadre_bloc, bloc_choisi.topleft)
                ter.grp_btn_bloc.draw(ecran)
                ter.grp_btn_maping.draw(ecran)
                for bouton in ter.grp_btn_maping:
                    ecran.blit(police30.render(bouton.numero, 1, (0, 0, 0)),
                               (bouton.rect.left + 12, bouton.rect.top + 12))
                try:
                    clic = pygame.Rect(arrondir(event.pos[0]), arrondir(event.pos[1]), 30, 30)
                    for bouton in ter.grp_btn_bloc:
                        if clic.colliderect(bouton.rect):
                            ecran.blit(im.bloc_vise, (arrondir(event.pos[0]), arrondir(event.pos[1])))
                    if event.pos[1] < (len(ter.contenu) - 6) * 30:
                        ecran.blit(im.bloc_vise, (arrondir(event.pos[0]), arrondir(event.pos[1])))
                except AttributeError:
                    None
                pygame.display.flip()

            horloge.tick(fps)


# Fonction qui gere la fen open_choose_type
class Choose():
    def __init__(self):
        Bouton(30 * 22 + 45, 30, 120, 30, im.cadre_bouton, "MENU ", ter.grp_btn_choose)
        Bouton(30 * 27 + 45, 30, 120, 30, im.cadre_bouton, "JOUER", ter.grp_btn_choose)

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
                    else:
                        i.tps_recharg_changement_type -= 1
                    if i.joystick.get_button(8):
                        i.pers_valide = True

                except AttributeError:
                    if i.tps_recharg_choix_type:
                        i.tps_recharg_choix_type -= 1
                    elif random.randint(0, 10) == 10:
                        i.pers_valide = True
                    if not i.pers_valide:
                        i.type += 1
                        if i.type > 2:
                            i.type = 0
                        i.changer_type()

            ecran.blit(im.fond_ground, (0, 0))
            ter.grp_btn_choose.draw(ecran)
            for bouton in ter.grp_btn_choose:
                ecran.blit(police30.render(bouton.numero, 1, (0, 0, 0)), (bouton.rect.left + 12, bouton.rect.top + 12))

            i = 0
            for pers in vert, rouge, bleu:
                ecran.blit(im.cadre_pers, (80 + i, 100))
                ecran.blit(pers.gros[pers.type], (160 - pers.rect.width + i, 180 - pers.rect.height))
                if pers.pers_valide:
                    ecran.blit(im.validation, (180 + i, 210))
                ecran.blit(im.cadre_stat, (135 + i, 278))
                ecran.blit(im.cadre_stat, (135 + i, 318))
                ecran.blit(im.coeur, (95 + i, 280))
                ecran.blit(im.eclair, (95 + i, 320))
                pygame.draw.rect(ecran, (255, 255, 0), (137 + i, 280, 81 * pers.vie / 100, 30))
                pygame.draw.rect(ecran, (255, 255, 0), (137 + i, 320, 81 * pers.vitesse / 6, 30))
                if pers.type == 0:
                    ecran.blit(im.gros_missiile, (100 + i, 360))
                    ecran.blit(police30.render("Missile", 1, (0, 0, 0)), (95 + i, 450))
                elif pers.type == 1:
                    ecran.blit(im.gros_bombe, (100 + i, 360))
                    ecran.blit(police30.render("Bombe", 1, (0, 0, 0)), (95 + i, 450))
                elif pers.type == 2:
                    ecran.blit(im.gros_exp_glace, (100 + i, 360))
                    ecran.blit(police30.render("Glace", 1, (0, 0, 0)), (95 + i, 450))
                i += 200

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == QUIT:
                    fen.open_choose = False
                    fen.open_window = False

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    clic = pygame.Rect(event.pos[0], event.pos[1], 1, 1)
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
                        ter.screenshot("screenshots/screenshot")
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


# ___________________________________________________________________________________________________________________________________________________________________________

# Initialisation
pygame.init()

ecran = pygame.display.set_mode((0, 0))
from Variables_pour_importer import Images

im = Images()
ter = Terrain()
ecran = pygame.display.set_mode((len(ter.contenu[0]) * 30 - 60, len(ter.contenu) * 30 - 60))
fps = 100

police30 = pygame.font.Font(None, 30)
police50 = pygame.font.Font(None, 50)

fen = Fenetre()
type = Types(0, 1, 2)
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
