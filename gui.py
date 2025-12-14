import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import subprocess
import sys
import threading
from bot.core import BotPersonality

# Defaults
DEFAULT_MMR = "3000"
DEFAULT_SC2_PATH = os.environ.get("SC2PATH", "C:/Program Files (x86)/StarCraft II")

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("VersusAI Bot Launcher")
        self.geometry("600x550")

        # Check for Bot folder
        if not os.path.exists("bot"):
            messagebox.showwarning("Warning", "Could not find 'bot' directory in current path.\nEnsure the launcher is in the root directory.")

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # === Section 1: Game Paths ===
        path_frame = ttk.LabelFrame(main_frame, text="System Configuration", padding="10")
        path_frame.pack(fill=tk.X, pady=5)

        ttk.Label(path_frame, text="StarCraft II Path:").grid(row=0, column=0, sticky="w")
        self.sc2_path_var = tk.StringVar(value=DEFAULT_SC2_PATH)
        ttk.Entry(path_frame, textvariable=self.sc2_path_var, width=40).grid(row=0, column=1, padx=5)
        ttk.Button(path_frame, text="Browse", command=self.browse_sc2).grid(row=0, column=2)

        ttk.Button(path_frame, text="Import Map file", command=self.import_map).grid(row=1, column=1, pady=5, sticky="w")

        # === Section 2: Bot Settings ===
        bot_frame = ttk.LabelFrame(main_frame, text="My Bot Settings", padding="10")
        bot_frame.pack(fill=tk.X, pady=5)

        # Race
        ttk.Label(bot_frame, text="My Race:").grid(row=0, column=0, sticky="w")
        self.bot_race_var = tk.StringVar(value="Zerg")
        race_combo = ttk.Combobox(bot_frame, textvariable=self.bot_race_var, values=["Zerg", "Terran", "Protoss", "Random"])
        race_combo.grid(row=0, column=1, sticky="w", padx=5)
        race_combo.state(["readonly"])

        # Personality
        ttk.Label(bot_frame, text="Playstyle:").grid(row=1, column=0, sticky="w", pady=5)
        self.personality_var = tk.StringVar(value="Standard")
        personalities = [p.value for p in BotPersonality]
        pers_combo = ttk.Combobox(bot_frame, textvariable=self.personality_var, values=personalities)
        pers_combo.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        pers_combo.state(["readonly"])

        # MMR
        ttk.Label(bot_frame, text="Skill MMR (0-9999):").grid(row=2, column=0, sticky="w")
        self.mmr_var = tk.StringVar(value=DEFAULT_MMR)
        ttk.Entry(bot_frame, textvariable=self.mmr_var, width=10).grid(row=2, column=1, sticky="w", padx=5)

        # === Section 3: Match Settings ===
        match_frame = ttk.LabelFrame(main_frame, text="Match Settings", padding="10")
        match_frame.pack(fill=tk.X, pady=5)

        # Opponent Race
        ttk.Label(match_frame, text="Enemy Race:").grid(row=0, column=0, sticky="w")
        self.opp_race_var = tk.StringVar(value="Random")
        ttk.Combobox(match_frame, textvariable=self.opp_race_var, values=["Terran", "Zerg", "Protoss", "Random"], state="readonly").grid(row=0, column=1, sticky="w", padx=5)

        # Difficulty
        ttk.Label(match_frame, text="Difficulty:").grid(row=1, column=0, sticky="w", pady=5)
        self.diff_var = tk.StringVar(value="VeryHard")
        diffs = ["VeryEasy", "Easy", "Medium", "Hard", "VeryHard", "CheatVision", "CheatMoney", "CheatInsane"]
        ttk.Combobox(match_frame, textvariable=self.diff_var, values=diffs, state="readonly").grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Map
        ttk.Label(match_frame, text="Map:").grid(row=2, column=0, sticky="w")
        self.map_var = tk.StringVar(value="(Random)")
        # Ideally we'd scan the maps folder, but for now allow typing or random
        ttk.Entry(match_frame, textvariable=self.map_var, width=30).grid(row=2, column=1, sticky="w", padx=5)

        # === Launch ===
        btn_frame = ttk.Frame(main_frame, padding="20")
        btn_frame.pack(fill=tk.X)

        self.launch_btn = ttk.Button(btn_frame, text="LAUNCH GAME", command=self.launch_game)
        self.launch_btn.pack(fill=tk.X, ipady=10)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var, foreground="gray").pack(side=tk.BOTTOM)

    def browse_sc2(self):
        path = filedialog.askdirectory(initialdir=self.sc2_path_var.get(), title="Select StarCraft II Directory")
        if path:
            self.sc2_path_var.set(path)

    def import_map(self):
        file_path = filedialog.askopenfilename(filetypes=[("SC2 Maps", "*.SC2Map")])
        if file_path:
            sc2_path = self.sc2_path_var.get()
            maps_dir = os.path.join(sc2_path, "Maps")
            if not os.path.exists(maps_dir):
                # Try to create it or ask user
                try:
                    os.makedirs(maps_dir)
                except Exception as e:
                    messagebox.showerror("Error", f"Could not find or create Maps directory at:\n{maps_dir}\n\nError: {e}")
                    return

            try:
                shutil.copy(file_path, maps_dir)
                filename = os.path.basename(file_path)
                messagebox.showinfo("Success", f"Imported {filename} to Maps folder.")
                self.map_var.set(filename.replace(".SC2Map", ""))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import map: {e}")

    def launch_game(self):
        # Validate inputs
        try:
            mmr = int(self.mmr_var.get())
            if not (0 <= mmr <= 9999): raise ValueError
        except ValueError:
            messagebox.showerror("Error", "MMR must be a number between 0 and 9999")
            return

        # Construct arguments
        args = [sys.executable]

        # If frozen (exe), sys.executable is the exe. We need to call it with args.
        # If running from source, sys.executable is python.exe, so we need "run.py".
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            pass
        else:
            # Running as script
            # We assume 'launcher.py' is in the same dir as 'run.py'
            script_dir = os.path.dirname(os.path.abspath(__file__))
            run_script = os.path.join(script_dir, "run.py") # Use run.py which imports main
            # Or better, just point to 'launcher.py' itself if we update launcher.py to dispatch
            # But earlier I decided launcher.py imports run_bot_main.
            # So if I run "python launcher.py arg", it works.
            args.append(sys.argv[0]) # This is launcher.py

        args.extend([
            "--bot-race", self.bot_race_var.get(),
            "--mmr", str(mmr),
            "--personality", self.personality_var.get(),
            "--opponent-race", self.opp_race_var.get(),
            "--difficulty", self.diff_var.get(),
            "--sc2-path", self.sc2_path_var.get()
        ])

        if self.map_var.get() and self.map_var.get() != "(Random)":
            args.extend(["--map", self.map_var.get()])

        # Disable button
        self.launch_btn.configure(state="disabled")
        self.status_var.set("Running...")

        # Run in thread
        threading.Thread(target=self._run_process, args=(args,), daemon=True).start()

    def _run_process(self, args):
        try:
            # subprocess.run blocks this thread, which is fine as it's a worker thread
            # Creation flags for Windows to hide console window?
            # If we want to see output, we shouldn't hide it.
            # For a polished app, maybe capture output and show in a text box?
            # For now, let it pop up a console or inherit.
            subprocess.run(args, check=True)
            self.status_var.set("Game Finished.")
        except subprocess.CalledProcessError as e:
            self.status_var.set(f"Error: Game crashed (Code {e.returncode})")
        except Exception as e:
            self.status_var.set(f"Error: {e}")
        finally:
            self.after(0, lambda: self.launch_btn.configure(state="normal"))

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
