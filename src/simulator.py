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

    def run_simulation(self, inputs):
        S0, V, X0, N, t = inputs['S0'], inputs['V'], inputs['X0'], inputs['N'], inputs['t']
        
        # Increased time resolution for smoother curves
        time_points = np.linspace(0, t, 1000)  # Increased to 1000 points
        
        # Initialize arrays
        X_t = np.zeros_like(time_points)
        S_t = np.zeros_like(time_points)
        P_t = np.zeros_like(time_points)
        
        # Initial conditions
        X_t[0] = X0
        S_t[0] = S0
        P_t[0] = 0
        
        # Simulation parameters
        mu_max = 0.203 * (N ** 0.6)
        lag_phase_duration = 3  # hours
        growth_phase_duration = 8  # hours
        
        for i in range(1, len(time_points)):
            current_time = time_points[i]
            
            # Phase-dependent growth rate
            if current_time < lag_phase_duration:
                # Lag phase - minimal growth
                phase_factor = 0.1 * (1 - np.exp(-current_time))
            elif current_time < lag_phase_duration + growth_phase_duration:
                # Exponential growth phase
                phase_factor = 1 - 0.9 * np.exp(-(current_time - lag_phase_duration)/2)
            else:
                # Stationary/decline phase
                phase_factor = np.exp(-(current_time - lag_phase_duration - growth_phase_duration)/10)
            
            mu = mu_max * (S_t[i-1] / (self.params['Ks'] + S_t[i-1])) * phase_factor
            
            # Biomass growth
            X_t[i] = X_t[i-1] + (mu * X_t[i-1] * (1 - X_t[i-1]/self.params['Xmax']) - self.params['kd'] * X_t[i-1]) * (t/1000)
            
            # Substrate consumption
            if S_t[i-1] > 0:
                Yxs = 0.4  # Biomass yield coefficient
                Yps = 0.5  # Product yield coefficient
                S_consumed = (X_t[i] - X_t[i-1])/Yxs + (P_t[i-1] - (0 if i==1 else P_t[i-2]))/Yps
                S_t[i] = max(S_t[i-1] - S_consumed, 0)
            
            # Ethanol production - modified Luedeking-Piret model
            if current_time < lag_phase_duration:
                # Lag phase - minimal production
                r_p = 0.05 * (self.params['alpha']*mu*X_t[i] + self.params['beta']*X_t[i])
            elif S_t[i] > 0.1*S0:
                # Active production phase
                r_p = (self.params['alpha']*mu*X_t[i] + self.params['beta']*X_t[i]) * (1 - P_t[i-1]/self.params['Pmax'])
            else:
                # Substrate limitation phase
                r_p = 0.2 * (self.params['alpha']*mu*X_t[i] + self.params['beta']*X_t[i])
            
            P_t[i] = min(P_t[i-1] + r_p * (t/1000), self.params['Pmax'])
        
        # Final calculations
        P_total = P_t[-1] * V
        unit_cost = inputs.get('cost', 100) / P_total if P_total > 0 else float('inf')
        
        return {
            'time': time_points,
            'X': X_t,
            'S': S_t,
            'P': P_t
        }, {
            'X_final': X_t[-1],
            'S_final': S_t[-1],
            'P_final': P_t[-1],
            'P_total': P_total,
            'unit_cost': unit_cost
        }