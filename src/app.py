import streamlit as st
import matplotlib.pyplot as plt
from simulator import BioethanolSimulator

def main():
    st.set_page_config(layout="wide", page_title="Bioethanol Fermentation Simulator")
    
    st.title("Bioethanol Fermentation Simulator")
    
    # Input parameters in columns
    col1, col2 = st.columns(2)
    
    with col1:
        S0 = st.slider("Initial Substrate (S₀, g/L):", 1.0, 500.0, 100.0, 1.0)
        V = st.slider("Broth Volume (V, L):", 0.1, 1000.0, 10.0, 0.1)
        X0 = st.slider("Initial Biomass (X₀, g/L):", 0.01, 10.0, 1.0, 0.01)
    
    with col2:
        N = st.slider("Impeller Speed (N, rpm):", 50, 500, 200, 1)
        t = st.slider("Fermentation Time (t, hrs):", 1, 168, 24, 1)
    
    if st.button("Run Simulation"):
        simulator = BioethanolSimulator()
        inputs = {
            'S0': S0,
            'V': V,
            'X0': X0,
            'N': N,
            't': t
        }
        
        # Run simulation
        results, outputs = simulator.run_simulation(inputs)
        
        # Display results
        st.subheader("Simulation Results")
        st.write(f"""
        - **Final Biomass (X):** {outputs['X_final']:.2f} g/L
        - **Final Substrate (S):** {outputs['S_final']:.2f} g/L  
        - **Ethanol Concentration (P):** {outputs['P_final']:.2f} g/L
        - **Total Ethanol Produced:** {outputs['P_total']:.2f} g
        - **Unit Cost:** ${outputs['unit_cost']:.4f} per gram
        """)
        
        # Create plots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Biomass and Substrate plot
        ax1.plot(results['time'], results['X'], 'g-', label='Biomass (X)', linewidth=2)
        ax1.plot(results['time'], results['S'], 'b-', label='Substrate (S)', linewidth=2)
        ax1.set_ylabel('Concentration (g/L)')
        ax1.legend()
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Ethanol plot
        ax2.plot(results['time'], results['P'], 'r-', label='Ethanol (P)', linewidth=2)
        ax2.set_xlabel('Time (hours)')
        ax2.set_ylabel('Ethanol (g/L)')
        ax2.legend()
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        st.pyplot(fig)

if __name__ == "__main__":
    main()
