import time
import random
import json
import requests
import pyperclip
# Import the active device connection and logging from your config.py
from config import device, add_log

# ==========================================
# --- EDGE FUNCTION CONFIGURATION ---
# ==========================================
FUNCTION_URL = "https://gnfzxjtvncioseapmmja.supabase.co/functions/v1/Post-deploy"

# ==========================================
# --- CORE AUTOMATION ENGINE ---
# ==========================================
def tap_coordinates(x, y, button_name="Button"):
    """Accepts X and Y coordinates and executes a tap command."""
    if not device:
        print("❌ [Error] Device object is not connected or found in config.py!")
        return False
        
    random_x = x + random.randint(-2, 2)
    random_y = y + random.randint(-2, 2)
    
    print(f"👉 Tapping {button_name} at: ({random_x}, {random_y})")
    device.shell(f"input tap {random_x} {random_y}")
    
    try:
        add_log("buttons", f"Clicked {button_name} via push_data at ({random_x}, {random_y})")
    except Exception:
        pass
        
    return True

def swipe_screen(start_x, start_y, end_x, end_y, duration=800):
    """Executes an ADB swipe gesture from start coordinates to end coordinates."""
    if not device:
        print("❌ [Error] Device object is not connected or found in config.py!")
        return False

    print(f"↕️ Swiping from ({start_x}, {start_y}) to ({end_x}, {end_y}) over {duration}ms...")
    device.shell(f"input swipe {start_x} {start_y} {end_x} {end_y} {duration}")
    return True

def send_data_to_function(copied_text):
    """
    Parses the raw clipboard string into proper JSON structure
    and sends it directly to your Supabase Edge Function.
    """
    print(f"📤 Preparing payload for Supabase Edge Function...")
    
    try:
        # Convert the raw clipboard string directly into a Python dictionary object
        payload = json.loads(copied_text)
        print("✅ Successfully parsed clipboard text into a clean JSON payload.")
    except Exception as parse_error:
        print(f"⚠️ [Format Warning] Data isn't JSON formatted string. Sending raw text fallback: {parse_error}")
        payload = {"tag": copied_text}
    
    try:
        print(f"🔗 Posting to: {FUNCTION_URL}")
        response = requests.post(FUNCTION_URL, json=payload)
        
        print(f"📬 Response Status Code: {response.status_code}")
        print(f"📄 Response Text: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ [Database] Data deployed successfully!")
            try:
                add_log("resources", "Successfully posted complete actual data payload to Edge Function.")
            except Exception:
                pass
        else:
            print("⚠️ [Database] Server accepted request but returned non-success code.")
            
    except Exception as e:
        print(f"❌ [Network Error] Failed to connect to Edge Function: {e}")

def run_four_step_pipeline(first_x, first_y, second_x, second_y, third_x, third_y, fourth_x, fourth_y):
    """
    Executes two taps, a clean scroll sweep, a final tap to copy, 
    and handles the direct parsing transmission.
    """
    print("\n🚀 Starting Automated Data Pipeline...")
    
    # Clear host PC clipboard before beginning so we don't send old text
    pyperclip.copy("")
    
    # 1. Tap the first button
    tap_coordinates(first_x, first_y, button_name="First Button")
    time.sleep(random.uniform(0.1, 0.2))
    
    # 2. Tap the second button
    tap_coordinates(second_x, second_y, button_name="Second Button")
    time.sleep(random.uniform(0.1, 0.2))
    
    # 3. Clean Swipe Sequence (Scroller)
    SWIPE_START_X = 1000
    SWIPE_START_Y = 700   
    SWIPE_END_X = 1000    
    SWIPE_END_Y = 300     
    swipe_screen(SWIPE_START_X, SWIPE_START_Y, SWIPE_END_X, SWIPE_END_Y, duration=850)
    swipe_screen(SWIPE_START_X, SWIPE_START_Y, SWIPE_END_X, SWIPE_END_Y, duration=850)
    swipe_screen(SWIPE_START_X, SWIPE_START_Y, SWIPE_END_X, SWIPE_END_Y, duration=850)
    
    print("⏳ Waiting for swipe scrolling momentum to freeze...")
    time.sleep(random.uniform(0.1, 0.2))

    # 4. Tap the third button (Triggers the internal "Copy to Clipboard" action)
    tap_coordinates(third_x, third_y, button_name="Third Button")

    tap_coordinates(fourth_x, fourth_y, button_name="Fourth Button")

    # Retry Loop to wait for PC Clipboard to catch up and sync from emulator
    print("⏳ Catching synchronized PC clipboard data...")
    copied_data = ""
    max_retries = 6
    
    for attempt in range(max_retries):
        time.sleep(random.uniform(0.1, 0.2)) 
        copied_data = pyperclip.paste()
        
        if copied_data != "":
            print(f"🎉 Success! Found data on attempt {attempt + 1}")
            break
        else:
            print(f"🔄 Clipboard still empty, retrying... ({attempt + 1}/{max_retries})")
    
    # 5. Extract raw data string and execute database POST push
    if copied_data:
        send_data_to_function(copied_data)
    else:
        print("❌ [Pipeline Error] Timed out waiting for PC clipboard.")

    print("✅ Full automation pipeline finished successfully!")


# ... [Keep all your existing code exactly the same] ...

def execute_data_deployment_pipeline():
    """
    Wrapper function so the main bot loop can trigger this pipeline 
    automatically using your confirmed coordinates.
    """
    # 📍 Your confirmed coordinates
    FIRST_BUTTON_X = 1532
    FIRST_BUTTON_Y = 665
    
    SECOND_BUTTON_X = 819
    SECOND_BUTTON_Y = 769
    
    THIRD_BUTTON_X = 1080  
    THIRD_BUTTON_Y = 670  
    
    FOUR_BUTTON_X = 1290  
    FOUR_BUTTON_Y = 98  

    # Trigger the pipeline engine
    run_four_step_pipeline(
        FIRST_BUTTON_X, FIRST_BUTTON_Y, 
        SECOND_BUTTON_X, SECOND_BUTTON_Y,
        THIRD_BUTTON_X, THIRD_BUTTON_Y,
        FOUR_BUTTON_X, FOUR_BUTTON_Y
    )

if __name__ == "__main__":
    print("Make sure BlueStacks is visible on your screen.")
    time.sleep(2) 
    
    # Now the manual tester runs the exact same wrapper function
    execute_data_deployment_pipeline()

# if __name__ == "__main__":
#     print("Make sure BlueStacks is visible on your screen.")
#     time.sleep(2) 
    
    # 📍 Your confirmed coordinates
    FIRST_BUTTON_X = 1532
    FIRST_BUTTON_Y = 665
    
    SECOND_BUTTON_X = 819
    SECOND_BUTTON_Y = 769
    
    THIRD_BUTTON_X = 1080  
    THIRD_BUTTON_Y = 670  
    
    FOUR_BUTTON_X = 1290  
    FOUR_BUTTON_Y = 98  

    # Run the full engine
    run_four_step_pipeline(
        FIRST_BUTTON_X, FIRST_BUTTON_Y, 
        SECOND_BUTTON_X, SECOND_BUTTON_Y,
        THIRD_BUTTON_X, THIRD_BUTTON_Y,
        FOUR_BUTTON_X, FOUR_BUTTON_Y
    )