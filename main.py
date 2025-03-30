import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from simulator import BioethanolSimulator

class FermentationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bioethanol Fermentation Simulator")
        self.root.geometry("1000x700")
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 10))
        self.style.configure('TButton', font=('Helvetica', 10))
        
        # Initialize simulator
        self.simulator = BioethanolSimulator()
        
        # Colors
        self.bg_color = '#f0f0f0'
        self.input_bg = '#e6f3ff'
        self.output_bg = '#fff2e6'
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Input Section
        input_frame = ttk.LabelFrame(main_frame, text="INPUT PARAMETERS", padding=15)
        input_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        input_frame.configure(style='TFrame')
        
        # Input fields
        self.create_input_field(input_frame, "Initial Substrate (S₀, g/L):", 'S0', 0)
        self.create_input_field(input_frame, "Broth Volume (V, L):", 'V', 1)
        self.create_input_field(input_frame, "Initial Biomass (X₀, g/L):", 'X0', 2)
        self.create_input_field(input_frame, "Impeller Speed (N, rpm):", 'N', 3)
        self.create_input_field(input_frame, "Fermentation Time (t, hrs):", 't', 4)
        
        # Run button
        ttk.Button(input_frame, text="RUN SIMULATION", command=self.run_simulation, 
                  style='TButton').grid(row=5, column=0, columnspan=2, pady=15)
        
        # Output Section
        output_frame = ttk.LabelFrame(main_frame, text="SIMULATION RESULTS", padding=15)
        output_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # Output text
        self.output_text = tk.Text(output_frame, height=8, width=60, wrap=tk.WORD, 
                                 font=('Courier', 10), bg=self.output_bg)
        self.output_text.grid(row=0, column=0, sticky="nsew")
        
        # Plot Section
        plot_frame = ttk.LabelFrame(main_frame, text="VISUALIZATION", padding=15)
        plot_frame.grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky="nsew")
        
        # Create figure
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 6))
        plt.tight_layout()
        
        # Canvas for plot
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
    def create_input_field(self, frame, label_text, field_name, row):
        ttk.Label(frame, text=label_text).grid(row=row, column=0, sticky="w", pady=5)
        entry = ttk.Entry(frame)
        entry.grid(row=row, column=1, pady=5)
        setattr(self, f"{field_name}_entry", entry)
        
    def run_simulation(self):
        # Clear previous outputs
        self.output_text.delete(1.0, tk.END)
        
        try:
            # Get inputs
            inputs = {
                'S0': float(self.S0_entry.get()),
                'V': float(self.V_entry.get()),
                'X0': float(self.X0_entry.get()),
                'N': float(self.N_entry.get()),
                't': float(self.t_entry.get())
            }
            
            # Run simulation
            results, outputs = self.simulator.run_simulation(inputs)
            
            # Display outputs
            output_str = (
                f"FINAL BIOMASS (X): {outputs['X_final']:.2f} g/L\n"
                f"FINAL SUBSTRATE (S): {outputs['S_final']:.2f} g/L\n"
                f"ETHANOL CONCENTRATION (P): {outputs['P_final']:.2f} g/L\n"
                f"TOTAL ETHANOL PRODUCED: {outputs['P_total']:.2f} g\n"
                f"UNIT COST: ${outputs['unit_cost']:.4f} per gram"
            )
            self.output_text.insert(tk.END, output_str)
            
            # Update plots
            self.update_plots(results)
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Simulation failed: {str(e)}")
    
    def update_plots(self, results):
        self.ax1.clear()
        self.ax2.clear()
        
        # Biomass and Substrate plot
        self.ax1.plot(results['time'], results['X'], 'g-', label='Biomass (X)')
        self.ax1.plot(results['time'], results['S'], 'b-', label='Substrate (S)')
        self.ax1.set_ylabel('Concentration (g/L)')
        self.ax1.legend()
        self.ax1.grid(True)
        
        # Ethanol plot
        self.ax2.plot(results['time'], results['P'], 'r-', label='Ethanol (P)')
        self.ax2.set_xlabel('Time (hours)')
        self.ax2.set_ylabel('Ethanol (g/L)')
        self.ax2.legend()
        self.ax2.grid(True)
        
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = FermentationApp(root)
    root.mainloop()