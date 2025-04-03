import numpy as np

class BioethanolSimulator:
    # Safe operating ranges for parameters
    PARAMETER_LIMITS = {
        'S0': (1, 500),      # g/L
        'V': (0.1, 1000),    # L
        'X0': (0.01, 10),    # g/L
        'N': (50, 500),      # rpm
        't': (1, 168)        # hours (1 week max)
    }

    def __init__(self):
        self.params = {
            'Ks': 5.0,      # g/L
            'kd': 0.01,     # h^-1
            'alpha': 0.3,   # from document
            'beta': 0.01,   # from document
            'Xmax': 15.0,   # from document
            'Pmax': 80.0    # from document
        }

    def validate_inputs(self, inputs):
        """Check if inputs are within safe limits"""
        warnings = []
        for param, value in inputs.items():
            min_val, max_val = self.PARAMETER_LIMITS[param]
            if not min_val <= value <= max_val:
                warnings.append(f"{param}: {value} is outside recommended range ({min_val}-{max_val})")
        return warnings
    
    def run_simulation(self, inputs):
        """Run simulation following the document's step-by-step scheme"""
        S0, V, X0, N, t = inputs['S0'], inputs['V'], inputs['X0'], inputs['N'], inputs['t']
        
        # Step 1: Calculate maximum specific growth rate
        mu_max = 0.203 * (N ** 0.6)
        
        # Step 2: Calculate specific growth rate (Monod equation)
        mu = mu_max * (S0 / (self.params['Ks'] + S0))
        
        # Step 3: Estimate final biomass concentration
        X = X0 * np.exp((mu - self.params['kd']) * t)
        if X > self.params['Xmax']:
            X = self.params['Xmax']
        
        # Step 4: Calculate average biomass
        X_avg = (X0 + X) / 2
        
        # Step 5: Calculate ethanol production rate (Luedeking-Piret)
        r_p = self.params['alpha'] * mu * X_avg + self.params['beta'] * X_avg
        
        # Step 6: Calculate theoretical ethanol concentration
        P = r_p * t
        if P > self.params['Pmax']:
            P = self.params['Pmax']
        
        # Step 7: Calculate substrate consumed
        S_consumed = (180 / 92) * P
        
        # Step 8: Calculate final substrate concentration
        S_f = S0 - S_consumed
        if S_f < 0:
            S_f = 0
            P = (S0 * 92) / 180  # Recalculate P based on available substrate
        
        # Step 9: Calculate total ethanol produced
        P_total = P * V
        
        # Step 10: Estimate unit cost
        unit_cost = inputs.get('cost', 100) / P_total if P_total > 0 else float('inf')
        
        # For plotting, create simple linear/exponential trends
        time_points = np.linspace(0, t, 100)
        results = {
            'time': time_points,
            'X': X0 * np.exp((mu - self.params['kd']) * time_points),  # Exponential growth
            'S': np.linspace(S0, S_f, 100),  # Linear substrate decrease
            'P': np.linspace(0, P, 100)      # Linear ethanol increase
        }
        # Cap X at Xmax for plotting
        results['X'] = np.minimum(results['X'], self.params['Xmax'])
        
        outputs = {
            'X_final': X,
            'S_final': S_f,
            'P_final': P,
            'P_total': P_total,
            'unit_cost': unit_cost
        }
        
        return results, outputs
