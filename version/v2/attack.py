import time
import random
from config import find_and_click, device

def deploy_troops():
    print(" [Attack] Deploying Swarm...")
    if find_and_click("barbarian.png"):
        time.sleep(0.2)
        
        # Keep tapping random spots until the gray exhausted icon appears
        while not find_and_click("end_barbarian.png", threshold=0.85, click=False):
            for _ in range(10):
                device.shell(f"input tap {random.randint(100, 600)} {random.randint(100, 250)}")
                
        print(" [Attack] Troops exhausted. Waiting for battle to finish...")
        time.sleep(8)
    else:
        print(" [Attack] WARNING: Could not find troop icon to deploy!")