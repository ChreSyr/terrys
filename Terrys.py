# -*- coding: utf-8 -*

import pygame
import math
import random
import os
import glob

pygame.init()
fullscreen = False
if fullscreen: fullscreen = pygame.FULLSCREEN
ecran = pygame.display.set_mode((1280, 750), fullscreen)

from Classes import BoutonText, BoutonImage, MissileChemin, AnimatedBloc, StaticBloc, AnimatedParticle, StaticParticle
from Classes import Vector, Position
from Classes import im, font
from Fonctions import arrondir, closest, distance_pnts, f, get_angle, modulo, racine, sign, trouve
# from Fonctions import print_grid
ter = vert = rouge = bleu = admin = 0
pygame.display.set_icon(im.game_icon)


class Object:
    def __init__(self, dict=None, **kwargs):
        if dict is None:
            dict = kwargs.items()
        for key, value in dict:
            self.__setattr__(key, value)

    def __str__(self):
        reply = "<Object("
        for key, value in self.__dict__.items():
            reply += "'" + str(key) + "': " + str(value) + ", "
        return reply[:-2] + ")>"


class Game:
    def __init__(self):
        """
        Constructeur de Game
        """

        self.open = "menu"

        self.act_ter = None
        self.rect_tot = self.rect_jeu = self.rect_btn = 0
        self.grp_ter = []
        self.create_grp_ter()

        self.non_solid_blocs = ("vide", "jump", 'grav', 'axlL', 'axlR')
        self.fps = 50
        self.gravity = Vector(0, 10)  # Gravity va vers le bas, donc positif
        self.horloge = pygame.time.Clock()

        self.nb_joysticks = pygame.joystick.get_count()
        for i in range(self.nb_joysticks):
            pygame.joystick.Joystick(i).init()

        global vert, rouge, bleu, admin
        vert = Player(0, ia=self.nb_joysticks < 1)  # S'il y a moins de 1 joueur, Player1 est une ia
        rouge = Player(1, ia=self.nb_joysticks < 2)
        bleu = Player(2, ia=self.nb_joysticks < 3)
        admin = Admin()

        self.grp_pers = pygame.sprite.Group()
        for pers in vert, rouge, bleu:
            self.grp_pers.add(pers)

        self.menu = Menu()
        self.play = Play()
        self.maping = Maping()
        self.choose = Choose()
        self.mini = Mini()

    def create_grp_ter(self):
        """
        Methode qui cree les terrains de jeu a partir des fichiers existants
        """

        f_infos = open("Infos.txt")
        infos = f_infos.read()
        f_infos.close()
        infos = infos.split("\n")
        values = []
        for i in range(len(infos)):
            sentence = infos[i]
            values.append(sentence[sentence.index(":") + 2:])
        actual_ter_name = values[0]

        filenames = glob.glob("Terrains/*.txt")
        for filename in filenames:
            ter1 = Terrain(filename)
            ter1.find_cases_libres()
            self.grp_ter.append(ter1)
            if ter1.name == actual_ter_name:
                global ter
                self.act_ter = ter = ter1

        self.define_rect_fen()

    def define_rect_fen(self):
        """
        Methode qui update trois rect qui permettent de diviser l'ecran en deux parties
        """
        self.rect_tot = pygame.Rect(0, 0, max(200 + self.act_ter.col * 32, 1280), max(self.act_ter.row * 32, 750))
        self.rect_jeu = pygame.Rect(0, 0, self.act_ter.col * 32, self.act_ter.row * 32)
        self.rect_btn = pygame.Rect(0, 0, 200, 750)

    def create_new_ter(self):
        """
        Methode qui cree un nouveau terrain vide de taille 32*20
        """
        grid = str("vide'" * 32 + "\n") * 20 + "0'0'64'0'120'0"
        grid = grid.replace("'\n", "\n")

        i = 0
        while True:
            i += 1
            name = "Terrain" + str(i)
            if name not in [jeu.grp_ter[j].name for j in range(len(jeu.grp_ter))]:
                break

        filename = "Terrains/" + name + ".txt"
        fichier_txt = open(filename, "w")
        fichier_txt.write(grid)
        fichier_txt.close()

        self.act_ter = Terrain(filename)
        self.act_ter.save_img()
        self.grp_ter.append(self.act_ter)

    def rem_terrain(self, ter1):
        """
        Methode qui supprime un terrain de la base de donnees
        :param ter1: Le terrain a supprimer
        """
        os.remove("Terrains/" + ter1.name + ".txt")
        os.remove("Terrains/" + ter1.name + ".png")
        self.grp_ter.remove(ter1)
        self.menu.place_ter()

    def ptt_fen(self, list_btn, titre, msg):
        """
        Methode qui cree une petite fenetre d'alerte
        Il n'est pour l'instant possible que de faire des fenetrres de 2 ou 3 boutons
        :param list_btn: Liste de str qui seront les textes des boutons de la fenetre
        :param titre: Titre de la fenetre, affiche en gros
        :param msg: Lignes de phrases, affichees sous le titre
        :return: Le nom du bouton qui a ete clique
        """
        (x, y) = self.rect_jeu.w / 2, self.rect_jeu.h / 2
        if len(list_btn) == 2:
            grp_btn = [BoutonText(jeu.rect_btn.w + x - 70 - 10 - 140, y + 103, list_btn[0], 0),
                       BoutonText(jeu.rect_btn.w + x + 80, y + 103, list_btn[1], 1)]
        else:    # if len(list_btn) == 3:
            grp_btn = [BoutonText(jeu.rect_btn.w + x - 70 - 10 - 140, y + 103, list_btn[0], 0),
                       BoutonText(jeu.rect_btn.w + x - 70, y + 103, list_btn[1], 1),
                       BoutonText(jeu.rect_btn.w + x + 80, y + 103, list_btn[2], 2)]
        font_titre = font.render(50, titre, 1, (0, 0, 0))
        font_titre_w = font.get_size(50, titre)[0]
        words = msg.split(" ")
        lines = [[]]
        index_line = 0
        for word in words:
            lines[index_line].append(word)
            line = " ".join(lines[index_line])
            width = font.get_size(24, line)[0]
            if width > 430:
                if len(lines[index_line]) != 1:  # Si la ligne contient plusieurs mots
                    lines[index_line].remove(word)
                    lines.append([word])
                index_line += 1
        for i in range(len(lines)):
            lines[i] = " ".join(lines[i])
        font_lines = [font.render(24, lines[i], 1, (0, 0, 0)) for i in range(len(lines))]

        reponse = None
        while reponse is None and jeu.open is not False:  # jeu.open peut etre modifie dans admin.update()

            admin.update()
            if admin.key_down == pygame.K_ESCAPE:
                reponse = "BREAK"
            if admin.mouse_button_down == 1 or admin.joystick_button_pressed[0]:
                for btn in grp_btn:
                    if btn.rect.collidepoint(admin.mouse_pos):
                        reponse = btn.name

            ecran.blit(im.cadre_resultats, (jeu.rect_btn.w + x - 227, y - 150))
            ecran.blit(font_titre, (jeu.rect_btn.w + x - font_titre_w / 2, y - 120))
            for i in range(len(lines)):
                ecran.blit(font_lines[i], (jeu.rect_btn.w + x - 210, y - 64 + i * 25))
            for btn in grp_btn:
                btn.draw(ecran)
                if btn.rect.collidepoint(admin.mouse_pos):
                    ecran.blit(im.cadre_btn_touch, btn.rect.topleft)
                    if admin.mouse_button_is_pressed[0]:
                        ecran.blit(im.cadre_btn_select, btn.rect.topleft)
            pygame.display.flip()

        return reponse

    @staticmethod
    def freeze_activity(key):
        """
        Methode qui freeze le jeu jusqu'a ce que key ne soit plus presse
        :param key: La touche qui doit etre depressee pour arreter le freeze
        """
        run = True
        while run:
            for event2 in pygame.event.get():
                if event2.type == pygame.KEYUP and event2.key == key:
                    run = False

    @staticmethod
    def screenshot():
        """
        Methode qui enregistre un screenshot dans le dossier Screenshot
        """
        sub = ecran.subsurface(0, 0, 1280, 750)
        conteur = 0
        while conteur >= 0:
            conteur += 1
            try:
                pygame.image.load("Screenshots/Screenshot" + str(conteur) + ".png")
            except pygame.error:
                pygame.image.save(sub, "Screenshots/Screenshot" + str(conteur) + ".png")
                conteur = -1

    def save_infos(self):
        """
        Methode qui reecrit le fichier "Infos.txt"
        :return:
        """
        fichier_text = open("Infos.txt", "w")
        fichier_text.write("Terrain selectionne lors de la derniere partie : " + self.act_ter.name)
        fichier_text.close()


class Terrain:
    def __init__(self, filename):
        """
        Constructeur de Terrain
        :param filename: Le chemin qui conduit au fichier texte qui definit le terrain
                         de type "Terrains/*******.txt"
        """
        self.filename = filename
        self.name = filename[9:-4]

        # Groupes
        self.grp_bloc = pygame.sprite.Group()
        self.grp_bloc_effet = pygame.sprite.Group()
        self.grp_poseur = []

        # Champs a initialiser
        self.position = [(), (), ()]  # Les positions des trois players
        self.grid = []
        self.cases_libres = []
        self.col = self.row = 0
        self.background = self.cadre_maping = None

        # Appel des fonctions qui finissent d'initialiser le terrain
        self.ouvrir_terrain()
        self.create_background()
        self.ptt_ter = None
        self.create_ptt_ter()

    def ouvrir_terrain(self):
        """
        Methode qui lit le fichier de self.filename et en fait self.grid
        Appelee dans __init__()
        """
        fichier_text = open(self.filename, "r")
        self.grid = fichier_text.read()
        fichier_text.close()

        self.grid = self.grid.split("\n")
        for i in range(len(self.grid)):
            self.grid[i] = self.grid[i].split("'")

        line_pos = self.grid[-1]
        self.grid.pop(-1)
        self.position[0] = (int(line_pos[0]), int(line_pos[1]))
        self.position[1] = (int(line_pos[2]), int(line_pos[3]))
        self.position[2] = (int(line_pos[4]), int(line_pos[5]))

        self.col = len(self.grid[0])
        self.row = len(self.grid)
        self.cadre_maping = im.create_cadre(self.col * 8 + 40, self.row * 8 + 40)

        # Placement des blocs
        x_bloc = y_bloc = 0
        for i in range(self.row):
            for j in range(self.col):
                self.ajout(self.grid[i][j], x_bloc, y_bloc)
                x_bloc += 32
            y_bloc += 32
            x_bloc = 0

    def find_cases_libres(self):
        """
        Methode qui lit self.grid et en fait self.cases_libres
        self.cases_libres est une grille dont les cases font 16*16
        Appuyer sur TAB dans la fen PLAY permet d'avoir une vue de self.cases_libres
        ATTENTION : Adapte aux sprinters seulement
        0 : vide
        1 : bloc
        2 : jump
        3 : jump & axel
        4 : axel
        """
        # On cree une grille qui correspond aux blocs de 15px
        self.cases_libres = []
        x_tot, y_tot = self.col * 2, self.row * 2
        for i in range(y_tot):
            self.cases_libres.append([0] * x_tot)
        # Pour chaque case, les tests considerent qu'on y place le bottomleft d'un sprinter

        # larg est la largeur du sprinter en nb de cases
        larg = 3
        haut = 4

        # Si le sprinter rencontre un bloc a effet, on l'ecrit
        for bloc in self.grp_bloc_effet:
            num = 2 if bloc.name == "jump" else 4
            x, y = int(bloc.rect.centerx / 16), int(bloc.rect.top / 16)
            for i2 in range(larg + 1):
                for j2 in range(haut + 1):
                    # On utilise x - i2 car la case correspond au bottomleft
                    if 0 <= x - i2 < x_tot and 0 <= y + j2 < y_tot:
                        ref = self.cases_libres[y + j2][x - i2]
                        if ref in (2, 4) and ref != num:
                            self.cases_libres[y + j2][x - i2] = 3
                        elif ref == 0:
                            self.cases_libres[y + j2][x - i2] = num

        # Si le sprinter rencontre un bloc, on ecrit 1
        for bloc in self.grp_bloc:
            for i in (0, 16):
                for j in (0, 16):
                    if bloc.rect.collidepoint(bloc.rect.left + i, bloc.rect.top + j):

                        # Alors on met 1 partout ou le sprinter rencontrera ce bloc
                        x, y = int((bloc.rect.left + i) / 16), int((bloc.rect.top + j) / 16)
                        for i2 in range(larg):
                            for j2 in range(haut):
                                # On utilise x - i2 car la case correspond au bottomleft
                                if 0 <= x - i2 < x_tot and 0 <= y + j2 < y_tot:
                                    self.cases_libres[y + j2][x - i2] = 1
        # On rajoute une colonne de 1 sur le mur de droite
        for line in self.cases_libres:
            line[-larg + 1:] = [1] * (larg - 1)

    def case_stand(self, x, y):
        """
        Methode qui permet de savoir si un sprinter peut rester en STANDING en x, y
        pour une case de coord x, y sur la grille self.cases_libres
        ATTENTION : self.cases_libres est en 16*16 alors que self.grid est en 32*32
        :param x: L'abscisse de la case
        :param y: L'ordonnee de la case
        :return: True si la case correspond a de l'air ou un axel au-dessus d'un bloc ou du sol
                 False sinon
        """
        # Si self.cases_libres[y][x] correspond a de l'air ou un axel
        # Et si self.cases_libres[y+1][x] correspond a un bloc ou au sol
        return self.cases_libres[y][x] in (0, 4) and (y + 1 == self.row * 2 or self.cases_libres[y + 1][x] == 1)

    def case_start_jump(self, x, y):
        """
        Methode qui permet de savoir si un sprinter peut commencer un saut en x, y
        ATTENTION : self.cases_libres est en 16*16 alors que self.grid est en 32*32
        :param x: L'abscisse de la case
        :param y: L'ordonnee de la case
        :return: True si la case correspond a de l'air, un jump ou un axel au-dessus d'un bloc ou du sol
                 False sinon
        """
        # Si self.cases_libres[y][x] correspond a un jump
        # Ou si self.cases_libres[y][x] est une case_stand()
        return self.cases_libres[y][x] in (2, 3) or self.case_stand(x, y)

    def ajout(self, name, x, y):
        """
        Methode qui cree un bloc de type name en x, y dans self.grp_bloc ou self.grp_bloc_effet
        :param name: Le type de bloc a creer
        :param x: L'abscisse du bloc
        :param y: L'ordonnee du bloc
        """
        # Changer le nom d'un bloc:
        """
        if name == "escR":  # L'ancien nom
            name = "esDR"  # Le nouveau nom
            self.grid[int(y/32)][int(x/32)] = name
        """

        # Ajout du bloc
        if name == "bloc":
            self.grp_bloc.add(StaticBloc(x, y, im.bloc, name))
        elif name == "esDR":
            self.grp_bloc.add(StaticBloc(x, y, im.corner_blocs[0], name))
            self.grp_bloc.add(StaticBloc(x, y + 16, im.slabs[1], name))
        elif name == "esDL":
            self.grp_bloc.add(StaticBloc(x + 16, y, im.corner_blocs[1], name))
            self.grp_bloc.add(StaticBloc(x, y + 16, im.slabs[1], name))
        elif name == "esUL":
            self.grp_bloc.add(StaticBloc(x, y + 16, im.corner_blocs[2], name))
            self.grp_bloc.add(StaticBloc(x, y, im.slabs[0], name))
        elif name == "esUR":
            self.grp_bloc.add(StaticBloc(x + 16, y + 16, im.corner_blocs[3], name))
            self.grp_bloc.add(StaticBloc(x, y, im.slabs[0], name))
        elif name == "dalU":
            self.grp_bloc.add(StaticBloc(x, y, im.slabs[0], name))
        elif name == "dalD":
            self.grp_bloc.add(StaticBloc(x, y + 16, im.slabs[1], name))
        elif name == "dalL":
            self.grp_bloc.add(StaticBloc(x, y, im.slides[0], name))
        elif name == "dalR":
            self.grp_bloc.add(StaticBloc(x + 16, y, im.slides[1], name))
        elif name == "slim":
            self.grp_bloc.add(StaticBloc(x, y, im.slimeblock, name))
        elif name == "jump":
            self.grp_bloc_effet.add(AnimatedBloc(x, y, im.jumper, name))
        elif name == "grav":
            self.grp_bloc_effet.add(AnimatedBloc(x, y, im.gravitor, name))
        elif name == "axlL":
            self.grp_bloc_effet.add(AnimatedBloc(x, y, im.axel_left, name))
        elif name == "axlR":
            self.grp_bloc_effet.add(AnimatedBloc(x, y, im.axel_right, name))
        elif name == "pieg":
            self.grp_bloc.add(StaticBloc(x, y + 16, im.poseur, name))
            self.grp_poseur.append(Poseur(x, y + 16))

    def sauvegarder(self):
        """
        Methode qui enregistre le terrain dans son fichier texte
        Ne devrait etre appele que lorsqu'on quitte la fen MAPING
        """
        # On cree une copie de self.grid
        grid = []
        for i in range(self.row):
            grid.append(self.grid[i].copy())

        # On insere les positions des joueurs
        grid.append([str(self.position[0][0]), str(self.position[0][1]),
                     str(self.position[1][0]), str(self.position[1][1]),
                     str(self.position[2][0]), str(self.position[2][1])])
        # On le met dans le format du fichier texte
        for i in range(len(grid)):
            grid[i] = "'".join(grid[i])
        grid = "\n".join(grid)

        # On le met dans le fichier texte
        fichier_text = open(self.filename, "w")
        fichier_text.write(grid)
        fichier_text.close()

    def save_img(self):
        """
        Methode qui enregistre une image du terrain dans le dossier Terrains
        """
        pygame.image.save(ecran.subsurface(jeu.rect_jeu), "Terrains/" + self.name + ".png")
        pygame.image.save(self.background, "Terrains/" + self.name + "_background.png")

    def create_background(self):
        """
        Methode qui cree un landscape adapte aux dimensions du terrain
        """
        largeur = arrondir(im.landscape.get_width())
        hauteur = arrondir(im.landscape.get_height())

        self.background = pygame.Surface((self.col * 32, self.row * 32))
        self.background.blit(im.landscape.subsurface(0, 0, largeur, hauteur), (0, 0))

        # Si le terrain est plus haut que landscape
        for i in range(self.row - 18):
            self.background.blit(im.landscape.subsurface(0, hauteur - 32, largeur, 32), (0, hauteur + i * 32))

        # Si le terrain est plus large que landscape
        if self.col > largeur / 32:
            for i in range(int(self.col / largeur * 32)):
                sub = self.background.copy().subsurface(0, 0, largeur, self.row * 32)
                self.background.blit(sub, (largeur * (i + 1), 0))

    def create_ptt_ter(self):
        """
        Methode qui cree une petite image de ter pour la fen MENU
        """
        apercu = pygame.Surface((self.col * 32, self.row * 32))
        apercu.blit(self.background, (0, 0))

        self.grp_bloc.draw(apercu)
        for bloc in self.grp_bloc_effet:
            apercu.blit(bloc.image[0], bloc.rect.topleft)
        for i in range(3):
            apercu.blit(im.sprinter[i][1][0], self.position[i])

        w = 30 * 8
        h = int(self.row / self.col * w)
        im_ptt_ter = im.redimensionner(apercu, w, h)

        self.ptt_ter = Object(image=im_ptt_ter, rect=im_ptt_ter.get_rect(), cadre=im.create_cadre(w + 20, h + 20))

    def redimensionner(self, x1, y1, x2, y2):
        """
        Methode qui redimensionne le terrain
        :param x1: Ajouter/Supprimer une colonne a gauche
        :param y1: Ajouter/Supprimer une ligne en haut
        :param x2: Ajouter/Supprimer une colonne a droite
        :param y2: Ajouter/Supprimer une ligne en bas
        """

        for groupe in (self.grp_bloc, self.grp_bloc_effet):
            for bloc in groupe:
                bloc.rect.left += x1
                bloc.rect.top += y1
        for bloc in self.grp_poseur:
            bloc.rect_bonus.left += x1
            bloc.rect_bonus.top += y1
        for btn in jeu.maping.grp_btn_hotbar:
            btn.move(0, y1 + y2)
        for btn in jeu.play.grp_btn_res:
            btn.move((x1 + x2) / 2, (y1 + y2) / 2)

        jeu.define_rect_fen()
        for pers in jeu.grp_pers:
            pers.rect.left += x1
            pers.rect.top += y1
            pers.rect = pers.rect.clamp(jeu.rect_jeu)
            if pers.rect.right == jeu.rect_jeu.right:
                pers.rect.left = jeu.rect_jeu.right - 64
            if pers.rect.bottom == jeu.rect_jeu.bottom:
                pers.rect.top = jeu.rect_jeu.bottom - 64
        self.position = [vert.rect.topleft, rouge.rect.topleft, bleu.rect.topleft]
        jeu.maping.right_clic_big_rect.size = self.col * 8 + 120, self.row * 8 + 120
        jeu.maping.right_clic_lit_rect.size = self.col * 8 + 40, self.row * 8 + 40
        jeu.maping.hotbar.top += y1 + y2
        self.cadre_maping = im.create_cadre(self.col * 8 + 40, self.row * 8 + 40)
        self.create_background()
        self.create_ptt_ter()
        self.sauvegarder()
        # On a pas besoin de recreer ptt_ter, il sera cree quand on quittera la fen MAPING


class Admin:
    """
    Toutes les commandes hors joueur doivent passer par la classe Admin
    """
    def __init__(self):

        self.mouse_pos = (0, 0)
        self.mouse_button_down = self.mouse_button_up = None  # Le bouton de souris qui vient d'etre clique / relache
        self.mouse_button_is_pressed = [0, 0, 0]  # L'etat des trois clics de la souris
        self.mouse_motion = None  # L'evenement du deplacement de la souris
        self.mouse_moving = False  # Etat du mouvement de la souris, principalement utile pour le joystick
        self.mouse_speed = 90  # La vitesse de deplacement de la souris, utile quand elle est commandee par le joystick
        self.mouse_last_clic = [0, 0]  # Num du bouton, heure du clic   INUTILISE

        self.joystick_button_down = self.joystick_button_up = None  # Le bouton du joystick qui vient d'etre clique
        self.joystick_button_pressed = [0] * vert.input.get_numbuttons()
        self.joystick_axes = [0] * vert.input.get_numaxes()  # L'etat des axes
        self.joystick_hats = [(0, 0)] * vert.input.get_numhats()  # L'etat des hats

        self.key_down = self.key_pressed = self.key_up = None

    def update(self):
        """
        Update les input de l'utilisateur
        :return: None
        """

        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_moving = False
        self.mouse_button_down = self.mouse_button_up = self.mouse_motion = None
        self.key_down = self.key_up = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                jeu.open = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_button_down = event.button
                if event.button in (1, 2, 3):
                    self.mouse_button_is_pressed[event.button - 1] = 1
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_button_up = event.button
                if event.button in (1, 2, 3):
                    self.mouse_button_is_pressed[event.button - 1] = 0
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_motion = event
                self.mouse_moving = True
            elif event.type == pygame.KEYDOWN:
                self.key_down = self.key_pressed = event.key
                if event.key == pygame.K_f:
                    jeu.freeze_activity(pygame.K_f)
                elif event.key == pygame.K_F5:
                    jeu.screenshot()
            elif event.type == pygame.KEYUP:
                self.key_up = event.key
                self.key_pressed = None

        self.joystick_button_down = self.joystick_button_up = -1
        for i in range(len(self.joystick_button_pressed)):
            if not self.joystick_button_pressed[i] and vert.input.get_button(i):
                self.joystick_button_down = i
            if self.joystick_button_pressed[i] and not vert.input.get_button(i):
                self.joystick_button_up = i
            self.joystick_button_pressed[i] = vert.input.get_button(i)

        a1 = round(vert.input.get_axis(0)) or round(vert.input.get_axis(1)) or vert.input.get_hat(0)[0] or vert.input.get_hat(0)[1]
        a2 = self.joystick_axes[0] or self.joystick_axes[1] or self.joystick_hats[0][0] or self.joystick_hats[0][1]
        if not a1 and a2:
            self.mouse_speed = 100
        elif a1 and a2:
            if self.mouse_speed < 108:
                self.mouse_speed += 2
            elif self.mouse_speed == 108:
                self.mouse_speed = 200
            elif self.mouse_speed < 209:
                self.mouse_speed += 1
            elif self.mouse_speed == 209:
                self.mouse_speed = 400
        for i in range(len(self.joystick_axes)):
            self.joystick_axes[i] = round(vert.input.get_axis(i)) * int(self.mouse_speed / 10)

        for i in range(len(self.joystick_hats)):
            self.joystick_hats[i] = (vert.input.get_hat(i)[0] * 5, vert.input.get_hat(i)[1] * 5)

        # return

        if round(self.joystick_axes[0]) or round(self.joystick_axes[1]):
            if jeu.open != "play" or jeu.play.pause:
                pygame.mouse.set_pos(self.mouse_pos[0] + round(self.joystick_axes[0]),
                                     self.mouse_pos[1] + round(self.joystick_axes[1]))
                self.mouse_moving = True
        elif self.joystick_hats[0][0] or self.joystick_hats[0][1]:
            pygame.mouse.set_pos(self.mouse_pos[0] + self.joystick_hats[0][0],
                                 self.mouse_pos[1] - self.joystick_hats[0][1])
            self.mouse_moving = True


"""__________________________________________________________________________________________________________________"""


class Missile(pygame.sprite.Sprite):
    def __init__(self, lanceur):
        pygame.sprite.Sprite.__init__(self)
        self.image = im.missile[0]
        self.color = lanceur.color
        self.rect = pygame.Rect(0, 0, 24, 24)
        self.rect.center = (arrondir(lanceur.rect.centerx) + 16, arrondir(lanceur.rect.centery) + 16)
        self.x, self.y = self.rect.center
        self.vie = 6
        self.index_img_explosion = 0
        self.degel = 0

        self.angle = 0
        self.cible = perso(modulo(lanceur.color - 1, 3))
        self.state = "phantom" if self.cible.vie <= 0 else "focus"
        self.recherche_deplacement_vers_cible()
        jeu.play.grp_missile.add(self)
        self.pos_case = (arrondir(self.x), arrondir(self.y))

    def move(self):

        if self.vie <= 0:
            self.index_img_explosion += 1
            if self.index_img_explosion > 24.5:
                jeu.play.grp_missile.remove(self)
        else:
            if self.degel:
                self.degel -= 1
            else:
                if self.besoin_tourner():
                    self.recherche_deplacement_vers_cible()
                    self.image = im.missile[int(math.degrees(self.angle))]

                self.x += round(math.cos(self.angle) * 5)
                self.y -= round(math.sin(self.angle) * 5)
                self.rect.centerx = self.x
                self.rect.centery = self.y

                for pers in jeu.grp_pers:
                    if pers.color != self.color and self.rect.colliderect(pers.rect) and 0 < pers.vie:
                        pers.vie -= 16
                        pers.tps_recharg_anim_degat = 20
                        self.vie = 0
                for missile in jeu.play.grp_missile:
                    if missile != self and self.rect.colliderect(missile.rect) and 0 < missile.vie:
                        missile.vie = 0
                        self.vie = 0

                for bloc in ter.grp_bloc:
                    if self.rect.colliderect(bloc.rect):
                        self.vie = 0

                if self.state == "phantom":
                    if not jeu.rect_jeu.contains(self.rect):
                        self.vie = 0

    def recherche_deplacement_vers_cible(self):
        self.state = "phantom" if self.cible.vie <= 0 else "alive"
        if self.state == "alive":
            cible = self.cible.rect
            test = MissileChemin((int(self.rect.centerx / 32), int(self.rect.centery / 32)),
                                 (int(cible.centerx / 32), int(cible.centery / 32)),
                                 ter.grid)
            if test.reussite:
                if len(test.chemin) == 1:
                    self.angle = 0
                else:
                    self.angle = get_angle(test.chemin[-2][0] - test.pos_dep[0], -test.chemin[-2][1] + test.pos_dep[1])
            else:
                self.state = "phantom"
        if self.state == "phantom":
            liste_d = []
            for i in range(1, 4):
                if not liste_d:
                    for d in (-i*math.pi/4, i*math.pi/4):
                        if self.peut_avancer(self.angle + d):
                            liste_d.append(d)
            if self.peut_avancer(self.angle):
                liste_d.append(0)

            if not liste_d:
                self.angle = modulo(-self.angle, math.pi*2)
            else:
                self.angle = modulo(self.angle + random.choice(liste_d), math.pi*2)

            # 3 a copier

    def besoin_tourner(self):
        (x, y) = (self.x, self.y)
        (x_mil, y_mil) = (int(x / 32) * 32 + 16, int(y / 32) * 32 + 16)
        if x_mil - 2 <= x <= x_mil + 2 and y_mil - 2 <= y <= y_mil + 2:
            (self.x, self.y) = (x_mil, y_mil)
            return True
        else:
            return False

    def peut_avancer(self, angle):
        if angle % (math.pi / 2) == 0:
            (x, y) = (int(self.rect.centerx / 32) + round(math.cos(angle)),
                      int(self.rect.centery / 32) - round(math.sin(angle)))
            if 0 <= x < len(ter.grid[0]) and 0 <= y < len(ter.grid) and ter.grid[y][x] in jeu.non_solid_blocs:
                return True
        else:
            (x1, y1) = (int(self.rect.centerx / 32) + round(math.cos(angle)),
                        int(self.rect.centery / 32) - round(math.sin(angle)))
            (x2, y2) = (int(self.rect.centerx / 32) + round(math.cos(angle + math.pi/4)),
                        int(self.rect.centery / 32) - round(math.sin(angle + math.pi/4)))
            (x3, y3) = (int(self.rect.centerx / 32) + round(math.cos(angle - math.pi/4)),
                        int(self.rect.centery / 32) - round(math.sin(angle - math.pi/4)))
            if 0 <= x1 < len(ter.grid[0]) and 0 <= y1 < len(ter.grid) and ter.grid[y1][x1] in jeu.non_solid_blocs \
                and 0 <= x2 < len(ter.grid[0]) and 0 <= y2 < len(ter.grid) and ter.grid[y2][x2] in jeu.non_solid_blocs \
                    and 0 <= x3 < len(ter.grid[0]) and 0 <= y3 < len(ter.grid) and ter.grid[y3][x3] in jeu.non_solid_blocs:
                return True
        return False


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

        jeu.play.grp_bombe.add(self)

    def move(self):
        if self.vie <= 0:
            self.index_img_explosion += 0.3
            if not self.index_img_explosion < 8:
                jeu.play.grp_bombe.remove(self)

        elif self.degel:
            self.degel -= 1

        else:
            self.count_traj += 1
            self.rect.centery = self.coord_lancement[1] - (-self.count_traj ** 2 + 80 * self.count_traj) / 64
            self.rect.centerx += self.direction * 8

            explode = False
            for groupe in (jeu.grp_pers, jeu.play.grp_missile, jeu.play.grp_bombe):
                for objet in groupe:
                    if self.rect.colliderect(objet.rect) and objet != self.lanceur and objet != self and objet.vie:
                        explode = True
                        break

            for bloc in ter.grp_bloc:
                if self.rect.colliderect(bloc.rect):
                    explode = True

            if explode:
                self.explosion()
            if not jeu.rect_jeu.contains(self.rect):
                self.vie = 0

    def explosion(self):
        self.vie = 0
        for groupe in (jeu.grp_pers, jeu.play.grp_attak, jeu.play.grp_missile, jeu.play.grp_bombe):
            for objet in groupe:
                distance = distance_pnts(objet.rect.center, self.rect.center)
                if distance < 210 and objet != self.lanceur and objet != self and objet.vie:
                    if groupe == jeu.play.grp_bombe:
                        objet.explosion()
                    objet.vie -= (-distance * 40) / 210 + 40
                    if groupe == jeu.grp_pers:
                        objet.tps_recharg_anim_degat = 20


class Glace(pygame.sprite.Sprite):
    def __init__(self, centerx, centery, lanceur):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(centerx - 192, centery - 192, 384, 384)
        self.index_img = 0
        self.lanceur = lanceur

        for groupe in (jeu.grp_pers, jeu.play.grp_attak, jeu.play.grp_missile, jeu.play.grp_bombe):
            for objet in groupe:
                if objet != self.lanceur:
                    distance = distance_pnts(self.rect.center, objet.rect.center)
                    if distance < 192 and objet.vie > 0 and objet.degel == 0:
                        objet.degel = 300

        jeu.play.grp_glace.add(self)


class Attak(pygame.sprite.Sprite):
    def __init__(self, angle, lanceur):

        pygame.sprite.Sprite.__init__(self)
        self.lanceur = lanceur
        self.color = self.lanceur.color
        self.angle = angle
        self.image = im.attak[self.color]
        self.explosion = im.expl[self.color]
        self.rect = pygame.Rect(self.lanceur.rect.centerx - 10, self.lanceur.rect.centery - 10, 20, 20)
        self.x, self.y = self.lanceur.rect.center

        self.vie = 1
        self.index_img_explosion = 0
        self.index_img = self.count = 0
        self.degel = 0

        jeu.play.grp_attak.add(self)

    def move(self, test=None):

        if self.vie <= 0:
            self.index_img_explosion += 0.3
            if not self.index_img_explosion < 8:
                jeu.play.grp_attak.remove(self)

        elif self.degel:
            self.degel -= 1
        else:
            self.count += 0.1
            if self.count > 4:
                self.count = 0
            self.index_img = int(self.count)
            self.x += math.cos(self.angle) * 7  # On garde les valeurs x et y afin d'avoir une position precise
            self.y -= math.sin(self.angle) * 7  # L'angle doit etre en radian
            self.rect.centerx = self.x
            self.rect.centery = self.y

            for groupe in (jeu.play.grp_attak, jeu.play.grp_missile):
                for objet in groupe:
                    if self.rect.colliderect(objet.rect) and objet != self and objet.vie > 0 and not test:
                        self.vie = 0
                        objet.vie -= 3
                        self.rect.left += math.cos(self.angle)
                        self.rect.top += math.sin(self.angle)
            for pers in jeu.grp_pers:
                if self.rect.colliderect(pers.rect) and pers != self.lanceur and pers.vie > 0:
                    self.vie = 0
                    if test == "test":
                        self.vie = -1
                    else:
                        pers.vie -= 7
                        pers.tps_recharg_anim_degat = 10
            for bloc in ter.grp_bloc:
                if self.rect.colliderect(bloc.rect):
                    self.vie = 0
            if not jeu.rect_jeu.contains(self.rect):
                self.vie = 0


class Poseur:

    def __init__(self, x, y):
        """
        Constructeur de Poseur
        :param x: L'abscisse du poseur
        :param y: L'ordonnee du poseur
        """
        self.rect_bonus = pygame.Rect(x, y - 45, 32, 45)
        self.obstructed = False
        self.bloc = StaticBloc(x, y, im.poseur, "pieg")  # Utile ?
        self.index_img_broken = 0
        # self.couleur_piege = 0
        self.bonus = None

    def move(self):
        """
        Methode qui update le poseur de bonus
        """
        if not self.obstructed:

            # Animation du cassage du bonus
            if self.index_img_broken:
                self.index_img_broken += 0.3
                if self.index_img_broken > 4.7:
                    self.index_img_broken = 0
                    self.bonus = None

            # Apparition d'un bonus
            elif self.bonus is None:
                if not random.randrange(0, 1):
                    # self.couleur_piege = random.randint(0, 2)
                    self.bonus = im.bonus[random.randint(0, 2)]

            # Collision avec un player
            else:
                couleur_piege = random.randint(0, 2)
                self.bonus = im.bonus[couleur_piege]
                for pers in jeu.grp_pers:
                    if self.rect_bonus.colliderect(pers.rect) and pers.vie > 0:
                        if couleur_piege == 0:
                            pers.effet_rapide = 3.3
                            pers.anim_flash = 200
                        elif couleur_piege == 1:
                            pers.anim_coeur = 20
                        elif couleur_piege == 2:
                            pers.indestructible = pers.vie
                            pers.anim_bouclier = 500
                        self.index_img_broken = 0.3

    def draw_bonus(self, sub):
        # Le bloc de poseur fait deja partie de grp_bloc, pas besoin de l'afficher
        if self.bonus is not None:
            sub.blit(self.bonus[int(self.index_img_broken)], (self.rect_bonus.left - 8, self.rect_bonus.top))


"""__________________________________________________________________________________________________________________"""


class InputIA:
    def __init__(self, ia):
        self.ia = ia
        self.dx = 1
        self.dy = 0
        self.adx = self.ady = 0
        self.etat_spe = self.tirer_attak_spe = False
        self.bloqx = self.bloqy = False
        self.hat = [(0, 0)]

    def get_button(self, x):
        if x == 5:
            return self.etat_spe
        elif x == 4:
            return self.tirer_attak_spe

    def get_numbuttons(self):
        return 12

    def get_axis(self, x):
        if x == 3:
            return self.dy
        elif x == 2:
            return self.dx
        elif x == 1:
            return self.ady
        elif x == 0:
            return self.adx

    def get_numaxes(self):
        return 4

    def get_hat(self, x):
        return self.hat[x]

    def get_numhats(self):
        return 1

    def update(self):
        if self.bloqx:
            self.dx *= -1
        self.bloqx = self.bloqy = False


class Player(pygame.sprite.Sprite):
    def __init__(self, color, ia=False):
        pygame.sprite.Sprite.__init__(self)

        self.color = color
        self.type = 0
        self.anc_type = 0
        self.sprinter = im.sprinter[color]
        self.fighter = im.fighter[color]
        self.tank = im.tank[color]
        self.gros = im.gros[color]
        self.sub_gros = self.gros.subsurface(240, 0, 120, 120)
        self.image = self.sprinter
        self.image_attak = im.attak[color]
        self.image_explosion = im.expl[color]
        self.anim_degat = im.anim_degat[0]
        self.index_img = 0
        self.direction = -1
        self.ia = ia
        if not ia:
            self.input = pygame.joystick.Joystick(color)
        else:
            self.input = InputIA(self)

        pos = ter.position[color]
        self.pos = Position(pos)
        self.rect = pygame.Rect(pos[0], pos[1], 40, 52)

        self.vitesse = 10  # FAIRE UNE DEPENDANCE DE FPS
        self.effet_rapide = self.acceleration = 1
        self.vie = self.full_vie = 45

        # Champs qui permettent de gerer la gravite
        self.vel = Vector(0, 0)
        self.acc = Vector(0, 0)
        density = .001
        surface = self.rect.w * self.rect.h
        self.m = density * surface

        self.dy = self.dx = 0
        self.tps_en_air = self.y_max = 0
        self.state = "STANDING"
        self.effet_gel = 1
        self.effet_poison = 0
        self.fantome = False
        self.anim_bouclier = 0
        self.anim_coeur = 0
        self.anim_flash = 0

        self.tps_recharg_attak = 0
        self.tps_recharg_anim_degat = 0
        self.tps_recharg_attak_spe = 0
        self.tps_recharg_changement_type = 0
        self.degel = 0

        self.mort = False
        self.animation = True
        self.indestructible = False

        if ia:
            self.pos_cible = self.distance_cible = 0
            self.destination = self.line_dest = self.count_saut_ia = self.pnt_a_aller = 0
            self.chemin = []

    def set_left(self, x):
        self.rect.left = x
        self.pos.x = x
    left = property(lambda self: self.rect.left, set_left)

    def set_top(self, y):
        self.rect.top = y
        self.pos.y = y
    top = property(lambda self: self.rect.top, set_top)

    def reinit(self):
        self.vie = self.full_vie
        self.pos.x, self.pos.y = self.left, self.top = ter.position[self.color]
        self.dy = self.dx = self.tps_en_air = self.y_max = self.effet_poison = self.tps_recharg_anim_degat = self.tps_recharg_attak = self.degel = 0
        self.vel.mult(0)  # Verifier si cela
        self.acc.mult(0)  # est necessaire
        self.state = "STANDING"
        self.acceleration = self.effet_gel = self.effet_rapide = 1
        self.anim_bouclier = self.anim_coeur = self.anim_flash = 0
        self.direction = -1
        self.mort = False
        self.animation = True
        self.indestructible = False

    def changer_type(self, t):
        t = modulo(t, 3)
        self.anc_type = self.type
        self.type = t
        self.anim_degat = im.anim_degat[t]
        if t == 0:
            self.image = self.sprinter
            self.rect = pygame.Rect(self.left, self.top, 40, 52)
            self.vitesse = 6
            self.vie = 45
        elif t == 1:
            self.image = self.fighter
            self.rect = pygame.Rect(self.left, self.top, 64, 48)
            self.vitesse = 3.5
            self.vie = 64
        elif t == 2:
            self.image = self.tank
            self.rect = pygame.Rect(self.left, self.top, 56, 64)
            self.vitesse = 2.5
            self.vie = 100
        self.full_vie = self.vie
        self.tps_recharg_changement_type = 10

    def move(self):
        # Quand self est mort
        if self.vie <= 0 and self.indestructible is False:
            if self.animation:
                if self.mort is False:
                    self.mort = True
                    self.tps_en_air = 0
                    jeu.play.nb_survivants -= 1

                self.jump()
                self.top += self.dy
                self.rect.top = self.top
                if self.top > jeu.rect_btn.bottom:
                    self.animation = False

        # Quand self est congele
        elif self.degel:
            self.degel -= 1

        # Quand self peut bouger
        else:

            if self.ia:
                self.ia_find_way()
                self.input.update()
            # Effets blocs
            if self.fantome is False:

                for bloc in ter.grp_bloc_effet:
                    if self.rect.colliderect(bloc):
                        if bloc.name == "axlL":
                            self.vel.x = -50
                        elif bloc.name == "axlR":
                            self.vel.x = 50
                        elif bloc.name == "jump":
                            self.vel.y = -25
                        elif bloc.name == "grav":
                            self.vel.y = 50

            # Effets speciaux
            if self.effet_gel > 1:
                self.effet_gel -= 0.001
                if not self.effet_gel > 3:
                    self.effet_gel = 1

            if self.effet_poison:
                if self.effet_poison % 100 == 0:
                    self.vie -= 1
                    self.tps_recharg_anim_degat = 10
                self.effet_poison -= 1

            if self.anim_bouclier > 0:
                self.anim_bouclier -= 1
                if self.anim_bouclier <= 0:
                    self.indestructible = False

            if self.anim_coeur > 0:
                self.anim_coeur -= 1
                jeu.play.grp_particule.add(StaticParticle(self.rect.centerx, self.rect.centery, im.soin, 20))
                self.vie += 1
                if self.vie > self.full_vie:
                    self.vie = self.full_vie

            if self.anim_flash > 0:
                self.anim_flash -= 1
                if self.state == "STANDING" and round(self.input.get_axis(2)):
                    jeu.play.grp_particule.add(AnimatedParticle(self.rect.centerx, self.rect.bottom, im.star, 20))
                if self.anim_flash <= 0:
                    self.effet_rapide = 1

            # Deplacement vectoriel
            anc_pos = self.rect.topleft
            if not self.is_colliding():

                # Acceleration de la gravite
                self.acc.mult(0)
                self.acc.apply_vect(jeu.gravity)
                self.acc.mult(8 / jeu.fps)

                # Deplacement vertical
                dy = self.input.get_axis(3)
                if round(dy):
                    if dy < 0:
                        if self.state == "STANDING":
                            self.vel.y = -20
                    else:
                        dy *= 20
                        # Si on monte
                        if sign(self.vel.y) == -1:
                            self.vel.y += dy
                        # Si on descend et que la vitesse en y est inferieure a dy
                        elif self.vel.y < dy:
                            self.vel.y = dy

                # Deplacement horizontal
                if round(self.input.get_axis(2)):
                    self.direction = round(self.input.get_axis(2))
                    dx = round(self.input.get_axis(2)) * self.vitesse * self.effet_rapide
                    # Si la vitesse en x est inferieure a dx
                    if sign(self.vel.x) == sign(dx) and abs(self.vel.x) < abs(dx):
                        self.vel.x += dx
                        # Ne peut aller plus vite que dx
                        if abs(self.vel.x) > abs(dx):
                            self.vel.x = dx
                    # Si la vitesse en x est opposee a dx
                    if sign(self.vel.x) != sign(dx):
                        self.vel.x += dx
                else:
                    # Le player essaie d'etre statique
                    dx = self.vitesse * self.effet_rapide / int(self.effet_gel)
                    if abs(self.vel.x) > dx:
                        self.vel.x -= dx * sign(self.vel.x)
                    else:
                        self.vel.x = 0

                # Frottements
                # self.vel.mult(.95)

                # Application de l'acceleration
                self.vel.apply_vect(self.acc)

                # Application de la vitesse
                self.left += self.vel.x
                self.collision(self.vel.x, 0)
                self.top += self.vel.y
                self.collision(0, self.vel.y)
                self.collision_bords()

            self.vel.x = self.pos.x - anc_pos[0]
            self.vel.y = self.pos.y - anc_pos[1]

            # Animation
            if anc_pos == self.rect.topleft:
                self.index_img = 0
            else:
                self.index_img += 0.5 / (self.effet_gel * 2)
                if not self.index_img < 4:
                    self.index_img = 0

            # Lancement attaque
            (x, y) = (self.input.get_axis(0), -self.input.get_axis(1))
            if self.tps_recharg_attak == 0 and math.sqrt(x ** 2 + y ** 2) > 0.7:
                Attak(get_angle(x, y), self)
                self.tps_recharg_attak = 32
            elif self.tps_recharg_attak != 0:
                self.tps_recharg_attak -= 1

            # Lancement attaque speciale
            if self.input.get_button(4):
                if self.type == 0:
                    if self.tps_recharg_attak_spe == 0 and self.rect.top >= jeu.rect_jeu.top:
                        Missile(self)
                        self.tps_recharg_attak_spe = 14  # 250
                if self.type == 2:
                    if self.tps_recharg_attak_spe == 0:
                        Glace(self.rect.centerx, self.rect.centery, self)
                        self.tps_recharg_attak_spe = 450

            # Changement etat special
            if self.type == 1:
                if self.input.get_button(5):
                    self.fantome = True
                else:
                    self.fantome = False
                if self.input.get_button(4):
                    if self.tps_recharg_attak_spe == 0:
                        Bombe(self.rect.centerx, self.rect.centery, self, self.direction)
                        self.tps_recharg_attak_spe = 300

            if self.tps_recharg_attak_spe != 0:
                self.tps_recharg_attak_spe -= 1

            # Detection etat
            self.statement()

            # Permet de monter les escaliers sans que vel ne croit a un saut
            if self.state == "STANDING":
                self.vel.y = 0

            if self.state == "STANDING" and self.dy > 0:  # Si on vient de tomber, pas si on monte sur un bloc
                self.dy = self.tps_en_air = self.y_max = 0

            if self.tps_recharg_anim_degat:
                self.tps_recharg_anim_degat -= 1

        if self.indestructible is not False:
            if self.vie > self.indestructible:
                self.indestructible = self.vie
            elif self.vie < self.indestructible:  # and self.anim_bouclier:
                self.vie = self.indestructible
                self.tps_recharg_anim_degat = 0
                # self.anim_bouclier -= 10 * (self.vie < self.indestructible)

    def collision(self, dx, dy):
        for bloc in ter.grp_bloc:
            if bloc.rect.colliderect(self.rect):
                if dx and self.state == "STANDING":
                    ecart = self.rect.bottom - bloc.rect.top
                    if ecart <= 16:
                        # self.rect.bottom -= ecart
                        self.top = bloc.rect.top - self.rect.h
                        if self.is_colliding():
                            self.rect.bottom += ecart
                            self.top = self.rect.top
                            self.bloquage(dx, dy, bloc)
                    else:
                        self.bloquage(dx, dy, bloc)
                else:
                    self.bloquage(dx, dy, bloc)

    def collision_bords(self):
        if self.rect.left < jeu.rect_jeu.left:
            self.rect.left = jeu.rect_jeu.left
            if self.ia:
                self.input.bloqx = True
        elif self.rect.right > jeu.rect_jeu.right:
            self.rect.right = jeu.rect_jeu.right
            if self.ia:
                self.input.bloqx = True
        """if self.rect.top < jeu.rect_jeu.top:
            self.rect.top = jeu.rect_jeu.top
            self.tps_en_air = 0
            self.force_saut = 0
            if self.ia:
                self.input.bloqy = True"""
        if self.rect.bottom > jeu.rect_jeu.bottom:
            self.rect.bottom = jeu.rect_jeu.bottom
            if self.ia:
                self.input.bloqy = True
        self.left, self.top = self.rect.topleft

    def is_colliding(self):
        """
        Methode quipermet de savoir si self collide un bloc
        :return: True si self collide un bloc
                 False sinon
        """
        for bloc in ter.grp_bloc:
            if self.rect.colliderect(bloc.rect):
                return True
        return False

    def bloquage(self, dx, dy, mur):
        if dx > 0:
            self.left = mur.rect.left - self.rect.w
        elif dx < 0:
            self.left = mur.rect.right
        if dy > 0:  # self monte
            if mur.name == "slim" and self.state == "JUMPING":
                self.vel.y = - dy * 7 + 8
                self.tps_en_air = 0
                self.top = self.rect.top
                self.y_max = 0
            self.rect.bottom = mur.rect.top
            self.top = self.rect.top
        elif dy < 0:  # self descend
            self.rect.top = mur.rect.bottom
            self.top = self.rect.top
            self.tps_en_air = 0
        if self.ia and mur.name == "slim":
            if dx:
                self.input.bloqx = True
            if dy:
                self.input.bloqy = True

    def statement(self):
        self.state = "JUMPING"
        list = []
        temp = self.rect.copy()
        temp.top += 1
        for bloc in ter.grp_bloc:
            if temp.colliderect(bloc.rect) and not (
                                bloc.name == "slim" and self.dy > 1 and self.input.get_axis(3) > -0.4):
                self.state = "STANDING"
        if temp.bottom > jeu.rect_jeu.bottom:
            self.state = "STANDING"

    def cache_ou_pas(self, rect):
        dis = distance_pnts(self.rect.center, rect.center)
        """if dis > 32:
            dx = (rect.centerx - self.rect.centerx) / dis
            dy = (rect.centery - self.rect.centery) / dis
            pos = [self.rect.centerx, self.rect.centery]
            while True:
                pos[0] += dx * 32
                pos[1] += dy * 32
                pos2 = int(pos[0] / 16) + 2, int(pos[1] / 16) + 2
                for i in 1, 0, -1:
                    for j in 1, 0, -1:
                        if ter.cases_libres[pos2[1] + i][pos2[0] + j]:
                            return True
                if rect.left <= pos[0] <= rect.right and rect.top <= pos[1] <= rect.bottom:
                    return False
        else:
            return False"""

    def ia_find_way(self):
        self.pos_cible = perso(self.color - 1).rect.center

    def ia_find_closest_cible_attak(self, list_pos_adversaires):
        self.pos_cible = closest(self.rect.center, list_pos_adversaires)

    def ia_can_shoot_attak(self):
        liste = []
        for pers in jeu.grp_pers:
            if pers != self and pers.vie > 0:
                liste.append(pers)
        for missile in jeu.play.grp_missile:
            if missile.vie > 0 and missile.cible == self:
                liste.append(missile)
        self.IA_choisir_cible_attak(liste)

        if self.tps_recharg_attak:
            self.tps_recharg_attak -= 1
        else:
            while liste != []:
                dis_x = self.cible.rect.centerx - self.rect.centerx
                dis_y = self.cible.rect.centery - self.rect.centery
                hyp = math.sqrt(dis_x ** 2 + dis_y ** 2)
                if hyp == 0: hyp = 1
                dx = dis_x / hyp
                dy = dis_y / hyp

                case_arrivee = (int(self.cible.rect.centerx / 32), int(self.cible.rect.centery / 32))

                x, y = self.rect.center
                while True:
                    x += dx * 32
                    y += dy * 32
                    if not ter.grid[int(y / 32) + 1][int(x / 32) + 1] in jeu.non_solid_blocs:
                        tir = False
                        liste.remove(self.cible)
                        self.IA_choisir_cible_attak(liste)
                        break
                    elif (int(x / 32), int(y / 32)) == case_arrivee:
                        tir = True
                        liste = []
                        break
                if tir:
                    dis_x += random.randint(-32, 32)
                    dis_y += random.randint(-32, 32)
                    hyp = math.sqrt(dis_x ** 2 + dis_y ** 2)
                    if hyp == 0: hyp = 1
                    dx = dis_x / hyp
                    dy = dis_y / hyp
                    Attak(-sign(dy) * int(math.degrees(math.acos(dx))), self)
                    self.tps_recharg_attak = 32


class Papy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        """
        Constructeur de Papy
        :param x: L'abscisse du papy
        :param y: L'ordonnee du papy
        """
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(x, y, 44, 56)
        self.image = im.papy[2][0]
        self.index_pas = 0
        self.direction = 0
        self.dx, self.dy = 0, 0
        self.speed = 10

    def updt(self):
        """
        Methode qui update papy
        """
        self.updt_pos()
        self.updt_image()

    def updt_pos(self):
        """
        Methode qui update la position de papy
        """
        pos_mouse = admin.mouse_pos
        dis = distance_pnts(pos_mouse, self.rect.center)
        if dis > 10:
            self.dx = (pos_mouse[0] - self.rect.centerx) / dis
            self.dy = (pos_mouse[1] - self.rect.centery) / dis
            self.rect.left += self.dx * self.speed
            self.rect.top += self.dy * self.speed
        else:
            self.rect.center = pos_mouse

    def updt_image(self):
        """
        Methode qui update l'image de papy
        """
        if self.dx or self.dy:
            self.index_pas += 0.5
        else:
            self.index_pas = 0
        if self.index_pas >= 4:
            self.index_pas = 0

        if abs(self.dx) > abs(self.dy):
            self.direction = 1 if self.dx > 0 else 0
        else:
            self.direction = 3 if self.dy < 0 else 2
        self.image = im.papy[self.direction][int(self.index_pas)]


"""__________________________________________________________________________________________________________________"""


class Menu:
    def __init__(self):
        """
        Constructeur de Menu
        """
        self.rect_create_new_ter = None
        self.del_ter = [-1, pygame.Rect(0, 0, 32, 32)]
        self.grp_btn = [BoutonText(30, 30, "JOUER", "choose"),
                        BoutonText(30, 80, "MODIFIER", "maping"),
                        BoutonText(30, 130, "MINI JEUX", "mini"),
                        BoutonText(30, 180, "QUITTER", False)]
        self.name_btn_select = None

    def place_ter(self):
        """
        Methode qui place les petits terrains
        """
        for ter1 in jeu.grp_ter:
            ter1.ptt_ter.rect.left = 2000
        w = ter1.ptt_ter.rect.w + 20
        grp_coins = [(200 + step, 0) for step in range(0, 4*w, w)]
        for ter1 in jeu.grp_ter:
            coin = grp_coins[0]
            ter1.ptt_ter.rect.topleft = coin
            grp_coins.remove(coin)
            grp_coins.append((ter1.ptt_ter.rect.left, ter1.ptt_ter.rect.bottom + 20))
            get_y = lambda x: x[1]
            grp_coins.sort(key=get_y)
        self.rect_create_new_ter = pygame.Rect(0, 0, 32 * 8 + 40, 20 * 8 + 40)
        coin = grp_coins[0]
        self.rect_create_new_ter.topleft = coin

    def run(self):

        self.place_ter()

        while jeu.open == "menu":
            self.react_event()
            self.blit_all()

        for ter1 in jeu.grp_ter:
            if ter1.name == jeu.act_ter.name:
                global ter
                ter = ter1

    def react_event(self):
        admin.update()
        if admin.key_down == pygame.K_ESCAPE:
            jeu.open = False
        elif admin.key_down == pygame.K_RETURN:
            jeu.open = "choose"

        if admin.joystick_button_down == 0:
            self.clic()
        if admin.mouse_button_down == 1:
            self.clic()

    def clic(self):
        pos = admin.mouse_pos
        if self.rect_create_new_ter.collidepoint(pos):
            jeu.create_new_ter()
            self.place_ter()
        for btn in self.grp_btn:
            if btn.rect.collidepoint(pos):
                jeu.open = btn.reponse
                self.name_btn_select = btn.name
        for ter1 in jeu.grp_ter:
            if ter1.ptt_ter.rect.collidepoint(pos):
                if self.del_ter[0] == ter1.name and self.del_ter[1].collidepoint(pos):
                    if jeu.ptt_fen(("ANNULER", "SUPPRIMER"), "ATTENTION !",
                                   "Vous etes sur le point de supprimer ce terrain. Voulez-vous continuer ?") == "SUPPRIMER":
                        jeu.rem_terrain(ter1)
                        self.place_ter()
                        if ter1.name == jeu.act_ter.name:
                            jeu.act_ter = jeu.grp_ter[-1]
                else:
                    jeu.act_ter = ter1
                    jeu.define_rect_fen()

    def blit_all(self):
        pos = admin.mouse_pos
        ecran.blit(im.fond_ground, (0, 0))
        ecran.blit(im.btn_column, (0, 0))
        for btn in self.grp_btn:
            btn.draw(ecran)
            if btn.rect.collidepoint(pos):
                if btn.name == self.name_btn_select:
                    ecran.blit(im.cadre_btn_select, btn.rect.topleft)
                    self.name_btn_select = None
                ecran.blit(im.cadre_btn_touch, btn.rect.topleft)

        for ter1 in jeu.grp_ter:
            if ter1.name == jeu.act_ter.name:
                ecran.blit(ter1.ptt_ter.cadre, (ter1.ptt_ter.rect.left + 10, ter1.ptt_ter.rect.top + 10))
            ecran.blit(ter1.ptt_ter.image, (ter1.ptt_ter.rect.left + 20, ter1.ptt_ter.rect.top + 20))
            if ter1.ptt_ter.rect.collidepoint(pos):
                ecran.blit(im.cadre_delete, (ter1.ptt_ter.rect.left + 10, ter1.ptt_ter.rect.top + 10))
                self.del_ter = [ter1.name, pygame.Rect(ter1.ptt_ter.rect.left + 10, ter1.ptt_ter.rect.top + 10, 32, 32)]
        ecran.blit(im.ajout_ter, (self.rect_create_new_ter.left + 20, self.rect_create_new_ter.top + 20))

        pygame.display.flip()
        jeu.horloge.tick(jeu.fps)


class Play:
    def __init__(self):

        self.grp_btn = []
        self.grp_btn_res = []
        self.name_btn_select = None
        self.grp_missile = pygame.sprite.Group()
        self.grp_bombe = pygame.sprite.Group()
        self.grp_attak = pygame.sprite.Group()
        self.grp_glace = pygame.sprite.Group()
        self.grp_particule = pygame.sprite.Group()
        self.tps_recharg_chang_btn = 0
        self.count_anim_bloc_effet = 0
        self.gagnant = None
        self.nb_survivants = 3

        self.cases_ia = []

    def place_btn(self):
        self.grp_btn = [BoutonText(30, 30, "PAUSE", None)]
        self.grp_btn_res = [BoutonText(jeu.rect_jeu.centerx - 220, jeu.rect_jeu.centery + 103, "REJOUER", "play"),
                            BoutonText(jeu.rect_jeu.centerx - 70, jeu.rect_jeu.centery + 103, "MENU", "menu"),
                            BoutonText(jeu.rect_jeu.centerx + 80, jeu.rect_jeu.centery + 103, "OPTIONS", "choose")]

    def start_new_game(self):
        self.tps_recharg_chang_btn = 0
        self.count_anim_bloc_effet = 0
        self.gagnant = None
        for groupe in (self.grp_attak, self.grp_missile, self.grp_bombe, self.grp_particule):
            for objet in groupe:
                groupe.remove(objet)
        for pers in jeu.grp_pers:
            pers.reinit()
            self.nb_survivants = 3

        for poseur in ter.grp_poseur:
            poseur.bonus = None
            poseur.obstructed = ter.grid[int(poseur.rect_bonus.top / 32)][
                                    int(poseur.rect_bonus.left / 32)] not in jeu.non_solid_blocs

    def run(self):
        self.place_btn()
        self.start_new_game()
        while jeu.open == "play":

            self.react_event()

            # Animation
            if self.count_anim_bloc_effet < 15:
                self.count_anim_bloc_effet += 1
            else:
                self.count_anim_bloc_effet = 0

            for groupe in (self.grp_attak, self.grp_bombe, self.grp_missile, ter.grp_poseur , jeu.grp_pers):
                for objet in groupe:
                    objet.move()

            # Gerance jeu auxiliaires
            if self.nb_survivants <= 2 and not jeu.play.gagnant:
                for pers in jeu.grp_pers:
                    if perso(pers.color - 1).mort:
                        pers.indestructible = pers.vie
                        self.gagnant = pers.sub_gros

            self.blit_all()

    def react_event(self):
        admin.update()
        if admin.joystick_button_down == 0 or admin.mouse_button_down == 1:
            self.clic()

        if admin.key_down == pygame.K_ESCAPE and not self.gagnant:
            confirmation = jeu.ptt_fen(("ANNULER", "QUITTER"), "ATTENTION !",
                                       "Vous etes sur le point de fermer ce jeu. "
                                       "Voulez-vous vraiment continuer ?")
            if confirmation == "QUITTER":
                jeu.open = False
        elif admin.key_down == pygame.K_SPACE:
            self.pause()
        elif admin.key_down == pygame.K_RETURN:
            jeu.open = "maping"
        elif admin.key_down == pygame.K_d:
            self.cases_ia.pop(0)

    @staticmethod
    def pause():
        pause = True
        while pause:
            clicked_btn = jeu.ptt_fen(("REPRENDRE", "MENU", "OPTIONS"), "PAUSE", "Le jeu est en pause")
            if clicked_btn == "REPRENDRE":
                pause = False
            elif clicked_btn in ("MENU", "OPTIONS"):
                confirmation = jeu.ptt_fen(("ANNULER", "QUITTER"), "ATTENTION !",
                                           "Vous etes sur le point de quitter la partie en cours. "
                                           "Voulez-vous vraiment quitter ?")
                if confirmation == "QUITTER":
                    pause = False
                    if clicked_btn == "MENU":
                        jeu.open = "menu"
                    elif clicked_btn == "OPTIONS":
                        jeu.open = "choose"
            elif clicked_btn == "BREAK":
                pause = False

    def clic(self):
        pos = admin.mouse_pos
        for btn in self.grp_btn:
            if btn.rect.collidepoint(pos):
                if btn.name == "PAUSE" and not self.gagnant:
                    self.pause()

        if self.gagnant:
            for btn in self.grp_btn_res:
                if btn.rect.collidepoint(pos):
                    jeu.open = btn.reponse
                    if btn.name == "REJOUER":
                        self.start_new_game()

        elif jeu.rect_jeu.collidepoint(pos):
            x, y = int(pos[0] / 16), int(pos[1] / 16)
            # if ter.cases_libres[y][x] in (0, 4) and (y == ter.row * 2 or ter.cases_libres[y + 1][x] == 1):
            if ter.case_start_jump(x, y):
                self.pathfinding_ia(x, y)

    def blit_all(self):
        pos = admin.mouse_pos
        ecran.blit(im.fond_ground, (0, 0))
        ecran.blit(ter.background, (0, 0))

        if pygame.key.get_pressed()[pygame.K_TAB]:
            x_bloc = y_bloc = 0
            for cases in ter.cases_libres:
                for case in cases:
                    if case == 1:
                        color = (0, 0, 0)
                    elif case == 2:
                        color = (255, 127, 0)
                    elif case == 3:
                        color = (127, 127, 0)
                    elif case == 4:
                        color = (0, 127, 0)
                    else:
                        color = (0, 0, 63)
                    pygame.draw.rect(ecran, color, (x_bloc, y_bloc, 16, 16))
                    x_bloc += 16
                y_bloc += 16
                x_bloc = 0

            # for i in range(len(self.cases_ia)):
                # grid = self.cases_ia[-i]
            if self.cases_ia:
                grid = self.cases_ia[0]
                x_bloc = y_bloc = 0
                for line in grid:
                    for case in line:
                        if type(case) == list:
                            color = int(case[0] * 255 / 10) if 0 <= case[0] <= 10 else 255
                            pygame.draw.rect(ecran, (color, color, color), (x_bloc, y_bloc, 16, 16))
                            if len(case) == 3 and case[2] == "dep":
                                pygame.draw.rect(ecran, (0, 127, 127), (x_bloc, y_bloc, 16, 16))
                        elif case == "fin":
                            pygame.draw.rect(ecran, (0, 255, 255), (x_bloc, y_bloc, 16, 16))
                        x_bloc += 16
                    y_bloc += 16
                    x_bloc = 0

            for pers in jeu.grp_pers:
                color = (0, 255, 0) if pers.color == 0 else (255, 0, 0) if pers.color == 1 else (0, 0, 255)
                pygame.draw.rect(ecran, color, (arrondir(pers.left, 16), arrondir(pers.rect.bottom - 1, 16), 16, 16))

        else:
            ter.grp_bloc.draw(ecran)
            for bloc in ter.grp_bloc_effet:
                ecran.blit(bloc.image[int(self.count_anim_bloc_effet)], (bloc.rect.left, bloc.rect.top))
            for poseur in ter.grp_poseur:
                poseur.draw_bonus(ecran)

            for pers in jeu.grp_pers:

                ecran.blit(pers.image[pers.direction][int(pers.index_img)], pers.rect.topleft)
                if pers.tps_recharg_anim_degat:  # and not pers.anim_bouclier:
                    ecran.blit(pers.anim_degat[pers.direction][int(pers.index_img)], pers.rect.topleft)
                if pers.effet_gel > 1:
                    ecran.blit(pers.anim_ralenti[pers.direction][int(pers.index_img)], pers.rect.topleft)
                if pers.effet_poison:
                    ecran.blit(pers.anim_poison[pers.direction][int(pers.index_img)], pers.rect.topleft)
                if pers.degel > 0:
                    ecran.blit(im.glacon_pers, (pers.rect.centerx - 32, pers.rect.centery - 32))
                if pers.vie > 0:
                    # Barre de vie
                    color = (55 + 200 * abs(pers.vie / pers.full_vie - 1),
                               255 - 200 * abs(pers.vie / pers.full_vie - 1), 50)
                    if pers.rect.bottom > jeu.rect_jeu.top:
                        haut = pers.rect.top - 10 if pers.rect.top - 10 >= 0 else 0
                        pygame.draw.rect(ecran, color,
                                         (pers.left, haut, pers.rect.width * pers.vie / pers.full_vie, 5))
                    else:
                        ecran.blit(im.fleches[pers.color], (pers.rect.centerx-16, 0))
                if pers.indestructible:
                    ecran.blit(im.shield[pers.color][modulo(int(-pers.anim_bouclier/4), 20)], (pers.rect.centerx - 42, pers.rect.centery - 42))
                # if pers.color == 1 and pers.ia is True:
                #      pygame.draw.line(ecran, (255, 0, 0), pers.rect.center, pers.pos_cible, 4)

        for attak in self.grp_attak:
            if attak.vie > 0:
                ecran.blit(attak.image[attak.index_img], attak.rect.topleft)
                if attak.degel > 0:
                    ecran.blit(im.glacon_attak, (attak.rect.centerx - 16, attak.rect.centery - 16))
            else:
                ecran.blit(attak.explosion[int(attak.index_img_explosion)],
                           (attak.rect.centerx - 18, attak.rect.centery - 18))

        for missile in self.grp_missile:
            if missile.vie > 0:
                ecran.blit(missile.image, missile.rect.topleft)
                if missile.degel > 0:
                    ecran.blit(im.glacon_attak, (missile.rect.centerx - 16, missile.rect.centery - 16))
            else:
                ecran.blit(im.expl_missile[int(missile.index_img_explosion)],
                           (missile.rect.centerx - 32, missile.rect.centery - 32))

        for bombe in self.grp_bombe:
            if bombe.vie > 0:
                ecran.blit(bombe.image, bombe.rect.topleft)
                if bombe.degel > 0:
                    ecran.blit(im.glacon_attak, (bombe.rect.centerx - 16, bombe.rect.centery - 16))
            else:
                ecran.blit(im.expl_bombe[int(bombe.index_img_explosion)],
                           (bombe.rect.centerx - 128, bombe.rect.centery - 128))

        for glace in self.grp_glace:
            glace.index_img += 0.3 if 5 < glace.index_img < 10 else 0.2
            self.grp_glace.remove(glace) if not glace.index_img < 19 else ecran.blit(
                im.expl_glace[int(glace.index_img)], glace.rect.topleft)

        for part in self.grp_particule:
            part.rect.top -= 1
            part.vie -= 1
            if part.vie <= 0:
                self.grp_particule.remove(part)
            else:
                if type(part.image) == list:
                    ecran.blit(part.image[2 - int(part.vie / 20 * 3)], part.rect.topleft)
                else:
                    ecran.blit(part.image, part.rect.topleft)

        ecran.scroll(200)

        if self.gagnant:
            self.blit_resultats()

        # Affichage des boutons
        ecran.blit(im.btn_column, (0, 0))
        for btn in self.grp_btn:
            btn.draw(ecran)
            if btn.rect.collidepoint(pos) and not self.gagnant:
                if btn.name == self.name_btn_select:
                    ecran.blit(im.cadre_btn_select, btn.rect.topleft)
                    self.name_btn_select = None
                ecran.blit(im.cadre_btn_touch, btn.rect.topleft)

        pygame.display.flip()
        jeu.horloge.tick(jeu.fps)

    def blit_resultats(self):

        ecran.blit(im.cadre_resultats, (ter.col * 16 - 70 - 10 - 140 - 7, ter.row * 16 - 150))
        ecran.blit(self.gagnant, (ter.col * 16 - 64, ter.row * 16 - 80))
        ecran.blit(font.render(50, "WINNER !", 1, (0, 0, 0)), (ter.col * 16 - 80, ter.row * 16 - 120))

        pos = admin.mouse_pos
        for btn in self.grp_btn_res:
            btn.draw(ecran)
            if btn.rect.collidepoint(pos):
                if admin.mouse_button_is_pressed[0]:
                    ecran.blit(im.cadre_btn_select, btn.rect.topleft)
                ecran.blit(im.cadre_btn_touch, btn.rect.topleft)

    def pathfinding_ia(self, x_dep, y_dep):

        v_pers = 6  # Vitesse de l'IA, en nb de px par boucle
        v = 16 / v_pers / 8  # tps_en_air mit pr se deplacer horizontalement de 15px

        self.cases_ia = []
        h = 0
        t2 = racine(-10, 80, -h, 1)
        list_pnts_dep = [[x_dep, y_dep, t2, 0]]
        while list_pnts_dep:

            if len(list_pnts_dep[0]) == 4:
                # On recree un grille pour que les tps ne se croisent pas
                row = int(ter.row * 32 / 16)
                col = int(ter.col * 32 / 16)
                grid = [["vide" if ter.cases_libres[j][i] == 1 else "bloc"
                         for i in range(col)]
                        for j in range(row)]
                x0, y0, t0, dx0 = list_pnts_dep[0]
                b = 104 if ter.cases_libres[y0][x0] in (2, 3) else 82  # C'est la force de saut, 100 pour un jumper
                grid[y0][x0] = [t0, dx0]

                # On rajoute des row a la fin pour permettre a l'ia de sauter en dehors de la fenetre
                t_max = b / 20
                h_max = int(f(-10, b, 0, t_max) / 16)
                for i in range(h_max):
                    grid.append(["vide"] * ter.col * 2)
                self.cases_ia.append(grid)
            else:
                grid = self.cases_ia[-1]
                x0, y0, t0, dx0, msg = list_pnts_dep[0]
                grid[y0][x0] = [t0, dx0]

            list_pnts_pr_la_recherche = [[x0, y0]]
            while list_pnts_pr_la_recherche:
                x, y = list_pnts_pr_la_recherche[0]
                t, dx = grid[y][x][0:2]
                # Si t <= b / 20, c'est qu'on est en train de monter
                montee = t <= b / 20
                not_start = (x, y) != (x0, y0)
                # Si on est sur un axel, on augmente la vitesse
                v = 16 / v_pers / 8 / 2 if ter.cases_libres[y][x] in (3, 4) else 16 / v_pers / 8
                # Si on descend et qu'on peut se poser ou qu'on touche un jumper, on s'arrete
                if y >= 0 and not montee and ter.case_stand(x, y) \
                        or y >= 0 and ter.cases_libres[y][x] in (2, 3) and not_start:
                    grid[y][x] = "fin"
                else:
                    if montee:
                        # Si on est sur un "stop" ou un "dep"
                        if y < ter.row * 2 - 1 and len(grid[y + 1][x]) == 3:
                            grid[y][x].append("stop")
                    else:
                        # Si on est sous un "stop" ou un "dep"
                        if y >= 0 and len(grid[y - 1][x]) == 3:
                            grid[y][x].append("stop")

                    # Si on est sur un "vide" et qu'on est pas un "stop"
                    if len(grid[y][x]) == 2 and y < ter.row * 2 - 1 and grid[y + 1][x] == "vide":
                        # round(f(-10, b, 0, t) / 16 - 1) * 16 est la hauteur du bloc de dessous
                        t2 = racine(-10, b, -round(f(-10, b, 0, t) / 16 - 1) * 16, 2)
                        if t2 != -1:
                            t2 = arrondir(t2, 0.001)
                            grid[y + 1][x] = [t2, dx]
                            list_pnts_pr_la_recherche.append([x, y + 1])
                    if montee:
                        # Si on est sous un "vide" ou un "stop" ou qu'on a depasse le top
                        # VERIFIER si le sous un "stop" est utile
                        if grid[y - 1][x] == "vide" or len(grid[y - 1][x]) == 3 and grid[y - 1][x][2] == "stop" or y < 0:
                            # round(f(-10, b, 0, t) / 16 + 1) * 16 est la hauteur du bloc de dessus
                            t2 = racine(-10, b, -round(f(-10, b, 0, t) / 16 + 1) * 16, 1)
                            if t2 != -1:
                                t2 = arrondir(t2, 0.001)
                                grid[y - 1][x] = [t2, dx]
                                list_pnts_pr_la_recherche.append([x, y - 1])
                    if len(grid[y][x]) == 2:
                        # Si on est pas sorti sur la gauche et que le bloc a gauche est un "vide"
                        if x >= 0 and grid[y][x - 1] == "vide":
                            # On se decale que si on peut pas y aller par en dessous
                            # Si on a pas depasse le bottom et on est dessus a droite d'un "bloc" et
                            # pas au debut et en montee
                            if y < ter.row * 2 - 1 and grid[y + 1][x - 1] == "bloc" and not_start:
                                grid[y][x].append("dep")
                            elif grid[y - 1][x - 1] == "bloc" and not_start:
                                grid[y][x].append("dep")
                            elif dx - dx0 + v <= t - t0:
                                grid[y][x - 1] = [t, dx + v]
                                list_pnts_pr_la_recherche.append([x - 1, y])
                        # Si on est pas sorti sur la droite et que le bloc de droite est un "vide"
                        if x < ter.col * 2 - 1 and grid[y][x + 1] == "vide":
                            # Si on a pas depasse le bottom et on est dessus a gauche d'un "bloc" et
                            # pas au debut et en montee
                            if y < ter.row * 2 - 1 and grid[y + 1][x + 1] == "bloc" and not_start:
                                grid[y][x].append("dep")
                            elif grid[y - 1][x + 1] == "bloc" and not_start:
                                grid[y][x].append("dep")
                            elif dx - dx0 + v <= t - t0:
                                grid[y][x + 1] = [t, dx + v]
                                list_pnts_pr_la_recherche.append([x + 1, y])
                        # Si la case est un dep, il faut partir de cette case
                        if len(grid[y][x]) == 3:
                            list_pnts_dep.append([x, y, t, dx, "dep"])
                list_pnts_pr_la_recherche.pop(0)
            list_pnts_dep.pop(0)


class YScrollableImage(pygame.Surface):
    def __init__(self, image, y_tot, step=1):
        pygame.Surface.__init__(self, (image.get_width(), y_tot + step * 2), pygame.SRCALPHA)
        self.fill((0, 0, 0, 0))
        self.image = image
        self.blit(image, (0, step))
        self.y_index = self.y_min = step
        self.y_max = self.get_height() - self.image.get_height()
        self.step = step

    def scroll_up(self):
        anc_y = self.y_index
        if self.y_index > self.y_min:
            self.y_index -= self.step
            if self.y_index < self.y_min:
                self.y_index = self.y_min
        self.scroll(dx=0, dy=self.y_index - anc_y)

    def scroll_down(self):
        anc_y = self.y_index
        if self.y_index < self.y_max:
            self.y_index += self.step
            if self.y_index > self.y_max:
                self.y_index = self.y_max
        self.scroll(dx=0, dy=self.y_index - anc_y)

    def fullscroll_up(self):
        self.y_index = self.y_min
        self.fill((0, 0, 0, 0))
        self.blit(self.image, (0, self.step))

    def fullscroll_down(self):
        self.y_index = self.y_max
        self.fill((0, 0, 0, 0))
        self.blit(self.image, (0, self.get_height() - self.image.get_height()))

    def is_up(self):
        return self.y_index == self.y_min

    def is_down(self):
        return self.y_index == self.y_max


class Slot:
    def __init__(self, x, y, image, name):
        """
        Constructeur de Slot
        Un slot fait 46 px de large
        :param btn: Les boutons accessibles a partir du slot
        """
        self.btn = BoutonImage(x, y, image, name)
        self.rect = pygame.Rect(0, 0, 46, 46)


class Col(list):
    def __init__(self, *slots):
        """
        Constructeur de Col
        Une Col fait 46 px de large
        Son image cree un contour de 4px
        :param slots: Les slots de la colonne
        """
        list.__init__(self, slots)
        self.selected_slot = slots[0]
        self.num = 0
        self.rect_slot = pygame.Rect(0, 0, 46, 46)
        self.rect_inventory = pygame.Rect(0, 0, 46 + 4 * 2, 46 * len(slots) + 4 * 2)
        self.is_open = 0

        # Creation self.image
        image = pygame.Surface(self.rect_inventory.size).convert_alpha()
        image.fill((0, 0, 0, 0))
        pygame.draw.rect(image, (192, 192, 192), (4, 4, 46, 46 * len(slots)))
        for i in range(4):  # Blit un rect d'epaisseur 4
            pygame.draw.rect(image, (51, 51, 51), (i, i, self.rect_inventory.w - i*2, self.rect_inventory.h - i*2), 1)
        for i, slot in enumerate(self):
            image.blit(slot.btn.image, (4 + 7, 4 + i * 46 + 7))
        self.image = YScrollableImage(image, image.get_height() * 2, int(image.get_height() / 8))
        self.image.fullscroll_down()

    def draw(self, sub):
        sub.blit(self.image.subsurface((0, self.image.step, 54, self.rect_inventory.h)),
                 self.rect_inventory.topleft)


class Hotbar(list):
    def __init__(self, *cols):
        """
        Constructeur de Hotbar
        Un Slot/Col fait 46 px de large
        Son image cree un contour de 4 px
        :param cols: Les cols de la hotbar
        """
        width_edge = 4
        width_slot = 46
        list.__init__(self, cols)
        self.selected_col = cols[0]
        for i, col in enumerate(cols):
            col.num = i
            col.rect_slot.left = 20 + 4 + i * 46
            col.rect_inventory.left = 20 + i * 46
            for slot in col:
                slot.btn.rect.left = 4 + i * 46

        self.rect = pygame.Rect(20, 0, len(cols) * width_slot + width_edge * 2, width_slot + width_edge * 2)
        self.rect_slots = pygame.Rect(20 + width_edge, 0, len(cols) * width_slot, width_slot)
        self.sub = pygame.Surface((20 + self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.sub.fill((0, 0, 0, 0))

        # Creation self.image et self.selected_slot_image
        self.image = pygame.Surface(self.rect.size)
        self.image.fill((192, 192, 192))
        for i in range(4):  # Blit un rect d'epaisseur 4
            pygame.draw.rect(self.image, (51, 51, 51), (i, i, self.rect.w - i*2, self.rect.h - i*2), 1)
        self.selected_slot_image = pygame.Surface((self.rect.h, self.rect.h), pygame.SRCALPHA)
        self.selected_slot_image.fill((0, 0, 0, 0))
        for i in range(6):
            pygame.draw.rect(self.selected_slot_image, (26, 26, 26), (i, i, self.rect.h - i*2, self.rect.h - i*2), 1)

    def set_top(self, top):
        self.rect.top = top
        self.rect_slots.top = top + 4
        for col in self:
            col.rect_slot.top = top + 4
            col.rect_inventory.top = self.rect.top - col.rect_inventory.h + 4
            for slot in col:
                slot.btn.rect.top = top + 4
    top = property(lambda self: self.rect.top, set_top)

    def draw(self, sub):
        """
        Methode qui affiche l'integralite de la hotbar
        :param sub: La surface sur laquelle est affichee la hotbar
        :return: None
        """
        self.sub.blit(self.image, (20, 0))
        for col in self:
            for slot in col:
                if slot.btn.name == col.selected_slot.btn.name:
                    self.sub.blit(slot.btn.image, (col.rect_slot.left + 7, 7 + 4))

            # Affichage selected btn
            if col.num == self.selected_col.num:
                self.sub.blit(self.selected_slot_image, (col.rect_slot.left - 4, 0))
        sub.blit(self.sub, (0, self.rect.top))


class Maping:
    def __init__(self):
        """
        Constructeur de Maping
        """
        self.grp_btn = [BoutonText(30, 30, "MENU", "menu")]
        self.btn_select = None
        self.grp_btn_hotbar = pygame.sprite.Group()
        self.grp_btn_right_clic = pygame.sprite.Group()
        self.right_clic_big_rect = None
        self.right_clic_lit_rect = None    # REVOIR POSITIONS BOUTONS de RightClic
        self.lines_clic_droit = [0, 0, 0, 0]
        self.focus = "Free"  # Permet de savoir quel element monopolise les evenements
        self.hover = ""  # Permet de savoir sur quel element se trouve la souris
        self.operation = None  # Permet de savoir si on est en train d'ajouter ou de supprimer des blocs

        # color_selected_pers = color du player, est en cours de deplacement
        self.color_selected_pers = None
        self.player_places = []

        # Barre d'acces au btn_bloc
        space = 14
        slot_place = 32 + space
        self.hotbar = Hotbar(Col(Slot(space + slot_place * 0, space + slot_place * 0, im.bloc, "bloc")),

                             Col(Slot(space + slot_place * 1, space + slot_place * 0, im.get_bloc("1110"), "esUL"),
                                 Slot(space + slot_place * 1, space + slot_place * 1, im.get_bloc("1011"), "esDR"),
                                 Slot(space + slot_place * 1, space + slot_place * 2, im.get_bloc("1101"), "esUR"),
                                 Slot(space + slot_place * 1, space + slot_place * 3, im.get_bloc("0111"), "esDL")),

                             Col(Slot(space + slot_place * 2, space + slot_place * 0, im.get_bloc("1100"), "dalU"),
                                 Slot(space + slot_place * 2, space + slot_place * 1, im.get_bloc("0011"), "dalD"),
                                 Slot(space + slot_place * 2, space + slot_place * 2, im.get_bloc("1010"), "dalL"),
                                 Slot(space + slot_place * 2, space + slot_place * 3, im.get_bloc("0101"), "dalR")),

                             Col(Slot(space + slot_place * 3, space + slot_place * 0, im.slimeblock, "slim")),

                             Col(Slot(space + slot_place * 4, space + slot_place * 0, im.jumper[0], "jump"),
                                 Slot(space + slot_place * 4, space + slot_place * 1, im.gravitor[0], "grav")),

                             Col(Slot(space + slot_place * 5, space + slot_place * 0, im.axel_left[0], "axlL"),
                                 Slot(space + slot_place * 5, space + slot_place * 1, im.axel_right[0], "axlR")),

                             Col(Slot(space + slot_place * 6, space + slot_place * 0, im.poseur_btn, "pieg"))
                             )
        self.selected_btn = self.hotbar[0][0].btn

    def place_btn(self):
        """
        Methode qui place les boutons de modifications et le bouton pour la fen MENU
        :return: None
        """
        self.hotbar.top = jeu.rect_jeu.h + 20
        self.selected_btn = self.hotbar[0][0].btn
        self.right_clic_big_rect = pygame.Rect(0, 0, jeu.act_ter.col * 8 + 120, jeu.act_ter.row * 8 + 120)
        self.right_clic_lit_rect = pygame.Rect(0, 0, jeu.act_ter.col * 8 + 40, jeu.act_ter.row * 8 + 40)

    def run(self):
        """
        Methode qui gere la boucle principale de MAPING
        :return: None
        """
        self.place_btn()
        self.set_player_places()

        for pers in jeu.grp_pers:
            pers.rect.topleft = jeu.act_ter.position[pers.color]

        while jeu.open == "maping":
            self.react_event()

            # Animations col de hotbar
            for col in self.hotbar:
                if col.is_open:
                    if not col.image.is_up():
                        col.image.scroll_up()
                else:
                    if not col.image.is_down():
                        col.image.scroll_down()

            self.blit_all()

        jeu.act_ter.save_img()
        jeu.act_ter.create_ptt_ter()
        jeu.act_ter.sauvegarder()
        jeu.act_ter.find_cases_libres()

    def react_event(self):
        """
        Methode qui reagit aux entrees de l'admin
        :return: None
        """
        admin.update()
        if admin.key_down == pygame.K_ESCAPE:
            jeu.open = False
        elif admin.key_down == pygame.K_RETURN:
            jeu.open = "play"

        if admin.mouse_moving:
            self.react_mouse_moving()

        if jeu.rect_tot.collidepoint(admin.mouse_pos):
            if admin.mouse_button_down:
                self.clic(admin.mouse_button_down)
            if admin.joystick_button_down == 0:
                self.clic(1)
            elif admin.joystick_button_down == 10:
                self.clic(2)
            elif admin.joystick_button_down == 2:
                self.clic(3)
            elif admin.joystick_button_down == 3:
                self.clic(4)
            elif admin.joystick_button_down == 1:
                self.clic(5)

            # Unclick du clic gauche
            if admin.mouse_button_up == 1 or admin.joystick_button_up == 0:
                if self.focus != "RightClic":
                    self.focus = "Free"

    def clic(self, btn=1):
        """
        Definit les fonctions a operer selon chaque evenement de la souris
        Le parametre btn est necessaire afin de permettre un clic avec une manette
        :param btn: Le bouton appuye
        :return: None
        """
        pos = admin.mouse_pos
        pos2 = (pos[0] - 200, pos[1])
        clic = pygame.Rect(arrondir(pos[0]), arrondir(pos[1]), 32, 32)
        clic2 = pygame.Rect(arrondir(pos2[0]), arrondir(pos2[1]), 32, 32)

        # Clic gauche
        if btn == 1:
            # Clic dans le RightClic
            if self.hover == "RightClic":
                for btn in self.grp_btn_right_clic:
                    if btn.rect.collidepoint(pos2):
                        self.react_btn_right_clic(btn.name)
                        self.hover = "Map"

            # Clic sur un PlayerPlacement
            elif self.hover == "PlayerPlacement":
                for pers in jeu.grp_pers:
                    if clic2.colliderect(pers.rect):
                        self.color_selected_pers = pers.color

            # Clic sur la map
            elif self.hover == "Map":
                self.operation = "adding" if jeu.act_ter.grid[int(pos2[1] / 32)][
                                                int(pos2[0] / 32)] == "vide" else "removing"
                if self.operation == "removing":
                    rect_pos = pygame.Rect(arrondir(pos2[0]), arrondir(pos2[1]), 32, 32)
                    for grp in jeu.act_ter.grp_bloc, jeu.act_ter.grp_bloc_effet:
                        for bloc in grp:
                            if bloc.rect.colliderect(rect_pos):
                                grp.remove(bloc)
                                jeu.act_ter.grid[int(bloc.rect.top / 32)][
                                    int(bloc.rect.left / 32)] = "vide"
                                if bloc.name == "pieg":
                                    for poseur in jeu.act_ter.grp_poseur:
                                        if poseur.rect_bonus.bottomleft == bloc.rect.topleft:
                                            jeu.act_ter.grp_poseur.remove(poseur)
                elif jeu.act_ter.grid[int(pos2[1] / 32)][int(pos2[0] / 32)] == "vide":
                    # Modif de ter.grp_bloc
                    jeu.act_ter.ajout(self.selected_btn.name, arrondir(pos2[0]), arrondir(pos2[1]))
                    # Modif de ter.grid
                    jeu.act_ter.grid[int(pos2[1] / 32)][int(pos2[0] / 32)] = self.selected_btn.name

            # Clic dans la colonne de boutons de menus ColBtn
            elif self.hover == "ColBtn":
                # Boutons de changement de fen
                for btn in self.grp_btn:
                    if btn.rect.colliderect(clic):
                        jeu.open = btn.reponse
                        self.btn_select = btn

            # Clic sur Hotbar ou sur un inventaire
            elif self.hover == "Hotbar":
                # Hotbar
                pos3 = (pos[0] - self.hotbar.rect.left, pos[1] - self.hotbar.rect.top)
                for col in self.hotbar:
                    for slot in col:
                        if slot.rect.collidepoint(pos3):
                            self.selected_btn = slot.btn
                            self.hotbar.selected_col = col
                            col.selected_slot = slot

            self.focus = self.hover

        # Clic de la molette
        elif btn == 2:
            if self.focus == "Free" and self.hover == "Map":
                name_bloc_select = jeu.act_ter.grid[int(pos2[1] / 32)][int(pos2[0] / 32)]
                if name_bloc_select != "vide":
                    for col in self.hotbar:
                        for slot in col:
                            if name_bloc_select == slot.btn.name:
                                self.selected_btn = slot.btn
                                self.hotbar.selected_col = col
                                col.selected_slot = slot
                                break
                """if name_bloc_select != "vide":
                    for slot in self.hotbar:
                        for btn in slot.inventory:
                            if name_bloc_select == btn.name:
                                self.selected_btn = btn
                                self.hotbar.selected_col = col
                                col.selected_slot = slot
                                break"""

        # Clic droit
        elif btn == 3:
            if self.focus == "Free" and self.hover in ("Map", "PlayerPlacement"):
                self.hover = self.focus = "RightClic"

                posx = jeu.act_ter.col * 22 - 40 if pos2[0] > jeu.act_ter.col * 22 - 40 else pos2[0]
                posy = jeu.act_ter.row * 22 - 40 if pos2[1] > jeu.act_ter.row * 22 - 40 else pos2[1]

                self.right_clic_lit_rect.topleft = (posx, posy)
                self.right_clic_big_rect.topleft = (posx - 40, posy - 40)
                jeu.act_ter.create_ptt_ter()

                self.grp_btn_right_clic.empty()
                list_pos = (((self.right_clic_lit_rect.left + 4, self.right_clic_lit_rect.centery - 17, 0),
                             (self.right_clic_lit_rect.left + 4, self.right_clic_lit_rect.centery + 1, 1)),
                            ((self.right_clic_lit_rect.right - 20, self.right_clic_lit_rect.centery - 17, 2),
                             (self.right_clic_lit_rect.right - 20, self.right_clic_lit_rect.centery + 1, 3)),
                            ((self.right_clic_lit_rect.centerx - 17, self.right_clic_lit_rect.top + 4, 4),
                             (self.right_clic_lit_rect.centerx + 1, self.right_clic_lit_rect.top + 4, 5)),
                            ((self.right_clic_lit_rect.centerx - 17, self.right_clic_lit_rect.bottom - 20, 6),
                             (self.right_clic_lit_rect.centerx + 1, self.right_clic_lit_rect.bottom - 20, 7)))
                for l1, l2 in list_pos:
                    self.grp_btn_right_clic.add(BoutonImage(l1[0], l1[1], im.plus_moins[0], l1[2]))
                    self.grp_btn_right_clic.add(BoutonImage(l2[0], l2[1], im.plus_moins[1], l2[2]))

        # Roulement de la molette
        elif btn in (4, 5):
            d = 1 if btn == 5 else -1
            new_slot_num = modulo(self.hotbar.selected_slot.num + d, len(self.hotbar))
            new_slot = self.hotbar[new_slot_num]
            self.hotbar.selected_slot = new_slot
            self.selected_btn = new_slot.selected_btn

    def react_mouse_moving(self):
        """
        Methode qui reagit a un deplacement de la souris
        """
        pos = admin.mouse_pos
        pos2 = (pos[0] - 200, pos[1])
        case2 = pygame.Rect(arrondir(pos2[0]), arrondir(pos2[1]), 32, 32)

        # Perte de focus pour le RightClic
        if self.focus == "RightClic":
            if not self.right_clic_big_rect.collidepoint(pos2):
                self.focus = "Free"

        # Update de hover
        if self.focus == "Free":
            if self.hotbar.rect_slots.collidepoint(pos2):
                self.hover = self.focus = "Hotbar"

            elif jeu.rect_jeu.collidepoint(pos2):
                self.hover = "Map"
                for pers in jeu.grp_pers:
                    if case2.colliderect(pers.rect):
                        self.hover = "PlayerPlacement"
                        self.color_selected_pers = pers.color

            elif jeu.rect_btn.collidepoint(pos):
                self.hover = "ColBtn"

            else:
                self.hover = "EmptySpace"

        # Deplacement d'un placement de player
        if self.focus == "PlayerPlacement":
            case2.size = 64, 64
            case2 = case2.clamp(jeu.rect_jeu)
            # On recherche la place libre la plus proche
            closest_place = self.get_closest_player_place(pos2)
            jeu.act_ter.position[self.color_selected_pers] = closest_place
            perso(self.color_selected_pers).rect.topleft = closest_place  # Utile pour passer de MAPING a PLAY

        # Ouverture / Fermeture des inventaires
        if self.focus == "Hotbar":
            if self.hotbar.rect_slots.collidepoint(pos2):
                for col in self.hotbar:
                    col.is_open = col.rect_slot.collidepoint(pos2)
            else:
                for col in self.hotbar:
                    if col.is_open:
                        col.is_open = col.rect_inventory.collidepoint(pos2)
                        # Quand on quitte la colonne,
                if 1 not in (col.is_open for col in self.hotbar):
                    self.focus = "Free"

        # Ajout / Retrait de bloc
        if self.focus == "Map":
            # removing de bloc
            if self.operation == "removing":
                for grp in jeu.act_ter.grp_bloc, jeu.act_ter.grp_bloc_effet:
                    for bloc in grp:
                        if bloc.rect.colliderect(case2):
                            grp.remove(bloc)
                            jeu.act_ter.grid[int(bloc.rect.top / 32)][
                                int(bloc.rect.left / 32)] = "vide"
                            if bloc.name == "pieg":
                                for poseur in jeu.act_ter.grp_poseur:
                                    if poseur.rect_bonus.bottomleft == bloc.rect.topleft:
                                        jeu.act_ter.grp_poseur.remove(poseur)
            # adding de bloc
            elif jeu.act_ter.grid[int(pos2[1] / 32)][int(pos2[0] / 32)] == "vide":
                if True not in (pers.rect.colliderect(case2) for pers in jeu.grp_pers):
                    jeu.act_ter.ajout(self.selected_btn.name, arrondir(pos2[0]), arrondir(pos2[1]))
                    jeu.act_ter.grid[int(pos2[1] / 32)][int(pos2[0] / 32)] = self.selected_btn.name

    def blit_all(self):
        """
        Methode qui gere tous les affichages
        :return: None
        """

        print(self.focus)

        pos = admin.mouse_pos
        pos2 = (pos[0] - 200, pos[1])
        case2 = pygame.Rect(arrondir(pos2[0]), arrondir(pos2[1]), 32, 32)
        red_rect = pygame.Surface((32, 32), pygame.SRCALPHA)
        red_rect.fill((255, 0, 0, 128))

        # Affichage ecran de jeu
        ecran.blit(im.fond_ground, (0, 0))
        ecran.blit(jeu.act_ter.background, (0, 0))
        jeu.act_ter.grp_bloc.draw(ecran)
        for bloc in jeu.act_ter.grp_bloc_effet:
            ecran.blit(bloc.image[0], bloc.rect.topleft)

        # Affichage places libres pour positionnement des player
        if pygame.key.get_pressed()[pygame.K_TAB]:
            x_bloc = y_bloc = 0
            for cases in self.player_places:
                for case in cases:
                    if not case:
                        color = (0, 0, 0)
                    else:
                        color = (128, 128, 128)
                    pygame.draw.rect(ecran, color, (x_bloc, y_bloc, 32, 32))
                    x_bloc += 32
                y_bloc += 32
                x_bloc = 0

            # Affichage de carres en haut a gauche de chaque player
            for pers in jeu.grp_pers:
                color = (0, 255, 0) if pers.color == 0 else (255, 0, 0) if pers.color == 1 else (0, 0, 255)
                pygame.draw.rect(ecran, color, (arrondir(pers.left), arrondir(pers.rect.top), 32, 32))

        else:
            for pers in vert, rouge, bleu:
                ecran.blit(pers.image[1][0], jeu.act_ter.position[pers.color])
            if self.hover == "PlayerPlacement":
                ecran.blit(im.pers_vise, jeu.act_ter.position[self.color_selected_pers])

        # Affichage hotbar
        for col in self.hotbar:
            if not col.is_open and col.image.is_down() is False:  # Quand la colonne descend
                col.draw(ecran)
        if self.focus == "Hotbar":
            for col in self.hotbar:
                if col.is_open:  # Quand la colonne monte ou est au max
                    col.draw(ecran)
            for btn in self.grp_btn_hotbar:
                if btn.rect.collidepoint(pos2):
                    ecran.blit(im.bloc_vise, btn.rect.topleft)
        self.hotbar.draw(ecran)

        # Affichage bloc_vise
        if self.focus == "Free" and self.hover == "Map":
            ecran.blit(im.bloc_vise, (arrondir(pos2[0]), arrondir(pos2[1])))
            ecran.blit(red_rect, case2.topleft)

        # Affichage fen right clic
        if self.focus == "RightClic":
            ecran.blit(jeu.act_ter.cadre_maping, self.right_clic_lit_rect.topleft)
            ecran.blit(jeu.act_ter.ptt_ter.image, (self.right_clic_lit_rect.left + 20, self.right_clic_lit_rect.top + 20))
            self.grp_btn_right_clic.draw(ecran)

        # On deplace tout l'ecran pour afficher la colonne de boutons
        ecran.scroll(200)

        # Affichage colonne de boutons
        ecran.blit(im.btn_column, (0, 0))
        for btn in self.grp_btn:
            btn.draw(ecran)
            if btn.rect.collidepoint(pos):
                ecran.blit(im.cadre_btn_touch, btn.rect.topleft)
                if self.btn_select:
                    if btn.name == self.btn_select.name:
                        ecran.blit(im.cadre_btn_select, btn.rect.topleft)
                        self.btn_select = None

        pygame.display.flip()
        jeu.horloge.tick(jeu.fps)

    def react_btn_right_clic(self, x):
        """
        Methode qui reagit a un clic sur l'un des boutons de right clic
        Appelee dans clic()
        :param x: Le bouton qui a ete presse
        :return: None
        """
        if x == 6:
            jeu.act_ter.grid.append(["vide"] * jeu.act_ter.col)
            jeu.act_ter.row += 1
            self.modif_dim_ter(0, 0, 0, 32)
        elif x == 7 and len(jeu.act_ter.grid) > 2:
            jeu.act_ter.grid.pop(-1)
            jeu.act_ter.row -= 1
            for grp in jeu.act_ter.grp_bloc_effet, jeu.act_ter.grp_bloc:
                for bloc in grp:
                    if bloc.rect.top >= jeu.act_ter.row * 32:
                        grp.remove(bloc)
            self.modif_dim_ter(0, 0, 0, -32)
        elif x == 5 and len(jeu.act_ter.grid) > 2:
            jeu.act_ter.grid.pop(0)
            jeu.act_ter.row -= 1
            for grp in jeu.act_ter.grp_bloc_effet, jeu.act_ter.grp_bloc:
                for bloc in grp:
                    if bloc.rect.top < 32:
                        grp.remove(bloc)
            self.modif_dim_ter(0, -32, 0, 0)
        elif x == 4:
            jeu.act_ter.grid.insert(0, ["vide"] * jeu.act_ter.col)
            jeu.act_ter.row += 1
            self.modif_dim_ter(0, 32, 0, 0)

        if x == 2:
            for ligne in jeu.act_ter.grid:
                ligne.append("vide")
            jeu.act_ter.col += 1
            self.modif_dim_ter(0, 0, 32, 0)
        elif x == 3 and len(jeu.act_ter.grid[0]) > 12:
            for ligne in jeu.act_ter.grid:
                ligne.pop(-1)
            jeu.act_ter.col -= 1
            for grp in jeu.act_ter.grp_bloc_effet, jeu.act_ter.grp_bloc:
                for bloc in grp:
                    if bloc.rect.left >= jeu.act_ter.col * 32:
                        grp.remove(bloc)
            self.modif_dim_ter(0, 0, -32, 0)
        elif x == 1 and len(jeu.act_ter.grid[0]) > 12:
            for ligne in jeu.act_ter.grid:
                ligne.pop(0)
            jeu.act_ter.col -= 1
            for grp in jeu.act_ter.grp_bloc_effet, jeu.act_ter.grp_bloc:
                for bloc in grp:
                    if bloc.rect.left < 32:
                        grp.remove(bloc)
            self.modif_dim_ter(-32, 0, 0, 0)
        elif x == 0:
            for ligne in jeu.act_ter.grid:
                ligne.insert(0, "vide")
            jeu.act_ter.col += 1
            self.modif_dim_ter(32, 0, 0, 0)

    def modif_dim_ter(self, x1, y1, x2, y2):
        """
        Methode qui appelle jeu.act_ter.redimensionner()
        :param x1: Ajouter/Supprimer une colonne a gauche
        :param y1: Ajouter/Supprimer une ligne en haut
        :param x2: Ajouter/Supprimer une colonne a droite
        :param y2: Ajouter/Supprimer une ligne en bas
        :return: None
        """
        jeu.act_ter.redimensionner(x1, y1, x2, y2)
        self.set_player_places()
        self.focus = "Free"

        # Besoin de changer ca
        try:
            pygame.display.set_mode((max(jeu.act_ter.col * 32, 1280), max(jeu.act_ter.row * 32 + 90, 750)),
                                    fullscreen)
        except pygame.error:
            pygame.display.set_mode((max(jeu.act_ter.col * 32, 1280), max(jeu.act_ter.row * 32 + 90, 750)))

    def set_player_places(self):
        """
        Methode qui initialise self.player_places
        :return: None
        """
        self.player_places = []
        for i in range(jeu.act_ter.row):
            self.player_places.append([0] * jeu.act_ter.col)

        # Recherche des espaces libres
        for i in range(jeu.act_ter.row - 1):
            for j in range(jeu.act_ter.col - 1):
                if jeu.act_ter.grid[i][j] in jeu.non_solid_blocs and \
                                jeu.act_ter.grid[i+1][j] in jeu.non_solid_blocs and \
                                jeu.act_ter.grid[i][j+1] in jeu.non_solid_blocs and \
                                jeu.act_ter.grid[i+1][j+1] in jeu.non_solid_blocs:
                    self.player_places[i][j] = 1

    def get_closest_player_place(self, pos):
        """
        Methode qui trouve la place disponible la plus proche de pos
        :param pos: La position de la souris
        :return: La place disponible pour un player la plus proche de pos
        """
        closest_place = None
        dis_closest_place = math.inf
        for i in range(jeu.act_ter.row - 1):
            for j in range(jeu.act_ter.col - 1):
                if self.player_places[i][j]:
                    i2, j2 = i*32, j*32
                    pos_place = (j2+32, i2+32)
                    dis = distance_pnts(pos_place, pos)
                    if dis < dis_closest_place:
                        dis_closest_place = dis
                        closest_place = (j2, i2)
        return closest_place


class Choose:
    def __init__(self):

        self.grp_btn = [BoutonText(30, 30, "JOUER", "play"),
                        BoutonText(30, 80, "MENU", "menu")]
        self.name_btn_select = None

    def run(self):

        while jeu.open == "choose":
            self.react_event()

            # Animation
            for pers in jeu.grp_pers:
                if pers.tps_recharg_changement_type:
                    pers.tps_recharg_changement_type -= 1
                    pers.gros.scroll((pers.anc_type - pers.type) * 12)
                    if not pers.tps_recharg_changement_type:
                        pers.sub_gros = pers.gros.subsurface(240, 0, 120, 120)
                if not pers.ia:
                    if not pers.tps_recharg_changement_type:
                        if round(pers.input.get_axis(2)):
                            pers.changer_type(pers.type + round(pers.input.get_axis(2)))

            self.blit_all()

    def react_event(self):
        admin.update()
        if admin.joystick_button_down == 0 or admin.mouse_button_down == 1:
            self.clic()

        if admin.key_down == pygame.K_ESCAPE:
            jeu.open = False
        elif admin.key_down == pygame.K_RETURN:
            jeu.open = "play"

    def clic(self):
        pos = admin.mouse_pos
        for btn in self.grp_btn:
            if btn.rect.collidepoint(pos):
                jeu.open = btn.reponse
        for (pers, x) in zip((vert, rouge, bleu), range(190, 190 + 451, 225)):
            if not pers.tps_recharg_changement_type:
                for x2 in (3, 160):
                    if x + x2 <= pos[0] <= x + x2 + 37 and 28 <= pos[1] <= 28 + 154:
                        if x2 == 3:
                            pers.changer_type(pers.type - 1)
                        else:
                            pers.changer_type(pers.type + 1)

    def blit_all(self):
        pos = admin.mouse_pos
        ecran.blit(im.fond_ground, (0, 0))
        ecran.blit(im.btn_column, (0, 0))
        for btn in self.grp_btn:
            btn.draw(ecran)
            if btn.rect.collidepoint(pos):
                if btn.name == self.name_btn_select:
                    ecran.blit(im.cadre_btn_select, btn.rect.topleft)
                    self.name_btn_select = None
                ecran.blit(im.cadre_btn_touch, btn.rect.topleft)

        y = 25
        for (pers, x) in zip((vert, rouge, bleu), range(200 + y, (200 + y) * 3 + 1, 200 + y)):
            ecran.blit(im.cadre_pers, (x, y))
            ecran.blit(pers.sub_gros, (40 + x, 20 + y))
            ecran.blit(im.fleche_noire[0], (10 + x, 65 + y))
            ecran.blit(im.fleche_noire[1], (172 + x, 65 + y))
            for x2 in (3, 160):
                if x + x2 <= pos[0] <= x + x2 + 37 and y + 3 <= pos[1] <= y + 3 + 154:
                    voile = pygame.Surface((37, 154), pygame.SRCALPHA)
                    a = 64 if admin.mouse_button_is_pressed[0] else 32
                    voile.fill((a, a, a, a))
                    ecran.blit(voile, (x + x2, y + 3), special_flags=pygame.BLEND_RGBA_SUB)
            ecran.blit(im.cadre_stat, (75 + x, 178 + y))
            ecran.blit(im.cadre_stat, (75 + x, 218 + y))
            ecran.blit(im.coeur, (35 + x, 180 + y))
            ecran.blit(im.eclair, (35 + x, 220 + y))
            pygame.draw.rect(ecran, (255, 255, 0), (77 + x, 180 + y, 81 * pers.vie / 100, 30))
            pygame.draw.rect(ecran, (255, 255, 0), (77 + x, 220 + y, 81 * pers.vitesse / 6, 30))
            msg = "Missile" if pers.type == 0 else "Bombe" if pers.type == 1 else "Glace"
            ecran.blit(im.gros_attak[pers.type], (40 + x, 260 + y))
            ecran.blit(font.render(30, msg, 1, (0, 0, 0)), (35 + x, 350 + y))

        pygame.display.update()

    @staticmethod
    def changer(fen):
        for pers in jeu.grp_pers:
            while pers.tps_recharg_changement_type:
                pers.tps_recharg_changement_type -= 1
                if not pers.tps_recharg_changement_type:
                    pers.sub_gros = pers.gros.subsurface(240, 0, 120, 120)
                pers.gros.scroll((pers.anc_type - pers.type) * 12)
        if fen == "MENU":
            jeu.open = "menu"
            for pers in jeu.grp_pers:
                pers.reinit()
        elif fen == "JOUER":
            jeu.open = "play"


class Mini:
    def __init__(self):

        self.papy = Papy(700, 500)
        self.grp_papy = pygame.sprite.Group()
        self.grp_papy.add(self.papy)
        self.grp_btn = [BoutonText(30, 30, "MENU", "menu"),
                        BoutonText(30, 80, "JOUER", "mini")]
        self.name_btn_select = None

    def run(self):

        while jeu.open == "mini":

            self.react_event()

            self.papy.updt()

            self.blit_all()

    def react_event(self):
        admin.update()
        if admin.joystick_button_down == 0 or admin.mouse_button_down == 1:
            self.clic()

        if admin.key_down == pygame.K_ESCAPE:
            jeu.open = False
        elif admin.key_down == pygame.K_RETURN:
            jeu.open = "menu"

        k = pygame.key.get_pressed()
        self.papy.dy = k[pygame.K_s] - k[pygame.K_z]
        self.papy.dx = k[pygame.K_d] - k[pygame.K_q]

    def clic(self):
        pos = admin.mouse_pos
        for btn in self.grp_btn:
            if btn.rect.collidepoint(pos):
                jeu.open = btn.reponse
                self.name_btn_select = btn.name

    def blit_all(self):
        pos = admin.mouse_pos
        ecran.blit(im.fond_ground, (0, 0))
        ecran.blit(im.btn_column, (0, 0))
        for btn in self.grp_btn:
            btn.draw(ecran)
            if btn.rect.collidepoint(pos):
                if btn.name == self.name_btn_select:
                    ecran.blit(im.cadre_btn_select, btn.rect.topleft)
                    self.name_btn_select = None
                ecran.blit(im.cadre_btn_touch, btn.rect.topleft)
        self.grp_papy.draw(ecran)
        pygame.draw.line(ecran, (255, 0, 0), self.papy.rect.center,
                         (self.papy.rect.centerx + self.papy.dx * 64, self.papy.rect.centery + self.papy.dy * 64), 3)
        pygame.display.flip()

    @staticmethod
    def changer(fen):
        if fen == "MENU":
            jeu.open = "menu"


def perso(color):
    return jeu.grp_pers.sprites()[modulo(color, 3)]

def libre(x, y):
    return ter.cases_libres[y][x] in (0, 2)


# Initialisation


jeu = Game()

while jeu.open:
    if jeu.open == "menu":
        jeu.menu.run()
    elif jeu.open == "choose":
        jeu.choose.run()
    elif jeu.open == "play":
        jeu.play.run()
    elif jeu.open == "mini":
        jeu.mini.run()
    elif jeu.open == "maping":
        jeu.maping.run()

jeu.save_infos()
pygame.quit()
