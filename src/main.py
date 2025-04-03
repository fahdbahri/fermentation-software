import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from simulator import BioethanolSimulator

class FermentationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bioethanol Fermentation Simulator")
        self.root.geometry("1100x750")
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#e6f0fa')
        self.style.configure('TLabel', background='#e6f0fa', font=('Arial', 11))
        self.style.configure('TButton', font=('Arial', 11, 'bold'), padding=5)
        self.style.configure('Warning.TLabel', foreground='#d9534f', font=('Arial', 9, 'italic'))
        self.style.configure('Header.TLabel', font=('Arial', 14, 'bold'), background='#e6f0fa')
        
        # Initialize simulator
        self.simulator = BioethanolSimulator()
        
        # Create UI
        self.create_widgets()
        
        # Setup validation
        self.setup_validation()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header
        ttk.Label(main_frame, text="Bioethanol Production Simulator", 
                 style='Header.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        # Left Panel (Inputs and Outputs)
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        
        # Input Section
        input_frame = ttk.LabelFrame(left_frame, text="Input Parameters", padding=15)
        input_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input fields
        self.create_input_field(input_frame, "Initial Substrate (S₀, g/L):", 'S0', 0, (1, 500))
        self.create_input_field(input_frame, "Broth Volume (V, L):", 'V', 2, (0.1, 1000))
        self.create_input_field(input_frame, "Initial Biomass (X₀, g/L):", 'X0', 4, (0.01, 10))
        self.create_input_field(input_frame, "Impeller Speed (N, rpm):", 'N', 6, (50, 500))
        self.create_input_field(input_frame, "Fermentation Time (t, hrs):", 't', 8, (1, 168))
        
        # Buttons Frame
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=10, column=0, columnspan=2, pady=15)
        ttk.Button(button_frame, text="Run Simulation", command=self.run_simulation,
                  style='TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Restart", command=self.restart,
                  style='TButton').pack(side=tk.LEFT, padx=5)
        
        # Output Section
        output_frame = ttk.LabelFrame(left_frame, text="Simulation Results", padding=15)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Output text
        self.output_text = tk.Text(output_frame, height=10, width=50, wrap=tk.WORD, 
                                 font=('Courier', 11), bg='#fff9e6', relief=tk.FLAT)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Plot Section
        plot_frame = ttk.LabelFrame(main_frame, text="Process Visualization", padding=15)
        plot_frame.grid(row=1, column=1, sticky="nsew")
        
        # Create figure
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(6, 6))
        self.fig.patch.set_facecolor('#e6f0fa')
        plt.tight_layout(pad=3.0)
        
        # Canvas for plot
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(1, weight=1)
    
    def create_input_field(self, frame, label_text, field_name, row, limits):
        """Create input field with range label"""
        ttk.Label(frame, text=label_text).grid(row=row, column=0, sticky="w", pady=(8, 0))
        
        # Range information
        ttk.Label(frame, text=f"Range: {limits[0]} to {limits[1]}", 
                 style='Warning.TLabel').grid(row=row+1, column=0, sticky="w")
        
        # Input entry
        entry = ttk.Entry(frame, width=15)
        entry.grid(row=row, column=1, pady=(8, 0))
        setattr(self, f"{field_name}_entry", entry)
        
        # Validation label
        validation_label = ttk.Label(frame, text="", style='Warning.TLabel')
        validation_label.grid(row=row+1, column=1, sticky="w")
        setattr(self, f"{field_name}_validation", validation_label)
    
    def setup_validation(self):
        """Bind validation to all input fields"""
        for field in ['S0', 'V', 'X0', 'N', 't']:
            entry = getattr(self, f"{field}_entry")
            entry.bind("<FocusOut>", lambda e, f=field: self.validate_input(f))
    
    def validate_input(self, field_name):
        """Validate a single input field"""
        entry = getattr(self, f"{field_name}_entry")
        validation_label = getattr(self, f"{field_name}_validation")
        
        try:
            value = float(entry.get())
            min_val, max_val = self.simulator.PARAMETER_LIMITS[field_name]
            
            if value < min_val or value > max_val:
                validation_label.config(text=f"Value out of range")
                return False
            else:
                validation_label.config(text="✓ Valid")
                return True
        except ValueError:
            validation_label.config(text="Enter a number")
            return False
    
    def validate_all_inputs(self):
        """Validate all inputs and return True if all are valid"""
        all_valid = True
        for field in ['S0', 'V', 'X0', 'N', 't']:
            if not self.validate_input(field):
                all_valid = False
        return all_valid
    
    def run_simulation(self):
        # Clear previous outputs
        self.output_text.delete(1.0, tk.END)
        
        # Validate all inputs first
        if not self.validate_all_inputs():
            messagebox.showerror("Invalid Inputs", "Please correct the highlighted inputs")
            return
            
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
            
        except Exception as e:
            messagebox.showerror("Error", f"Simulation failed: {str(e)}")
    
    def restart(self):
        """Reset all inputs and outputs"""
        for field in ['S0', 'V', 'X0', 'N', 't']:
            entry = getattr(self, f"{field}_entry")
            entry.delete(0, tk.END)
            validation_label = getattr(self, f"{field}_validation")
            validation_label.config(text="")
        self.output_text.delete(1.0, tk.END)
        self.ax1.clear()
        self.ax2.clear()
        self.ax1.set_ylabel('Concentration (g/L)')
        self.ax2.set_xlabel('Time (hours)')
        self.ax2.set_ylabel('Ethanol (g/L)')
        self.canvas.draw()
    
    def update_plots(self, results):
        self.ax1.clear()
        self.ax2.clear()
        
        # Biomass and Substrate plot
        self.ax1.plot(results['time'], results['X'], 'g-', label='Biomass (X)', linewidth=2)
        self.ax1.plot(results['time'], results['S'], 'b-', label='Substrate (S)', linewidth=2)
        self.ax1.set_ylabel('Concentration (g/L)')
        self.ax1.legend(loc='best', frameon=False)
        self.ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Ethanol plot
        self.ax2.plot(results['time'], results['P'], 'r-', label='Ethanol (P)', linewidth=2)
        self.ax2.set_xlabel('Time (hours)')
        self.ax2.set_ylabel('Ethanol (g/L)')
        self.ax2.legend(loc='best', frameon=False)
        self.ax2.grid(True, linestyle='--', alpha=0.7)
        
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = FermentationApp(root)
    root.mainloop()