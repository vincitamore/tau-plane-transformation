# τ-Plane: Reimagined Cartesian Plane

A Python library for visualizing the τ-plane, a reimagined Cartesian plane where:
- Infinity is at the origin (0,0)
- The infinitesimal δ is at the boundary
- Zero is explicitly excluded from the system

## Core Concept

This project implements a novel mathematical visualization where we invert the traditional Cartesian geometry using the transformation τ = 1/z. This creates a space where:

- The point (0,0) in the τ-plane corresponds to ±∞ in the standard plane
- Points far from the origin in the τ-plane correspond to values approaching zero
- A "unit circle" centered at the infinite origin has interesting mathematical properties
- The geometry may offer new perspectives on number theory and potentially the Riemann Hypothesis

## Installation

This project uses Poetry for dependency management. After cloning the repository:

```bash
# Install dependencies with Poetry
poetry install

# Activate the virtual environment
poetry shell
```

## Project Structure

```
t_plane/
├── core/             # Core transformation logic
├── visualization/    # Visualization utilities
└── analysis/         # Mathematical analysis modules
```

## Usage Examples

```python
# Basic usage
from t_plane.core.tau_plane import TauPlane
from t_plane.visualization.plotter import TauPlotter

# Create a τ-plane instance
tau_plane = TauPlane(delta=1e-3)  # delta is the infinitesimal boundary

# Create a plotter
plotter = TauPlotter(tau_plane)

# Plot the basic τ-plane grid
fig = plotter.plot_tau_grid(
    tau_min=-5.0, 
    tau_max=5.0,
    show_unit_circle=True,
    show_liminal_circle=True
)
fig.savefig('tau_plane_grid.png')

# Visualize a function in the τ-plane
def my_function(tau):
    return tau**2 + 1/tau

fig = plotter.plot_function_in_tau_plane(
    func=my_function,
    tau_min=-3.0,
    tau_max=3.0
)
fig.savefig('function_visualization.png')
```

## Example Script

Run the example script to generate sample visualizations:

```bash
python example.py
```

This will generate:
- Basic τ-plane grid
- Function visualization
- Riemann zeta function in the τ-plane with critical line and zeros

## Testing

Run the tests to verify functionality:

```bash
pytest
```

## Mathematical Background

The τ-plane is based on the transformation τ = 1/z, which:
- Maps infinity to the origin
- Maps zero to "infinity"
- Preserves angles (conformal)
- Inverts distances (points close to the origin in z are far in τ)

This creates a geometric perspective where:
- The "unit circle" has radius δ (infinitesimal)
- The circumference relates to infinity through the identity: ∞·δ = 1
- The critical line of the Riemann zeta function maps to a curve in the τ-plane

## License

MIT 