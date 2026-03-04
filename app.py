"""
MSK AI Data Collection Tool
Entry point — run this file to launch the application.
"""
import customtkinter as ctk

# Must be set BEFORE any CTk widgets are created
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

from ui.main_window import MainWindow


def main():
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
