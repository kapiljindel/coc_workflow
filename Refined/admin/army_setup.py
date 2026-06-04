"""
Army Setup Module
Interactive army configuration tool
"""

from utils.logger import get_logger

logger = get_logger(__name__)

def setup_army_loadout() -> list:
    """
    Interactive wizard to configure army loadout
    
    Returns:
        Army composition list ready for config.json
    """
    print("\n" + "=" * 50)
    print("   ⚙️  COMMANDER: CONFIGURE YOUR ARMY")
    print("=" * 50)
    print(" Note: The bot maps slots from Left to Right.")
    print(" Look at your game screen and enter your army in order.\n")
    
    my_army = []
    current_slot = 1
    
    # 1. Troops
    num_troops = int(input(" [?] How many TROOP cards do you have? (e.g., 1 or 2): "))
    for i in range(num_troops):
        name = input(f"     > Name of Troop {i+1} (e.g., dragon): ").strip().lower()
        count = int(input(f"     > How many {name}s?: "))
        my_army.append({
            "name": name,
            "count": count,
            "category": "troop",
            "slot": f"slot_{current_slot}"
        })
        current_slot += 1
    
    # 2. Heroes
    print("\n [?] Which HEROES are active? (Type 'y' or 'n')")
    for hero in ["king", "queen", "warden", "royal_champion"]:
        response = input(f"     > Is {hero.replace('_', ' ').title()} active?: ").strip().lower()
        if response == 'y':
            my_army.append({
                "name": hero,
                "count": 1,
                "category": "hero",
                "slot": f"slot_{current_slot}"
            })
            current_slot += 1
    
    # 3. Spells
    num_spells = int(input("\n [?] How many SPELL cards do you have?: "))
    for i in range(num_spells):
        name = input(f"     > Name of Spell {i+1} (e.g., rage): ").strip().lower()
        count = int(input(f"     > How many {name} spells?: "))
        my_army.append({
            "name": name,
            "count": count,
            "category": "spell",
            "slot": f"slot_{current_slot}"
        })
        current_slot += 1
    
    # Display summary
    print("\n [✓] Army Configuration Complete!")
    print("=" * 50)
    for unit in my_army:
        print(f"   {unit['name'].title():20} x{unit['count']:2}  [{unit['category'].upper()}]  {unit['slot']}")
    print("=" * 50 + "\n")
    
    return my_army

if __name__ == "__main__":
    army = setup_army_loadout()
    print("\nAdd this to your config.json:")
    import json
    print(json.dumps(army, indent=2))
