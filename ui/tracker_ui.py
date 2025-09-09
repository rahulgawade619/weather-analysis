import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from core.analysis import (
    load_weather_data,
    calculate_monthly_averages,
    get_hottest_month,
    get_rainiest_month,
    get_monthly_trends,
    calculate_monthly_rainfall,
    export_to_csv,
    filter_by_month
)
import os
import numpy as np


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌤️ Weather Data Analyzer")
        self.root.geometry("1100x750")
        self.root.configure(bg="#f0f4fa")

        self.data = None
        self.months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        self.create_widgets()

    def create_widgets(self):
        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("TLabel", background="#f0f4fa")

        title = ttk.Label(self.root, text="📊 Weather Analyzer Dashboard", font=("Segoe UI", 20, "bold"))
        title.pack(pady=12)

        # Controls Frame
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10)

        ttk.Button(control_frame, text="📂 Load Data", command=self.load_data).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="📈 Show Analysis", command=self.show_analysis).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="📊 Show Charts", command=self.show_charts).grid(row=0, column=2, padx=5)
        ttk.Button(control_frame, text="📁 Export CSV", command=self.export_csv).grid(row=0, column=3, padx=5)

        # Search by month
        ttk.Label(control_frame, text="🔍 Filter by Month:").grid(row=0, column=4, padx=5)
        self.month_var = tk.StringVar()
        month_dropdown = ttk.Combobox(control_frame, textvariable=self.month_var, values=self.months, state="readonly", width=8)
        month_dropdown.grid(row=0, column=5)
        month_dropdown.set("Jan")
        ttk.Button(control_frame, text="Go", command=self.search_by_month).grid(row=0, column=6, padx=5)

        # Output
        output_label = ttk.Label(self.root, text="📋 Output Console:", font=("Segoe UI", 12, "bold"))
        output_label.pack(anchor="w", padx=20)
        self.output = tk.Text(self.root, height=15, width=130, font=("Consolas", 10))
        self.output.pack(padx=20, pady=10)

        # Chart
        chart_label = ttk.Label(self.root, text="📈 Weather Trends Chart:", font=("Segoe UI", 12, "bold"))
        chart_label.pack(anchor="w", padx=20, pady=(10, 0))
        self.chart_frame = ttk.Frame(self.root)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def load_data(self):
        path = filedialog.askopenfilename(
            title="Select Weather CSV File",
            filetypes=[("CSV files", "*.csv")],
            initialdir=os.path.join(os.getcwd(), "assets")
        )
        if path:
            try:
                self.data = load_weather_data(path)
                messagebox.showinfo("Success", f"✅ Loaded: {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def show_analysis(self):
        if self.data is None:
            messagebox.showwarning("No Data", "⚠️ Please load data first.")
            return

        self.output.delete(1.0, tk.END)
        months, avg_temps, avg_rains, avg_humids = calculate_monthly_averages(self.data)

        self.output.insert(tk.END, "\n📋 Average Weather Data Per Month:\n")
        for i, m in enumerate(months):
            line = f"{self.months[i % 12]} - Temp: {avg_temps[i]:.2f}°C, Rain: {avg_rains[i]:.2f}mm"
            if avg_humids:
                line += f", Humidity: {avg_humids[i]:.2f}%"
            self.output.insert(tk.END, line + "\n")

        hottest_month, max_temp = get_hottest_month(self.data)
        rainiest_month, max_rain = get_rainiest_month(self.data)

        self.output.insert(tk.END, f"\n🔥 Hottest Month: {self.months[hottest_month - 1]} ({max_temp:.2f}°C)")
        self.output.insert(tk.END, f"\n🌧️ Rainiest Month: {self.months[rainiest_month - 1]} ({max_rain:.2f}mm)\n")

    def show_charts(self):
        if self.data is None:
            messagebox.showwarning("No Data", "⚠️ Please load data first.")
            return

        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        months, avg_temps, avg_rains, _ = calculate_monthly_averages(self.data)

        fig, ax1 = plt.subplots(figsize=(8, 4))
        ax1.plot(months, avg_temps, marker='o', label='Avg Temp (°C)', color='tomato')
        ax1.plot(months, avg_rains, marker='s', label='Avg Rainfall (mm)', color='dodgerblue')
        ax1.set_xticks(months)
        ax1.set_xticklabels([self.months[int(m) - 1] for m in months])
        ax1.set_title("Monthly Weather Trends")
        ax1.set_xlabel("Month")
        ax1.set_ylabel("Values")
        ax1.legend()
        ax1.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def export_csv(self):
        if self.data is None:
            messagebox.showwarning("No Data", "⚠️ Please load data first.")
            return

        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filepath:
            export_to_csv(self.data, filepath)
            messagebox.showinfo("Exported", f"✅ Data exported to {filepath}")

    def search_by_month(self):
        if self.data is None:
            messagebox.showwarning("No Data", "⚠️ Please load data first.")
            return

        month_name = self.month_var.get()
        if month_name:
            month_index = self.months.index(month_name) + 1
            filtered = filter_by_month(self.data, month_index)

            self.output.delete(1.0, tk.END)
            self.output.insert(tk.END, f"📅 Weather data for {month_name}:\n")
            for row in filtered:
                line = ", ".join(f"{val:.2f}" for val in row)
                self.output.insert(tk.END, line + "\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
