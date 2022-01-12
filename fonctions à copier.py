"A copier"

1 = """
        robot = IA(ter.position_vert,type.vert,im.vert_sprinter,im.vert_fighter,im.vert_tank,im.attak_vert,im.explosion_vert,"rouge","vert")

        global groupe_lignes, groupe_chute

        groupe_lignes = []
        line = False
        for i in range(60, (len(ter.contenu)-6)*30 +15, 15 ):
            robot.rect.bottom = i
            for j in range(6, (len(ter.contenu[0])-3)*30, 1 ):
                robot.rect.left = j

                collide = False
                for bloc in ter.grp_bloc:
                    if robot.rect.colliderect(bloc.rect):
                        collide = True
                        if line == True:
                            groupe_lignes.append((point_depart, point_arrivee))
                            line = False
                        break
                if collide == False:
                    robot.rect.top += 1
                    for bloc in ter.grp_bloc:
                        if robot.rect.colliderect(bloc.rect):
                            collide = True
                    robot.rect.top -= 1

                    if collide == True:
                        if line == False:
                            line = True
                            point_depart = robot.rect.center
                        elif line == True:
                            point_arrivee = robot.rect.center

                    elif collide == False and line == True:
                        groupe_lignes.append((point_depart, point_arrivee))
                        line = False

        for bloc_piege in ter.grp_bloc_pieg:
            line = False
            robot.rect.bottom = bloc_piege.rect.bottom
            robot.rect.right = bloc_piege.rect.left
            i = 1
            while i:
                i += 1
                robot.rect.left += 1
                if robot.test_collision() == None:
                    print("on a marchÃƒÆ’Ã‚Â© sur un piege !")
                    robot.rect.top += 1
                    if robot.test_collision() == True:
                        robot.rect.top -= 1
                        if line == False:
                            point_depart = robot.rect.center
                            line = True
                        else:
                            point_arrivee = robot.rect.center
                    else:
                        robot.rect.top -= 1
                        if line == True:
                            groupe_lignes.append((point_depart, point_arrivee))
                            line = False
                            break
                if i > 30 + robot.rect.width and line == False:
                    i = 0




        ecran.blit(im.fond, (0,0))
        ter.grp_bloc.draw(ecran)
        for bloc in ter.grp_bloc_effet:
            ecran.blit(bloc.image.subsurface(0,0,30,30), bloc.rect.topleft)
        for pers in ter.grp_pers:
            ecran.blit(pers.image[pers.direction][pers.index_img], pers.rect.topleft)
            couleur = (55 + 200 * abs( pers.vie/pers.full_vie -1 ), 255 - 200 * abs( pers.vie/pers.full_vie -1 ), 50)
            pygame.draw.rect(ecran, couleur, (pers.rect.left, pers.rect.top-10, pers.rect.width*pers.vie/pers.full_vie, 5))
        for ligne in groupe_lignes:
            pygame.draw.line(ecran, (0,0,0), ligne[0], ligne[1])
        pygame.display.flip()
        pygame.time.wait(3000)

        print("groupe_lignes = [", end = "")
        for ligne in groupe_lignes:
            print("",ligne,",", end = "")
        print("]")

        groupe_chute = []
        for i in 1, -1:
            for ligne in groupe_lignes:
                robot.rect.center = ligne[0]
                robot.rect.centerx -= i

                collide = False
                for bloc in ter.grp_bloc:
                    if robot.rect.colliderect(bloc):
                        collide = True

                if collide == False:
                    for ligne2 in groupe_lignes:
                        if ligne[0][0] - ligne2[1][0] == i:
                            if -15 <= ligne[0][1] - ligne2[0][1] < 0:
                                groupe_chute.append([ligne, ligne2])
                        elif ligne[1][0] - ligne2[0][0] == i:
                            if -15 <= ligne[0][1] - ligne2[0][1] < 0:
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

        for line1 in groupe_lignes:
            ajout = True
            for lines in groupe_chute:
                for line2 in lines:
                    if line1 == line2:
                        ajout = False
            if ajout == True:
                groupe_chute.append([line1])

        ecran.blit(im.fond, (0,0))
        ter.grp_bloc.draw(ecran)
        for bloc in ter.grp_bloc_effet:
            ecran.blit(bloc.image.subsurface(0,0,30,30), bloc.rect.topleft)
        for lines in groupe_chute:
            for line in lines:
                pygame.draw.line(ecran,(0,0,0),line[0], line[1])
            pygame.display.flip()
            pygame.time.wait(1000)

        print("groupe_chute = [", end = "")
        for lines in groupe_chute:
            print("[", end = "")
            for line in lines:
                print("",line,",", end = "")
            print("],", end = "")
        print("]")
            """

2 =         """ecran.blit(im.fond, (0,0))
            for groupe in (ter.grp_bloc, ter.grp_btn_bloc, ter.grp_btn_play):
                groupe.draw(ecran)
            for bloc in ter.grp_bloc_effet:
                ecran.blit(bloc.image.subsurface(0,0,30,30), (bloc.rect.left, bloc.rect.top))

            for liste in self.act_listes:
                pygame.draw.rect(ecran, (0,0,200), ((liste[-1][0]*30, liste[-1][1]*30), (30,30)))

            pygame.display.update()
            pygame.time.wait(100)"""

3 =     """ecran.blit(im.fond, (0,0))
        for groupe in (ter.grp_bloc, ter.grp_btn_bloc, ter.grp_btn_play):
            groupe.draw(ecran)
        for bloc in ter.grp_bloc_effet:
            ecran.blit(bloc.image.subsurface(0,0,30,30), (bloc.rect.left, bloc.rect.top))

        for point in self.chemin:
            pygame.draw.rect(ecran, (0,0,200), ((point[0]*30, point[1]*30), (30,30)))

        pygame.display.update()
        #pygame.time.wait(100)"""

4 = """
    def create_cadre(self,longueur, hauteur,name):
        vide = self.vide.copy()
        image = vide.subsurface(0,0,longueur,hauteur)
        image.blit(self.cadre.subsurface(0,0,4,4),(0,0))
        image.blit(self.cadre.subsurface(0,5,4,4),(0,hauteur-4))
        image.blit(self.cadre.subsurface(5,0,4,4),(longueur-4,0))
        image.blit(self.cadre.subsurface(5,5,4,4),(longueur-4,hauteur-4))
        for i in range(longueur-8):
            for j in range(hauteur-8):
                image.blit(self.cadre.subsurface(4,4,1,1),(i+4,j+4))
        for i in range(longueur-8):
            image.blit(self.cadre.subsurface(4,0,1,4),(i+4,0))
            image.blit(self.cadre.subsurface(4,5,1,4),(i+4,hauteur-4))
        for j in range(hauteur-8):
            image.blit(self.cadre.subsurface(0,4,4,1),(0,j+4))
            image.blit(self.cadre.subsurface(5,4,4,1),(longueur-4,j+4))
        pygame.image.save(image,"Images/Cadres/"+name+".png")
        return image
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
        self.index_img = int(self.dx/2 +0.5) +2 if self.dx else int(self.dy/2 +0.5)

    #__________________________________________

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
            for liste1 in self.act_listes:
                deplacements = []
                for i in (1,0), (0,1), (-1,0), (0,-1):
                    if self.deplacement_possible( (liste1[-1][0]+i[0], liste1[-1][1]+i[1]) ):
                        deplacements.append(i)
                deplacements_diagonale = []
                for i in deplacements:
                    for j in deplacements:
                        if math.sqrt((i[0]+j[0])**2) == 1:
                            if self.deplacement_possible( (liste1[-1][0]+i[0]+j[0], liste1[-1][1]+i[1]+j[1]) ):
                                ajout = True
                                for vecteur in deplacements_diagonale:
                                    if (i[0]+j[0], i[1]+j[1]) == vecteur:
                                        ajout = False
                                if ajout: deplacements_diagonale.append( (i[0]+j[0], i[1]+j[1]) )
                for i in deplacements_diagonale:
                    deplacements.append(i)
                for i in deplacements:
                    point = ( (liste1[-1][0]+i[0], liste1[-1][1]+i[1]) )
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

            #2 aÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â  copier

        self.dx = self.chemin[1][0]-self.x
        self.dy = self.chemin[1][1]-self.y

        #3 aÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â  copier

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

    def besoin_tourner(self, x,y):
        return True if x == int(x/30)*30+15 and y == int(y/30)*30+15 else False

"""
Classe qui definit le missiles a tete chercheuse envoyes par les Sprinters
"""

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
                distance = math.sqrt((objet.rect.centerx - self.rect.centerx)**2 + (objet.rect.centery - self.rect.centery)**2)
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
                    distance = math.sqrt( (self.rect.centerx - objet.rect.centerx)**2 + (self.rect.centery - objet.rect.centery)**2 )
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

5 =     """
        self.robot = IA((0,0),0,im.vert_sprinter,im.vert_fighter,im.vert_tank,im.attak_vert,im.explosion_vert,"rouge","vert")
        self.act_listes = self.new_listes = self.chemins = []
        self.groupe_extremites = []
        self.liste_chemins = []
        self.recherche_deplacements-possibles()
        """
"""
    def recherche_deplacements_possibles(self):

        for lines in groupe_chute.grp:
            self.groupe_extremites.append((lines.extr1,lines.extr2))

        for pnts in self.groupe_extremites:
            for pnt in pnts:

                self.act_listes = [IA_chemin([])]
                self.chemins = []
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
                                for lines2 in groupe_chute.grp:
                                    if pnt != lines2.extr1 and pnt != lines2.extr2:
                                        for line2 in lines2.grp:
                                            if self.robot.rect.centery == line2[0][1]:
                                                if line2[0][0] <= self.robot.rect.centerx <= line2[1][0]:
                                                    ajout = True
                                                    for chemin in self.chemins:
                                                        if chemin.chemin[-1] == lines2:
                                                            ajout = False
                                                    if ajout == True:
                                                        temp.chemin.append(lines2)
                                                        temp.chemin.insert(0,pnt)
                                                        self.chemins.append(temp)
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


                self.liste_chemins.append(self.chemins)

                ecran.blit(im.fond,(0,0))
                ter.grp_bloc.draw(ecran)
                pygame.draw.rect(ecran, (255,255,0), (pnt, (5,5)))
                for chemins in self.chemins:
                    for line in chemins.chemin[-1].grp:
                        pygame.draw.line(ecran, (255,255,0),line[0],line[1])
                pygame.display.flip()
                pygame.time.wait(1000)

        print("self.liste_chemins = [",end ="")
        for chemins in self.liste_chemins:
            print("[", end = "")
            for chemin in chemins:
                print(chemin.chemin,",",end = "")
            print("],",end = "")
        print("]")

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
"""

6 = """
        for lines in self.lines_bottom_left,self.lines_top_left,self.lines_bottom_right,self.lines_top_right:
            ecran.blit(im.fond, (0,0))
            ter.grp_bloc.draw(ecran)
            for line in lines.grp:
                pygame.draw.line(ecran,(255,255,255),line[0],line[1])
            pygame.display.update()
            pygame.time.wait(1000)
        """