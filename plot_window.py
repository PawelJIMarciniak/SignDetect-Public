import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PlotWindow:
    def __init__(self, root, probability_tracker):
        self.plot_toplevel , self.fig, self.ax, self.canvas = None, None, None, None
        self.create_plot_window()

        self.root = root
        self.probability_tracker = probability_tracker

    def create_plot_window(self):
        self.plot_toplevel  = tk.Toplevel()
        self.plot_toplevel .title("Probability Graph")

        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.ax.set_title("Probability of sign over time")
        self.ax.set_xlabel("Time (frame count)")
        self.ax.set_ylabel("Probability (%)")
        self.ax.set_ylim(0, 100)

        plt.subplots_adjust(right=0.8)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_toplevel )
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def update_plot(self, predictions):
        if not (self.ax and self.canvas):
            return

        for sign, prob in predictions.items():
            if sign not in self.probability_tracker:
                self.probability_tracker[sign] = []
            self.probability_tracker[sign].append(prob * 100)

            if len(self.probability_tracker[sign]) > 100:
                self.probability_tracker[sign] = self.probability_tracker[sign][-100:]

        self.ax.cla()
        self.ax.set_title("Probability of sign over time")
        self.ax.set_xlabel("Time (frame count)")
        self.ax.set_ylabel("Probability (%)")
        self.ax.set_ylim(0, 100)

        for sign, history in self.probability_tracker.items():
            self.ax.plot(history, label=sign)

        self.ax.legend(loc="upper left", bbox_to_anchor=(1.05, 1.15), fontsize='xx-small', frameon=True)
        self.canvas.draw()

    def on_closing(self):
        if self.plot_toplevel :
            self.plot_toplevel.destroy()
            self.plot_toplevel = None
        self.root.destroy()