import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import os
import json
import webbrowser
from PIL import Image, ImageTk
from pynput import mouse, keyboard
import sys
from pathlib import Path

from core.engine import CoreEngine, SystemState, MAX_INACTIVITY_SECONDS
from core.session import SessionEndReason
from output.generator import OutputGenerator

def _app_base_dir() -> Path:
    """
    Returns the directory that contains bundled app resources.
    - PyInstaller: sys._MEIPASS (temp unpack folder)
    - Normal run: project root (based on this file's location)
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent

def _user_data_dir() -> Path:
    """
    Per-user writable data location on Windows.
    """
    base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    return Path(base) / "TimeTickIt"

APP_BASE_DIR = _app_base_dir()
USER_DATA_DIR = _user_data_dir()
CONFIG_FILE = USER_DATA_DIR / "config.json"

AVATARS = ["cat.png", "dog.png", "fox.png", "panda.png"]
ASSETS_DIR = APP_BASE_DIR / "assets"

class TimeTickItApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TimeTickIt")
        self.root.geometry("320x400")
        
        self.engine = CoreEngine()
        self.generator = OutputGenerator()
        
        self.load_config()
        self.setup_ui()
        self.update_loop()
        
        # Global listeners for keyboard and mouse to reset inactivity
        self.mouse_listener = mouse.Listener(on_move=self.on_input, on_click=self.on_input, on_scroll=self.on_input)
        self.key_listener = keyboard.Listener(on_press=self.on_input)
        self.mouse_listener.start()
        self.key_listener.start()

    def on_input(self, *args):
        self.engine.handle_input()
        if hasattr(self, 'inactivity_label'):
            self.root.after_idle(lambda: self.inactivity_label.config(text=""))

    def load_config(self):
        USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Migration: if an old config exists next to the app but the new one doesn't, use old once.
        legacy_config = Path("config.json")
        if not CONFIG_FILE.exists() and legacy_config.exists():
            try:
                CONFIG_FILE.write_text(legacy_config.read_text(encoding="utf-8"), encoding="utf-8")
            except Exception:
                pass

        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except Exception:
                self.config = {"user_name": "Employee", "avatar_index": 0, "hourly_rate": 0.0}
        else:
            self.config = {"user_name": "Employee", "avatar_index": 0, "hourly_rate": 0.0}
        
        self.user_name_var = tk.StringVar(value=self.config.get("user_name", "Employee"))
        self.hourly_rate_var = tk.StringVar(value=str(self.config.get("hourly_rate", 0.0)))
        self.avatar_index = self.config.get("avatar_index", 0)

        # Restore completed sessions
        saved_sessions = self.config.get("completed_sessions", [])
        from core.session import Session
        self.engine.completed_sessions = [Session.from_dict(s) for s in saved_sessions]

    def save_config(self):
        USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

        self.config["user_name"] = self.user_name_var.get()
        try:
            self.config["hourly_rate"] = float(self.hourly_rate_var.get())
        except ValueError:
            self.config["hourly_rate"] = 0.0
        self.config["avatar_index"] = self.avatar_index
        
        # Save completed sessions
        self.config["completed_sessions"] = [s.to_dict() for s in self.engine.completed_sessions]
        
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f)

    def create_menu_bar(self):
        menubar = tk.Menu(self.root)

        # Account Menu
        account_menu = tk.Menu(menubar, tearoff=0)
        account_menu.add_command(label="See Record", command=self.show_record)
        menubar.add_cascade(label="Account", menu=account_menu)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="How to Use", command=self.open_how_to_use)
        help_menu.add_command(label="About", command=self.open_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def open_how_to_use(self):
        webbrowser.open("https://github.com/ccstack27/TimeTickIt/blob/main/README.md")

    def open_about(self):
        webbrowser.open("https://github.com/ccstack27/TimeTickIt/blob/main/docs/00_about.md")

    def show_record(self):
        record_window = tk.Toplevel(self.root)
        record_window.title("Account Record")
        record_window.geometry("400x300")
        
        # Use a canvas with a scrollbar in case there are many sessions
        main_frame = tk.Frame(record_window)
        main_frame.pack(fill=tk.BOTH, expand=1)

        canvas = tk.Canvas(main_frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        content_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=content_frame, anchor="nw")

        tk.Label(content_frame, text="Session History", font=("Helvetica", 12, "bold")).pack(pady=10)

        total_seconds = 0
        if not self.engine.completed_sessions:
            tk.Label(content_frame, text="No recorded sessions yet.").pack(pady=5)
        else:
            for i, session in enumerate(self.engine.completed_sessions):
                duration = session.get_duration_seconds()
                total_seconds += duration
                
                hours, remainder = divmod(duration, 3600)
                minutes, seconds = divmod(remainder, 60)
                duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                
                start_str = session.start_time.strftime('%Y-%m-%d %H:%M:%S')
                task_text = f"Task: {session.task}" if session.task else "Task: [No Task]"
                
                session_text = f"{i+1}. {start_str} | Duration: {duration_str}\n   {task_text}"
                tk.Label(content_frame, text=session_text, justify=tk.LEFT, anchor="w").pack(fill=tk.X, padx=10, pady=2)

        # Accumulated Time at the bottom
        total_hours, total_remainder = divmod(total_seconds, 3600)
        total_minutes, total_seconds_final = divmod(total_remainder, 60)
        total_time_str = f"{total_hours:02d}:{total_minutes:02d}:{total_seconds_final:02d}"

        tk.Label(record_window, text=f"Accumulated Session Time: {total_time_str}", font=("Helvetica", 10, "bold")).pack(pady=10)

    def setup_ui(self):
        self.root.columnconfigure(0, weight=1)
        
        # Menu Bar
        self.create_menu_bar()

        # Empty grid at the top
        tk.Label(self.root, text="").grid(row=0, column=0, columnspan=2)

        # Avatar
        self.avatar_label = tk.Label(self.root)
        self.avatar_label.grid(row=1, column=0, rowspan=4)
        self.avatar_label.bind("<Button-1>", self.cycle_avatar)
        self.update_avatar_display()
        
        # User Name (Editable)
        name_frame = tk.Frame(self.root)
        name_frame.grid(row=1, column=1, sticky='w')
        tk.Label(name_frame, text="Name:").grid(row=0, column=0)
        self.name_entry = tk.Entry(name_frame, textvariable=self.user_name_var, highlightthickness=0)
        self.name_entry.grid(row=0, column=1, padx=8)
        self.name_entry.bind("<FocusOut>", lambda e: self.save_config())

        # Hourly Rate (Editable)
        rate_frame = tk.Frame(self.root)
        rate_frame.grid(row=2, column=1, sticky='w')
        tk.Label(rate_frame, text="Rate:").grid(row=0, column=0)
        self.rate_entry = tk.Entry(rate_frame, textvariable=self.hourly_rate_var, highlightthickness=0)
        self.rate_entry.grid(row=0, column=1, padx=17)
        self.rate_entry.bind("<FocusOut>", lambda e: self.save_config())

        # Task Entry
        task_frame = tk.Frame(self.root)
        task_frame.grid(row=3, column=1, sticky='w')
        tk.Label(task_frame, text="Task:").grid(row=0, column=0)
        self.task_var = tk.StringVar()
        self.task_entry = tk.Entry(task_frame, textvariable=self.task_var, highlightthickness=0)
        self.task_entry.grid(row=0, column=1, padx=16)

        # Divider
        ttk.Separator(self.root, orient='horizontal').grid(row=6, column=0, sticky='ew', padx=20, pady=10, columnspan=2)
        
        # State Display
        self.state_label = tk.Label(self.root, font=("Helvetica", 14, "bold"))
        self.state_label.grid(row=7, column=0, pady=5, columnspan=2)
        
        # Timing Information
        self.timing_info_label = tk.Label(self.root, font=("Helvetica", 10))
        self.timing_info_label.grid(row=8, column=0, pady=5, columnspan=2)
        
        # Inactivity Feedback
        self.inactivity_label = tk.Label(self.root, font=("Helvetica", 10, "italic"), fg="red")
        self.inactivity_label.grid(row=9, column=0, pady=5, columnspan=2)
        
        # Controls
        control_frame = tk.Frame(self.root)
        control_frame.grid(row=10, column=0, pady=10, columnspan=2)
        
        self.start_btn = tk.Button(control_frame, text="Start", font=("Arial", 14), command=self.start_session, height=2, width=11)
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.stop_btn = tk.Button(control_frame, text="Stop", font=("Arial", 14), command=self.stop_session, height=2, width=11)
        self.stop_btn.grid(row=0, column=1, padx=5)
        
        # Output Trigger
        self.output_btn = tk.Button(self.root, text="Generate Invoice", font=("Arial", 9), command=self.generate_output, width=37)
        self.output_btn.grid(row=11, column=0, columnspan=2)

    def cycle_avatar(self, event):
        self.avatar_index = (self.avatar_index + 1) % len(AVATARS)
        self.update_avatar_display()
        self.save_config()

    def update_avatar_display(self):
        avatar_path = ASSETS_DIR / AVATARS[self.avatar_index]
        if avatar_path.exists():
            try:
                img = Image.open(avatar_path)
                img = img.resize((100, 100), Image.LANCZOS)
                self.avatar_photo = ImageTk.PhotoImage(img)
                self.avatar_label.config(image=self.avatar_photo, text="")
            except Exception:
                self.avatar_label.config(text="[Error]", image="")
        else:
            self.avatar_label.config(text="[Missing]", image="")

    def start_session(self):
        self.engine.start_session(task=self.task_var.get())
        self.task_entry.config(state=tk.DISABLED)

    def stop_session(self):
        self.engine.stop_session()
        self.task_entry.config(state=tk.NORMAL)
        self.task_var.set("")
        self.save_config()

    def generate_output(self):
        if not self.engine.completed_sessions:
            messagebox.showinfo("Output", "No completed sessions to include in output.")
            return
            
        filename = f"TimeTickIt_Output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        file_path = filedialog.asksaveasfilename(defaultextension=".zip", initialfile=filename)
        
        if file_path:
            try:
                # Add user name to session tasks or pass separately? 
                # The doc says user name is used in output files.
                # Let's assume OutputGenerator could use it if we passed it.
                # For now I'll just generate with current data.
                self.generator.generate_package(
                    self.engine.completed_sessions, 
                    file_path, 
                    user_name=self.user_name_var.get(),
                    hourly_rate=self.config.get("hourly_rate", 0.0)
                )
                self.engine.completed_sessions = []
                self.save_config()
                messagebox.showinfo("Output", f"Output package generated successfully at:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Output Error", f"Failed to generate output: {str(e)}")

    def update_loop(self):
        # Tick the engine
        old_state = self.engine.state
        self.engine.tick()
        
        # Check for auto-end
        if old_state == SystemState.ACTIVE and self.engine.state == SystemState.IDLE:
            # Check why it ended
            last_session = self.engine.completed_sessions[-1] if self.engine.completed_sessions else None
            if last_session and last_session.end_reason == SessionEndReason.INACTIVITY_LIMIT:
                messagebox.showinfo("Notification", "Session ended automatically due to inactivity.")
                self.task_entry.config(state=tk.NORMAL)
                self.task_var.set("")
            self.save_config()

        # Update UI elements
        self.state_label.config(text=f"STATE: {self.engine.state.name}")

        # Locking logic for User Name and Hourly Rate
        if self.engine.state == SystemState.ACTIVE or self.engine.completed_sessions:
            self.name_entry.config(state=tk.DISABLED)
            self.rate_entry.config(state=tk.DISABLED)
        else:
            self.name_entry.config(state=tk.NORMAL)
            self.rate_entry.config(state=tk.NORMAL)
        
        if self.engine.state == SystemState.ACTIVE:
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            s = self.engine.active_session
            elapsed = int((datetime.now() - s.start_time).total_seconds())
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)
            elapsed_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            start_str = s.start_time.strftime('%H:%M:%S')
            self.timing_info_label.config(text=f"Session Start: {start_str} | Elapsed: {elapsed_str}")
            
            # Inactivity feedback
            # Show countdown only after passing 3 minutes (remaining < 3 mins)
            # 5:00 - 3:00 = 2:00 (120 seconds)
            if self.engine.inactivity_timer_seconds > 120:
                remaining = MAX_INACTIVITY_SECONDS - self.engine.inactivity_timer_seconds
                mins, secs = divmod(remaining, 60)
                self.inactivity_label.config(text=f"No activity detected — session will end in {mins:02d}:{secs:02d}")
            else:
                self.inactivity_label.config(text="")
        else:
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.timing_info_label.config(text="No active session")
            self.inactivity_label.config(text="")

        self.root.after(1000, self.update_loop)

    def on_closing(self):
        self.mouse_listener.stop()
        self.key_listener.stop()
        self.engine.handle_interruption()
        self.save_config()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTickItApp(root)
    
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
