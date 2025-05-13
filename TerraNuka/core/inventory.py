# core/inventory.py

if __name__ == "__main__":
    import sys
    print("This module is not meant to be run directly.", file=sys.stderr)
    sys.exit(0)


from .globals import ALL_WEAPONS
from .entities import weapon_data

def cycle_weapon(tank, direction=1):
    owned_weapons = [w for w in ALL_WEAPONS if tank.inventory.get(w, 0) > 0]
    if not owned_weapons:
        return  # no weapons available

    current_index = owned_weapons.index(tank.current_weapon) if tank.current_weapon in owned_weapons else 0
    new_index = (current_index + direction) % len(owned_weapons)
    tank.current_weapon_str = owned_weapons[new_index]
    tank.current_weapon = weapon_data[owned_weapons[new_index]]

def buy_weapon(tank, weapon) -> bool:
    if weapon not in ALL_WEAPONS:
        raise ValueError(f"Weapon {weapon} is not a valid weapon.")

    if weapon.cost <= tank.money:
        tank.inventory[weapon] += 1
        tank.money -= weapon.cost
        return True
    else:
        return False