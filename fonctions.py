# -*- coding: utf-8 -*

import math

def arrondir(x, d=32, mult=True):
    """
    Renvoi le plus grand multiple de d inferieur ou egal a x
    :param x: La borne superieure
    :param d: La base, 32 par defaut
    :param mult: Si passe a False, arrondir() renvoi combien de fois d est dans x
    :return: Le grand multiple de d inferieur ou egal a x
             Si mult=False, renvoi combien de fois d est dans x
    """
    return d*int(x/d) if mult else int(x/d)

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

def trouve(point, type):
    if type == "sprinter":
        point[1] = 5
    elif type == "fighter":
        point[1] = 95
    elif type == "tank":
        point[1] = 185
    return point

def distance_pnts(pnt1, pnt2):
    return math.hypot(pnt1[0]-pnt2[0], pnt1[1]-pnt2[1])

def modulo(x, mod):
    return divmod(x, mod)[1]

def closest(pnt, list_pnt):  # Renvoie le pnt le plus proche d'un point cible
    dis = math.inf
    closest_pnt = ()
    for x in list_pnt:
        dis_x = distance_pnts(pnt, x)
        if dis_x < dis:
            dis = dis_x
            closest_pnt = x
    return closest_pnt

def get_angle(x, y):  # renvoi un angle en radian
    if x or y:
        return modulo(sign(y) * math.acos(x / math.hypot(x, y)), math.pi*2)
    else:
        return 0

"""def print_grid(grid):
    for line in grid:
        for i in line:
            if i == "vide":
                print(0, end=" ")
            elif i == "bloc":
                print(1, end=" ")
            else:
                print(i, end=" ")
        print("")"""

def racine(a, b, c, r=1):
    delta = b ** 2 - 4 * a * c
    if delta >= 0:
        return (- b + math.sqrt(delta)) / (2 * a) if r == 1 else (- b - math.sqrt(delta)) / (2 * a)
    else:
        return -1

def f(a, b, c, x):
    return a * x ** 2 + b * x + c
