# -*- coding: utf-8 -*

import pygame
import random
import math


class MissileChemin:
    def __init__(self, pos_dep, pos_arr, grid):
        self.pos_arr = pos_arr
        self.pos_dep = pos_dep
        self.chemin = [self.pos_arr]
        self.grid = []
        for y in range(len(grid)):
            self.grid.append([-1] * len(grid[0]))
            for x in range(len(grid[0])):
                if grid[y][x] in ("vide", "axel", "jump"):
                    self.grid[y][x] = 0
        self.grid[self.pos_dep[1]][self.pos_dep[0]] = 1

        run = True if self.pos_arr[1] >= 0 else False
        self.reussite = False
        num = 1
        while run:
            action = False
            num += 1
            for y in range(len(self.grid)):
                for x in range(len(self.grid[y])):
                    if self.grid[y][x] == num - 1:
                        for (i, j) in (0, 1), (1, 0), (0, -1), (-1, 0):
                            if 0 <= y + j < len(self.grid) and 0 <= x + i < len(self.grid[0]):
                                if not self.grid[y + j][x + i]:
                                    self.grid[y + j][x + i] = num
                                    action = True
            if not action:
                run = False
                self.reussite = False
            elif self.grid[self.pos_arr[1]][self.pos_arr[0]]:
                run = False
                self.reussite = True

        if self.reussite:
            pnt = self.pos_arr
            case = math.inf
            while pnt != self.pos_dep:
                (x, y) = pnt

                for (i, j) in (0, 1), (1, 0), (0, -1), (-1, 0):
                    if 0 <= y + j < len(self.grid) and 0 <= x + i < len(self.grid[0]):
                        if 0 < self.grid[y + j][x + i] < case:
                            case = self.grid[y + j][x + i]
                            pnt = (x + i, y + j)
                for (i, j) in (1, 1), (1, -1), (-1, -1), (-1, 1):
                    if 0 <= y + j < len(self.grid) and 0 <= x + i < len(self.grid[0]):
                        if 0 < self.grid[y + j][x] and 0 < self.grid[y][x + i] and 0 < self.grid[y + j][x + i] < case:
                            case = self.grid[y + j][x + i]
                            pnt = (x + i, y + j)

                self.chemin.append(pnt)

        """self.ecran = pygame.display.set_mode((len(grid[0])*32, len(grid)*32))
        self.pause()
        pygame.display.set_mode((len(grid[0])*32, len(grid)*32 + 90))

    def pause(self):
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.grid[y][x] >= 0:
                    c = self.grid[y][x]
                    pygame.draw.rect(self.ecran, (255-c*6, 255-c*6, 255-c*6), (x*32, y*32, 32, 32))
        d = 0
        for pnt in self.chemin:
            pygame.draw.rect(self.ecran, (255-d*6, 0, 0), (pnt[0]*32, pnt[1]*32, 32, 32))
            d += 1

        pygame.display.flip()
        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    run = False"""


class Images:

    def __init__(self):

        self.game_icon = pygame.image.load("Images/Blocs/stonebrick.png")

        # Fonds
        self.landscape = pygame.image.load("Images/fond ecran.png").convert()
        self.fond_ground = pygame.image.load("Images/fond ground.png").convert()
        self.fond_btn = self.fond_ground.subsurface(0, 0, 960, 90)
        self.wallpaper = 1

        # Cadres
        self.cadre = pygame.image.load("Images/Cadres/cadre.png").convert_alpha()
        self.cadre_pers = pygame.image.load("Images/Cadres/choix personnage.png").convert_alpha()
        self.cadre_bloc = pygame.image.load("Images/Cadres/bloc.png").convert_alpha()
        self.cadre_btn = pygame.image.load("Images/Cadres/bouton.png").convert_alpha()
        self.cadre_btn_select = pygame.image.load("Images/Cadres/bouton select.png").convert_alpha()
        self.cadre_btn_touch = pygame.image.load("Images/Cadres/bouton touch.png").convert_alpha()
        self.cadre_resultats = pygame.image.load("Images/Cadres/resultats.png").convert_alpha()
        self.cadre_delete = pygame.image.load("Images/Cadres/delete.png").convert_alpha()

        # Boutons
        self.btn_column = pygame.image.load("Images/buttons column.png")

        # Blocs
        self.bloc = pygame.image.load("Images/Blocs/stonebrick.png").convert()
        self.corner_blocs = [self.bloc.subsurface(pygame.Rect(x, y, 16, 16))
                             for x, y in ((0, 0), (16,  0), (0, 16), (16, 16))]
        self.slabs = [self.bloc.subsurface(pygame.Rect(0, y, 32, 16))
                      for y in (0, 16)]
        self.slides = [self.bloc.subsurface(pygame.Rect(x, 0, 16, 32))
                       for x in (0, 16)]
        self.slimeblock = pygame.image.load("Images/Blocs/slimeblock.png").convert()
        self.poseur = pygame.image.load("Images/Blocs/poseur de bonus.png").convert_alpha()
        self.poseur_btn = pygame.Surface((32, 32)).convert_alpha()
        self.poseur_btn.fill((0, 0, 0, 0))
        self.poseur_btn.blit(self.poseur, (0, 16))
        bonus = pygame.image.load("Images/Blocs/bonus.png").convert_alpha()
        self.bonus = [[bonus.subsurface(0, y * 48, 240, 48).subsurface(48 * x, 0, 48, 48)
                       for x in range(5)] for y in range(3)]
        animated_blocs = pygame.image.load("Images/Blocs/animated blocs.png").convert()
        self.jumper = [animated_blocs.subsurface(32*x, 0, 32, 32) for x in range(16)]
        self.gravitor = [animated_blocs.subsurface(32*x, 32, 32, 32) for x in range(16)]
        self.axel_left = [animated_blocs.subsurface(32*x, 64, 32, 32) for x in range(16)]
        self.axel_right = [animated_blocs.subsurface(32*x, 96, 32, 32) for x in range(16)]

        # Players
        team_gros = pygame.image.load("Images/Perso/team gros.png").convert_alpha()
        team_sprinter = pygame.image.load("Images/Perso/team sprinter.png").convert_alpha()
        team_fighter = pygame.image.load("Images/Perso/team fighter.png").convert_alpha()
        team_tank = pygame.image.load("Images/Perso/team tank.png").convert_alpha()
        self.sprinter = [team_sprinter.subsurface(0, 104*x, 160, 104) for x in range(3)]
        self.fighter = [team_fighter.subsurface(0, 96*x, 240, 96) for x in range(3)]
        self.tank = [team_tank.subsurface(0, 120*x, 224, 120) for x in range(3)]
        self.gros = [team_gros.subsurface(0, 120*x, 600, 120) for x in range(3)]
        anim_pers = pygame.image.load("Images/Perso/Animation_pers.png").convert_alpha()
        self.anim_degat = [anim_pers.subsurface(60 * 0, 0, 40 * 4, 52 * 2),
                           anim_pers.subsurface(60 * 4, 0, 60 * 4, 48 * 2),
                           anim_pers.subsurface(60 * 8, 0, 56 * 4, 60 * 2)]
        for list_img in self.sprinter, self.fighter, self.tank, self.anim_degat:
            for i in range(len(list_img)):
                (w, h) = (int(list_img[i].get_size()[0]/4), int(list_img[i].get_size()[1]/2))
                list_img[i] = dict([(direction, [list_img[i].subsurface(x, y, w, h) for x in range(0, w * 4, w)])
                                    for direction, y in zip((-1, 1), range(0, h * 2, h))])
        self.type = [self.sprinter, self.fighter, self.tank]
        fleches = pygame.image.load("Images/Perso/fleches.png").convert_alpha()
        self.fleches = [fleches.subsurface(32*x, 0, 32, 32) for x in range(3)]
        shield = pygame.image.load("Images/Perso/shield.png").convert_alpha()
        self.shield = [[shield.subsurface(0, y * 84, 1680, 84).subsurface(84 * x, 0, 84, 84)
                        for x in range(20)] for y in range(3)]

        # Attaques petites
        attak = pygame.image.load("Images/Perso/attak.png").convert_alpha()
        self.attak = [[attak.subsurface(0, y * 20, 80, 20).subsurface(20*x, 0, 20, 20)
                       for x in range(4)] for y in range(3)]
        expl = pygame.image.load("Images/Perso/explosions attak.png")
        self.expl = [[expl.subsurface(0, y * 38, 300, 38).subsurface(37*x, 0, 37, 37)
                      for x in range(8)] for y in range(3)]

        # Attaques speciales
        missile = pygame.image.load("Images/Attaques/missile.png").convert_alpha()
        self.missile = dict([(direction, missile.subsurface(24*x, 0, 24, 24))
                             for direction, x in zip(range(0, 360, 45), range(8))])
        expl_missile = pygame.image.load("Images/Attaques/explosion missile.png").convert_alpha()
        self.expl_missile = [expl_missile.subsurface(64*x, 0, 64, 64) for x in range(25)]

        self.bombe = pygame.image.load("Images/Attaques/bombe.png").convert_alpha()
        expl_bombe = pygame.image.load("Images/Attaques/explosion bombe.png").convert_alpha()
        self.expl_bombe = [expl_bombe.subsurface(256*x, 0, 256, 256) for x in range(12)]

        self.glacon_pers = pygame.image.load("Images/Attaques/glacon pers.png").convert_alpha()
        self.glacon_attak = pygame.image.load("Images/Attaques/glacon missile.png").convert_alpha()
        expl_glace = pygame.image.load("Images/Attaques/explosion glace.png").convert_alpha()
        self.expl_glace = [expl_glace.subsurface(384 * x, 0, 384, 384) for x in range(19)]

        gros_attak = pygame.image.load("Images/Attaques/gros attaque.png")
        self.gros_attak = [gros_attak.subsurface(x * 80, 0, 80, 80) for x in range(3)]

        # Particules
        self.soin = pygame.image.load("Images/Particules/soin.png").convert_alpha()
        star = pygame.image.load("Images/Particules/star.png").convert_alpha()
        self.star = [star.subsurface(x * 32, 0, 32, 32) for x in range(3)]

        # Menu
        self.ajout_ter = pygame.image.load("Images/Menu/ajout terrain.png").convert_alpha()

        # Choose
        self.cadre_stat = pygame.image.load("Images/Choose/cadre stat.png").convert_alpha()
        self.coeur = pygame.image.load("Images/Choose/coeur.png").convert_alpha()
        self.eclair = pygame.image.load("Images/Choose/eclair.png").convert_alpha()
        fleches = pygame.image.load("Images/Choose/fleches noires.png").convert_alpha()
        self.fleche_noire = [fleches.subsurface(18 * x, 0, 18, 30) for x in range(2)]

        # Maping
        self.bloc_vise = pygame.image.load("Images/Maping/bloc vise.png").convert_alpha()
        self.pers_vise = pygame.image.load("Images/Maping/pers vise.png").convert_alpha()
        plus_moins = pygame.image.load("Images/Maping/plus moins.png").convert_alpha()
        self.plus_moins = [plus_moins.subsurface(x * 16, 0, 16, 16) for x in range(2)]

        # Mini jeu
        self.papy = pygame.image.load("Images/Mini Jeux/Papy.png").convert_alpha()
        (w, h) = (int(self.papy.get_width() / 4), int(self.papy.get_height() / 4))
        self.papy = [([self.papy.subsurface(x, y, w, h) for x in range(0, w * 4, w)]) for y in range(0, h * 4, h)]

    def get_bloc(self, bin_number):
        """
        Methode qui renvoi une image 32*32
        bin_number precise quels corner_blocs doivent etre colles sur cette image
        :param bin_number: str de 4 caracteres, soit "0" soit "1"
        :return: Une image 32*32 constituee de corner_blocs
        """
        surf = pygame.Surface((32, 32)).convert_alpha()
        surf.fill((255, 255, 255, 0))
        for i in range(4):
            if bin_number[i] == "1":
                surf.blit(self.corner_blocs[i], (0 if i%2 == 0 else 16, 0 if i<2 else 16))
        return surf

    @staticmethod
    def changer_couleur(image, dt, ds, dv):
        """
        Change les couleurs d'une image en travaillant sur la teinte, la saturation et la value
        :param image: L'image a modifier
        :param dt: La modification a faire sur la teinte
        :param ds: La modification a faire sur la saturation
        :param dv: La modification a faire sur la value
        :return: L'image avec ses couleurs modifiees
        """
        x = image.get_width()
        y = image.get_height()
        new_image = pygame.Surface((x, y)).convert_alpha()
        new_image.fill((255, 255, 255, 0))

        for i in range(x):
            for j in range(y):
                # On commence par convertir en tsv
                (r, g, b, a) = image.get_at((i, j))
                (t, s, v) = rgb_to_tsv(r, g, b)

                # On fait les modif qu'on veut
                t = (t + dt) % 360    # = (t + dt) mudulo 360
                s = s + ds if s + ds < 255 else 255
                v = v + dv if v + dv < 255 else 255

                # Ensuite on repasse en rgb
                (r, g, b) = tsv_to_rgb(t, s, v)

                new_image.set_at((i, j), (r, g, b, a))
        return new_image

    @staticmethod
    def redimensionner(image, w, h):
        """
        Redimensionne une image aux nouvelles dimensions (w, h)
        La redimension est au pixel par pixel, sans floutage
        :param image: L'image a redimensionner
        :param w: La nouvelle largeur
        :param h: La nouvelle hauteur
        :return: Renvoi l'image redimensionnee
        """
        coef_x = image.get_width()/w
        coef_y = image.get_height()/h
        new_image = pygame.Surface((w, h)).convert_alpha()
        new_image.fill((255, 255, 255, 0))
        for i in range(w):
            for j in range(h):
                new_image.set_at((i, j), image.get_at((int(i*coef_x), int(j*coef_y))))
        return new_image

    @staticmethod
    def rotate(image, angle):  # angle en radian
        x = image.get_width()
        y = image.get_height()
        new_image = pygame.Surface((x, y)).convert_alpha()
        new_image.fill((255, 255, 255, 0))
        o = (x / 2, y / 2)
        o2 = get_proj(o, angle)
        (ox, oy) = (o[0] - o2[0], o[1] - o2[1])
        d = math.sqrt(2)
        for i in range(math.floor(-x*d), math.ceil(x*d)):
            for j in range(math.floor(-y*d), math.ceil(y*d)):
                (x2, y2) = get_proj((i, j), angle)
                if 0 <= x2 < x and 0 <= y2 < y:
                    color = image.get_at((x2, y2))
                    new_image.set_at((round(i+oy), round(j+ox)), color)

        return new_image

    def create_cadre(self, w, h, name=None):
        """
        Cree un cadre de dimension (w, h)
        Si le param name est entre, un png sera sauvegarde dans le dossier Images/Cadres/ sous le nom name
        :param w: The cadre's width
        :param h: The cadre's height
        :param name: Le nom de l'image pour une sauvegarde optionnelle du cadre
        :return: Renvoi le cadre cree
        """
        image = pygame.Surface((w, h)).convert_alpha()
        image.fill((255, 255, 255, 0))

        image.fill((217, 217, 182), (2, 2, w-4, h-4))
        image.blit(self.cadre.subsurface(0, 0, 4, 4), (0, 0))
        image.blit(self.cadre.subsurface(0, 5, 4, 4), (0, h-4))
        image.blit(self.cadre.subsurface(5, 0, 4, 4), (w-4, 0))
        image.blit(self.cadre.subsurface(5, 5, 4, 4), (w-4, h-4))
        for i in range(w-4):
            image.blit(self.cadre.subsurface(2, 0, 1, 3), (i+2, 0))
            image.blit(self.cadre.subsurface(2, 6, 1, 3), (i+2, h-3))
        for j in range(h-4):
            image.blit(self.cadre.subsurface(0, 2, 3, 1), (0, j+2))
            image.blit(self.cadre.subsurface(6, 2, 3, 1), (w-3, j+2))

        if name:
            pygame.image.save(image, "Images/Cadres/" + name + ".png")

        return image

    @staticmethod
    def sub_alpha(img, alpha):
        voile = pygame.Surface(img.get_rect().size, pygame.SRCALPHA)
        voile.fill((0, 0, 0, alpha))
        img.blit(voile, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)


class Bloc(pygame.sprite.Sprite):
    def __init__(self, rect, img, name):
        """
        Bloc's constructor
        :param rect: Le rectangle de collision du bloc
        :param image: L'image du bloc
        :param name: Le nom du bloc
        """
        pygame.sprite.Sprite.__init__(self)
        self.rect = rect
        self.image = img
        self.name = name


class AnimatedBloc(Bloc):
    def __init__(self, x, y, img, name):
        """
        AnimatedBloc's constructor
        :param x: L'abscisse coin topleft du bloc
        :param y: L'ordonnee coin topleft du bloc
        :param image: L'image du bloc
        :param name: Le nom du bloc
        """
        w, h = img[0].get_size()
        Bloc.__init__(self, pygame.Rect(x, y, w, h), img, name)


class StaticBloc(Bloc):
    def __init__(self, x, y, img, name):
        """
        Constructeur de StaticBloc
        :param x: L'abscisse coin topleft du bloc
        :param y: L'ordonnee coin topleft du bloc
        :param image: L'image du bloc
        :param name: Le nom du bloc
        """
        w, h = img.get_size()
        Bloc.__init__(self, pygame.Rect(x, y, w, h), img, name)


class Bouton(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, image, name):
        """
        Constructeur de Bouton
        :param x: L'abscisse coin topleft du bouton
        :param y: L'ordonnee coin topleft du bouton
        :param w: La largeur du bouton
        :param h: La hauteur du bouton
        :param image: L'image du bouton
        :param name: Le nom du bouton
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = pygame.Rect(x, y, w, h)
        self.name = name

    def draw(self, sub):
        """
        Affiche le bouton sur l'ecran sub
        :param sub: L'ecran sur lequel doit etre affiche le bouton
        """
        sub.blit(self.image, self.rect.topleft)

    def move(self, x, y):
        """
        Deplace le bouton
        Utile dans la fenetre Maping
        :param x: Le decalage a faire sur l'axe des x
        :param y: Le decalage a faire sur l'axe des y
        """
        self.rect.left += x
        self.rect.top += y


class BoutonText(Bouton):
    def __init__(self, x, y, name, reponse):
        """
        Constructeur de BoutonText
        :param x: L'abscisse du coin topleft du bouton
        :param y: L'ordonnee du coin topleft du bouton
        :param name: Le nom du bouton
        :param reponse: La reponse a envoyer si l'on clique sur le bouton
        """
        Bouton.__init__(self, x, y, 140, 40, im.cadre_btn, name)

        police = 26
        size_w, size_h = font.get_size(police, name)
        while size_w > self.rect.w - 10:
            police -= 2
            size_w, size_h = font.get_size(police, name)
            if police <= 14:
                break
        self.msg = font.render(police, name, 1, (0, 0, 0))
        self.pos_msg = (self.rect.centerx - size_w / 2, self.rect.centery - size_h / 2)
        self.reponse = reponse

    def draw(self, sub):
        """
        Affiche le bouton sur l'ecran sub
        :param sub: L'ecran sur lequel doit etre affiche le bouton
        """
        super().draw(sub)
        sub.blit(self.msg, self.pos_msg)

    def move(self, x, y):
        """
        Deplace le bouton
        Utile dans la fenetre Maping
        :param x: Le decalage a faire sur l'axe des x
        :param y: Le decalage a faire sur l'axe des y
        """
        super().move(x, y)
        self.pos_msg = (self.pos_msg[0] + x, self.pos_msg[1] + y)


class BoutonImage(Bouton):
    def __init__(self, x, y, image, name):
        """
        Constructeur de BoutonImage
        :param x: L'abscisse du coin topleft du bouton
        :param y: L'ordonnee du coin topleft du bouton
        :param image: L'image du bouton
        :param name: Le nom du bouton
        """
        Bouton.__init__(self, x, y, image.get_width(), image.get_height(), image, name)


class Particle(pygame.sprite.Sprite):

    def __init__(self, x, y, w, h, image, vie):
        """
        Constructeur de Particle
        :param x: L'abscisse du coin topleft de la particule
        :param y: L'ordonnee du coin topleft de la particule
        :param w: La largeur de la particule
        :param h: La hauteur de la particule
        :param image: L'image de la particule
        :param vie: La vie de la particule
        """
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(x, y, w, h)
        self.rect.center = (random.randint(x-10, x+10), random.randint(y-10, y+10))
        self.image = image
        self.vie = vie


class AnimatedParticle(Particle):
    def __init__(self, x, y, image, vie):
        """
        Constructeur de AnimatedParticle
        :param x: L'abscisse du coin topleft de la particule
        :param y: L'ordonnee du coin topleft de la particule
        :param image: L'image de la particule
        :param vie: La vie de la particule
        """
        Particle.__init__(self, x, y, image[0].get_width(), image[0].get_height(), image, vie)


class StaticParticle(Particle):
    def __init__(self, x, y, image, vie):
        """
        Constructeur de StaticParticle
        :param x: L'abscisse du coin topleft de la particule
        :param y: L'ordonnee du coin topleft de la particule
        :param image: L'image de la particule
        :param vie: La vie de la particule
        """
        Particle.__init__(self, x, y, image.get_width(), image.get_height(), image, vie)


class Font:
    def __init__(self):
        """
        Constructeur de Font
        Font est une classe qui contient des polices paires de tailles allant de 14 a 50
        """
        pygame.font.init()
        font_filename = "Polices/Edson_Comics_Bold.ttf"
        self.font = dict([(d, x) for d, x in
                          zip(range(14, 51, 2), (pygame.font.Font(font_filename, x) for x in range(14, 51, 2)))])

    def get_size(self, taille_police, text):
        """
        Methode qui calcule la taille que prendrai un text avec une taille de police donnee
        :param taille_police: La taille de police
        :param text: Le text
        :return: La taille que prendrai text avec la taille de police taille_police
        """
        return self.font[taille_police].size(text)

    def render(self, taille_police, text, antialias, color, background=None):
        """
        Methode qui realise une rendu de text
        :param taille_police: La taille de la police
        :param text: Le texte
        :param antialias: ...
        :param color: La couleur du texte
        :param background: La couleur optionnelle de l'arriere texte
        :return: Renvoi une surface avec le texte imprime dessus
        """
        return self.font[taille_police].render(text, antialias, color, background)


class Pathfinding:
    def __init__(self, ter):
        self.ter = ter.copy()
        scl = 16

        self.v_pers = 6  # Vitesse de l'IA, en nb de px par boucle
        self.v = scl / v_pers / 8  # tps_en_air mit pr se deplacer horizontalement de scl px (15px)

        self.grids = []
        self.add_grid()

    def add_grid(self, acc):
        """Rajoute une grille dans self.grids
        acc permet de savoir combien de ligne rajouter a la fin du terrain
        pour permettre les sauts en dehors de l'ecran"""
        row = int(self.ter.row * 32 / self.scl)
        col = int(self.ter.col * 32 / self.scl)
        grid = [["vide" if self.ter.cases_libres[j][i] == 1 else "bloc" for i in range(col)] for j in range(row)]

        # On rajoute des lignes a la fin pour permettre a l'ia de sauter en dehors de la fenetre
        t_max = acc / 20
        h_max = int(f(-10, acc, 0, t_max) / 16)
        for i in range(h_max):
            grid.append(["vide"] * ter.col * 32 / self.scl)
        self.grids.append(grid)

    def find_path_jump(self, x_dep, y_dep, acceleration, h):
        """Trouve tous les chemins possibles en un saut a partir du pnt donne"""
        acc = acceleration  # 100 pour un jumper, 80 pour un sprinter
        t2 = racine(-10, acc, -h, 1)
        list_pnts_dep = [[x_dep, y_dep, t2, 0]]
        x0, y0, t0, dx0 = list_pnts_dep[0]
        self.add_grid(acc)
        self.grids[-1][y0][x0] = [t0, dx0]


class Vector(list):
    def __init__(self, x, y):
        """
        Cree un vecteur de coord (x, y)
        OU
        Cree un vecteur allant de x a y
        """
        if type(x) in (int, float):
            list.__init__(self, (x, y))
        else:
            list.__init__(self, (y[0] - x[0], y[1] - x[1]))

    def apply_vect(self, vect):
        """
        Methode qui applique a self le vecteur vect multiplie par la longueur coef
        :param vect: le vecteur a appliquer sur self
        :return: None
        """
        for i in range(2):
            self[i] += vect[i]

    def mult(self, scl):
        """
        Methode qui multiplie self par scl
        :param scl: scalaire qui multiplie self
        :return: None
        """
        for i in range(2):
            self[i] *= scl

    def set_x(self, x):
        self[0] = x
    x = property(lambda self: self[0], set_x)

    def set_y(self, y):
        self[1] = y
    y = property(lambda self: self[1], set_y)


class Position(list):
    def __init__(self, x, y=int):
        """
        Cree un point de coord (x, y)
        OU
        Cree un point de coord x[0], x[1]
        """
        if type(x) in (int, float):
            list.__init__(self, (x, y))
        else:
            list.__init__(self, (x[0], x[1]))

    def set_x(self, x):
        self[0] = x
    x = property(lambda self: self[0], set_x)

    def set_y(self, y):
        self[1] = y
    y = property(lambda self: self[1], set_y)


def sign(x):
    """
    Fonction qui renvoit le signe d'un nombre
    :param x: Le nombre dont on cherche le signe
    :return: Le signe de x
    """
    if x >= 0:
        return 1
    elif x < 0:
        return -1

def get_angle(x, y):
    if math.hypot(x, y):
        return sign(y) * math.acos(x / math.hypot(x, y))
    else:
        return 0

def get_proj(pnt, angle):
    return round(pnt[0] * math.cos(angle) - pnt[1] * math.sin(angle)),\
           round(pnt[0] * math.sin(angle) + pnt[1] * math.cos(angle))

def rgb_to_tsv(r, g, b):
    ma = max(r, g, b)
    mi = min(r, g, b)
    if ma == mi:
        t = 0
    elif ma == r:
        t = (60 * (g - b) / (ma - mi)) % 360
    elif ma == g:
        t = 60 * (b - r) / (ma - mi) + 120
    else:
        t = 60 * (r - g) / (ma - mi) + 240
    if ma == 0:
        s = 0
    else:
        s = 1 - mi / ma
    v = ma

    return t, s, v

def tsv_to_rgb(t, s, v):
    ti = int(h / 60) % 6  # = int(h/60) modulo 6
    f = t/60 - ti
    l = v * (1 - s)
    m = v * (1 - f * s)
    n = v * (1 - (1 - f) * s)

    if ti == 0:
        return v, n, l
    elif ti == 1:
        return m, v, l
    elif ti == 2:
        return l, v, n
    elif ti == 3:
        return l, m, v
    elif ti == 4:
        return n, l, v
    else:
        return v, l, m


im = Images()
font = Font()
