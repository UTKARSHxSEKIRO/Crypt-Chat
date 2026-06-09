import sys
import tkinter as tk
from ui import CryptChatApp
import cli

def main():
    # Detect the headless initialization flag in terminal arguments
    if "--cli" in sys.argv:
        try:
            cli.run_cli()
        except KeyboardInterrupt:
            print("\n[System] Exiting headless session cleanly.")
            sys.exit(0)
    else:
        # Fall back to standard Graphical User Interface layout
        root = tk.Tk()
        app = CryptChatApp(root)
        root.mainloop()

if __name__ == "__main__":
    main()