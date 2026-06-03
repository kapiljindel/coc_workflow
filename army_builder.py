def setup_army_loadout():
    print("\n" + "="*45)
    print("   COMMANDER: SET UP YOUR ARMY LOADOUT")
    print("="*45)
    print(" Note: The bot maps slots from Left to Right.")
    print(" Look at your game screen and enter your army in order.\n")

    my_army = []
    current_slot = 1

    # 1. Troops
    num_troops = int(input(" [?] How many TROOP cards do you have? (e.g., 1 or 2): "))
    for i in range(num_troops):
        name = input(f"     > Name of Troop {i+1} (e.g., dragon): ").strip().lower()
        count = int(input(f"     > How many {name}s?: "))
        my_army.append({"name": name, "count": count, "slot": f"slot_{current_slot}"})
        current_slot += 1

    # 2. Heroes
    print("\n [?] Which HEROES are active? (Type 'y' or 'n')")
    for hero in ["king", "queen", "warden", "rc"]:
        if input(f"     > Is {hero.capitalize()} active?: ").strip().lower() == 'y':
            my_army.append({"name": hero, "count": 1, "slot": f"slot_{current_slot}"})
            current_slot += 1

    # 3. Spells
    num_spells = int(input("\n [?] How many SPELL cards do you have?: "))
    for i in range(num_spells):
        name = input(f"     > Name of Spell {i+1} (e.g., rage): ").strip().lower()
        count = int(input(f"     > How many {name} spells?: "))
        my_army.append({"name": name, "count": count, "slot": f"slot_{current_slot}"})
        current_slot += 1

    print("\n [+] Army Loadout mapped successfully!")
    for unit in my_army:
        print(f"     - {unit['name'].capitalize()} x{unit['count']} mapped to {unit['slot']}")
    print("="*45 + "\n")

    return my_army