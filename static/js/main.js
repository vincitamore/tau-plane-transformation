document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Element References ---
    const tauRangeSlider = document.getElementById('tauRange');
    const tauRangeValueSpan = document.getElementById('tauRangeValue');
    const pointsSlider = document.getElementById('pointsRange');
    const pointsValueSpan = document.getElementById('pointsValue');
    const numZerosSlider = document.getElementById('numZerosRange');
    const numZerosValueSpan = document.getElementById('numZerosValue');
    const tMaxCritSlider = document.getElementById('tMaxCritRange');
    const tMaxCritValueSpan = document.getElementById('tMaxCritValue');
    const liminalZoneSlider = document.getElementById('liminalZoneRange');
    const liminalZoneValueSpan = document.getElementById('liminalZoneValue');
    const updateButton = document.getElementById('updateButton');
    const phasePlotDiv = document.getElementById('phasePlot');
    const magnitudePlotDiv = document.getElementById('magnitudePlot');
    const plot2dDiv = document.getElementById('plot2d');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const zetaControlsDiv = document.getElementById('zetaControls');
    const liminalZoneControlDiv = document.getElementById('liminalZoneControl');
    const functionInput = document.getElementById('functionInput');
    const functionSelect = document.getElementById('functionSelect');
    const planeSelect = document.getElementById('planeSelect');
    const rangeLabel = document.getElementById('rangeLabel');
    const functionAnalysisDiv = document.getElementById('function-analysis');
    const latexFunctionSpan = document.getElementById('latex-function');
    const criticalPointsList = document.getElementById('critical-points-list');
    const domainProperties = document.getElementById('domain-properties');
    
    // Get radio buttons for 2D plot view
    const plot2dViewRadios = document.querySelectorAll('input[name="plot2d-view"]');
    
    // Additional UI elements for plane explanations
    const tauExplanation = document.getElementById('tau-explanation');
    const wExplanation = document.getElementById('w-explanation');
    const zExplanation = document.getElementById('z-explanation');
    const tauRangeExplanation = document.getElementById('tau-range-explanation');
    const wRangeExplanation = document.getElementById('w-range-explanation');
    const zRangeExplanation = document.getElementById('z-range-explanation');
    const tauInfo = document.getElementById('tau-info');
    const wInfo = document.getElementById('w-info');
    const zInfo = document.getElementById('z-info');
    const generalFuncInfo = document.getElementById('general-func-info');
    const tauPlaneExplanation = document.getElementById('tau-plane-explanation');
    const zPlaneExplanation = document.getElementById('z-plane-explanation');
    const wPlaneExplanation = document.getElementById('w-plane-explanation');

    // --- Initial Plot Layouts (Modern Look) ---
    const createLayout = (functionType, plane, plotAspect) => {
        // Set axis titles based on selected function and plane
        let xTitle = 'τ_x';
        let yTitle = 'τ_y';
        let zTitle = plotAspect === 'phase' ? 'Phase' : 'Log Magnitude';
        
        // Default tick settings
        let xTickMode = 'auto';
        let yTickMode = 'auto';
        let xTickValues = null;
        let yTickValues = null;
        let xTickText = null;
        let yTickText = null;
        
        if (plane === 'w_plane') {
            xTitle = 'w_x (Re(w) = log|τ|)';
            yTitle = 'w_y (Im(w) = arg(τ))';
        } else if (plane === 'z_plane') {
            xTitle = 'τ_x (Direct)';
            yTitle = 'τ_y (Direct)';
            
            // Create custom tick values and labels for the z-plane
            // Get the current range from the slider
            const tauRange = parseFloat(document.getElementById('tauRange').value);
            
            // Create tick values for x-axis with 0 at center (representing infinity)
            const tickCount = 5; // Number of ticks on each side
            const tickStep = tauRange / tickCount;
            xTickValues = Array.from({length: 2 * tickCount + 1}, (_, i) => -tauRange + i * tickStep);
            
            // Generate special tick labels based on the original conception
            xTickText = xTickValues.map(val => {
                if (Math.abs(val) < 0.001) return '±∞'; // Origin is infinity
                
                // Calculate how far we are from the origin as a fraction (0 = at origin, 1 = at boundary)
                const fraction = Math.abs(val) / tauRange;
                
                // The midpoint is our transition point between infinity-based and natural numbers
                const midpoint = 0.5;
                
                if (val < 0) {
                    // Left side
                    if (fraction < midpoint) {
                        // First half: -∞+1, -∞+2, etc.
                        const n = Math.max(1, Math.round(fraction * tickCount));
                        return `-∞+${n}`;
                    } else {
                        // Second half approaching -δ: natural numbers counting down
                        const n = Math.round((1 - fraction) * tickCount);
                        if (fraction > 0.95) return '-δ';
                        return `${n}`;
                    }
                } else {
                    // Right side
                    if (fraction < midpoint) {
                        // First half: ∞-1, ∞-2, etc.
                        const n = Math.max(1, Math.round(fraction * tickCount));
                        return `∞-${n}`;
                    } else {
                        // Second half approaching +δ: natural numbers counting down
                        const n = Math.round((1 - fraction) * tickCount);
                        if (fraction > 0.95) return '+δ';
                        return `${n}`;
                    }
                }
            });
            
            // Do the same for y-axis
            yTickValues = Array.from({length: 2 * tickCount + 1}, (_, i) => -tauRange + i * tickStep);
            yTickText = yTickValues.map(val => {
                if (Math.abs(val) < 0.001) return '±∞'; // Origin is infinity
                
                // Calculate how far we are from the origin as a fraction (0 = at origin, 1 = at boundary)
                const fraction = Math.abs(val) / tauRange;
                
                // The midpoint is our transition point between infinity-based and natural numbers
                const midpoint = 0.5;
                
                if (val < 0) {
                    // Bottom side
                    if (fraction < midpoint) {
                        // First half: -∞+1, -∞+2, etc.
                        const n = Math.max(1, Math.round(fraction * tickCount));
                        return `-∞+${n}`;
                    } else {
                        // Second half approaching -δ: natural numbers counting down
                        const n = Math.round((1 - fraction) * tickCount);
                        if (fraction > 0.95) return '-δ';
                        return `${n}`;
                    }
                } else {
                    // Top side
                    if (fraction < midpoint) {
                        // First half: ∞-1, ∞-2, etc.
                        const n = Math.max(1, Math.round(fraction * tickCount));
                        return `∞-${n}`;
                    } else {
                        // Second half approaching +δ: natural numbers counting down
                        const n = Math.round((1 - fraction) * tickCount);
                        if (fraction > 0.95) return '+δ';
                        return `${n}`;
                    }
                }
            });
            
            // Set tick mode to array to use custom ticks
            xTickMode = 'array';
            yTickMode = 'array';
        }
        
        return {
            autosize: true,
            margin: { l: 50, r: 50, b: 50, t: 50, pad: 4 },
            scene: {
                aspectratio: { x: 1, y: 1, z: 0.7 },
                xaxis: { 
                    title: xTitle,
                    backgroundcolor: "rgb(230, 230,230)", 
                    gridcolor: "rgb(255, 255, 255)", 
                    zerolinecolor: "rgb(255, 255, 255)",
                    tickmode: xTickMode,
                    tickvals: xTickValues,
                    ticktext: xTickText
                },
                yaxis: { 
                    title: yTitle,
                    backgroundcolor: "rgb(230, 230,230)", 
                    gridcolor: "rgb(255, 255, 255)", 
                    zerolinecolor: "rgb(255, 255, 255)",
                    tickmode: yTickMode,
                    tickvals: yTickValues,
                    ticktext: yTickText
                },
                zaxis: { 
                    title: zTitle,
                    backgroundcolor: "rgb(230, 230,230)", 
                    gridcolor: "rgb(255, 255, 255)", 
                    zerolinecolor: "rgb(255, 255, 255)" 
                },
            },
            paper_bgcolor: 'rgba(0,0,0,0)', // Transparent background
            plot_bgcolor: 'rgba(0,0,0,0)'   // Transparent plot area
        };
    };
    
    // Layout for 2D plots
    const create2DLayout = (functionType, plane, plotType) => {
        // Set axis titles based on selected function and plane
        let xTitle = 'τ_x';
        let yTitle = 'τ_y';
        
        // Default tick settings (same as in createLayout function)
        let xTickMode = 'auto';
        let yTickMode = 'auto';
        let xTickValues = null;
        let yTickValues = null;
        let xTickText = null;
        let yTickText = null;
        
        if (plane === 'w_plane') {
            xTitle = 'w_x (Re(w) = log|τ|)';
            yTitle = 'w_y (Im(w) = arg(τ))';
        } else if (plane === 'z_plane') {
            xTitle = 'τ_x (Direct)';
            yTitle = 'τ_y (Direct)';
            
            // Using the same custom ticks as in the 3D plot
            const tauRange = parseFloat(document.getElementById('tauRange').value);
            const tickCount = 5;
            const tickStep = tauRange / tickCount;
            xTickValues = Array.from({length: 2 * tickCount + 1}, (_, i) => -tauRange + i * tickStep);
            yTickValues = Array.from({length: 2 * tickCount + 1}, (_, i) => -tauRange + i * tickStep);
            
            xTickText = xTickValues.map(val => {
                if (Math.abs(val) < 0.001) return '±∞';
                const fraction = Math.abs(val) / tauRange;
                const midpoint = 0.5;
                
                if (val < 0) {
                    if (fraction < midpoint) {
                        const n = Math.max(1, Math.round(fraction * tickCount));
                        return `-∞+${n}`;
                    } else {
                        const n = Math.round((1 - fraction) * tickCount);
                        if (fraction > 0.95) return '-δ';
                        return `${n}`;
                    }
                } else {
                    if (fraction < midpoint) {
                        const n = Math.max(1, Math.round(fraction * tickCount));
                        return `∞-${n}`;
                    } else {
                        const n = Math.round((1 - fraction) * tickCount);
                        if (fraction > 0.95) return '+δ';
                        return `${n}`;
                    }
                }
            });
            
            yTickText = yTickValues.map(val => {
                if (Math.abs(val) < 0.001) return '±∞';
                const fraction = Math.abs(val) / tauRange;
                const midpoint = 0.5;
                
                if (val < 0) {
                    if (fraction < midpoint) {
                        const n = Math.max(1, Math.round(fraction * tickCount));
                        return `-∞+${n}`;
                    } else {
                        const n = Math.round((1 - fraction) * tickCount);
                        if (fraction > 0.95) return '-δ';
                        return `${n}`;
                    }
                } else {
                    if (fraction < midpoint) {
                        const n = Math.max(1, Math.round(fraction * tickCount));
                        return `∞-${n}`;
                    } else {
                        const n = Math.round((1 - fraction) * tickCount);
                        if (fraction > 0.95) return '+δ';
                        return `${n}`;
                    }
                }
            });
            
            xTickMode = 'array';
            yTickMode = 'array';
        }
        
        // Get plot title based on selected view
        let plotTitle;
        switch (plotType) {
            case 'real':
                plotTitle = 'Real Part';
                break;
            case 'imag':
                plotTitle = 'Imaginary Part';
                break;
            case 'mag':
                plotTitle = 'Magnitude';
                break;
            case 'phase':
                plotTitle = 'Phase';
                break;
            default:
                plotTitle = 'Function Values';
        }
        
        return {
            title: plotTitle,
            autosize: true,
            margin: { l: 50, r: 50, b: 50, t: 50, pad: 4 },
            xaxis: { 
                title: xTitle,
                tickmode: xTickMode,
                tickvals: xTickValues,
                ticktext: xTickText,
                zeroline: true,
                zerolinecolor: 'rgba(0,0,0,0.2)',
                gridcolor: 'rgba(200,200,200,0.2)'
            },
            yaxis: { 
                title: yTitle,
                tickmode: yTickMode,
                tickvals: yTickValues,
                ticktext: yTickText,
                zeroline: true,
                zerolinecolor: 'rgba(0,0,0,0.2)',
                gridcolor: 'rgba(200,200,200,0.2)',
                scaleanchor: "x",
                scaleratio: 1
            },
            shapes: [],  // Will be populated with shapes like the liminal circle
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(245,245,245,0.8)'
        };
    };

    // --- Helper Functions ---
    function showLoading() {
        loadingIndicator.style.display = 'block';
        phasePlotDiv.style.display = 'none';
        magnitudePlotDiv.style.display = 'none';
        plot2dDiv.style.display = 'none';
    }

    function hideLoading() {
        loadingIndicator.style.display = 'none';
        phasePlotDiv.style.display = 'block';
        magnitudePlotDiv.style.display = 'block';
        plot2dDiv.style.display = 'block';
    }

    function updateSliderValue(slider, span) {
        const value = parseFloat(slider.value).toFixed(1);
        if (slider.id === 'tauRange') {
            span.textContent = `±${value}`;
        } else if (slider.id === 'liminalZoneRange') {
            span.textContent = `ε = ${value}`;
        } else {
            span.textContent = slider.value;
        }
    }

    function toggleZetaControls(show) {
        zetaControlsDiv.style.display = show ? 'block' : 'none';
    }
    
    function toggleLiminalZoneControl(plane) {
        // Only show liminal zone control for z-plane
        liminalZoneControlDiv.style.display = plane === 'z_plane' ? 'block' : 'none';
        
        // Also toggle the circles legend for the 2D plot
        const circlesLegend = document.getElementById('circles-legend');
        if (circlesLegend) {
            circlesLegend.style.display = plane === 'z_plane' ? 'flex' : 'none';
        }
    }
    
    function updateRangeLabel(plane) {
        if (plane === 'z_plane') {
            rangeLabel.textContent = 'z Range:';
        } else {
            rangeLabel.textContent = 'Range:';
        }
    }
    
    function updatePlaneExplanations(plane) {
        // First hide all explanations
        [tauExplanation, wExplanation, zExplanation].forEach(el => {
            el.style.display = 'none';
        });
        
        [tauRangeExplanation, wRangeExplanation, zRangeExplanation].forEach(el => {
            el.style.display = 'none';
        });
        
        [tauInfo, wInfo, zInfo, generalFuncInfo].forEach(el => {
            el.style.display = 'none';
        });
        
        [tauPlaneExplanation, zPlaneExplanation, wPlaneExplanation].forEach(el => {
            el.style.display = 'none';
        });
        
        // Then show the appropriate ones based on selected plane
        if (plane === 'w_plane') {
            wExplanation.style.display = 'inline';
            wRangeExplanation.style.display = 'inline';
            wInfo.style.display = 'block';
            wPlaneExplanation.style.display = 'inline';
        } else if (plane === 'z_plane') {
            zExplanation.style.display = 'inline';
            zRangeExplanation.style.display = 'inline';
            zInfo.style.display = 'block';
            zPlaneExplanation.style.display = 'inline';
        } else {
            // Default to tau plane
            tauExplanation.style.display = 'inline';
            tauRangeExplanation.style.display = 'inline';
            tauInfo.style.display = 'block';
            tauPlaneExplanation.style.display = 'inline';
        }
        
        // Always show general function info for context
        generalFuncInfo.style.display = 'block';
    }
    
    // Add shapes to the 2D cartesian plot
    function addShapesToPlot(layout, plane) {
        // Clear existing shapes
        layout.shapes = [];
        
        const tauRange = parseFloat(tauRangeSlider.value);
        
        // For z-plane, we add the liminal zone circle
        if (plane === 'z_plane') {
            // Add the outer circle representing the "±δ boundary"
            layout.shapes.push({
                type: 'circle',
                xref: 'x',
                yref: 'y',
                x0: -tauRange,
                y0: -tauRange,
                x1: tauRange,
                y1: tauRange,
                line: {
                    color: 'rgba(0,0,0,0.5)',
                    width: 2,
                    dash: 'dot'
                },
                fillcolor: 'rgba(0,0,0,0)',
                name: 'Boundary (±δ)'
            });
            
            // The liminal zone is always halfway between origin and boundary
            // regardless of the slider value
            const fixedLiminalRadius = tauRange * 0.5;
            
            // Add the liminal zone circle (inner circle)
            layout.shapes.push({
                type: 'circle',
                xref: 'x',
                yref: 'y',
                x0: -fixedLiminalRadius,
                y0: -fixedLiminalRadius,
                x1: fixedLiminalRadius,
                y1: fixedLiminalRadius,
                line: {
                    color: 'rgba(255,0,0,0.7)',
                    width: 2
                },
                fillcolor: 'rgba(255,0,0,0.1)',
                name: 'Liminal Zone (ε)'
            });
            
            // Also add the dynamic analysis radius controlled by the slider
            const analysisRadius = parseFloat(liminalZoneSlider.value);
            layout.shapes.push({
                type: 'circle',
                xref: 'x',
                yref: 'y',
                x0: -analysisRadius,
                y0: -analysisRadius,
                x1: analysisRadius,
                y1: analysisRadius,
                line: {
                    color: 'rgba(0,0,255,0.7)',
                    width: 2,
                    dash: 'dash'
                },
                fillcolor: 'rgba(0,0,255,0.05)',
                name: 'Analysis Radius (ε)'
            });
            
            // Add a point at the origin (representing infinity)
            layout.shapes.push({
                type: 'circle',
                xref: 'x',
                yref: 'y',
                x0: -0.05,
                y0: -0.05,
                x1: 0.05,
                y1: 0.05,
                line: {
                    color: 'black',
                    width: 2
                },
                fillcolor: 'black',
                name: 'Origin (±∞)'
            });
        }
        
        return layout;
    }
    
    // Function to convert expression to LaTeX format
    function convertToLatex(expression) {
        // Special case for Zeta function
        if (expression === 'zeta') {
            return '\\zeta(s)';
        }
        
        // Replace common patterns with LaTeX equivalents
        let latex = expression
            .replace(/\*/g, ' \\cdot ')
            .replace(/\^(\d+)/g, '^{$1}')
            .replace(/sqrt\(/g, '\\sqrt{')
            .replace(/sin\(/g, '\\sin(')
            .replace(/cos\(/g, '\\cos(')
            .replace(/tan\(/g, '\\tan(')
            .replace(/exp\(/g, '\\exp(')
            .replace(/log\(/g, '\\log(')
            .replace(/pi/g, '\\pi')
            .replace(/\(/g, '{(')
            .replace(/\)/g, ')}');
        
        // Restore some patterns that might have been over-replaced
        latex = latex
            .replace(/{(\(})\}/g, '(')
            .replace(/{\)}/g, ')')
            .replace(/\^{(\d+)}/g, '^{$1}');
        
        return latex;
    }
    
    // Function to populate function analysis section
    function updateFunctionAnalysis(functionString, data) {
        functionAnalysisDiv.style.display = 'block';
        
        // Update LaTeX formula
        const latexFormula = convertToLatex(functionString);
        latexFunctionSpan.innerHTML = `f(z) = \\(${latexFormula}\\)`;
        
        // Update/render MathJax
        if (window.MathJax) {
            // Force a complete typeset of the page
            MathJax.typesetClear();
            MathJax.typeset();
        }
        
        // Build comprehensive analysis content
        let analysisHTML = '';
        
        // Add special section for Riemann Zeta function
        if (functionString === 'zeta' && data.analysis && data.analysis.important_facts) {
            analysisHTML += `
                <div class="analysis-section zeta-facts">
                    <h3>Riemann Zeta Function Properties</h3>
                    <div class="important-facts">
                        <h4>Key Mathematical Facts</h4>
                        <ul>
                            ${Object.entries(data.analysis.important_facts)
                                .filter(([key, _]) => key !== 'first_few_zeros')
                                .map(([key, value]) => `<li><strong>${key.replace(/_/g, ' ')}:</strong> ${value}</li>`)
                                .join('')}
                        </ul>
                    </div>
                    
                    <div class="special-values">
                        <h4>Special Values</h4>
                        <ul>
                            ${Object.entries(data.analysis.special_values).map(([key, value]) => 
                                `<li><strong>ζ${key.startsWith('at_') ? `(${key.substring(3)})` : ''}:</strong> ${value}</li>`
                            ).join('')}
                        </ul>
                    </div>
                    
                    <div class="zeta-zeros">
                        <h4>First Few Non-Trivial Zeros</h4>
                        <ul>
                            ${data.analysis.important_facts.first_few_zeros.map(zero => 
                                `<li>s = ${zero}</li>`
                            ).join('')}
                        </ul>
                    </div>
                </div>
            `;
        }
        
        // Critical points for any function
        if (data.analysis && data.analysis.critical_points && data.analysis.critical_points.length > 0) {
            analysisHTML += `
                <div class="analysis-section">
                    <h4>Critical Points</h4>
                    <div class="critical-points-grid">
                        ${data.analysis.critical_points.map(point => `
                            <div class="critical-point">
                                <p>z = \\(${point.z_real.toFixed(4)} ${point.z_imag >= 0 ? '+' : ''}${point.z_imag.toFixed(4)}i\\)</p>
                                <p>Type: ${point.type}</p>
                                ${point.function_value ? `<p>Value: \\(${point.function_value}\\)</p>` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        } else {
            analysisHTML += `
                <div class="analysis-section">
                    <h4>Critical Points</h4>
                    <p>No critical points found in the analyzed region</p>
                </div>
            `;
        }
        
        // Domain properties
        if (data.analysis && data.analysis.domain_properties) {
            const props = data.analysis.domain_properties;
            
            analysisHTML += `
                <div class="analysis-section">
                    <h4>Domain Properties</h4>
                    <table class="properties-table">
                        <tr><td>Description:</td><td>${props.description || 'Not available'}</td></tr>
                        <tr><td>Domain:</td><td>${props.domain || 'Not specified'}</td></tr>
                        <tr><td>Singularities:</td><td>${props.singularities || 'None detected'}</td></tr>
                        <tr><td>Branch points:</td><td>${props.branch_points || 'None detected'}</td></tr>
                        <tr><td>Growth rate:</td><td>${props.growth_rate || 'Undetermined'}</td></tr>
                    </table>
                </div>
            `;
            
            // Series expansions if available
            if (props.series_expansion || props.laurent_expansion) {
                analysisHTML += `
                    <div class="analysis-section">
                        <h4>Series Expansions</h4>
                `;
                
                if (props.series_expansion) {
                    const seriesLatex = props.series_expansion
                        .replace(/\*\*/g, '^')
                        .replace(/\*/g, ' \\cdot ')
                        .replace(/\^(\d+)/g, '^{$1}');
                    
                    analysisHTML += `
                        <p><strong>Taylor series:</strong> \\(${seriesLatex}\\)</p>
                    `;
                }
                
                if (props.laurent_expansion) {
                    const laurentLatex = props.laurent_expansion
                        .replace(/\*\*/g, '^')
                        .replace(/\*/g, ' \\cdot ')
                        .replace(/\^(\d+)/g, '^{$1}');
                    
                    analysisHTML += `
                        <p><strong>Laurent series:</strong> \\(${laurentLatex}\\)</p>
                    `;
                }
                
                analysisHTML += `</div>`;
            }
        }
        
        // Special values
        if (data.analysis && data.analysis.special_values) {
            const specialVals = data.analysis.special_values;
            
            analysisHTML += `
                <div class="analysis-section">
                    <h4>Special Values</h4>
                    <table class="properties-table">
                        ${Object.entries(specialVals).map(([key, value]) => 
                            `<tr><td>f(${key.replace('at_', '')}): </td><td>\\(${value}\\)</td></tr>`
                        ).join('')}
                    </table>
                </div>
            `;
        }
        
        // Differential equations
        if (data.analysis && data.analysis.differential_equations && data.analysis.differential_equations.note) {
            analysisHTML += `
                <div class="analysis-section">
                    <h4>Differential Equations</h4>
                    <p>${data.analysis.differential_equations.note}</p>
                </div>
            `;
        }
        
        // Update the analysis sections
        const analysisContent = document.getElementById('analysis-content');
        if (analysisContent) {
            analysisContent.innerHTML = analysisHTML;
        } else {
            functionAnalysisDiv.innerHTML = `
                <h3>Function Analysis</h3>
                <div class="latex-formula">
                    <p>Current function: <span id="latex-function">${latexFunctionSpan.innerHTML}</span></p>
                </div>
                <div id="analysis-content">
                    ${analysisHTML}
                </div>
            `;
        }
        
        // Force MathJax to typeset again after updating all content
        if (window.MathJax) {
            setTimeout(() => {
                MathJax.typesetClear();
                MathJax.typeset();
            }, 100);
        }
    }

    // --- Fetch and Update Plot Function ---
    async function fetchAndUpdatePlot() {
        showLoading();

        const tauAbs = parseFloat(tauRangeSlider.value);
        const points = parseInt(pointsSlider.value);
        const numZeros = parseInt(numZerosSlider.value);
        const tMaxCrit = parseInt(tMaxCritSlider.value);
        const plane = planeSelect.value; 
        const liminalRadius = parseFloat(liminalZoneSlider.value);
        
        // Get function from input or dropdown
        let functionText = '';
        let plotType = 'general_func';  // Default to general function
        
        if (functionSelect.value === 'zeta') {
            plotType = 'zeta';
            functionText = 'zeta';
        } else if (functionSelect.value === 'custom') {
            functionText = functionInput.value;
        } else {
            functionText = functionSelect.value;
            // Also update the function input box to show the selected function
            functionInput.value = functionText;
        }

        // Construct API URL with parameters
        const params = new URLSearchParams({
            plot_type: plotType,
            tau_min: -tauAbs,
            tau_max: tauAbs,
            points: points,
            plane: plane,
            liminal_radius: liminalRadius
        });

        if (plotType === 'zeta') {
            params.append('num_zeros', numZeros);
            params.append('t_max_crit', tMaxCrit);
        } else {
            params.append('function', functionText);
            params.append('analyze', 'true'); // Request function analysis
        }

        try {
            const response = await fetch(`/api/plot_data?${params.toString()}`);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
            const data = await response.json();

            // --- Create layouts based on selected function and plane ---
            const phaseLayout = createLayout(functionText, plane, 'phase');
            const magnitudeLayout = createLayout(functionText, plane, 'magnitude');
            
            // Get selected 2D view type from radio buttons
            const selectedView = document.querySelector('input[name="plot2d-view"]:checked').value;
            let plot2dLayout = create2DLayout(functionText, plane, selectedView);
            plot2dLayout = addShapesToPlot(plot2dLayout, plane);

            // --- Clear existing plots ---
            Plotly.purge(phasePlotDiv);
            Plotly.purge(magnitudePlotDiv);
            Plotly.purge(plot2dDiv);

            // --- Create Traces based on data type ---
            const phaseTrace = {
                type: 'surface',
                x: data.tau_x,
                y: data.tau_y,
                z: data.phase,
                colorscale: 'Viridis', // Or a more modern one like 'Plasma' or 'Cividis'
                showscale: true,
                name: 'Phase'
            };

            const magnitudeTrace = {
                type: 'surface',
                x: data.tau_x,
                y: data.tau_y,
                z: data.magnitude,
                colorscale: 'Plasma',
                showscale: true,
                name: 'Magnitude'
            };
            
            const plotTracesPhase = [phaseTrace];
            const plotTracesMagnitude = [magnitudeTrace];
            
            // --- Create 2D Cartesian plot traces ---
            // Create a more detailed grid for contour plots
            const plot2dTraces = [];
            
            // Create 2D trace based on selected view type
            if (selectedView === 'real') {
                plot2dTraces.push({
                    type: 'contour',
                    x: data.tau_x,
                    y: data.tau_y,
                    z: data.real_part || [],
                    colorscale: 'RdBu',
                    contours: {
                        coloring: 'heatmap'
                    },
                    showscale: true,
                    name: 'Real Part'
                });
            } else if (selectedView === 'imag') {
                plot2dTraces.push({
                    type: 'contour',
                    x: data.tau_x,
                    y: data.tau_y,
                    z: data.imag_part || [],
                    colorscale: 'RdBu',
                    contours: {
                        coloring: 'heatmap'
                    },
                    showscale: true,
                    name: 'Imaginary Part'
                });
            } else if (selectedView === 'mag') {
                // Log scale for magnitude is often more informative
                const logMagnitude = data.magnitude.map(row => 
                    row.map(val => Math.log(Math.max(val, 1e-10)))
                );
                
                plot2dTraces.push({
                    type: 'contour',
                    x: data.tau_x,
                    y: data.tau_y,
                    z: data.magnitude,
                    colorscale: 'Viridis',
                    contours: {
                        coloring: 'heatmap'
                    },
                    showscale: true,
                    name: 'Magnitude (Log Scale)'
                });
            } else if (selectedView === 'phase') {
                plot2dTraces.push({
                    type: 'contour',
                    x: data.tau_x,
                    y: data.tau_y,
                    z: data.phase,
                    colorscale: 'Jet',
                    contours: {
                        coloring: 'heatmap'
                    },
                    showscale: true,
                    name: 'Phase'
                });
            }

            // Add critical line and zeros for zeta plots
            if ((data.type === 'zeta') && data.critical_line && data.zeros) {
                const criticalLineTrace = {
                    type: 'scatter3d',
                    mode: 'lines',
                    x: data.critical_line.x,
                    y: data.critical_line.y,
                    z: Array(data.critical_line.x.length).fill(0), // Plot on z=0 plane for visibility
                    line: { color: 'red', width: 4 },
                    name: 'Critical Line'
                };
                const zerosTrace = {
                    type: 'scatter3d',
                    mode: 'markers',
                    x: data.zeros.x,
                    y: data.zeros.y,
                    z: Array(data.zeros.x.length).fill(0), // Plot on z=0 plane
                    marker: { color: 'black', size: 5, symbol: 'circle' },
                    name: 'Zeros'
                };
                plotTracesPhase.push(criticalLineTrace, zerosTrace);
                plotTracesMagnitude.push(criticalLineTrace, zerosTrace);
                
                // Also add to 2D plot
                plot2dTraces.push({
                    type: 'scatter',
                    mode: 'lines',
                    x: data.critical_line.x,
                    y: data.critical_line.y,
                    line: { color: 'red', width: 2 },
                    name: 'Critical Line'
                });
                
                plot2dTraces.push({
                    type: 'scatter',
                    mode: 'markers',
                    x: data.zeros.x,
                    y: data.zeros.y,
                    marker: { color: 'black', size: 8, symbol: 'x' },
                    name: 'Zeros'
                });
            }
            
            // Add critical points if available
            if (data.type === 'general_func' && data.analysis && data.analysis.critical_points) {
                const criticalPointsTrace = {
                    type: 'scatter3d',
                    mode: 'markers',
                    x: data.analysis.critical_points.map(p => p.tau_real),
                    y: data.analysis.critical_points.map(p => p.tau_imag),
                    z: Array(data.analysis.critical_points.length).fill(0), // Plot on z=0 plane
                    marker: { color: 'red', size: 6, symbol: 'cross' },
                    name: 'Critical Points'
                };
                plotTracesPhase.push(criticalPointsTrace);
                plotTracesMagnitude.push(criticalPointsTrace);
                
                // Also add to 2D plot
                plot2dTraces.push({
                    type: 'scatter',
                    mode: 'markers',
                    x: data.analysis.critical_points.map(p => p.tau_real),
                    y: data.analysis.critical_points.map(p => p.tau_imag),
                    marker: { color: 'red', size: 8, symbol: 'star' },
                    name: 'Critical Points'
                });
            }
            
            // Apply custom formatting to the 2D plot
            plot2dLayout.margin = { l: 60, r: 60, t: 40, b: 60 };  // Increase margins for tick labels
            plot2dLayout.annotations = [];  // Clear any existing annotations
            
            // Customize font sizes for better readability
            plot2dLayout.font = { size: 11 };
            plot2dLayout.xaxis.title = { text: plot2dLayout.xaxis.title, font: { size: 12 } };
            plot2dLayout.yaxis.title = { text: plot2dLayout.yaxis.title, font: { size: 12 } };
            
            // Add a title annotation for z-plane to explain the liminal circles
            if (plane === 'z_plane') {
                // Adjust the colorscale range to highlight the liminal zone boundary
                if (plot2dTraces[0].type === 'contour') {
                    plot2dTraces[0].contours = {
                        coloring: 'heatmap',
                        showlabels: true,
                        labelfont: {
                            size: 10,
                            color: 'rgba(0,0,0,0.5)'
                        }
                    };
                }
            }
            
            // --- Render Plots ---
            Plotly.newPlot(phasePlotDiv, plotTracesPhase, phaseLayout, {responsive: true});
            Plotly.newPlot(magnitudePlotDiv, plotTracesMagnitude, magnitudeLayout, {responsive: true});
            Plotly.newPlot(plot2dDiv, plot2dTraces, plot2dLayout, {responsive: true});

            // Update function analysis section if this is a general function
            if (data.type === 'general_func' && data.function) {
                updateFunctionAnalysis(data.function, data);
            } else if (data.type === 'zeta') {
                // For zeta function, we can show a special analysis or hide it
                functionAnalysisDiv.style.display = 'none';
            } else {
                functionAnalysisDiv.style.display = 'none';
            }

        } catch (error) {
            console.error('Error fetching or plotting data:', error);
            
            // Create more user-friendly error messages based on the error text
            let errorMessage = error.message;
            
            // Handle specific function evaluation errors with more helpful messages
            if (errorMessage.includes('Function evaluation error')) {
                if (errorMessage.includes('not defined')) {
                    errorMessage = 'Function error: Make sure you\'re using supported functions (sin, cos, tan, log, exp, sqrt, abs)';
                } else if (errorMessage.includes('division by zero')) {
                    errorMessage = 'Function error: Division by zero in your expression';
                } else if (errorMessage.includes('Invalid function string')) {
                    errorMessage = 'Function error: Please use only valid mathematical expressions with z as the variable';
                }
            }
            
            // Display error messages in the plot divs
            phasePlotDiv.innerHTML = `<p style="color: red; padding: 20px;">Error loading phase plot: ${errorMessage}</p>`;
            magnitudePlotDiv.innerHTML = `<p style="color: red; padding: 20px;">Error loading magnitude plot: ${errorMessage}</p>`;
            plot2dDiv.innerHTML = `<p style="color: red; padding: 20px;">Error loading 2D plot: ${errorMessage}</p>`;
            
            // Hide analysis panel on error
            functionAnalysisDiv.style.display = 'none';
        } finally {
            hideLoading();
        }
    }

    // --- Event Listeners ---
    tauRangeSlider.addEventListener('input', () => updateSliderValue(tauRangeSlider, tauRangeValueSpan));
    pointsSlider.addEventListener('input', () => updateSliderValue(pointsSlider, pointsValueSpan));
    numZerosSlider.addEventListener('input', () => updateSliderValue(numZerosSlider, numZerosValueSpan));
    tMaxCritSlider.addEventListener('input', () => updateSliderValue(tMaxCritSlider, tMaxCritValueSpan));
    liminalZoneSlider.addEventListener('input', () => {
        updateSliderValue(liminalZoneSlider, liminalZoneValueSpan);
        // If in z-plane, update plot to reflect new liminal zone
        if (planeSelect.value === 'z_plane') {
            fetchAndUpdatePlot();
        }
    });
    
    functionSelect.addEventListener('change', () => {
        // Show/hide appropriate controls based on function selection
        toggleZetaControls(functionSelect.value === 'zeta');
        
        // Update function input if a predefined function is selected
        if (functionSelect.value !== 'custom') {
            functionInput.value = functionSelect.value;
        }
        
        // Don't auto-update on change to avoid excessive server load
    });
    
    planeSelect.addEventListener('change', () => {
        const plane = planeSelect.value;
        
        // Update range labels and explanations
        updateRangeLabel(plane);
        updatePlaneExplanations(plane);
        toggleLiminalZoneControl(plane);
        
        // Update plot
        fetchAndUpdatePlot();
    });

    // Add event listeners for 2D view radio buttons
    plot2dViewRadios.forEach(radio => {
        radio.addEventListener('change', fetchAndUpdatePlot);
    });

    updateButton.addEventListener('click', fetchAndUpdatePlot);
    
    // Event listener for function input (debounced)
    let debounceTimeout;
    functionInput.addEventListener('input', () => {
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(() => {
            // If the user edits the function input, switch the dropdown to "custom"
            functionSelect.value = 'custom';
        }, 500);
    });

    // --- Initial Setup ---
    updateSliderValue(tauRangeSlider, tauRangeValueSpan);
    updateSliderValue(pointsSlider, pointsValueSpan);
    updateSliderValue(numZerosSlider, numZerosValueSpan);
    updateSliderValue(tMaxCritSlider, tMaxCritValueSpan);
    updateSliderValue(liminalZoneSlider, liminalZoneValueSpan);
    toggleZetaControls(functionSelect.value === 'zeta');
    updateRangeLabel(planeSelect.value);
    updatePlaneExplanations(planeSelect.value);
    toggleLiminalZoneControl(planeSelect.value);
    fetchAndUpdatePlot(); // Initial plot load
});
