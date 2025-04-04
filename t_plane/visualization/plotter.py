import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from typing import Callable, Optional, Tuple, Union
from ..core.tau_plane import TauPlane

class TauPlotter:
    """
    Class for visualizing functions in the τ-plane.
    """
    
    def __init__(self, tau_plane: Optional[TauPlane] = None):
        """
        Initialize the plotter with a TauPlane instance.
        
        Args:
            tau_plane: TauPlane instance for transformations
        """
        self.tau_plane = tau_plane or TauPlane()
    
    def plot_tau_grid(self, 
                      tau_min: float = -10.0, 
                      tau_max: float = 10.0, 
                      points: int = 100,
                      show_unit_circle: bool = True,
                      show_liminal_circle: bool = False,
                      epsilon: Optional[float] = None,
                      figsize: Tuple[int, int] = (10, 10)) -> plt.Figure:
        """
        Plot the basic τ-plane grid.
        
        Args:
            tau_min: Minimum τ value
            tau_max: Maximum τ value
            points: Number of points per dimension
            show_unit_circle: Whether to show the unit circle
            show_liminal_circle: Whether to show the liminal circle
            epsilon: Radius of the liminal circle (if shown)
            figsize: Size of the figure
            
        Returns:
            Matplotlib figure
        """
        tau_x, tau_y = self.tau_plane.create_tau_grid(tau_min, tau_max, points)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot grid lines
        ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
        
        # Plot unit circle centered at origin with radius delta
        if show_unit_circle:
            x, y = self.tau_plane.unit_circle()
            ax.plot(x, y, 'r-', label=f'Unit Circle (r={self.tau_plane.delta})')
        
        # Plot liminal circle
        if show_liminal_circle:
            x, y = self.tau_plane.liminal_circle(epsilon)
            ax.plot(x, y, 'g--', label=f'Liminal Circle (r={epsilon or 10*self.tau_plane.delta})')
        
        # Set labels and limits
        ax.set_xlabel(r'$\tau_x$')
        ax.set_ylabel(r'$\tau_y$')
        ax.set_title(r'$\tau$-Plane Grid')
        
        # Add legend and grid
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Set equal aspect ratio
        ax.set_aspect('equal')
        
        return fig
    
    def plot_function_in_tau_plane(self,
                                  func: Callable[[np.ndarray, np.ndarray], np.ndarray],
                                  tau_min: float = -5.0,
                                  tau_max: float = 5.0,
                                  points: int = 200,
                                  cmap: str = 'viridis',
                                  show_unit_circle: bool = True,
                                  show_liminal_circle: bool = False,
                                  epsilon: Optional[float] = None,
                                  figsize: Tuple[int, int] = (12, 10)) -> plt.Figure:
        """
        Plot a function in the τ-plane using domain coloring.
        
        Args:
            func: The function to plot, should accept complex input and return complex output
            tau_min: Minimum τ value
            tau_max: Maximum τ value
            points: Number of points per dimension
            cmap: Colormap for domain coloring
            show_unit_circle: Whether to show the unit circle
            show_liminal_circle: Whether to show the liminal circle
            epsilon: Radius of the liminal circle (if shown)
            figsize: Size of the figure
            
        Returns:
            Matplotlib figure with domain coloring
        """
        # Create tau grid
        tau_x, tau_y = self.tau_plane.create_tau_grid(tau_min, tau_max, points)
        tau = tau_x + 1j * tau_y
        
        # Apply the function to complex tau values
        z = func(tau)
        
        # Calculate phase and magnitude for domain coloring
        phase = np.angle(z)
        magnitude = np.abs(z)
        
        # Create plots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Phase plot
        phase_plot = ax1.pcolormesh(tau_x, tau_y, phase, cmap=cmap)
        plt.colorbar(phase_plot, ax=ax1, label='Phase')
        
        # Magnitude plot (log scale for better visualization)
        with np.errstate(divide='ignore', invalid='ignore'):
            log_magnitude = np.log(magnitude)
            log_magnitude[np.isinf(log_magnitude)] = np.nan
        
        magnitude_plot = ax2.pcolormesh(tau_x, tau_y, log_magnitude, cmap='plasma')
        plt.colorbar(magnitude_plot, ax=ax2, label='Log Magnitude')
        
        # Add unit circle and liminal circle
        if show_unit_circle:
            x, y = self.tau_plane.unit_circle()
            ax1.plot(x, y, 'r-', label=f'Unit Circle (r={self.tau_plane.delta})')
            ax2.plot(x, y, 'r-', label=f'Unit Circle (r={self.tau_plane.delta})')
        
        if show_liminal_circle:
            x, y = self.tau_plane.liminal_circle(epsilon)
            radius = epsilon or 10*self.tau_plane.delta
            ax1.plot(x, y, 'g--', label=f'Liminal Circle (r={radius})')
            ax2.plot(x, y, 'g--', label=f'Liminal Circle (r={radius})')
        
        # Set labels and titles
        ax1.set_xlabel(r'$\tau_x$')
        ax1.set_ylabel(r'$\tau_y$')
        ax1.set_title('Phase')
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')
        ax1.legend()
        
        ax2.set_xlabel(r'$\tau_x$')
        ax2.set_ylabel(r'$\tau_y$')
        ax2.set_title('Magnitude (log scale)')
        ax2.grid(True, alpha=0.3)
        ax2.set_aspect('equal')
        ax2.legend()
        
        plt.tight_layout()
        fig.suptitle(r'Function Visualization in $\tau$-plane', y=1.02)
        
        return fig
    
    def interactive_tau_plane(self,
                              func: Callable[[np.ndarray], np.ndarray],
                              tau_min: float = -5.0,
                              tau_max: float = 5.0,
                              points: int = 100) -> go.Figure:
        """
        Create an interactive plot of the τ-plane using Plotly.
        
        Args:
            func: The function to plot, should accept complex input and return complex output
            tau_min: Minimum τ value
            tau_max: Maximum τ value
            points: Number of points per dimension
            
        Returns:
            Plotly figure for interactive exploration
        """
        # Create tau grid
        tau_x, tau_y = self.tau_plane.create_tau_grid(tau_min, tau_max, points)
        tau = tau_x + 1j * tau_y
        
        # Apply the function to the complex tau values
        z = func(tau)
        
        # Calculate phase and magnitude
        phase = np.angle(z)
        magnitude = np.log(np.abs(z) + 1)  # Add 1 to avoid log(0)
        
        # Create figures
        fig = go.Figure()
        
        # Add phase as surface
        fig.add_trace(go.Surface(
            x=tau_x, y=tau_y, z=phase,
            colorscale='Viridis',
            name='Phase',
            showscale=True
        ))
        
        # Add unit circle
        x, y = self.tau_plane.unit_circle()
        z = np.zeros_like(x)
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode='lines',
            line=dict(color='red', width=5),
            name=f'Unit Circle (r={self.tau_plane.delta})'
        ))
        
        # Set layout
        fig.update_layout(
            title=r'Interactive τ-plane Visualization',
            scene=dict(
                xaxis_title=r'τ_x',
                yaxis_title=r'τ_y',
                zaxis_title='Phase',
                aspectratio=dict(x=1, y=1, z=0.5)
            ),
            width=900,
            height=700
        )
        
        return fig
