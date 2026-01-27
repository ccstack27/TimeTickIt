import tkinter as tk
from ui.app import TimeTickItApp

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTickItApp(root)
    
    def on_closing():
        app.engine.handle_interruption()
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
