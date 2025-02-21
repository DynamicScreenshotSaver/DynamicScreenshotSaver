import os
import mss
import mss.tools
import keyboard
import tkinter as tk
import win32gui

from tkinter import ttk
from datetime import datetime

# Base directory where your folders are located
BASE_DIR = r"E:\FIB\CID"

# Map menu options to complete folder paths
FOLDER_MAP = {
    'Attaching Bodycam': os.path.join(BASE_DIR, 'Attaching_bodycam'),
    'End of Shifts': os.path.join(BASE_DIR, 'end_of_shifts'),
    'Events': os.path.join(BASE_DIR, 'events'),
    'Evidences': os.path.join(BASE_DIR, 'evidences'),
    'License Plates': os.path.join(BASE_DIR, 'license_plates'),
    'Refreshing Bodycam': os.path.join(BASE_DIR, 'refreshing_bodycam'),
    'Saving Bodycam': os.path.join(BASE_DIR, 'saving_bodycam'),
    'Start of Shifts': os.path.join(BASE_DIR, 'start_of_shifts')
}

class ScreenshotTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window
        self.ensure_folders()
        self.create_context_menu()
        self.current_screenshot = None
        self.hotkey_pressed = False
        
    def ensure_folders(self):
        """Ensure that all target folders exist."""
        for folder_path in FOLDER_MAP.values():
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"Created folder: {folder_path}")

    def create_context_menu(self):
        """Create the context menu."""
        self.menu = tk.Menu(self.root, tearoff=0)
        # Set menu attributes for better visibility
        self.menu.config(font=('Arial', 10))
        
        for display_name, folder in FOLDER_MAP.items():
            self.menu.add_command(
                label=display_name,
                command=lambda f=folder: self.save_screenshot(f)
            )
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.exit_program)

    def take_screenshot(self):
        """Capture the screen and store it temporarily."""
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            self.current_screenshot = sct.grab(monitor)
            print("Screenshot captured, waiting for save location...")

    def save_screenshot(self, folder_path):
        """Save the captured screenshot to the specified folder with date organization."""
        if self.current_screenshot is None:
            print("No screenshot available to save")
            return

        # Get current date for folder structure
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H-%M-%S")
        
        # Create date folder inside the destination folder
        date_folder = os.path.join(folder_path, current_date)
        if not os.path.exists(date_folder):
            os.makedirs(date_folder)

        # Save with time as filename
        filename = f"{current_time}.png"
        save_path = os.path.join(date_folder, filename)
        
        # Save the screenshot
        mss.tools.to_png(self.current_screenshot.rgb, 
                        self.current_screenshot.size, 
                        output=save_path)
        
        print(f"Screenshot saved: {save_path}")
        self.current_screenshot = None  # Clear the stored screenshot

    def show_menu(self):
        """Take screenshot and show the context menu at the current cursor position."""
        if self.hotkey_pressed:  # Prevent multiple triggers
            return
            
        self.hotkey_pressed = True
        
        # Take screenshot first
        self.take_screenshot()
        
        try:
            # Get cursor position
            x = self.root.winfo_pointerx()
            y = self.root.winfo_pointery()
            
            # Force the menu to be topmost
            self.root.attributes('-topmost', True)
            
            # Set menu window position and make it topmost
            hwnd = win32gui.GetForegroundWindow()
            win32gui.SetWindowPos(hwnd, -1, x, y, 0, 0, 0x0001 | 0x0002 | 0x0040)
            
            self.menu.post(x, y)  # Using post instead of tk_popup for better reliability
            
        finally:
            self.menu.grab_release()
            self.hotkey_pressed = False

    def exit_program(self):
        """Exit the program."""
        keyboard.unhook_all()  # Clean up keyboard hooks
        self.root.quit()

    def check_hotkey(self, e):
        """Check if both Alt and F3 are pressed."""
        if keyboard.is_pressed('alt') and keyboard.is_pressed('f3'):
            self.show_menu()

    def run(self):
        """Run the main program loop."""
        # Monitor F3 key and check for Alt when F3 is pressed
        keyboard.on_press_key('f3', self.check_hotkey, suppress=True)
        
        print("Screenshot tool is running. Press Alt + F3 to show menu. Close the menu to exit.")
        self.root.mainloop()

if __name__ == '__main__':
    tool = ScreenshotTool()
    tool.run()
