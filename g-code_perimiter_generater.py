import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
import json

# Find X and Y furthest position and lowest position
#-----------------------------------------------------------------------
def parse_gcode(file_path):
    
    highest_x = float('-inf')
    highest_y = float('-inf')
    lowest_x = float('inf')
    lowest_y = float('inf')

    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('G0') or line.startswith('G1') or line.startswith('G2') or line.startswith('G3'):
                parts = line.split()
                for part in parts:
                    if part.startswith('X'):
                        x = float(part[1:])
                        if x > highest_x:
                            highest_x = x
                        if x < lowest_x:
                            lowest_x = x
                    elif part.startswith('Y'):
                        y = float(part[1:])
                        if y > highest_y:
                            highest_y = y
                        if y < lowest_y:
                            lowest_y = y
    
    return highest_x, highest_y, lowest_x, lowest_y
#preview the G-code 
#---------------------------------------------------------------------
def preview_and_save(file_path, feed_rate_entry, root):
    hX, hY, lX, lY = parse_gcode(file_path)

    feed_rate = feed_rate_entry.get()
    try:
        F_value = int(feed_rate)
    except ValueError:
        messagebox.showerror("Error", "Invalid feed rate value. Please enter a valid integer.")
        return

    # Load machine options from JSON file
    machine_options = load_machine_options()

    if machine_options and "machine_orientation" in machine_options:
        machine_orientation = machine_options["machine_orientation"]
    else:
        messagebox.showerror("Error", "Machine orientation not found in the machine options.")
        return

    if machine_orientation == "X+/Y+":
        metadata_text = (
            f'G1 X{hX} F{F_value}\n'
            f'G1 Y{hY} F{F_value}\n'
            f'G1 X{lX} F{F_value}\n'
            f'G1 Y{lY} F{F_value}\n'
            f'M225 #100 "Cycle Start to continue, or Cancel to adjust the starting point."\n'
        )
    elif machine_orientation == "X+/Y-":
        metadata_text = (
            f'G1 X{hX} F{F_value}\n'
            f'G1 Y{lY} F{F_value}\n'
            f'G1 X{lX} F{F_value}\n'
            f'G1 Y{hY} F{F_value}\n'
            f'M225 #100 "Cycle Start to continue, or Cancel to adjust the starting point."\n'
        )
    elif machine_orientation == "X-/Y-":
        metadata_text = (
            f'G1 X{lX} F{F_value}\n'
            f'G1 Y{lY} F{F_value}\n'
            f'G1 X{hX} F{F_value}\n'
            f'G1 Y{hY} F{F_value}\n'
            f'M225 #100 "Cycle Start to continue, or Cancel to adjust the starting point."\n'
        )
    elif machine_orientation == "X-/Y+":
        metadata_text = (
            f'G1 X{lX} F{F_value}\n'
            f'G1 Y{hY} F{F_value}\n'
            f'G1 X{hX} F{F_value}\n'
            f'G1 Y{lY} F{F_value}\n'
            f'M225 #100 "Cycle Start to continue, or Cancel to adjust the starting point."\n'
        )
    else:
        messagebox.showerror("Error", "Invalid machine orientation.")
        return

    with open(file_path, 'r') as f:
        lines = f.readlines()
        m225_found = False
        for i, line in enumerate(lines):
            if line.strip().startswith('M225'):
                m225_found = True
            if line.strip().startswith('M65'):
                if m225_found:
                    # Modify previous G1 lines with new feed rate value
                    for j in range(i - 1, -1, -1):
                        if lines[j].strip().startswith('G1'):
                            lines[j] = lines[j].split('F')[0] + f'F{F_value}\n'
                else:
                    # Insert metadata text if M225 not found before M65
                    lines.insert(i, metadata_text)
                break

    preview_window = tk.Toplevel(root)
    preview_window.title("Preview")
    preview_window.iconbitmap("iconn.ico")
    preview_window.configure(bg="#444444")

    preview_text_widget = tk.Text(preview_window, wrap="word")
    preview_text_widget.insert("1.0", ''.join(lines))  # Display entire G-code with added metadata
    preview_text_widget.pack(expand=True, fill="both")

    def save():
        new_file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if new_file_path:
            with open(new_file_path, 'w') as new_file:
                new_file.writelines(lines)
            messagebox.showinfo("Success", "Metadata added and file saved successfully.")
            preview_window.destroy()

    save_button = tk.Button(preview_window, text="Save", command=save)
    save_button.pack(side="left", padx=5, pady=5)

    cancel_button = tk.Button(preview_window, text="Cancel", command=preview_window.destroy)
    cancel_button.pack(side="right", padx=5, pady=5)

#Select a .txt files
#---------------------------------------------        
def select_file(feed_rate_entry, root):
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        preview_and_save(file_path, feed_rate_entry, root)  # Pass 'root' as an additional argument

#------------------------------------------------------
def validate_input(new_value):
    if new_value.isdigit() or new_value == "":
        return True
    else:
        return False

# Example function to refresh the main page
#----------------------------------------------------
def refresh_main_page():
    # Write your code to refresh the main page here
    pass

#------------------------------------------------------
def open_machine_option_setting(root, feed_rate_label):
    machine_option_window = tk.Toplevel(root)
    machine_option_window.title("Machine Option Setting")
    
    # Set the machine option window properties to match the main window
    machine_option_window.geometry("400x300")
    machine_option_window.configure(bg=root.cget('bg'))
    machine_option_window.iconbitmap(root.iconbitmap())

    def handle_radiobutton_selection(option, group):
        print(f"Selected {option} for {group}")

    # Load saved options
    saved_options = load_machine_options()

    # Feed rate options
    feed_rate_frame = ttk.LabelFrame(machine_option_window, text="Feed Rate")
    feed_rate_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    feed_rate_var = tk.StringVar(value="inch/min")  # Default value
    feed_rate_options = ["inch/min", "ft/min", "mm/sec", "mm/min", "m/min", "m/sec"]
    for i, option in enumerate(feed_rate_options):
        radiobutton = ttk.Radiobutton(feed_rate_frame, text=option, variable=feed_rate_var, value=option, command=lambda option=option: handle_radiobutton_selection(option, "Feed Rate"))
        radiobutton.grid(row=i, column=0, padx=5, pady=2, sticky="w")

    # Set the radio button to the value saved in the JSON file, if available
    if saved_options and "feed_rate" in saved_options:
        feed_rate_var.set(saved_options["feed_rate"])

    # Machine orientation options
    machine_orientation_frame = ttk.LabelFrame(machine_option_window, text="Machine Orientation")
    machine_orientation_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    machine_orientation_options = ["X+/Y+", "X-/Y+", "X-/Y-", "X+/Y-"]
    machine_orientation_var = tk.StringVar(value="X+/Y+")  # Default value
    for i, option in enumerate(machine_orientation_options):
        radiobutton = ttk.Radiobutton(machine_orientation_frame, text=option, variable=machine_orientation_var, value=option, command=lambda option=option: handle_radiobutton_selection(option, "Machine Orientation"))
        radiobutton.grid(row=i, column=0, padx=5, pady=2, sticky="w")

    # Set the radio button to the value saved in the JSON file, if available
    if saved_options and "machine_orientation" in saved_options:
        machine_orientation_var.set(saved_options["machine_orientation"])

    # Configure column weights for equal spacing
    machine_option_window.columnconfigure(0, weight=1)
    machine_option_window.columnconfigure(1, weight=1)

    # Save button
    save_button = tk.Button(machine_option_window, text="Save", command=lambda: save_machine_options(root, machine_option_window, feed_rate_var, machine_orientation_var, feed_rate_label))
    save_button.grid(row=1, column=0, columnspan=2, pady=(50, 0), padx=150, sticky="ew")

#------------------------------------------------------------------
def save_machine_options(root, machine_option_window, feed_rate_var, machine_orientation_var, feed_rate_label):
    # Get the selected options
    selected_options = {
        "feed_rate": feed_rate_var.get(),
        "machine_orientation": machine_orientation_var.get()
    }
    
    # Save the options to a JSON file
    with open("machine_option.json", "w") as json_file:
        json.dump(selected_options, json_file)
    
    # Update the feed rate label text in the main window
    if feed_rate_label is not None:
        if selected_options and "feed_rate" in selected_options:
            feed_rate_label_text = f"Enter feed rate in {selected_options['feed_rate']}:"
        else:
            feed_rate_label_text = "configure machine option"
        feed_rate_label.config(text=feed_rate_label_text)

    # Close the machine option window
    machine_option_window.destroy()

    # Refresh the main page (assuming you have a function to refresh the main page)
    refresh_main_page()

    # Show a message indicating successful save
    messagebox.showinfo("Success", "Options saved")

# Load saved options from JSON file
#------------------------------------------------------------------
def load_machine_options():
    try:
        with open("machine_option.json", "r") as json_file:
            options = json.load(json_file)
            return options
    except FileNotFoundError:
        return None

#------------------------------------------------------------------
def main():
    root = tk.Tk()
    root.title("G-code Perimeter Generator")
    root.geometry("400x400")
    root.iconbitmap("iconn.ico")
    root.configure(bg="#444444")

    # Load saved options
    saved_options = load_machine_options()

    # Load the logo image
    logo_image = tk.PhotoImage(file="logo.png")  # Replace "logo.png" with the path to your logo image
    logo_image_resized = logo_image.subsample(7, 7)

    # Create a label to display the logo
    logo_label = tk.Label(root, image=logo_image_resized, bg="#444444")
    logo_label.pack(pady=10)  # Adjust the padding as needed

    title_label = tk.Label(root, text="G-code Perimeter Generator", font=("Helvetica", 16), bg="#444444", fg="white")
    title_label.pack(padx=20, pady=20)

    validate_cmd = root.register(validate_input)

    # Configure and display feed rate label
    feed_rate_label = tk.Label(root, text="Enter feed rate in inch/min:", font=("Helvetica", 11), bg="#444444", fg="white")
    feed_rate_label.pack(padx=20, pady=(20, 5))

    feed_rate_entry = tk.Entry(root, validate="key", validatecommand=(validate_cmd, "%P"))
    feed_rate_entry.insert(0, "150")  # Set default value to 150
    feed_rate_entry.pack(padx=20, pady=(0, 20))

    select_button = tk.Button(root, text="Select File", command=lambda: select_file(feed_rate_entry, root))
    select_button.pack(padx=20, pady=(0, 20))

    machine_option_button = tk.Button(root, text="Machine Option", command=lambda: open_machine_option_setting(root, feed_rate_label))

    #machine_option_button = tk.Button(root, text="Machine Option", command=lambda: open_machine_option_setting(feed_rate_entry, root))
    machine_option_button.pack(padx=20, pady=(0, 20))

    # If saved_options exist, update the feed rate label text
    if saved_options and "feed_rate" in saved_options:
        feed_rate_label_text = f"Enter feed rate in {saved_options['feed_rate']}:"
        feed_rate_label.config(text=feed_rate_label_text)
    else:
        # If no saved options, open machine option window
        open_machine_option_setting(root, feed_rate_label)

    root.mainloop()


if __name__ == "__main__":
    main()