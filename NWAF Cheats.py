import tkinter as tk
from tkinter import Checkbutton, BooleanVar
import pymem
import pymem.process
import threading
import time

# Game Info
GAME_PROCESS_NAME = "NWaF-Win64-Shipping.exe"
BASE_MODULE = "NWaF-Win64-Shipping.exe"

# Cheat Addresses (Multi-Level Pointer Offsets)
CHEATS = {
    "Unlimited Power": {
        "base_offset": 0x06C3AFA8,  # Static base offset
        "offsets": [0xA0, 0x90, 0x308, 0x440, 0x320, 0x50, 0x318],  # Multi-level pointer offsets
        "type": "double",
        "set_value": 99.8  # Always set this value when active
    },
    "Unlimited Pressure": {
        "base_offset": 0x06C4A5F0,  # Static base offset
        "offsets": [0x30, 0x20, 0x2C0, 0x20, 0x50, 0x2E0],  # Multi-level pointer offsets
        "type": "double",
        "set_value": 95.0  # Always set this value when active
    }
}

# Function to resolve multi-level pointer
def get_real_address(pm, base_offset, offsets):
    try:
        base_address = pymem.process.module_from_name(pm.process_handle, BASE_MODULE).lpBaseOfDll
        address = pm.read_longlong(base_address + base_offset)  # Read first pointer

        for offset in offsets[:-1]:  # Follow offsets except last one
            address = pm.read_longlong(address + offset)

        return address + offsets[-1]  # Final offset
    except:
        return None

# Function to continuously set the value (loop runs while checked)
def freeze_cheat(cheat_name):
    cheat = CHEATS[cheat_name]

    while cheats_status[cheat_name].get():  # Loop while the cheat is active
        try:
            pm = pymem.Pymem(GAME_PROCESS_NAME)  # Try to attach to the game process
            real_address = get_real_address(pm, cheat["base_offset"], cheat["offsets"])

            if not real_address:  # If the address cannot be resolved, retry
                time.sleep(1)  # Wait before retrying
                continue

            # Write the value if the address is resolved
            while cheats_status[cheat_name].get():  # Stay in inner loop while cheat is active
                if cheat["type"] == "double":
                    pm.write_double(real_address, cheat["set_value"])
                time.sleep(0.5)  # Adjust write rate
        except pymem.exception.ProcessNotFound:  # Handle case where the process is not found
            time.sleep(1)  # Wait before retrying to reconnect
        except Exception:  # Handle other exceptions
            time.sleep(1)  # Wait before retrying

# Function to handle checkbox toggle
def toggle_cheat(cheat_name):
    if cheats_status[cheat_name].get():  # If checked, start setting value
        threading.Thread(target=freeze_cheat, args=(cheat_name,), daemon=True).start()

# Create GUI Window
root = tk.Tk()
root.title("NWAF Cheats")
root.geometry("400x300")
root.configure(bg="#1e1e1e")  # Dark gray background

# Set minimum resize limits
root.minsize(400, 300)

# Set custom icon (replace 'icon.ico' with your icon file)
try:
    root.iconbitmap("icon.ico")  # Replace with the path to your custom icon
except Exception as e:
    print(f"Could not set icon: {e}")

# Center the window
window_width = 400
window_height = 300
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_coordinate = (screen_width // 2) - (window_width // 2)
y_coordinate = (screen_height // 2) - (window_height // 2)
root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

# Header
header = tk.Label(root, text="NWAF Cheats", font=("Arial", 16, "bold"), bg="#1e1e1e", fg="white")
header.pack(pady=10)

# Cheat Checkbox Variables
cheats_status = {}

# Create a frame to center the checkboxes
checkbox_frame = tk.Frame(root, bg="#1e1e1e")
checkbox_frame.pack(expand=True)

# Create Checkboxes for Cheats
for cheat_name in CHEATS.keys():
    var = BooleanVar()
    cheats_status[cheat_name] = var
    chk = Checkbutton(
        checkbox_frame, text=cheat_name, variable=var,
        command=lambda name=cheat_name: toggle_cheat(name),
        bg="#1e1e1e", fg="white", font=("Arial", 12),
        selectcolor="#1e1e1e", activebackground="#333333", activeforeground="white"
    )
    chk.pack(pady=5, anchor="center")

# Footer with credits
footer = tk.Label(
    root, text="Created by MathieuAR (mathieuar on Discord)",
    font=("Arial", 10, "italic"), bg="#1e1e1e", fg="gray"
)
footer.pack(side="bottom", pady=10)

# Run GUI
root.mainloop()
