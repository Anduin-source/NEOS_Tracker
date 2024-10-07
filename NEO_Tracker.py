import subprocess
import os
import requests
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import scrolledtext, messagebox, font
import re
import logging
import threading
import argparse
import configparser
import sys
import json  # Para manipulação de JSON
import pandas as pd  # Para manipulação de dados

# Configure logging to log to both file and console
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# File handler for logging to a file
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)

# Console handler for logging to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Log format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Definition of the Tooltip class to add tooltips to widgets
class Tooltip:
    """
    Class to create tooltips for Tkinter widgets.
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        x, y, _, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += cy + self.widget.winfo_rooty() + 20
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(tw, text=self.text, background="#ffffe0", relief='solid', borderwidth=1)
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        tw = self.tooltip_window
        if tw:
            tw.destroy()
        self.tooltip_window = None

def get_observations(object_type_value, target_object):
    """
    Retrieves the observations of the specified object from the Minor Planet Center API.
    """
    if object_type_value == "NEO":
        url = "https://data.minorplanetcenter.net/api/get-obs"
        payload = {"desigs": [target_object], "output_format": ["OBS80"]}
    elif object_type_value == "NEOCP":
        url = "https://data.minorplanetcenter.net/api/get-obs-neocp"
        payload = {"trksubs": [target_object], "output_format": ["OBS80"]}
    else:
        raise ValueError("Invalid option for object type.")

    try:
        response = requests.get(url, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        raise requests.exceptions.RequestException(f"Request error: {e}")

    try:
        data = response.json()
    except ValueError:
        logger.error("Error decoding JSON response.")
        raise ValueError("Error decoding JSON response.")

    try:
        obs80_string = data[0]['OBS80']
        return obs80_string
    except (KeyError, IndexError):
        logger.error("Error processing response data. Check if the object name is correct.")
        raise KeyError("Error processing response data. Check if the object name is correct.")

def run_find_orb(obs_file, obs_code, find_orb_path, eph_steps):
    """
    Executes the find_orb program with the specified parameters.
    """
    ephemeris_output_path = os.path.join(find_orb_path, 'efemerides.txt')
    elements_output_path = os.path.join(find_orb_path, 'elements.txt')

    # Safe construction of the command
    executable = os.path.join(find_orb_path, 'fo64.exe')
    if not os.path.exists(executable):
        logger.error(f"The find_orb executable was not found at: {executable}")
        raise FileNotFoundError(f"The find_orb executable was not found at: {executable}")

    command = [
        executable, obs_file,
        '-e', ephemeris_output_path,
        '-E', '3,5,24',
        '-C', obs_code,
        f'EPHEM_STEPS={eph_steps}',
        'EPHEM_STEP_SIZE=1h'
    ]

    try:
        subprocess.run(command, cwd=find_orb_path, check=True)

        if os.path.exists(ephemeris_output_path):
            with open(ephemeris_output_path, 'r') as eph_file:
                eph_content = eph_file.read()
        else:
            logger.error("The file efemerides.txt was not found.")
            raise FileNotFoundError("The file efemerides.txt was not found.")

        if os.path.exists(elements_output_path):
            with open(elements_output_path, 'r') as elements_file:
                elements_content = elements_file.read()
        else:
            logger.error("The file elements.txt was not found.")
            raise FileNotFoundError("The file elements.txt was not found.")

        return elements_content, eph_content

    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing find_orb: {e}")
        raise Exception(f"Error executing find_orb: {e}")

def delete_temporary_files(files):
    """
    Deletes temporary files to avoid accumulation in the directory.
    """
    for file in files:
        try:
            if os.path.exists(file):
                os.remove(file)
        except Exception as e:
            logger.error(f"Could not delete file {file}: {e}")

class FindOrbApp:
    def run_neofixer(self):
        """
        Runs the NEOFIXER module to retrieve targets and display them.
        """
        try:
            site_code = self.obs_code_entry.get() or 'X93'
            base_url = 'https://neofixerapi.arizona.edu/targets/?site=' + site_code + '&num=40'
            response = requests.get(base_url)
            response.raise_for_status()
            data = response.json()
            
            # Extract targets
            targets = data.get('result', {}).get('objects', {})
            if not targets:
                messagebox.showinfo("NEOFIXER", "No targets found.")
                return

            # Create a new window to display the targets
            neofixer_window = tk.Toplevel(self.root)
            neofixer_window.title("NEOFIXER Targets")
            neofixer_window.geometry("800x400")

            # Create a Treeview to display the targets
            tree = ttk.Treeview(neofixer_window)
            tree.pack(expand=True, fill='both', padx=10, pady=10)

            # Define columns
            columns = ('ID', 'Priority', 'Score', 'Cost', 'Magnitude', '1-sigma Uncertainty')
            tree["columns"] = columns
            tree["show"] = "headings"

            # Configure headers with sorting capability
            for col in columns:
                tree.heading(col, text=col, command=lambda _col=col: self.sort_by(tree, _col, False))
                tree.column(col, anchor='center', width=120)

            # Insert target data
            for sID, dObj in targets.items():
                priority = dObj.get('priority', '-')
                score = dObj.get('score', -1)
                cost = dObj.get('cost', -1)
                magnitude = dObj.get('vmag', -1)
                uncertainty = dObj.get('uncert', -1)

                tree.insert("", "end", values=(
                    sID,
                    priority,
                    f"{score:.2f}",
                    f"{cost:.1f}",
                    f"{magnitude:.1f}",
                    f"{uncertainty:.4f}"
                ))

            # Add a vertical scrollbar
            scrollbar = ttk.Scrollbar(neofixer_window, orient="vertical", command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            scrollbar.pack(side='right', fill='y')

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching NEOFIXER targets: {e}")
            messagebox.showerror("Error", f"Unable to fetch NEOFIXER targets: {e}")
            base_url = 'https://neofixerapi.arizona.edu/targets/?site=' + site_code + '&num=40'
            response = requests.get(base_url)
            response.raise_for_status()
            data = response.json()
            
            # Extract targets
            targets = data.get('result', {}).get('objects', {})
            if not targets:
                messagebox.showinfo("NEOFIXER", "No targets found.")
                return

            # Create a new window to display the targets
            neofixer_window = tk.Toplevel(self.root)
            neofixer_window.title("NEOFIXER Targets")
            neofixer_window.geometry("800x400")

            # Create a Treeview to display the targets
            tree = ttk.Treeview(neofixer_window)
            tree.pack(expand=True, fill='both', padx=10, pady=10)

            # Define columns
            columns = ('ID', 'Priority', 'Score', 'Cost', 'Magnitude', '1-sigma Uncertainty')
            tree["columns"] = columns
            tree["show"] = "headings"

            # Configure headers
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, anchor='center', width=120)

            # Insert target data
            for sID, dObj in targets.items():
                priority = dObj.get('priority', '-')
                score = dObj.get('score', -1)
                cost = dObj.get('cost', -1)
                magnitude = dObj.get('vmag', -1)
                uncertainty = dObj.get('uncert', -1)

                tree.insert("", "end", values=(
                    sID,
                    priority,
                    f"{score:.2f}",
                    f"{cost:.1f}",
                    f"{magnitude:.1f}",
                    f"{uncertainty:.4f}"
                ))

            # Add a vertical scrollbar
            scrollbar = ttk.Scrollbar(neofixer_window, orient="vertical", command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            scrollbar.pack(side='right', fill='y')

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching NEOFIXER targets: {e}")
            messagebox.showerror("Error", f"Unable to fetch NEOFIXER targets: {e}")
    """
    Main application class that manages the GUI and user interactions.
    """

    def __init__(self, root, find_orb_path):
        """
        Initializes the GUI and widgets.
        """
        self.root = root
        self.root.title("Ephemeris Calculator")
        self.root.geometry("1000x700")

        # Apply ttk theme
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.find_orb_path = find_orb_path
        self.validate_find_orb_path()

        self.create_widgets()
        self.create_menu()
        self.create_status_bar()

    def validate_find_orb_path(self):
        """
        Validates the find_orb_path to ensure the executable exists.
        """
        executable = os.path.join(self.find_orb_path, 'fo64.exe')
        if not os.path.exists(executable):
            messagebox.showerror("Error", f"The find_orb executable was not found at: {executable}")
            sys.exit(1)

    def create_widgets(self):
        """
        Creates and configures the GUI widgets.
        """
        # Fonts
        header_font = font.Font(family='Helvetica', size=12, weight='bold')

        # Frame for inputs
        self.input_frame = ttk.Frame(self.root)
        self.input_frame.pack(pady=10, padx=10, fill='x')

        # Grid configuration
        self.input_frame.columnconfigure(1, weight=1)

        # Variables
        self.object_type = tk.StringVar(value="NEO")
        self.message_label = ttk.Label(self.input_frame, text="")
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=('Courier New', 10))
        self.text_area.configure(state='disabled')

        # Input widgets
        ttk.Label(self.input_frame, text="Select object type:", font=header_font).grid(row=0, column=0, sticky='w')

        # Create a frame for the radiobuttons
        radio_frame = ttk.Frame(self.input_frame)
        radio_frame.grid(row=0, column=1, sticky='w')

        ttk.Radiobutton(radio_frame, text="NEO", variable=self.object_type, value="NEO").pack(side='left')
        ttk.Radiobutton(radio_frame, text="NEOCP", variable=self.object_type, value="NEOCP").pack(side='left')

        ttk.Label(self.input_frame, text="Enter the object's name:", font=header_font).grid(row=1, column=0, sticky='w')
        self.target_object_entry = ttk.Entry(self.input_frame)
        self.target_object_entry.grid(row=1, column=1, sticky='ew')
        self.target_object_entry.insert(0, "Ex: 2021 PDC")
        self.target_object_placeholder = "Ex: 2021 PDC"
        self.target_object_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(event, self.target_object_entry, self.target_object_placeholder))
        self.target_object_entry.bind("<FocusOut>", lambda event: self.add_placeholder(event, self.target_object_entry, self.target_object_placeholder))
        Tooltip(self.target_object_entry, "Enter the object's name or designation.")

        ttk.Label(self.input_frame, text="Enter the observatory code (MPC code):", font=header_font).grid(row=2, column=0, sticky='w')
        self.obs_code_entry = ttk.Entry(self.input_frame)
        self.obs_code_entry.grid(row=2, column=1, sticky='ew')
        self.obs_code_entry.insert(0, "Ex: X93")
        self.obs_code_placeholder = "Ex: X93"
        self.obs_code_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(event, self.obs_code_entry, self.obs_code_placeholder))
        self.obs_code_entry.bind("<FocusOut>", lambda event: self.add_placeholder(event, self.obs_code_entry, self.obs_code_placeholder))
        Tooltip(self.obs_code_entry, "Enter your observatory's MPC code.")

        # Optional field to configure ephemeris steps
        ttk.Label(self.input_frame, text="Ephemeris Steps:", font=header_font).grid(row=3, column=0, sticky='w')
        self.eph_steps_entry = ttk.Entry(self.input_frame)
        self.eph_steps_entry.grid(row=3, column=1, sticky='ew')
        self.eph_steps_entry.insert(0, "10")
        Tooltip(self.eph_steps_entry, "Number of steps to calculate the ephemeris.")

        # Message
        self.message_label.grid(row=5, column=0, columnspan=3, sticky='w')

        # Buttons in a separate frame
        button_frame = ttk.Frame(self.input_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=10)

        submit_button = ttk.Button(button_frame, text="Submit", command=self.submit)
        submit_button.pack(side='left', padx=5)
        self.root.bind('<Control-s>', self.submit)

        refresh_button = ttk.Button(button_frame, text="Reset", command=self.refresh)
        refresh_button.pack(side='left', padx=5)
        self.root.bind('<Control-n>', self.refresh)

        # Progress bar
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')

        # Text area
        self.text_area.pack(expand=True, fill='both', padx=10, pady=10)

    def create_menu(self):
        """
        Creates the application menu with Help, About, Quit, NEOCP, and NEOFIXER options.
        """
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # NEOCP Menu
        neocp_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="NEOCP", menu=neocp_menu)
        neocp_menu.add_command(label="View NEO Candidates", command=self.view_neocp_candidates)

        # NEOFIXER Menu
        neofixer_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="NEOFIXER", menu=neofixer_menu)
        neofixer_menu.add_command(label="Run NEOFIXER", command=self.run_neofixer)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Manual", command=self.show_help)

        # About Menu
        about_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="About", menu=about_menu)
        about_menu.add_command(label="About", command=self.show_about)

        # Quit Menu
        quit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Quit", menu=quit_menu)
        quit_menu.add_command(label="Quit", command=self.quit_application)

    def create_status_bar(self):
        """
        Creates the status bar at the bottom of the window.
        """
        self.status_bar = ttk.Label(self.root, text="Ready", relief='sunken', anchor='w')
        self.status_bar.pack(side='bottom', fill='x')

    def clear_placeholder(self, event, entry, placeholder):
        """
        Clears the placeholder when the field gains focus.
        """
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.configure(foreground='black')

    def add_placeholder(self, event, entry, placeholder):
        """
        Adds the placeholder if the field is empty when it loses focus.
        """
        if entry.get() == '':
            entry.insert(0, placeholder)
            entry.configure(foreground='grey')

    def validate_entries(self):
        """
        Validates the input fields, displaying visual indications if necessary.
        """
        valid = True
        obj_name = self.target_object_entry.get()
        obs_code = self.obs_code_entry.get()

        # Validate object name
        if obj_name == '' or obj_name == self.target_object_placeholder:
            self.target_object_entry.configure(background='#ffcccc')
            valid = False
        else:
            if not re.match(r'^[A-Za-z0-9\s\-]+$', obj_name):
                self.target_object_entry.configure(background='#ffcccc')
                messagebox.showerror("Error", "Invalid object name. Please enter a valid designation.")
                valid = False
            else:
                self.target_object_entry.configure(background='white')

        # Validate observatory code
        if obs_code == '' or obs_code == self.obs_code_placeholder:
            self.obs_code_entry.configure(background='#ffcccc')
            valid = False
        else:
            if not re.match(r'^[A-Za-z0-9]{3}$', obs_code):
                self.obs_code_entry.configure(background='#ffcccc')
                messagebox.showerror("Error", "Invalid observatory code. It should be a 3-character alphanumeric code.")
                valid = False
            else:
                self.obs_code_entry.configure(background='white')

        return valid

    def submit(self, event=None):
        """
        Handles the submission event of the data entered by the user.
        """
        if not self.validate_entries():
            return

        # Start processing in a new thread
        thread = threading.Thread(target=self.process_submission)
        thread.start()

    def process_submission(self):
        """
        Processes the submission in a separate thread to keep the GUI responsive.
        """
        object_type_value = self.object_type.get()
        target_object = self.target_object_entry.get()
        obs_code = self.obs_code_entry.get()
        eph_steps = self.eph_steps_entry.get()

        try:
            eph_steps_int = int(eph_steps)
        except ValueError:
            self.root.after(0, lambda: messagebox.showerror("Error", "The 'Ephemeris Steps' field must be an integer."))
            return

        self.root.after(0, self.progress.pack, {'pady': 10})
        self.root.after(0, self.progress.start)
        self.root.after(0, lambda: self.status_bar.config(text="Fetching observations..."))
        self.root.update_idletasks()

        try:
            # Get observations
            obs80_string = get_observations(object_type_value, target_object)

            # Create observation file
            obs_file_path = os.path.join(self.find_orb_path, f"obs_{target_object}.txt")
            with open(obs_file_path, 'w') as obs_file:
                obs_file.write(obs80_string)

            self.root.after(0, lambda: self.status_bar.config(text="Running find_orb..."))
            self.root.update_idletasks()

            # Execute find_orb
            elements_content, eph_content = run_find_orb(obs_file_path, obs_code, self.find_orb_path, eph_steps_int)

            self.root.after(0, lambda: self.status_bar.config(text="Processing results..."))
            self.root.update_idletasks()

            # Read observation data
            with open(obs_file_path, 'r') as obs_file_content:
                obs_content = obs_file_content.read()

            # Display results
            self.root.after(0, self.show_text, elements_content, eph_content, obs_content)
                        
            # Delete temporary files
            self.delete_temp_files([
                obs_file_path,
                os.path.join(self.find_orb_path, 'efemerides.txt'),
                os.path.join(self.find_orb_path, 'elements.txt')
            ])

        except Exception as e:
            logger.error(str(e))
            error_message = str(e)
            if "Invalid observatory code" in error_message:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    "Invalid observatory code. Please check the code and try again.\nYou can find valid codes at https://minorplanetcenter.net/iau/lists/ObsCodes.html"
                ))
            elif "Error processing response data" in error_message:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    "Object not located."
                ))
                self.root.after(0, self.refresh)
            elif "Error executing find_orb" in error_message:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    "An error occurred while executing find_orb. Please ensure that find_orb is properly installed and configured."
                ))
            else:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"An unexpected error occurred: {error_message}\nPlease check the error log for details."
                ))
            self.root.after(0, lambda: self.status_bar.config(text="Error processing."))
        finally:
            self.root.after(0, self.progress.stop)
            self.root.after(0, self.progress.pack_forget)

    def delete_temp_files(self, files):
        """
        Deletes temporary files to avoid accumulation in the directory.
        """
        for file in files:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except Exception as e:
                logger.error(f"Could not delete file {file}: {e}")

    def refresh(self, event=None):
        """
        Clears the input fields and resets messages and the text area.
        """
        if messagebox.askyesno("Confirmation", "Do you really want to reset?"):
            self.target_object_entry.delete(0, tk.END)
            self.target_object_entry.insert(0, self.target_object_placeholder)
            self.target_object_entry.configure(foreground='grey')

            self.obs_code_entry.delete(0, tk.END)
            self.obs_code_entry.insert(0, self.obs_code_placeholder)
            self.obs_code_entry.configure(foreground='grey')

            self.eph_steps_entry.delete(0, tk.END)
            self.eph_steps_entry.insert(0, "10")

            self.message_label.config(text="")
            self.text_area.configure(state='normal')
            self.text_area.delete(1.0, tk.END)
            self.text_area.configure(state='disabled')
            self.status_bar.config(text="Ready")

    def show_text(self, elements_content, eph_content, obs_content):
        """
        Displays the orbital elements, ephemerides, and observations in the text area.
        """
        self.text_area.configure(state='normal')
        self.text_area.delete(1.0, tk.END)
        # Style headers and content
        self.text_area.tag_configure('header', font=('Helvetica', 12, 'bold'))
        self.text_area.tag_configure('content', font=('Courier New', 10))
        self.text_area.insert(tk.INSERT, "Orbital Elements:\n", 'header')
        self.text_area.insert(tk.INSERT, elements_content + "\n", 'content')
        self.text_area.insert(tk.INSERT, "Ephemerides:\n", 'header')
        self.text_area.insert(tk.INSERT, eph_content + "\n", 'content')
        self.text_area.insert(tk.INSERT, "Observations:\n", 'header')
        self.text_area.insert(tk.INSERT, obs_content, 'content')
        self.text_area.configure(state='disabled')

    def show_about(self):
        """
        Displays the 'About' window with application information.
        """
        messagebox.showinfo("About", "Ephemeris Calculator Application.\nDeveloped by Your Company.")

    def show_help(self):
        """
        Displays the help window with usage instructions and user manual.
        """
        help_text = (
            "User Manual:\n\n"
            "Welcome to the Ephemeris Calculator!\n\n"
            "This application allows you to calculate the ephemerides and orbital elements of Near-Earth Objects (NEOs) and NEO Candidates (NEOCP).\n\n"
            "Instructions:\n"
            "1. Select the object type (NEO or NEOCP).\n"
            "2. Enter the object's name or designation.\n"
            "   - Example: '2021 PDC' for a known object.\n"
            "3. Enter your observatory's code (MPC code).\n"
            "   - This is a 3-character alphanumeric code assigned by the Minor Planet Center.\n"
            "   - You can find valid codes at: https://minorplanetcenter.net/iau/lists/ObsCodes.html\n"
            "4. Optionally, adjust the number of ephemeris steps.\n"
            "   - This determines how many data points will be calculated.\n"
            "5. Click 'Submit' to process.\n"
            "6. The results, including orbital elements, ephemerides, and observations, will be displayed in the text area.\n\n"
            "Configuration:\n"
            "To configure the path to the 'find_orb' executable, follow these steps:\n"
            "1. Locate or create the `config.ini` file in the same directory as this application.\n"
            "2. Open `config.ini` with a text editor and add the following content:\n\n"
            "```ini\n"
            "[Paths]\n"
            "find_orb_path = C:\\Path\\To\\Your\\find_orb\n"
            "```\n\n"
            "   - Replace `C:\\Path\\To\\Your\\find_orb` with the actual path where the `find_orb` executable (`fo64.exe`) is located.\n"
            "   - Ensure that the path is correct and that `fo64.exe` exists in the specified directory.\n\n"
            "3. Save the `config.ini` file.\n"
            "4. Alternatively, you can specify the `find_orb_path` via command-line arguments when running the application:\n"
            "   ```bash\n"
            "   python ephemeris_calculator.py --find_orb_path \"C:\\Path\\To\\Your\\find_orb\"\n"
            "   ```\n\n"
            "Notes:\n"
            "- Ensure that 'find_orb' is properly installed and the path is correctly set in the configuration file or via command-line arguments.\n"
            "- For any errors or issues, check the 'app.log' file for details.\n\n"
            "Support:\n"
            "For assistance, please contact support@yourcompany.com"
        )
        help_window = tk.Toplevel(self.root)
        help_window.title("User Manual")
        help_window.geometry("700x600")
        help_text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD)
        help_text_widget.insert(tk.INSERT, help_text)
        help_text_widget.configure(state='disabled', font=('Helvetica', 10))
        help_text_widget.pack(expand=True, fill='both', padx=10, pady=10)

    def view_neocp_candidates(self):
        """
        Initiates the process to fetch and display NEO Candidates.
        """
        # Start fetching in a new thread to keep GUI responsive
        thread = threading.Thread(target=self.fetch_and_display_neocp)
        thread.start()

    def fetch_and_display_neocp(self):
        """
        Fetches the NEO Candidates JSON and displays it in a new window using pandas.
        """
        url = "https://www.minorplanetcenter.net/Extended_Files/neocp.json"
        try:
            self.root.after(0, lambda: self.status_bar.config(text="Fetching NEO Candidates..."))
            response = requests.get(url)
            response.raise_for_status()
            neocp_data = response.json()
            self.root.after(0, lambda: self.status_bar.config(text="NEO Candidates fetched successfully."))
            self.display_neocp(neocp_data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching NEO Candidates: {e}")
            self.root.after(0, lambda: messagebox.showerror(
                "Error",
                f"An error occurred while fetching NEO Candidates:\n{e}"
            ))
            self.root.after(0, lambda: self.status_bar.config(text="Error fetching NEO Candidates."))

    def display_neocp(self, data):
        """
        Displays the NEO Candidates data in a new window using pandas and Treeview with aesthetic adjustments.
        """
        try:
            # Convert JSON data to pandas DataFrame
            df = pd.json_normalize(data)

            # Agrupar 'discovery year', 'discovery month', 'discovery day' em 'Discovery Date'
            if all(col in df.columns for col in ['Discovery_year', 'Discovery_month', 'Discovery_day']):
                df['Discovery Date'] = df['Discovery_year'].astype(str) + '-' + df['Discovery_month'].astype(str).str.zfill(2) + '-' + df['Discovery_day'].astype(str).str.zfill(2)
                df.drop(['Discovery_year', 'Discovery_month', 'Discovery_day'], axis=1, inplace=True)
            else:
                logger.warning("Some discovery date columns are missing.")

            # Formatar 'not_seen_days' para uma casa decimal
            if 'not_seen_dys' in df.columns:
                df['not_seen_dys'] = df['not_seen_dys'].astype(float).round(1)
            else:
                logger.warning("'not_seen_days' column is missing.")

            # Criar uma nova janela
            neocp_window = tk.Toplevel(self.root)
            neocp_window.title("NEO Candidates")
            neocp_window.geometry("1000x600")

            # Criar uma Treeview para exibir a tabela
            tree = ttk.Treeview(neocp_window)
            tree.pack(expand=True, fill='both', padx=10, pady=10)

            # Definir as colunas
            columns = list(df.columns)
            
            tree["columns"] = columns
            tree["show"] = "headings"  # Esconder a coluna de árvore

            # Configurar os cabeçalhos das colunas com alinhamento e adicionar funcionalidade de ordenação
            for col in df.columns:
                tree.heading(col, text=col, command=lambda _col=col: self.sort_by(tree, _col, False))
                # Definir o alinhamento
                if col in ['Temp_Desig', 'Updated', 'Note']:
                    tree.column(col, anchor='w', width=150)  # Alinhamento à esquerda
                elif col == 'not_seen_days':
                    tree.column(col, anchor='center', width=100)  # Alinhamento centralizado
                elif col == 'Discovery Date':
                    tree.column(col, anchor='center', width=120)  # Alinhamento centralizado
                else:
                    tree.column(col, anchor='center', width=100)  # Alinhamento centralizado

            # Inserir os dados na Treeview
            for _, row in df.iterrows():
                values = []
                for col in df.columns:
                    if col == 'not_seen_days':
                        # Garantir que 'not_seen_days' tenha uma casa decimal
                        value = f"{row[col]:.1f}"
                    else:
                        value = row[col]
                    values.append(value)
                tree.insert("", "end", values=values)

            # Adicionar uma barra de rolagem vertical
            scrollbar = ttk.Scrollbar(neocp_window, orient="vertical", command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            scrollbar.pack(side='right', fill='y')

        except Exception as e:
            logger.error(f"Error processing NEO Candidates data: {e}")
            messagebox.showerror(
                "Error",
                f"An error occurred while processing NEO Candidates data:\n{e}"
            )

    def sort_by(self, tree, col, descending):
        """
        Sort the Treeview by a given column.
        """
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        data.sort(reverse=descending)

        # Rearrange items in sorted positions
        for ix, item in enumerate(data):
            tree.move(item[1], '', ix)

        # Reverse sort next time
        tree.heading(col, command=lambda: self.sort_by(tree, col, not descending))

    def quit_application(self):
        """
        Exits the application gracefully.
        """
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            self.root.quit()

def main():
    """
    Main function that starts the application.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Ephemeris Calculator')
    parser.add_argument('--find_orb_path', type=str,
                        help='Path to the find_orb executable directory')
    args = parser.parse_args()

    # Load configuration from config.ini
    config = configparser.ConfigParser()
    config.read('config.ini')
    find_orb_path = config.get('Paths', 'find_orb_path', fallback=None)

    # Override with command-line argument if provided
    if args.find_orb_path:
        find_orb_path = args.find_orb_path

    # Initialize Tkinter root for message boxes
    root = tk.Tk()
    root.withdraw()  # Hide the root window initially

    # Validate find_orb_path
    if not find_orb_path or not os.path.exists(find_orb_path):
        messagebox.showerror(
            "Error",
            "The path to find_orb is not specified or does not exist.\n"
            "Please specify the path in the config.ini file or use the --find_orb_path argument."
        )
        sys.exit(1)

    # Check for fo64.exe
    executable = os.path.join(find_orb_path, 'fo64.exe')
    if not os.path.exists(executable):
        messagebox.showerror(
            "Error",
            f"The find_orb executable was not found at: {executable}\n"
            "Please ensure that fo64.exe is present in the specified find_orb_path."
        )
        sys.exit(1)

    # Proceed with the application
    root.deiconify()  # Show the root window
    app = FindOrbApp(root, find_orb_path=find_orb_path)
    root.mainloop()

if __name__ == "__main__":
    main()
