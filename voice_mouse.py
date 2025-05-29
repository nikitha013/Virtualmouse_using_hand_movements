import speech_recognition as sr
import pyautogui
import webbrowser
import subprocess
import threading
import time

# Configure PyAutoGUI
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.1

# Initialize recognizer and microphone
recognizer = sr.Recognizer()
mic = sr.Microphone()
recognizer.energy_threshold = 4000  # Adjust based on ambient noise

# Define cursor movement step size
MOVE_STEP = 50

# Scrolling control variables
scrolling = False
scroll_direction = 0  # 1 for up, -1 for down
scroll_thread = None

# Define folders (customize these paths to match your system)
folders = {
    "documents": r"C:\Users\Nikitha\Documents",
    "downloads": r"C:\Users\Nikitha\Downloads",
    "pictures": r"C:\Users\Nikitha\Pictures",
    # Add more folders as needed
}

def extract_after_keyword(command, keyword):
    """Extract text after a specific keyword in the command."""
    parts = command.split(keyword, 1)
    if len(parts) > 1:
        return parts[1].strip()
    return None

def continuous_scroll():
    """Handle continuous scrolling in a separate thread."""
    global scrolling, scroll_direction
    while scrolling:
        pyautogui.scroll(50 * scroll_direction)
        time.sleep(0.1)  # Adjust speed as needed

def process_command(command):
    """Process the voice command and execute the appropriate action."""
    global scrolling, scroll_direction, scroll_thread
    command = command.lower()
    print(f"Recognized: {command}")

    # Handle folder opening
    if "open" in command and "folder" in command:
        folder_part = extract_after_keyword(command, "open")
        if folder_part:
            folder_name = folder_part.replace("folder", "").strip()
            for name, path in folders.items():
                if name in folder_name:
                    try:
                        subprocess.Popen(['explorer', path])
                        print(f"Opened folder: {name}")
                        return True
                    except Exception as e:
                        print(f"Failed to open folder: {e}")
                        return True
            print(f"Folder not found: {folder_name}")
        else:
            print("Please specify a folder name")
        return True

    # Handle opening YouTube
    elif "open youtube" in command:
        webbrowser.open("https://www.youtube.com")
        print("Opened YouTube")
        return True

    # Handle playing a song/video on YouTube
    elif "play" in command and "youtube" in command:
        song_part = extract_after_keyword(command, "play")
        if song_part:
            song_name = song_part.replace("in youtube", "").replace("on youtube", "").strip()
            if song_name:
                search_url = f"https://www.youtube.com/results?search_query={song_name}"
                webbrowser.open(search_url)
                print(f"Searching for '{song_name}' on YouTube")
            else:
                print("Please specify a song or video to play")
        else:
            print("Please specify a song or video to play")
        return True

    # Existing mouse control commands (example placeholders)
    elif "move left" in command:
        x, y = pyautogui.position()
        pyautogui.moveTo(x - MOVE_STEP, y)
        print("Moved cursor left")
    elif "start scrolling up" in command:
        if not scrolling:
            scrolling = True
            scroll_direction = 1
            scroll_thread = threading.Thread(target=continuous_scroll)
            scroll_thread.start()
            print("Started scrolling up")
    elif "stop scrolling" in command:
        if scrolling:
            scrolling = False
            scroll_thread.join()
            print("Stopped scrolling")
    elif "exit" in command:
        print("Exiting program")
        return False
    else:
        print("Command not recognized, please try again")
    return True

def main():
    """Main function to listen for voice commands."""
    print("Starting voice control. Say 'exit' to stop.")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        while True:
            print("Listening...")
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                command = recognizer.recognize_google(audio, language="en-IN")
                if not process_command(command):
                    break
            except sr.WaitTimeoutError:
                print("No speech detected")
            except sr.UnknownValueError:
                print("Couldn’t understand audio")
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")
                break
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                break

if __name__ == "__main__":
    main()