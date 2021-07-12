class item:
    def __init__(self, name, modifier, category) -> None:
        self.name = name
        self.modifier = modifier
        self.category = category

    def __str__(self) -> str:
        self.name

class material(item):
    def __init__(self, name) -> None:
        super().__init__(name, 0, "material")

class weapon(item):
    def __init__(self, name, attack_power, crafting_material) -> None:
        super().__init__(name, attack_power, "weapon")
        self.crafting_material = crafting_material

class armor(item):
    def __init__(self, name, defense_power, crafting_material) -> None:
        super().__init__(name, defense_power, "armor")
        self.crafting_material = crafting_material

class itemDatabase:
    def __init__(self) -> None:
        # self.weapon = [weapon("Wooden Sword", 3, [(material("Wood"), 10), (material("Leather"), 10)]), weapon("Iron Sword", 7, [(material("Iron"), 8), (material("Leather"), 2)])]
        self.weapon = {
            "Wooden Sword": weapon("Wooden Sword", 3, [(material("Wood"), 10), (material("Leather"), 10)]),
            "Iron Sword": weapon("Iron Sword", 7, [(material("Iron"), 8), (material("Leather"), 2)])
        }
        # self.armor = [armor("Wooden Armor", 1, [(material("Wood"), 10), (material("Leather"), 10)]), armor("Wolf Armor", 5, [(material("Wolf Pelt"), 20)])]
        self.armor = {
            "Wooden Armor": armor("Wooden Armor", 1, [(material("Wood"), 10), (material("Leather"), 10)]),
            "Wolf Armor": armor("Wolf Armor", 5, [(material("Wolf Pelt"), 20)])
        }
        self.equipment = {}
        self.equipment.update(self.weapon)
        self.equipment.update(self.armor)
        self.foraging_material = [material("Wood"), material("Iron")]
        self.hunting_material = [material("Leather"), material("Wolf Pelt")]

        self.category = [self.weapon, self.armor, self.foraging_material, self.hunting_material]
        self.craftable_category = [self.weapon, self.armor]

    def getHuntingMaterial(self):
        return self.hunting_material
    
    def getForagingMaterial(self):
        return self.foraging_material