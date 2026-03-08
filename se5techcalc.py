import tkinter as tk
import re
import math
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo
from tkinter import ttk

# autocomplete code taken from https://mail.python.org/pipermail/tkinter-discuss/2012-January/003041.html
class AutocompleteCombobox(ttk.Combobox):

        def set_completion_list(self, completion_list):
                """Use our completion list as our drop down selection menu, arrows move through menu."""
                self._completion_list = sorted(completion_list, key=str.lower) # Work with a sorted list
                self._hits = []
                self._hit_index = 0
                self.position = 0
                self.bind('<KeyRelease>', self.handle_keyrelease)
                self['values'] = self._completion_list  # Setup our popup menu

        def autocomplete(self, delta=0):
                """autocomplete the Combobox, delta may be 0/1/-1 to cycle through possible hits"""
                if delta: # need to delete selection otherwise we would fix the current position
                        self.delete(self.position, tk.END)
                else: # set position to end so selection starts where textentry ended
                        self.position = len(self.get())
                # collect hits
                _hits = []
                for element in self._completion_list:
                        if element.lower().startswith(self.get().lower()): # Match case insensitively
                                _hits.append(element)
                # if we have a new hit list, keep this in mind
                if _hits != self._hits:
                        self._hit_index = 0
                        self._hits=_hits
                # only allow cycling if we are in a known hit list
                if _hits == self._hits and self._hits:
                        self._hit_index = (self._hit_index + delta) % len(self._hits)
                # now finally perform the auto completion
                if self._hits:
                        self.delete(0,tk.END)
                        self.insert(0,self._hits[self._hit_index])
                        self.select_range(self.position,tk.END)

        def handle_keyrelease(self, event):
                """event handler for the keyrelease event on this widget"""
                if event.keysym == "BackSpace":
                        self.delete(self.index(tk.INSERT), tk.END)
                        self.position = self.index(tk.END)
                if event.keysym == "Left":
                        if self.position < self.index(tk.END): # delete the selection
                                self.delete(self.position, tk.END)
                        else:
                                self.position = self.position-1 # delete one character
                                self.delete(self.position, tk.END)
                if event.keysym == "Right":
                        self.position = self.index(tk.END) # go to end (no selection)
                if len(event.keysym) == 1:
                        self.autocomplete()
                # No need for up/down, we'll jump to the popup
                # list at the position of the autocompletion

def open_file():
    """Open a file for editing."""
    filepath = askopenfilename(
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if not filepath:
        return
    
    with open(filepath, mode="r", encoding="utf-8") as input_file:
        text = input_file.read() # read the file
        lines = text.splitlines() # split by lines
        newdict = dict() # init dict handle
        longest = 0 # track length of names
        techlist.clear() # clear list for combobox
        techdicts.clear() # clear dicts
        for line in lines:
            if " := " in line: # only consider lines with data we care about
                line = re.sub(' +', ' ', line) # remove extra spaces
                keyval = line.split(" := ") # extract key:value pair
                if keyval[0] == "Name": # check if we are on a new entry by looking for name
                    if newdict.get("Name") != None: # make sure we dont add a null dict to the list
                        techdicts.append(newdict) # add previous dictionary to list
                    techlist.append(keyval[1]) # save name for combo
                    newdict = dict() # new dictionary
                    newdict[keyval[0]] = keyval[1] # assign name to new dict
                    if len(keyval[1]) > longest: # update longest name if needed
                        longest = len(keyval[1])
                else:
                    newdict[keyval[0]] = keyval[1] # assign value to existing dict
                
        if newdict.get("Name") != None: # make sure we dont add a null dict to the list
            techdicts.append(newdict) # add last dictionary to the list
        
        combobox['values'] = techlist # populate combobox
        combobox.set_completion_list(techlist) # autocomplete list for combobox
        combobox.configure(width=longest+2)
        
    window.title(f"SE5 Tech Cost Calculator - TechAreas file loaded: {filepath}")

def update_tech(*args):
    """Update tech costs from selection
    """
    techname = combobox.get() # get the chosen tech from the combobox
    for x in techdicts:
        if x.get("Name") == techname: # find matching dict
            levelcost = x.get("Level Cost") # get level cost and fill entry
            if selected.get() == "Low":
                levelcost = str(round(int(levelcost)/2))
            if selected.get() == "High":
                levelcost = str(round(int(levelcost)*2))
            ent_costperlevel.delete(0, tk.END)
            ent_costperlevel.insert(0, levelcost)
            startlevel = x.get("Start Level") # get start level and adjust entry if lower
            if not ent_level.get().isdigit() or int(ent_level.get()) < int(startlevel):
                ent_level.delete(0, tk.END)
                ent_level.insert(0, startlevel)
            maxlevel = x.get("Maximum Level") # get max level and adjust entry if higher
            if not ent_target.get().isdigit() or int(ent_target.get()) > int(maxlevel):
                ent_target.delete(0, tk.END)
                ent_target.insert(0, maxlevel)

def calc_cost(*args):
    """Calculate cost to desired tech level
    """
    #set minimum default values if invalid values are present
    if not ent_level.get().isdigit() or int(ent_level.get()) < 0:
        ent_level.delete(0, tk.END)
        ent_level.insert(0, "0")
    if not ent_costperlevel.get().isdigit() or int(ent_costperlevel.get()) < 1:
        ent_costperlevel.delete(0, tk.END)
        ent_costperlevel.insert(0, "1")
    if not ent_target.get().isdigit() or int(ent_target.get()) < 1:
        ent_target.delete(0, tk.END)
        ent_target.insert(0, "1")
    if not ent_progress.get().isdigit() or int(ent_progress.get()) < 0:
        ent_progress.delete(0, tk.END)
        ent_progress.insert(0, "0")
    if not ent_points.get().isdigit() or int(ent_points.get()) < 1:
        ent_points.delete(0, tk.END)
        ent_points.insert(0, "1")
    # make sure values dependent on combobox selection match it
    update_tech()
    # read numbers from text
    level = int(ent_level.get())
    costperlevel = int(ent_costperlevel.get())
    target = int(ent_target.get())
    progress = int(ent_progress.get())
    points = int(ent_points.get())
    costtotarget = 0
    # calculate
    for x in range(level+1, target+1):
        costtotarget += x*costperlevel
    costtotarget -= progress
    ratiototarget = (costtotarget/points)
    pcttotarget = ratiototarget*100
    # update labels
    lbl_costtotarget["text"] = f"Total Cost: {round(costtotarget, 2)}"
    lbl_pcttotarget["text"] = f"Percent Needed: {round(pcttotarget, 2)}%"
    lbl_turnstotarget["text"] = f"Estimated Turns: {math.ceil(ratiototarget)}"

def popup_help(*args):
    """Create a popup with instructions
    """
    showinfo("HELP", helpstring)

# Set up the window
window = tk.Tk()
window.title("SE5 Tech Cost Calculator")
window.resizable(width=True, height=False)
# init lists
techlist = []
techdicts = []
# help text string
helpstring = ("Welcome to the Space Empires 5 Tech Cost Calculator!\n\n"
              "This utility can be used to determine how much research to allocate to reach a "
              "specific goal over multiple levels.\n\n"
              "Basic Instructions:\n"
              "Open the in game research screen and scroll to find your chosen tech area.\n"
              "Enter your Current Level, the Cost Per Level (right click the tech to see it, "
              "listed as Cost), and your Target Level (your goal).\n"
              "Select the Accumulated Cost option on the right panel to see how many research "
              "points have been accumulated toward the next level and enter that number under "
              "Current Progress.\n"
              "Look near the top right corner to find the total research points for this turn "
              "and enter that number under Research Points Available.\n"
              "Click on the CALCULATE button (or press Enter while in the last field) to see the "
              "total cost, percentage points to allocate to reach the target, and estimated number "
              "of turns assuming points remain the same. The Percent Needed value will need to "
              "rounded up when entering the number ingame, and if it is over 100, then 100% will "
              "be needed until the last turn.\n\n"
              "Advanced Instructions:\n"
              "This calculator can also load the TechAreas.txt file used by the game to make it "
              "easier to choose tech areas.\n"
              "To do this, click on the Load Tech Definitions button and then browse to your "
              "TechAreas.txt file (usually under data directory in the main game directory).\n"
              "Now, you can start typing in the box next to that button, and it will autocomplete "
              "to the closest tech area name as you type. You can also just use the dropdown to "
              "select a tech area instead.\n"
              "Press Enter when you have the tech area you want, and it will automatically load "
              "the associated Cost Per Level, and adjust the Target Level if it is above the "
              "maximum for that field.\n"
              "If you are playing the game with a tech cost other than the default of medium, "
              "you can select that from the Technology Cost radio buttons to adjust the cost.\n"
              "Now you can follow the basic instructions without needing to refer back to the "
              "game for the cost per level.\n\n"
              "Note: this calculator was made to help research multiple levels at once while "
              "not overshooting the target. However, if you are generating a very large amount "
              "of research points while researching a field with many levels but a low cost per "
              "level, it is still possible to overshoot because the minimum you can assign is "
              "1% of your total points.\n\n"
              "Thank you for using this calculator, I hope you found it useful."
             )

# Create the entry frame with an Entry
# widget and label in it
frm_top = tk.Frame(master=window)
frm_entry = tk.Frame(master=frm_top)
lbl_level = tk.Label(master=frm_entry, text="Current Level")
ent_level = tk.Entry(master=frm_entry, width=11)
lbl_costperlevel = tk.Label(master=frm_entry, text="Cost Per Level")
ent_costperlevel = tk.Entry(master=frm_entry, width=11)
lbl_target = tk.Label(master=frm_entry, text="Target Level")
ent_target = tk.Entry(master=frm_entry, width=11)
lbl_progress = tk.Label(master=frm_entry, text="Current Progress")
ent_progress = tk.Entry(master=frm_entry, width=17)
lbl_points = tk.Label(master=frm_entry, text="Research Points Available")
ent_points = tk.Entry(master=frm_entry, width=21)

# Layout the Labels and Entries in frm_entry
# using the .grid() geometry manager
lbl_level.grid(row=0, column=0, padx=10)
ent_level.grid(row=1, column=0, padx=10)
lbl_costperlevel.grid(row=0, column=1, padx=10)
ent_costperlevel.grid(row=1, column=1, padx=10)
lbl_target.grid(row=0, column=2, padx=10)
ent_target.grid(row=1, column=2, padx=10)
lbl_progress.grid(row=0, column=3, padx=10)
ent_progress.grid(row=1, column=3, padx=10)
lbl_points.grid(row=0, column=5, padx=10)
ent_points.grid(row=1, column=5, padx=10)

# cycle entry fields with return
ent_level.bind('<Return>', lambda e: ent_costperlevel.focus_set())
ent_costperlevel.bind('<Return>', lambda e: ent_target.focus_set())
ent_target.bind('<Return>', lambda e: ent_progress.focus_set())
ent_progress.bind('<Return>', lambda e: ent_points.focus_set())
ent_points.bind('<Return>', calc_cost)

# create radio buttons
frm_radio = tk.Frame(master=frm_entry)
lbl_radio = tk.Label(master=frm_entry, text="Technology Cost")
selected = tk.StringVar()
r1 = ttk.Radiobutton(frm_radio, text='Low', value='Low', variable=selected, command=update_tech)
r2 = ttk.Radiobutton(frm_radio, text='Med', value='Med', variable=selected, command=update_tech)
r3 = ttk.Radiobutton(frm_radio, text='High', value='High', variable=selected, command=update_tech)

lbl_radio.grid(row=0, column=6, padx=10)
frm_radio.grid(row=1, column=6, padx=10)
r1.grid(row=0, column=0, padx=1)
r2.grid(row=0, column=1, padx=1)
r3.grid(row=0, column=2, padx=1)
selected.set("Med")
btn_help = tk.Button(
    frm_top,
    text="HELP",
    command=popup_help
)
btn_help.grid(row=0, column=1, pady=1)

# Create the calc Button and result display Labels
frm_buttons = tk.Frame(master=window)
btn_open = tk.Button(frm_buttons, text="Load Tech Definitions", command=open_file)
btn_open.grid(row=0, column=0, pady=10)
combobox = AutocompleteCombobox(frm_buttons, width=33)
combobox.bind('<<ComboboxSelected>>', update_tech)
combobox.bind('<Return>', update_tech)
btn_convert = tk.Button(
    frm_buttons,
    text="CALCULATE",
    command=calc_cost
)
lbl_costtotarget = tk.Label(frm_buttons, text="Total Cost:")
lbl_pcttotarget = tk.Label(frm_buttons, text="Percent Needed:")
lbl_turnstotarget = tk.Label(frm_buttons, text="Estimated Turns:")

# Set up the layout using the .grid() geometry manager
btn_open.grid(row=0, column=0, pady=10)
combobox.grid(row=0, column=1, padx=10)
btn_convert.grid(row=0, column=2, pady=10)
lbl_costtotarget.grid(row=0, column=3, padx=10)
lbl_pcttotarget.grid(row=0, column=4, padx=10)
lbl_turnstotarget.grid(row=0, column=5, padx=10)

frm_top.grid(row=0, column=0, padx=10, sticky="w")
frm_entry.grid(row=0, column=0, padx=10, sticky="w")
frm_buttons.grid(row=1, column=0, padx=10, sticky="w")

# Run the application
window.mainloop()