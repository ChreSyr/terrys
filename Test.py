# Taken from mission The Vampires


class Warrior:
    def __init__(self, army=None):
        self.health = 50
        self.attack = 5
        self.army = army

    @property
    def is_alive(self):
        return self.health > 0

    def hit(self, ennemy):
        ennemy.get_hit(self.attack)

    def get_hit(self, damage):
        self.health -= damage


class Knight(Warrior):
    def __init__(self, army=None):
        Warrior.__init__(self, army)
        self.attack = 7


class Defender(Warrior):
    def __init__(self, army=None):
        Warrior.__init__(self, army)
        self.health = 60
        self.attack = 3
        self.defense = 2

    def get_hit(self, damage):
        damage = damage - self.defense
        if damage > 0:
            self.health -= damage


class Vampire(Warrior):
    def __init__(self, army=None):
        Warrior.__init__(self, army)
        self.health = 40
        self.attack = 4
        self.vampirism = .5

    def hit(self, ennemy):
        life_before = ennemy.health
        super().hit(ennemy)
        damage = life_before - ennemy.health
        self.health += int(damage * self.vampirism)


class Lancer(Warrior):
    def __init__(self, army=None):
        Warrior.__init__(self, army)
        self.attack = 6

    def hit(self, ennemy):
        super().hit(ennemy)
        if ennemy.army is not None:
            try:
                ennemy2 = ennemy.army[ennemy.army.index(ennemy) + 1]
                self.lance_hit(ennemy2)
            except IndexError:
                pass

    def lance_hit(self, ennemy):
        ennemy.get_hit(int(self.attack / 2))


class Army(list):
    @property
    def is_armed(self):
        return any(unit.is_alive for unit in self)

    def add_units(self, unit, amount):
        for i in range(amount):
            warrior = unit()
            self.append(warrior)
            warrior.army = self

    def clean(self):
        if not self[0].is_alive:
            self.pop(0)


class Battle:
    def __init__(self):
        self.armies = None

    def fight(self, a1, a2):
        self.armies = (a1, a2)

        while a1.is_armed and a2.is_armed:
            fight(a1[0], a2[0])
            for army in self.armies:
                army.clean()

        return a1.is_armed


def fight(u1, u2):
    fighters = (u2, u1)
    while u1.is_alive and u2.is_alive:
        fighters = tuple(reversed(fighters))
        fighters[0].hit(fighters[1])
    return u1.is_alive


if __name__ == '__main__':
    # These "asserts" using only for self-checking and not necessary for auto-testing

    # fight tests
    chuck = Warrior()
    bruce = Warrior()
    carl = Knight()
    dave = Warrior()
    mark = Warrior()
    bob = Defender()
    mike = Knight()
    rog = Warrior()
    lancelot = Defender()
    eric = Vampire()
    adam = Vampire()
    richard = Defender()
    ogre = Warrior()
    freelancer = Lancer()
    vampire = Vampire()

    assert fight(chuck, bruce) == True
    assert fight(dave, carl) == False
    assert chuck.is_alive == True
    assert bruce.is_alive == False
    assert carl.is_alive == True
    assert dave.is_alive == False
    assert fight(carl, mark) == False
    assert carl.is_alive == False
    assert fight(bob, mike) == False
    assert fight(lancelot, rog) == True
    assert fight(eric, richard) == False
    assert fight(ogre, adam) == True
    assert fight(freelancer, vampire) == True
    assert freelancer.is_alive == True

    # battle tests
    my_army = Army()
    my_army.add_units(Defender, 2)
    my_army.add_units(Vampire, 2)
    my_army.add_units(Lancer, 4)
    my_army.add_units(Warrior, 1)

    enemy_army = Army()
    enemy_army.add_units(Warrior, 2)
    enemy_army.add_units(Lancer, 2)
    enemy_army.add_units(Defender, 2)
    enemy_army.add_units(Vampire, 3)

    army_3 = Army()
    army_3.add_units(Warrior, 1)
    army_3.add_units(Lancer, 1)
    army_3.add_units(Defender, 2)

    army_4 = Army()
    army_4.add_units(Vampire, 3)
    army_4.add_units(Warrior, 1)
    army_4.add_units(Lancer, 2)

    battle = Battle()

    assert battle.fight(my_army, enemy_army) == True
    assert battle.fight(army_3, army_4) == False
    print("Coding complete? Let's try tests!")