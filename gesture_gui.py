import os
import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from plot_window import PlotWindow


class GestureGUI:
    def __init__(self, toggle_recording, record_single_frame, toggle_live_view, probability_tracker, signs_dict):
        # Create the main application window
        self.root = tk.Tk()
        self.root.geometry("800x1000")
        self.root.resizable(False, False)
        self.root.title("Sign Language Recognition")

        # Theme setup
        self.theme = None
        self.load_theme()
        self.available_themes = ["Dark Theme", "Light Theme", "System Theme"]
        self.selected_theme = tk.StringVar(value="Dark Theme")

        # Main container frame
        self.main_frame = ttk.Frame(self.root, width=780, height=950)
        self.main_frame.pack_propagate(False)
        self.main_frame.pack(padx=10, pady=10)

        # Video display
        #self.video_frame = ttk.Frame(self.main_frame, width=640, height=480, style="VideoFrame.TFrame")
        self.video_frame = tk.Frame(self.main_frame, width=640, height=480, bg="gray", highlightthickness=5, highlightbackground="gray")
        self.video_frame.pack_propagate(False)
        self.video_frame.pack(pady=10)

        self.video_label = ttk.Label(self.video_frame, borderwidth=0, padding=0)
        #elf.video_label.pack()
        self.video_label.pack(fill=tk.BOTH, expand=True)

        # Buttons
        self.create_buttons(toggle_recording, record_single_frame, toggle_live_view)

        # Results table
        self.result_table = self.create_result_table()

        # Plot window and canvas
        self.plot_window = PlotWindow(self.root, probability_tracker)

        # Store references to external resources
        self.highlight_video_frame("gray")
        self.signs_dict = signs_dict
        self.last_processed_frame = None

        self.root.protocol("WM_DELETE_WINDOW", self.plot_window.on_closing)

    def load_theme(self):
        azure_tcl_path = os.path.join(os.path.dirname(__file__), 'themes', 'Azure-ttk-theme-main', 'azure.tcl')
        self.root.tk.call("source", azure_tcl_path)
        self.theme = "dark"
        self.root.tk.call("set_theme", "dark")

    def create_buttons(self, toggle_recording, record_single_frame, toggle_live_view):
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.pack(pady=10)
        buttons_frame.pack_propagate(False)
        buttons_frame.configure(width=800, height=50)

        self.record_button = ttk.Button(
            buttons_frame, text="Start Recording",
            command=toggle_recording,
            width=20
        )
        self.record_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            buttons_frame, text="Check Single Frame",
            command=record_single_frame,
            width=20
        ).pack(side=tk.LEFT, padx=5)

        self.toggle_view_button = ttk.Button(
            buttons_frame, text="Show Last Frame",
            command=toggle_live_view,
            state=tk.NORMAL,
            width=20
        )
        self.toggle_view_button.pack(side=tk.LEFT, padx=5)

        theme_frame = ttk.Frame(buttons_frame)
        theme_frame.pack(side=tk.LEFT, padx=5)
        theme_frame.pack_propagate(False)
        theme_frame.configure(width=160, height=30)

        theme_selector = ttk.Combobox(
            theme_frame,
            textvariable=self.selected_theme,
            values=["Dark Theme", "Light Theme", "System Theme"],
            state="readonly",
            width=20
        )
        theme_selector.pack()
        theme_selector.bind("<<ComboboxSelected>>", lambda e: self.apply_selected_theme())

        self.toggle_plot_button = ttk.Button(
            buttons_frame,
            text="Hide Plot",
            command=self.toggle_plot_window,
            width=20
        )
        self.toggle_plot_button.pack(side=tk.LEFT, padx=5)

    def apply_selected_theme(self):
        theme_map = {
            "Dark Theme": "dark",
            "Light Theme": "light",
            "System Theme": "system"
        }
        selected = self.selected_theme.get()
        theme_value = theme_map.get(selected, "dark")
        self.root.tk.call("set_theme", theme_value)

    def activate_toggle_view_button(self):
        current_state = self.toggle_view_button.cget("state")
        new_state = tk.NORMAL if current_state == tk.DISABLED else tk.DISABLED
        self.toggle_view_button.config(state=new_state)

    def toggle_plot_window(self):
        if not self.plot_window.plot_toplevel:
            self.plot_window.create_plot_window()

        self.plot_toplevel = None
        if self.plot_window.plot_toplevel is not None and self.plot_window.plot_toplevel.state() != 'withdrawn':
            self.plot_window.plot_toplevel.withdraw()
            self.toggle_plot_button.config(text="Show Plot")
        else:
            if self.plot_window.plot_toplevel is None:
                self.plot_window.create_plot_window()
            else:
                self.plot_window.plot_toplevel.deiconify()
            self.toggle_plot_button.config(text="Hide Plot")

    def create_result_table(self):
        table_frame = ttk.Frame(self.main_frame, width=260, height=250)
        table_frame.pack_propagate(False)
        table_frame.pack(pady=10)

        result_table = ttk.Treeview(
            table_frame,
            columns=("Rank", "Sign", "Probability"),
            show="headings",
            height=10
        )

        result_table.heading("Rank", text="Rank", command=lambda: self.sort_table(result_table, "Rank", False))
        result_table.heading("Sign", text="Sign", command=lambda: self.sort_table(result_table, "Sign", False))
        result_table.heading("Probability", text="Probability (%)", command=lambda: self.sort_table(result_table, "Probability", False))

        result_table.column("Rank", width=50, anchor=tk.CENTER, stretch=False)
        result_table.column("Sign", width=100, anchor=tk.CENTER, stretch=False)
        result_table.column("Probability", width=100, anchor=tk.CENTER, stretch=False)

        # result_table.pack(pady=10, ipadx=10)
        result_table.pack()
        return result_table

    def sort_table(self, result_table, col, descending):
        data = [(result_table.set(item, col), item) for item in result_table.get_children('')]

        if col == "Rank":
            data = [(int(value), item) for value, item in data]
        elif col == "Sign":
            value_to_index = {v: k for k, v in self.signs_dict.items()}
            data = [(value_to_index.get(value, float('inf')), item) for value, item in data]
        elif col == "Probability":
            data = [(float(value), item) for value, item in data]

        data.sort(reverse=descending)

        for index, (value, item) in enumerate(data):
            result_table.move(item, '', index)

        result_table.heading(col, command=lambda: self.sort_table(result_table, col, not descending))

    def highlight_video_frame(self, color: str):
        #style = ttk.Style()
        #style.configure("VideoFrame.TFrame", borderwidth=5, relief="solid", bordercolor=color)
        #self.video_frame.configure(style="VideoFrame.TFrame")
        self.video_frame.config(highlightbackground=color)

    def display_image(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)
        self.video_label.configure(image=image)
        self.video_label.image = image

    def display_predictions(self, predictions):
        if not predictions:
            return

        self.update_result_table(predictions)
        self.plot_window.update_plot(predictions)

    def update_result_table(self, predictions):
        for item in self.result_table.get_children():
            self.result_table.delete(item)

        sorted_predictions = sorted(predictions.items(), key=lambda x: x[1], reverse=True)

        for rank, (sign, prob) in enumerate(sorted_predictions, start=1):
            self.result_table.insert("", tk.END, values=(rank, sign, f"{prob * 100:.2f}"))

    def on_closing(self):
        if self.plot_window:
            self.plot_window.plot_toplevel.destroy()
        self.root.destroy()
