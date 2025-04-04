import numpy as np
import pytest
from t_plane.core.tau_plane import TauPlane

def test_to_tau_scalar():
    """Test scalar transformation to τ-plane."""
    tau_plane = TauPlane()
    z = 2.0 + 3.0j
    tau = tau_plane.to_tau(z)
    expected = 1.0 / z
    assert abs(tau - expected) < 1e-10

def test_to_tau_array():
    """Test array transformation to τ-plane."""
    tau_plane = TauPlane()
    z = np.array([[1.0 + 1.0j, 2.0 + 2.0j], [3.0 + 3.0j, 4.0 + 4.0j]])
    tau = tau_plane.to_tau(z)
    expected = 1.0 / z
    assert np.allclose(tau, expected)

def test_zero_exclusion():
    """Test that zero is properly excluded from the τ-plane."""
    tau_plane = TauPlane()
    with pytest.raises(ValueError):
        tau_plane.to_tau(0)
    
    z = np.array([1.0, 0.0, 2.0])
    with pytest.raises(ValueError):
        tau_plane.to_tau(z)

def test_roundtrip_transformation():
    """Test that transforming to τ and back preserves the original value."""
    tau_plane = TauPlane()
    z = 2.0 + 3.0j
    tau = tau_plane.to_tau(z)
    z_roundtrip = tau_plane.from_tau(tau)
    assert abs(z - z_roundtrip) < 1e-10

def test_create_tau_grid():
    """Test the creation of a τ-plane grid with zero excluded."""
    tau_plane = TauPlane(delta=0.1)
    tau_min, tau_max = -5.0, 5.0
    points = 100
    
    tau_x, tau_y = tau_plane.create_tau_grid(tau_min=tau_min, tau_max=tau_max, points=points)
    
    # Check shapes
    assert tau_x.shape == tau_y.shape
    
    # Check that zero is excluded (no values very close to zero)
    all_values = np.concatenate((tau_x.flatten(), tau_y.flatten()))
    assert not np.any(np.abs(all_values) < tau_plane.delta / 2)

def test_unit_circle():
    """Test the creation of the unit circle."""
    tau_plane = TauPlane(delta=0.2)
    x, y = tau_plane.unit_circle()
    
    # Check that all points are at distance delta from origin
    distances = np.sqrt(x**2 + y**2)
    assert np.allclose(distances, tau_plane.delta)

def test_liminal_circle():
    """Test the creation of the liminal circle."""
    tau_plane = TauPlane(delta=0.1)
    epsilon = 0.5
    x, y = tau_plane.liminal_circle(epsilon=epsilon)
    
    # Check that all points are at distance epsilon from origin
    distances = np.sqrt(x**2 + y**2)
    assert np.allclose(distances, epsilon)
    
    # Test default epsilon
    x, y = tau_plane.liminal_circle()
    distances = np.sqrt(x**2 + y**2)
    assert np.allclose(distances, 10 * tau_plane.delta)
