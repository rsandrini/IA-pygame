

class Upgrade:
    """
    Represent Upgrades in Agend
    """

    def __init__(self, name, icon, icon_disabled,
                 position, type_upgrade, bonus, cost=10):

        self.name = name
        self.icon = icon
        self.icon_disabled = icon_disabled
        self.position = position
        self.type_upgrade = type_upgrade
        self.bonus = bonus

        self.cost = cost
        self.upgrade_level = 0
        self.get_rect()
        self.hovered = False

    def get_rect(self):
        self.rect = self.icon.get_rect()
        self.rect.topleft = (self.position)

    def up(self):
        self.cost += 2
        self.upgrade_level += 1
