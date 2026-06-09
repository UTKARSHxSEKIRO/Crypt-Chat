import sys
import tkinter as tk
from ui import CryptChatApp
import cli 

def main():
    # Check for the presence of the CLI flag execution
    if "--cli" in sys.argv:
        print("Launching Crypt-Chat in Headless CLI Mode...")
        cli.run_cli()
    else:
        # Fallback to standard Graphical User Interface
        root = tk.Tk()
        app = CryptChatApp(root)
        root.mainloop()

if __name__ == "__main__":
    main()