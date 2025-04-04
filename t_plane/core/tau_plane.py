import numpy as np
from typing import Tuple, Union, Optional

class TauPlane:
    """
    A class representing the τ-plane transformation, where τ = 1/z.
    
    This plane inverts the traditional Cartesian geometry by placing 
    infinity at the origin and approaching the infinitesimal at the boundary.
    Zero is explicitly excluded from this system.
    """
    
    def __init__(self, delta: float = 1e-6):
        """
        Initialize the τ-plane with an infinitesimal bound.
        
        Args:
            delta: The infinitesimal value defining the boundary of the plane
        """
        self.delta = delta
    
    def to_tau(self, z: Union[complex, np.ndarray]) -> Union[complex, np.ndarray]:
        """
        Transform a point or array from the standard complex plane to the τ-plane.
        
        Args:
            z: Point(s) in the standard complex plane (z ≠ 0)
            
        Returns:
            The transformed point(s) in the τ-plane
        """
        # Ensure z ≠ 0 to avoid division by zero
        if isinstance(z, np.ndarray):
            if np.any(z == 0):
                raise ValueError("Zero is explicitly excluded from the τ-plane")
            return 1.0 / z
        elif z == 0:
            raise ValueError("Zero is explicitly excluded from the τ-plane")
        return 1.0 / z
    
    def from_tau(self, tau: Union[complex, np.ndarray]) -> Union[complex, np.ndarray]:
        """
        Transform a point or array from the τ-plane back to the standard complex plane.
        
        Args:
            tau: Point(s) in the τ-plane (τ ≠ 0)
            
        Returns:
            The transformed point(s) in the standard complex plane
        """
        # Ensure τ ≠ 0 to avoid division by zero (τ = 0 corresponds to ±∞)
        if isinstance(tau, np.ndarray):
            if np.any(tau == 0):
                raise ValueError("τ = 0 corresponds to infinity and cannot be mapped back")
            return 1.0 / tau
        elif tau == 0:
            raise ValueError("τ = 0 corresponds to infinity and cannot be mapped back")
        return 1.0 / tau
    
    def create_tau_grid(self, 
                        tau_min: float = -10.0, 
                        tau_max: float = 10.0, 
                        points: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create a grid in the τ-plane excluding the origin.
        
        Args:
            tau_min: Minimum τ value
            tau_max: Maximum τ value
            points: Number of points per dimension
            
        Returns:
            A tuple of (tau_x, tau_y) meshgrids for the τ-plane
        """
        # Exclude τ = 0 by creating two ranges and concatenating
        if tau_min < 0 < tau_max:
            # Create range from tau_min to -delta
            left_count = int(points * abs(tau_min) / (tau_max - tau_min))
            left_range = np.linspace(tau_min, -self.delta, max(left_count, 2))
            
            # Create range from delta to tau_max
            right_count = int(points * abs(tau_max) / (tau_max - tau_min))
            right_range = np.linspace(self.delta, tau_max, max(right_count, 2))
            
            # Combine the ranges
            tau_range = np.concatenate((left_range, right_range))
        else:
            # If range doesn't cross zero, use standard linspace
            tau_range = np.linspace(tau_min, tau_max, points)
        
        # Create meshgrid
        tau_x, tau_y = np.meshgrid(tau_range, tau_range)
        return tau_x, tau_y
    
    def unit_circle(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create a unit circle in the τ-plane centered at the origin with radius delta.
        
        Returns:
            A tuple of (x, y) coordinates for the unit circle
        """
        theta = np.linspace(0, 2 * np.pi, 1000)
        x = self.delta * np.cos(theta)
        y = self.delta * np.sin(theta)
        return x, y
    
    def liminal_circle(self, epsilon: Optional[float] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create a liminal circle in the τ-plane for analysis focus.
        
        Args:
            epsilon: Radius of the liminal circle (defaults to 10*delta)
            
        Returns:
            A tuple of (x, y) coordinates for the liminal circle
        """
        if epsilon is None:
            epsilon = 10 * self.delta
        
        theta = np.linspace(0, 2 * np.pi, 1000)
        x = epsilon * np.cos(theta)
        y = epsilon * np.sin(theta)
        return x, y
