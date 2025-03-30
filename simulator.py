import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class BioethanolSimulator:
    def __init__(self):
        self.params = {
            'Ks': 5.0,      # Saturation constant (g/L)
            'kd': 0.01,     # Death rate (h⁻¹)
            'alpha': 0.3,   # Growth-associated coefficient (from document)
            'beta': 0.01,   # Non-growth coefficient (from document)
            'Xmax': 15.0,   # Max biomass (g/L) (from document)
            'Pmax': 80.0    # Max ethanol (g/L) (from document)
        }
    
    def run_simulation(self, inputs):
        """Run simulation with time series for plotting"""
        S0, V, X0, N, t_total = inputs['S0'], inputs['V'], inputs['X0'], inputs['N'], inputs['t']
        
        # Time points for plotting
        time_points = np.linspace(0, t_total, 100)
        dt = time_points[1] - time_points[0]  # Time step
        
        # Initialize arrays
        results = {
            'time': time_points,
            'X': np.zeros_like(time_points),
            'S': np.zeros_like(time_points),
            'P': np.zeros_like(time_points)
        }
        
        # Initial conditions
        results['X'][0] = X0
        results['S'][0] = S0
        results['P'][0] = 0
        
        # Calculate maximum growth rate (constant)
        mu_max = 0.203 * (N ** 0.6)
        
        # Time-step integration
        for i in range(1, len(time_points)):
            # Current values
            X_prev = results['X'][i-1]
            S_prev = results['S'][i-1]
            P_prev = results['P'][i-1]
            
            # Step 2: Specific growth rate (depends on current substrate)
            mu = mu_max * (S_prev / (self.params['Ks'] + S_prev)) if S_prev > 0 else 0
            
            # Step 3: Biomass growth (incremental)
            dX_dt = (mu - self.params['kd']) * X_prev
            X = X_prev + dX_dt * dt
            X = min(X, self.params['Xmax'])
            
            # Step 4: Average biomass (for this time step)
            X_avg = (X_prev + X) / 2
            
            # Step 5: Ethanol production rate
            r_p = self.params['alpha'] * mu * X_avg + self.params['beta'] * X_avg
            
            # Step 6: Ethanol increase
            dP_dt = r_p
            P = P_prev + dP_dt * dt
            P = min(P, self.params['Pmax'])
            
            # Step 7: Substrate consumption
            dS_dt = -(180 / 92) * dP_dt  # Negative because substrate is consumed
            S = S_prev + dS_dt * dt
            
            # Step 8: Check substrate depletion
            if S < 0:
                S = 0
                # Adjust P based on available substrate at this point
                P = P_prev + (S_prev * 92 / 180)
                # Fill remaining time points with final values
                results['X'][i:] = X
                results['S'][i:] = S
                results['P'][i:] = P
                break
            
            # Store results
            results['X'][i] = X
            results['S'][i] = S
            results['P'][i] = P
        
        # Final outputs
        P_total = results['P'][-1] * V
        unit_cost = inputs.get('cost', 100) / P_total if P_total > 0 else float('inf')
        
        outputs = {
            'X_final': results['X'][-1],
            'S_final': results['S'][-1],
            'P_final': results['P'][-1],
            'P_total': P_total,
            'unit_cost': unit_cost
        }
        
        return results, outputs