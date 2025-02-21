import os
import json
import mss
import mss.tools
import keyboard
import tkinter as tk
import win32gui

from tkinter import filedialog
from datetime import datetime
 
CONFIG_FILE = "folders.json"
 
def load_folders():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_folders(folder_map):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(folder_map, f, indent=4)

FOLDER_MAP = load_folders()

class ScreenshotTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.create_context_menu()
        self.current_screenshot = None
        self.hotkey_pressed = False
        
    def create_context_menu(self):
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.config(font=('Arial', 10))

        for display_name, folder in FOLDER_MAP.items():
            self.menu.add_command(
                label=display_name,
                command=lambda f=folder: self.save_screenshot(f)
            )
        
        self.menu.add_separator()
        self.menu.add_command(label="Add Folder", command=self.add_folder) 
        self.menu.add_command(label="Exit", command=self.exit_program)

    def take_screenshot(self):
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            self.current_screenshot = sct.grab(monitor)
            print("Screenshot captured, waiting for save location...")

    def save_screenshot(self, folder_path):
        if self.current_screenshot is None:
            print("No screenshot available to save")
            return

        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H-%M-%S")
        
        date_folder = os.path.join(folder_path, current_date)
        os.makedirs(date_folder, exist_ok=True)
        
        filename = f"{current_time}.png"
        save_path = os.path.join(date_folder, filename)
        
        mss.tools.to_png(self.current_screenshot.rgb, 
                        self.current_screenshot.size, 
                        output=save_path)
        
        print(f"Screenshot saved: {save_path}")
        self.current_screenshot = None

    def show_menu(self):
        if self.hotkey_pressed:
            return
        self.hotkey_pressed = True
        
        self.take_screenshot()
        try:
            x, y = self.root.winfo_pointerx(), self.root.winfo_pointery()
            self.root.attributes('-topmost', True)
            hwnd = win32gui.GetForegroundWindow()
            win32gui.SetWindowPos(hwnd, -1, x, y, 0, 0, 0x0001 | 0x0002 | 0x0040)
            self.menu.post(x, y)
        finally:
            self.menu.grab_release()
            self.hotkey_pressed = False

    def add_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder")
        if folder_path:
            folder_name = os.path.basename(folder_path)
            FOLDER_MAP[folder_name] = folder_path
            save_folders(FOLDER_MAP)
            self.create_context_menu()
            print(f"Added folder: {folder_path}")

    def exit_program(self):
        keyboard.unhook_all()
        self.root.quit()

    def check_hotkey(self, e):
        if keyboard.is_pressed('alt') and keyboard.is_pressed('f3'):
            self.show_menu()

    def run(self):
        keyboard.on_press_key('f3', self.check_hotkey, suppress=True)
        print("Screenshot tool is running. Press Alt + F3 to show menu.")
        self.root.mainloop()

if __name__ == '__main__':
    tool = ScreenshotTool()
    tool.run()
