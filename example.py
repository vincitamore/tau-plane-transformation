import numpy as np
import matplotlib.pyplot as plt
from t_plane.core.tau_plane import TauPlane
from t_plane.visualization.plotter import TauPlotter
from t_plane.analysis.riemann import RiemannAnalysis

def main():
    """
    Demonstrate the τ-plane visualization with examples.
    """
    # Create instances
    tau_plane = TauPlane(delta=1e-2)
    plotter = TauPlotter(tau_plane)
    riemann = RiemannAnalysis(tau_plane)
    
    # Example 1: Basic τ-plane grid
    print("Generating basic τ-plane grid...")
    fig1 = plotter.plot_tau_grid(
        tau_min=-5.0, 
        tau_max=5.0, 
        points=100,
        show_unit_circle=True,
        show_liminal_circle=True,
        epsilon=0.5
    )
    fig1.savefig('tau_plane_grid.png', dpi=300, bbox_inches='tight')
    plt.close(fig1)
    print("Saved τ-plane grid to tau_plane_grid.png")
    
    # Example 2: Simple function visualization in τ-plane
    print("Generating function visualization in τ-plane...")
    
    # Define a simple function to visualize: f(τ) = τ²
    def square_function(tau):
        return tau**2
    
    fig2 = plotter.plot_function_in_tau_plane(
        func=square_function,
        tau_min=-3.0,
        tau_max=3.0,
        points=200,
        show_unit_circle=True
    )
    fig2.savefig('tau_plane_function.png', dpi=300, bbox_inches='tight')
    plt.close(fig2)
    print("Saved function visualization to tau_plane_function.png")
    
    # Example 3: Riemann zeta function in τ-plane
    print("Generating Riemann zeta function visualization...")
    
    # Define a wrapper for the zeta function
    def zeta_wrapper(tau):
        return riemann.zeta_in_tau_plane(tau)
    
    # Find the critical line and zeros
    critical_x, critical_y = riemann.find_critical_line(
        tau_min=0.1, tau_max=5.0, points=1000
    )
    zeros_x, zeros_y = riemann.calculate_zeros_in_tau_plane(num_zeros=5)
    
    # Create a custom plot for the zeta function
    fig3, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    
    # Generate the grid and compute zeta values
    tau_min, tau_max = -3.0, 3.0
    points = 150
    tau_x, tau_y = tau_plane.create_tau_grid(tau_min, tau_max, points)
    tau = tau_x + 1j * tau_y
    
    try:
        # This may produce warnings for points where zeta calculation fails
        with np.errstate(all='ignore'):
            zeta_values = zeta_wrapper(tau)
            phase = np.angle(zeta_values)
            with np.errstate(divide='ignore', invalid='ignore'):
                log_magnitude = np.log(np.abs(zeta_values))
                log_magnitude[np.isinf(log_magnitude) | np.isnan(log_magnitude)] = np.nan
    
        # Phase plot
        phase_plot = ax1.pcolormesh(tau_x, tau_y, phase, cmap='viridis')
        plt.colorbar(phase_plot, ax=ax1, label='Phase')
        
        # Add critical line and zeros
        ax1.plot(critical_x, critical_y, 'r-', linewidth=2, label='Critical Line')
        ax1.plot(zeros_x, zeros_y, 'ko', markersize=5, label='Zeta Zeros')
        
        # Magnitude plot
        magnitude_plot = ax2.pcolormesh(tau_x, tau_y, log_magnitude, cmap='plasma')
        plt.colorbar(magnitude_plot, ax=ax2, label='Log Magnitude')
        ax2.plot(critical_x, critical_y, 'r-', linewidth=2, label='Critical Line')
        ax2.plot(zeros_x, zeros_y, 'ko', markersize=5, label='Zeta Zeros')
        
        # Format the plots
        for ax in [ax1, ax2]:
            ax.set_xlabel(r'$\tau_x$')
            ax.set_ylabel(r'$\tau_y$')
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
            ax.legend()
        
        ax1.set_title('Zeta Function Phase in τ-plane')
        ax2.set_title('Zeta Function Magnitude in τ-plane')
        
        plt.tight_layout()
        fig3.savefig('riemann_zeta_tau_plane.png', dpi=300, bbox_inches='tight')
        plt.close(fig3)
        print("Saved Riemann zeta visualization to riemann_zeta_tau_plane.png")
    
    except Exception as e:
        print(f"Error generating Riemann zeta visualization: {e}")
    
    print("Examples completed successfully!")

if __name__ == "__main__":
    main() 