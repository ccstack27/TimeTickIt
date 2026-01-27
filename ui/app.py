import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import os
import json
from PIL import Image, ImageTk

from core.engine import CoreEngine, SystemState, MAX_INACTIVITY_SECONDS
from core.session import SessionEndReason
from output.generator import OutputGenerator

CONFIG_FILE = "config.json"
AVATARS = ["cat.png", "dog.png", "fox.png", "panda.png"]
ASSETS_DIR = "assets"

class TimeTickItApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TimeTickIt")
        self.root.geometry("500x600")
        
        self.engine = CoreEngine()
        self.generator = OutputGenerator()
        
        self.load_config()
        self.setup_ui()
        self.update_loop()
        
        # Bind keyboard and mouse to reset inactivity
        self.root.bind_all("<Key>", lambda e: self.engine.handle_input())
        self.root.bind_all("<Motion>", lambda e: self.engine.handle_input())
        self.root.bind_all("<Button>", lambda e: self.engine.handle_input())

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self.config = json.load(f)
            except:
                self.config = {"user_name": "Employee", "avatar_index": 0}
        else:
            self.config = {"user_name": "Employee", "avatar_index": 0}
        
        self.user_name_var = tk.StringVar(value=self.config.get("user_name", "Employee"))
        self.avatar_index = self.config.get("avatar_index", 0)

    def save_config(self):
        self.config["user_name"] = self.user_name_var.get()
        self.config["avatar_index"] = self.avatar_index
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f)

    def setup_ui(self):
        # Avatar
        self.avatar_label = tk.Label(self.root)
        self.avatar_label.pack(pady=10)
        self.avatar_label.bind("<Button-1>", self.cycle_avatar)
        self.update_avatar_display()
        
        # User Name (Editable)
        name_frame = tk.Frame(self.root)
        name_frame.pack(pady=5)
        tk.Label(name_frame, text="User Name:").pack(side=tk.LEFT)
        name_entry = tk.Entry(name_frame, textvariable=self.user_name_var)
        name_entry.pack(side=tk.LEFT, padx=5)
        name_entry.bind("<FocusOut>", lambda e: self.save_config())
        
        # Divider
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', padx=20, pady=10)
        
        # State Display
        self.state_label = tk.Label(self.root, font=("Helvetica", 14, "bold"))
        self.state_label.pack(pady=5)
        
        # Timing Information
        self.timing_info_label = tk.Label(self.root, font=("Helvetica", 10))
        self.timing_info_label.pack(pady=5)
        
        # Inactivity Feedback
        self.inactivity_label = tk.Label(self.root, font=("Helvetica", 10, "italic"), fg="red")
        self.inactivity_label.pack(pady=5)
        
        # Task Entry
        task_frame = tk.Frame(self.root)
        task_frame.pack(pady=5)
        tk.Label(task_frame, text="Task (optional):").pack(side=tk.LEFT)
        self.task_var = tk.StringVar()
        self.task_entry = tk.Entry(task_frame, textvariable=self.task_var)
        self.task_entry.pack(side=tk.LEFT, padx=5)
        
        # Controls
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=20)
        
        self.start_btn = tk.Button(control_frame, text="Start Session", command=self.start_session, width=15)
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_btn = tk.Button(control_frame, text="Stop Session", command=self.stop_session, width=15)
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        # Output Trigger
        self.output_btn = tk.Button(self.root, text="Generate Output", command=self.generate_output)
        self.output_btn.pack(pady=20)

    def cycle_avatar(self, event):
        self.avatar_index = (self.avatar_index + 1) % len(AVATARS)
        self.update_avatar_display()
        self.save_config()

    def update_avatar_display(self):
        avatar_path = os.path.join(ASSETS_DIR, AVATARS[self.avatar_index])
        if os.path.exists(avatar_path):
            img = Image.open(avatar_path)
            img = img.resize((100, 100), Image.LANCZOS)
            self.avatar_photo = ImageTk.PhotoImage(img)
            self.avatar_label.config(image=self.avatar_photo)
        else:
            self.avatar_label.config(text="[Avatar]")

    def start_session(self):
        self.engine.start_session(task=self.task_var.get())
        self.task_entry.config(state=tk.DISABLED)

    def stop_session(self):
        self.engine.stop_session()
        self.task_entry.config(state=tk.NORMAL)
        self.task_var.set("")

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
                    user_name=self.user_name_var.get()
                )
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

        # Update UI elements
        self.state_label.config(text=f"STATE: {self.engine.state.name}")
        
        if self.engine.state == SystemState.ACTIVE:
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            s = self.engine.active_session
            elapsed = int((datetime.now() - s.start_time).total_seconds())
            start_str = s.start_time.strftime('%H:%M:%S')
            self.timing_info_label.config(text=f"Session Start: {start_str} | Elapsed: {elapsed}s")
            
            # Inactivity feedback
            if self.engine.inactivity_timer_seconds > 0:
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

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTickItApp(root)
    
    def on_closing():
        app.engine.handle_interruption()
        # Note: If we had persistence for completed sessions, we'd save them here.
        # But the doc doesn't explicitly mention persistence of history yet, 
        # just that the app terminates and records last known time.
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
