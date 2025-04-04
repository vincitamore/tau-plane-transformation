import numpy as np
from flask import Flask, render_template, jsonify, request
from t_plane.core.tau_plane import TauPlane
from t_plane.analysis.riemann import RiemannAnalysis
import math
import re
import ast
from sympy import symbols, diff, sympify, solve, roots, series, lambdify
from sympy.abc import z
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
# We might need to adapt the plotter or create a new one for web use
# from t_plane.visualization.plotter import TauPlotter 
import mpmath as mp
import traceback

app = Flask(__name__)

# Initialize core components (adjust delta as needed)
tau_plane_instance = TauPlane(delta=1e-3) 
riemann_analyzer = RiemannAnalysis(tau_plane_instance)
# plotter_instance = TauPlotter(tau_plane_instance) # Keep for now, might adapt

@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')

def analyze_function(function_str, is_zeta=False):
    """
    Perform mathematical analysis on a function to find critical points,
    singularities, and other properties.
    
    Args:
        function_str: String representation of the function to analyze
        is_zeta: Boolean indicating whether the function is the Riemann Zeta function
        
    Returns:
        A dictionary containing analysis results
    """
    if is_zeta:
        # Special analysis for the Riemann Zeta function
        return analyze_zeta_function()
    
    try:
        # Set up SymPy for parsing with implicit multiplication
        transformations = standard_transformations + (implicit_multiplication_application,)
        
        # Convert to a format SymPy can parse
        sympy_str = (function_str
            .replace('^', '**')
            .replace('sin', 'sin')  # Already in SymPy format
            .replace('cos', 'cos')  # Already in SymPy format
            .replace('tan', 'tan')  # Already in SymPy format
            .replace('exp', 'exp')  # Already in SymPy format
            .replace('log', 'log')  # Already in SymPy format
            .replace('sqrt', 'sqrt')  # Already in SymPy format
            .replace('pi', 'pi')     # Already in SymPy format
            .replace('e', 'E')       # Convert to SymPy's E
        )
        
        # Parse the expression
        expr = parse_expr(sympy_str, transformations=transformations)
        
        # Calculate the derivative
        derivative = diff(expr, z)
        second_derivative = diff(derivative, z)
        
        # Find critical points (where derivative = 0)
        critical_points = []
        try:
            solutions = list(roots(derivative, z))
            if not solutions:
                solutions = solve(derivative, z)
            
            # Convert solutions to a list of complex numbers
            for sol in solutions:
                if sol.is_real:
                    z_value = complex(float(sol), 0)
                else:
                    z_value = complex(float(sol.as_real_imag()[0]), float(sol.as_real_imag()[1]))
                
                # Determine point type (maximum, minimum, saddle, etc.)
                try:
                    # Calculate second derivative at this point
                    second_deriv_val = complex(second_derivative.subs(z, sol))
                    
                    if second_deriv_val.real > 0:
                        point_type = "Minimum"
                    elif second_deriv_val.real < 0:
                        point_type = "Maximum"
                    else:
                        point_type = "Saddle point or inflection"
                except:
                    point_type = "Unknown"
                
                # Convert z back to tau space
                tau_value = 1.0 / z_value if z_value != 0 else None
                
                if tau_value is not None:
                    critical_points.append({
                        'z_real': z_value.real,
                        'z_imag': z_value.imag,
                        'tau_real': tau_value.real if not math.isinf(tau_value.real) else 0,
                        'tau_imag': tau_value.imag if not math.isinf(tau_value.imag) else 0,
                        'type': point_type,
                        'function_value': str(expr.subs(z, sol))
                    })
        except Exception as e:
            print(f"Error finding critical points: {e}")
            pass  # Critical points analysis failed
        
        # Find domain properties (singularities, branch points)
        domain_properties = {
            'description': 'Complex analytic function',
            'singularities': 'None detected',
            'branch_points': 'None detected',
            'domain': 'Entire complex plane',
            'growth_rate': 'Undetermined'
        }
        
        # Check for potential singularities
        try:
            # Look for division by expressions that could be zero
            if '/' in function_str:
                domain_properties['description'] = 'Meromorphic function with possible poles'
                domain_properties['singularities'] = 'Potential poles where denominator = 0'
                domain_properties['domain'] = 'Complex plane excluding singularities'
            
            # Check for logarithms or fractional powers that could create branch cuts
            if 'log' in function_str or 'sqrt' in function_str or re.search(r'\^\s*\d*\.\d+', function_str):
                if 'log' in function_str:
                    domain_properties['description'] = 'Function with logarithmic branch cut'
                    domain_properties['branch_points'] = 'At z = 0 extending to -∞'
                    domain_properties['domain'] = 'Complex plane excluding branch cut'
                elif 'sqrt' in function_str:
                    domain_properties['description'] = 'Function with square root branch cut'
                    domain_properties['branch_points'] = 'Present (specific points not calculated)'
                    domain_properties['domain'] = 'Complex plane excluding branch cut'
            
            # Determine growth rate for polynomial-like functions
            if all(term not in function_str for term in ['sin', 'cos', 'tan', 'exp', 'log']):
                try:
                    # Check if function resembles a polynomial (by examining highest power)
                    degree = 0
                    if 'z**' in sympy_str:
                        powers = re.findall(r'z\*\*(\d+)', sympy_str)
                        if powers:
                            degree = max(int(p) for p in powers)
                    
                    if degree > 0:
                        domain_properties['growth_rate'] = f"O(|z|^{degree}) as |z| → ∞"
                    else:
                        domain_properties['growth_rate'] = "Bounded or sublinear growth"
                except:
                    pass
            elif 'exp' in function_str:
                domain_properties['growth_rate'] = "Exponential growth"
        except Exception as e:
            print(f"Error analyzing domain: {e}")
            pass  # Domain analysis failed
        
        # Function series expansion
        try:
            # Get Taylor series around z=0 (up to order 5)
            taylor_series = series(expr, z, 0, 5).removeO()
            domain_properties['series_expansion'] = str(taylor_series)
            
            # Get Laurent series for functions with singularity at z=0
            if '/' in function_str and 'z' in function_str.split('/')[1]:
                from sympy import Laurent
                try:
                    laurent_series = series(expr, z, 0, n=None)
                    domain_properties['laurent_expansion'] = str(laurent_series)
                except:
                    pass
        except Exception as e:
            print(f"Error calculating series: {e}")
            domain_properties['series_expansion'] = "Could not compute Taylor series"
        
        # Check special values and limits
        special_values = {}
        try:
            special_values['at_zero'] = str(expr.subs(z, 0)) if '/' not in function_str or 'z' not in function_str.split('/')[1] else "Undefined (singularity)"
            special_values['at_one'] = str(expr.subs(z, 1))
            special_values['at_i'] = str(expr.subs(z, 1j))
            
            # Add limits for more context
            from sympy import limit, oo
            if '/' in function_str:
                # Try to compute limit at infinity
                try:
                    lim_inf = limit(expr, z, oo)
                    special_values['limit_at_infinity'] = str(lim_inf)
                except:
                    special_values['limit_at_infinity'] = "Could not compute"
        except Exception as e:
            print(f"Error calculating special values: {e}")
            pass
        
        # Differential equation information
        diff_eq_info = {}
        try:
            # Check if function satisfies a simple differential equation
            if 'sin' in function_str:
                diff_eq_info['note'] = "Function may satisfy y'' + y = 0 (harmonic oscillator equation)"
            elif 'exp' in function_str:
                diff_eq_info['note'] = "Function may satisfy y' = y (exponential growth equation)"
            elif any(fn in function_str for fn in ['tan', 'cot']):
                diff_eq_info['note'] = "Function may satisfy a nonlinear first-order differential equation"
        except Exception as e:
            print(f"Error in differential equation analysis: {e}")
            pass
        
        return {
            'critical_points': critical_points,
            'domain_properties': domain_properties,
            'special_values': special_values,
            'differential_equations': diff_eq_info
        }
        
    except Exception as e:
        print(f"Function analysis failed: {e}")
        return {
            'error': f"Analysis failed: {str(e)}",
            'critical_points': [],
            'domain_properties': {
                'description': 'Analysis failed',
                'singularities': 'Unknown',
                'branch_points': 'Unknown'
            }
        }

def analyze_zeta_function():
    """
    Special analysis for the Riemann Zeta function.
    
    Returns:
        Dictionary containing zeta-specific analysis results
    """
    # Define important properties of the Riemann Zeta function
    critical_points = [
        {
            'z_real': -1.0,
            'z_imag': 0.0,
            'tau_real': -1.0,
            'tau_imag': 0.0,
            'type': 'Extremum',
            'function_value': '-1/12'
        }
    ]
    
    domain_properties = {
        'description': 'Meromorphic function with analytic continuation',
        'singularities': 'Simple pole at s = 1',
        'branch_points': 'None',
        'domain': 'Entire complex plane except s = 1',
        'growth_rate': 'Various rates in different regions',
        'series_expansion': 'ζ(s) = 1/s-1 + Σ(-1)^n γ_n/(n!) · (s-1)^n for s near 1',
        'laurent_expansion': '1/(s-1) + γ + O((s-1))'
    }
    
    special_values = {
        'at_zero': '-1/2',
        'at_two': 'π²/6 ≈ 1.645',
        'at_four': 'π⁴/90 ≈ 1.082',
        'at_negative_even': '0 (trivial zeros)',
        'functional_equation': 'ζ(s) = 2^s · π^(s-1) · sin(πs/2) · Γ(1-s) · ζ(1-s)',
        'critical_line': 'Re(s) = 1/2 is where all non-trivial zeros are conjectured to lie (Riemann Hypothesis)'
    }
    
    important_facts = {
        'riemann_hypothesis': 'All non-trivial zeros lie on the critical line Re(s) = 1/2',
        'prime_number_connection': 'Euler product formula: ζ(s) = ∏ᵨ(1 - p^(-s))^(-1)',
        'analytic_continuation': 'Originally defined for Re(s) > 1, but can be extended to the entire complex plane',
        'reflection_formula': 'ζ(1-s) = 2^(1-s) · π^(-s) · cos(πs/2) · Γ(s) · ζ(s)',
        'number_theory': 'Central to the distribution of prime numbers through the Prime Number Theorem',
        'trivial_zeros': 'At negative even integers: -2, -4, -6, ...',
        'first_few_zeros': [
            '1/2 + 14.1347i',
            '1/2 + 21.0220i',
            '1/2 + 25.0109i',
            '1/2 + 30.4249i',
            '1/2 + 32.9351i'
        ]
    }
    
    return {
        'critical_points': critical_points,
        'domain_properties': domain_properties,
        'special_values': special_values,
        'important_facts': important_facts
    }

def evaluate_function(z_values, function_str):
    """
    Safely evaluate a mathematical function string for an array of complex values.
    
    Args:
        z_values: NumPy array of complex values
        function_str: String representation of function using 'z' as variable
        
    Returns:
        NumPy array of resulting complex values
    """
    # Sanitize and validate function string for security
    # Only allow valid math operations and functions
    if not re.match(r'^[0-9z\s\+\-\*\/\(\)\.\,\^\|\&\!\=\>\<\%\:\~sine\scosine\stan\slog\sexp\sabs\ssqrt\spi\se]+$', 
                   function_str.replace('sin', 'sine').replace('cos', 'cosine').replace('tan', 'tan')
                   .replace('sqrt', 'sqrt').replace('log', 'log').replace('exp', 'exp')
                   .replace('pi', 'pi').replace('e', 'e')):
        raise ValueError("Invalid function string. Only use z and basic operations.")
    
    # Replace caret with power operator
    function_str = function_str.replace('^', '**')
    
    # Create evaluation namespace with all necessary functions
    namespace = {
        "np": np,
        "z_values": z_values,
        "sin": np.sin,
        "cos": np.cos,
        "tan": np.tan,
        "log": np.log,
        "exp": np.exp,
        "sqrt": np.sqrt,
        "abs": np.abs,
        "pi": np.pi,
        "e": np.e
    }
    
    # Replace z with z_values
    function_str = function_str.replace('z', 'z_values')
    
    try:
        # Evaluate the function with NumPy functions for the array
        result = eval(function_str, namespace)
        return result
    except Exception as e:
        raise ValueError(f"Error evaluating function: {str(e)}")

@app.route('/api/plot_data')
def plot_data():
    try:
        # Get plot parameters from request arguments
        plot_type = request.args.get('plot_type', 'simple_func')
        tau_min = float(request.args.get('tau_min', -3.0))
        tau_max = float(request.args.get('tau_max', 3.0))
        points = int(request.args.get('points', 100))
        liminal_radius = float(request.args.get('liminal_radius', 1.0))  # Analysis radius
        plane = request.args.get('plane', 'tau_plane')  
        
        # Create a grid of tau values
        tau_x = np.linspace(tau_min, tau_max, points)
        tau_y = np.linspace(tau_min, tau_max, points)
        
        # Create meshgrid for evaluation
        tau_x_mesh, tau_y_mesh = np.meshgrid(tau_x, tau_y)
        tau_values = tau_x_mesh + 1j * tau_y_mesh
        
        # Replace values very close to the origin (infinity in z-plane) with NaN
        # This prevents division by zero and creates a clear visual at infinity
        if plane in ['tau_plane', 'z_plane']:
            mask = np.abs(tau_values) < 1e-10
            tau_values[mask] = np.nan
            
        # Calculate the fixed liminal zone radius (always halfway between origin and boundary)
        fixed_liminal_radius = (tau_max - 0) / 2
        
        # For z-plane mode, apply the liminal zone analysis transformation
        if plane == 'z_plane':
            # Create a mask for points within the analysis radius
            analysis_radius_mask = np.abs(tau_values) <= liminal_radius
            
            # Create a mask for points within the fixed liminal zone
            liminal_zone_mask = np.abs(tau_values) <= fixed_liminal_radius
            
            # Record these masks for the visualization
            liminal_mask = liminal_zone_mask.astype(int).tolist()
            analysis_mask = analysis_radius_mask.astype(int).tolist()
            
        # Initialize result object
        result = {
            'tau_x': tau_x.tolist(),
            'tau_y': tau_y.tolist(),
            'type': plot_type,
            'liminal_radius': liminal_radius,
            'fixed_liminal_radius': fixed_liminal_radius
        }
        
        # Add masks for the liminal zone rendering if in z-plane
        if plane == 'z_plane':
            result['liminal_zone_mask'] = liminal_mask
            result['analysis_radius_mask'] = analysis_mask
        
        # Prepare z-values according to the selected plane
        if plane == 'w_plane':
            # w = log(τ) = -log(z) logarithmic transformation
            # Apply logarithmic transformation to tau values
            # w_real = log|τ|, w_imag = arg(τ)
            w_values = np.log(tau_values)
            
            # Extract components for separate plotting
            w_x_mesh = np.real(w_values)
            w_y_mesh = np.imag(w_values) 
            
            # Store w-plane values for plotting
            result['w_x'] = w_x_mesh.tolist()
            result['w_y'] = w_y_mesh.tolist()
            
            # We need to compute function values in the tau-plane then transform coordinates
            z_values = None  # Will be defined based on function type
        else:
            # For tau_plane and z_plane, we work directly with tau values
            z_values = None  # Will be defined based on function type
            
        # Evaluate the appropriate function based on plot_type
        if plot_type == 'zeta':
            # For zeta function visualization
            if plane == 'tau_plane' or plane == 'z_plane':
                # In τ-plane: τ = 1/s, so s = 1/τ
                z_values = 1 / tau_values
                
                # For z_plane, we visualize directly in the tau-plane but use
                # the direct 1/τ transformation for the special coordinate system
                
                # Evaluate Riemann zeta function
                func_values = np.zeros_like(z_values, dtype=complex)
                mask = ~np.isnan(z_values)  # Skip NaN values
                
                # Use mpmath for high-precision zeta evaluation
                for i in range(points):
                    for j in range(points):
                        if mask[i, j]:
                            z = complex(z_values[i, j])
                            if abs(z) < 1e-10:
                                func_values[i, j] = np.nan + 1j * np.nan
                            else:
                                func_values[i, j] = complex(mp.zeta(z))

            elif plane == 'w_plane':
                # In w-plane, w = log(τ) = -log(s)
                # So s = exp(-w)
                z_values = np.exp(-w_values)
                
                # Evaluate zeta
                func_values = np.zeros_like(z_values, dtype=complex)
                mask = ~np.isnan(z_values)
                
                for i in range(points):
                    for j in range(points):
                        if mask[i, j]:
                            z = complex(z_values[i, j])
                            if abs(z) < 1e-10:
                                func_values[i, j] = np.nan + 1j * np.nan
                            else:
                                func_values[i, j] = complex(mp.zeta(z))
            
            # Add critical line and zeros to the result for zeta
            num_zeros = int(request.args.get('num_zeros', 5))
            t_max_crit = float(request.args.get('t_max_crit', 50.0))
            
            # Add critical line and zeros to the result
            add_critical_line_and_zeros(result, num_zeros, t_max_crit, plane)
                        
        elif plot_type == 'general_func':
            # For custom function visualization
            function_str = request.args.get('function', 'z*z')
            
            if plane == 'tau_plane':
                # In τ-plane: τ = 1/z, so z = 1/τ
                z_values = 1 / tau_values
                # Evaluate the function at z = 1/τ
                func_values = evaluate_function(z_values, function_str)
                
            elif plane == 'z_plane':
                # In z-plane (direct), we evaluate the function directly at tau values
                # but still exclude the origin (representing infinity)
                func_values = evaluate_function(tau_values, function_str)
                
            elif plane == 'w_plane':
                # In w-plane, w = log(τ) = -log(z)
                # So z = exp(-w)
                z_values = np.exp(-w_values)
                func_values = evaluate_function(z_values, function_str)
            
            # Store the function string for reference
            result['function'] = function_str
            
            # Add function analysis
            if request.args.get('analyze', 'false').lower() == 'true':
                result['analysis'] = analyze_function(function_str, plot_type == 'zeta')
                
        else:  # 'simple_func' or other
            # Fallback to a simple function (for testing/default)
            function_str = request.args.get('function', 'z*z')
            
            if plane == 'tau_plane':
                z_values = 1 / tau_values
                func_values = evaluate_function(z_values, function_str)
            elif plane == 'z_plane':
                func_values = evaluate_function(tau_values, function_str)
            elif plane == 'w_plane':
                z_values = np.exp(-w_values)
                func_values = evaluate_function(z_values, function_str)
                
            result['function'] = function_str
        
        # Extract phase and magnitude for plotting
        phase = np.angle(func_values)
        magnitude = np.abs(func_values)
        
        # Take the log of magnitude to better visualize large variations
        log_magnitude = np.log10(np.maximum(magnitude, 1e-10))
        
        # Extract real and imaginary parts for 2D plotting
        real_part = np.real(func_values)
        imag_part = np.imag(func_values)
        
        # Add results to the response
        result['phase'] = phase.tolist()
        result['magnitude'] = magnitude.tolist()
        result['log_magnitude'] = log_magnitude.tolist()
        result['real_part'] = real_part.tolist()
        result['imag_part'] = imag_part.tolist()
        
        return jsonify(result)
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

def add_critical_line_and_zeros(result, num_zeros, t_max, plane='tau_plane'):
    """Add the critical line and zeros to the result object in the appropriate coordinate system."""
    # Calculate t values for the critical line
    t_values = np.linspace(0.1, t_max, 1000)
    
    # Critical line in s-plane is at Re(s) = 1/2
    s_critical = 0.5 + 1j * t_values
    
    # Convert to tau-plane coordinates: tau = 1/s
    tau_critical = 1.0 / s_critical
    
    # Get approximate zeros from the first few non-trivial zeros
    # These are the known t-values for the first few non-trivial zeros
    zero_t_values = [14.1347, 21.0220, 25.0109, 30.4249, 32.9351, 37.5862, 40.9187, 
                     43.3271, 48.0052, 49.7738, 52.9703, 56.4462, 59.3470, 60.8318, 65.1125]
    
    # Use only the requested number of zeros
    zero_t_values = zero_t_values[:num_zeros]
    
    # Convert to s-plane: s = 1/2 + it
    s_zeros = 0.5 + 1j * np.array(zero_t_values)
    
    # Convert to tau-plane: tau = 1/s
    tau_zeros = 1.0 / s_zeros
    
    # Prepare data according to the plane type
    if plane == 'w_plane':
        # In w-plane, w = log(τ)
        w_critical_real = np.log(np.abs(tau_critical))
        w_critical_imag = np.angle(tau_critical)
        
        w_zeros_real = np.log(np.abs(tau_zeros))
        w_zeros_imag = np.angle(tau_zeros)
        
        result['critical_line'] = {
            'x': w_critical_real.tolist(),
            'y': w_critical_imag.tolist()
        }
        
        result['zeros'] = {
            'x': w_zeros_real.tolist(),
            'y': w_zeros_imag.tolist()
        }
    else:
        # For both tau_plane and z_plane, we use the tau coordinates directly
        result['critical_line'] = {
            'x': np.real(tau_critical).tolist(),
            'y': np.imag(tau_critical).tolist()
        }
        
        result['zeros'] = {
            'x': np.real(tau_zeros).tolist(),
            'y': np.imag(tau_zeros).tolist()
        }
    
    return result

if __name__ == '__main__':
    # Enable debug mode for development (auto-reloads, provides debugger)
    # Use host='0.0.0.0' to make it accessible on your network if needed
    app.run(debug=True, host='127.0.0.1', port=5000)
