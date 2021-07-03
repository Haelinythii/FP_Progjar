import ntpath


class Player:
    def __init__(self, hp, experience, attack, defense, speed, inventory) -> None:
        self.level = 1
        self.hp = hp
        self.maxhp = hp
        self.experience = experience
        self.neededExpToLevelUp = self.level * (self.level + 1) * 5
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.inventory = inventory
        self.weapon = None
        self.armor = None

    def get_damage(self):
        base_damage = self.attack + self.weapon.modifier
        return base_damage

    def take_damage_battle(self, attack):
        damage = attack - self.defense
        if damage < 0:
            damage = 0
        self.hp = self.hp - damage
    
    def take_damage_hunting(self, damage):
        self.hp = self.hp - damage
        is_dead = self.check_dead()
        if is_dead:
            self.level_down()
        return is_dead

    def check_dead(self):
        if self.hp < 0:
            return True
        return False

    def heal(self):
        self.hp = self.maxhp
    
    def training(self, experience):
        self.experience = self.experience + experience
        if self.experience > self.neededExpToLevelUp:
            self.level_up()
            return True
        return False

    def level_up(self):
        self.experience = 0
        #((n(n+1))/2)x100
        self.neededExpToLevelUp = self.level * (self.level + 1) * 5
        self.level = self.level + 1

        self.hp = self.hp + 5
        self.attack = self.attack + 1
        self.defense = self.defense + 1
        self.speed = self.speed + 1

    def level_down(self):
        self.experience = 0
        #((n(n+1))/2)x100
        self.level = self.level - 1
        self.neededExpToLevelUp = self.level * (self.level + 1) * 5

        self.hp = self.hp - 5
        self.attack = self.attack - 1
        self.defense = self.defense - 1
        self.speed = self.speed - 1
        
        self.heal()

    def set_experience(self, experience):
        self.experience = experience

    def set_attack(self, attack):
        self.attack = attack

    def set_defense(self, defense):
        self.defense = defense

    def set_speed(self, speed):
        self.speed = speed
    
    def set_weapon(self, weapon):
        self.weapon = weapon

    def set_armor(self, armor):
        self.armor = armor
    
    def get_level(self):
        return self.level

    def get_hp(self):
        return self.hp

    def get_attack(self):
        return self.attack

    def get_defense(self):
        return self.defense

    def get_speed(self):
        return self.speed

    