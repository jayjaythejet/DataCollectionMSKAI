"""
MSK Knee Data Collection Tool
Entry point — run this file to launch the knee scoring application.
"""
import customtkinter as ctk

# Must be set BEFORE any CTk widgets are created
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

from configs.knee import KNEE_CONFIG
from ui.main_window import MainWindow


def main():
    app = MainWindow(config=KNEE_CONFIG)
    app.mainloop()


if __name__ == "__main__":
    main()
