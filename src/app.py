import streamlit as st
import matplotlib.pyplot as plt
from simulator import BioethanolSimulator


def main():
    st.set_page_config(layout="wide", page_title="Bioethanol Fermentation Simulator")
    

    st.title("Bioethanol Fermentation Simulator")
    
    # Input parameters in columns
    col1, col2 = st.columns(2)
    
    with col1:
        S0 = st.number_input("Initial Substrate (S₀, g/L):", min_value=0.0, max_value=500.0, value=None, step=None, placeholder="0")
        V = st.number_input("Broth Volume (V, L):", min_value=0.0, max_value=1000.0, value=None, step=None, placeholder="0")
        X0 = st.number_input("Initial Biomass (X₀, g/L):", min_value=0.0, max_value=10.0, value=None, step=None, placeholder="0")
    
    with col2:
        N = st.number_input("Impeller Speed (N, rpm):", min_value=0, max_value=500, value=None, step=None, placeholder="0")
        t = st.number_input("Fermentation Time (t, hrs):", min_value=0, max_value=168, value=None, step=None, placeholder="0")
    
    if st.button("Run Simulation"):
        # Validate inputs
        if S0 <= 0 or V <= 0 or X0 <= 0 or N <= 0 or t <= 0:
            st.error("All input parameters must be greater than 0 to run the simulation.")
            return
        
        with st.spinner("Running simulation..."):
            inputs = {
                'S0': S0,
                'V': V,
                'X0': X0,
                'N': N,
                't': t
            }
            
            # Run simulation
            simulator = BioethanolSimulator()
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
            
            # Create plots with a dark theme
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), facecolor='#1e1e1e')  # Dark background for the figure
            fig.patch.set_alpha(1.0)  # Ensure the background is fully opaque

            # Biomass and Substrate plot
            ax1.set_facecolor('#2e2e2e')  # Dark background for the axes
            ax1.plot(results['time'], results['X'], 'limegreen', label='Biomass (X)', linewidth=2)  # Brighter green for visibility
            ax1.plot(results['time'], results['S'], 'dodgerblue', label='Substrate (S)', linewidth=2)  # Brighter blue for visibility
            ax1.set_ylabel('Concentration (g/L)', color='white')  # White text for readability
            ax1.tick_params(axis='both', colors='white')  # White ticks
            ax1.legend(facecolor='#2e2e2e', edgecolor='white', labelcolor='white')  # Dark legend background, white text
            ax1.grid(True, linestyle='--', alpha=0.3, color='gray')  # Subtle gray grid

            # Ethanol plot
            ax2.set_facecolor('#2e2e2e')  # Dark background for the axes
            ax2.plot(results['time'], results['P'], 'orangered', label='Ethanol (P)', linewidth=2)  # Brighter red for visibility
            ax2.set_xlabel('Time (hours)', color='white')  # White text for readability
            ax2.set_ylabel('Ethanol (g/L)', color='white')  # White text for readability
            ax2.tick_params(axis='both', colors='white')  # White ticks
            ax2.legend(facecolor='#2e2e2e', edgecolor='white', labelcolor='white')  # Dark legend background, white text
            ax2.grid(True, linestyle='--', alpha=0.3, color='gray')  # Subtle gray grid

            st.pyplot(fig)

if __name__ == "__main__":
    main()