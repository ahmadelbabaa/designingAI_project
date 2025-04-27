# HPC Prediction Analysis Project - Implementation Rules and Guidelines

## CRITICAL NOTICE: READ BEFORE ANY IMPLEMENTATION

This document provides **mandatory rules and guidelines** for implementing any changes to the HPC Prediction Analysis project. These rules are designed to prevent disruption to existing functionality, preserve completed work, and ensure seamless integration of new components.

## 1. GENERAL PRINCIPLES

### 1.1 Preservation of Existing Work

**CRITICAL - DO NOT:**
- **NEVER replace or rewrite existing functional code** - The project has established components that are working correctly
- **NEVER modify the core architecture** - The Flask application structure, data flow, and component organization are fixed
- **NEVER delete or rename existing files** - This breaks established references and dependencies
- **NEVER modify existing function signatures** - Other code depends on these interfaces

**MUST DO:**
- **ALWAYS build upon existing components** - Extend functionality through defined extension points
- **ALWAYS maintain backward compatibility** - Ensure existing code continues to function
- **ALWAYS use established patterns** - Follow the patterns in existing files
- **ALWAYS commit incremental changes** - Make small, testable additions rather than large rewrites

### 1.2 Integration Philosophy

**CRITICAL - DO NOT:**
- **NEVER create parallel implementations** - Do not create new versions of existing functionality
- **NEVER introduce conflicting dependencies** - Check `requirements.txt` before adding new libraries
- **NEVER bypass established data flows** - All components must use the defined data exchange mechanisms
- **NEVER implement functionality that duplicates existing code** - Reuse existing utilities

**MUST DO:**
- **ALWAYS leverage existing utilities** - Check `utils/` directory before implementing new helper functions
- **ALWAYS follow the modular architecture** - Each component should have clear boundaries
- **ALWAYS use the component registration system** - New dashboard elements must register properly
- **ALWAYS validate integration points** - Test that your component works with existing ones

## 2. PROTECTED COMPONENTS - DO NOT MODIFY

### 2.1 Core Framework Files

The following files form the core framework and **MUST NOT be modified** except through the designated extension points:

```
enhanced_dashboard.py                # Core Flask application - only add routes, do not modify existing ones
api_gateway.py                       # API gateway - only add new endpoints, never modify existing ones
utils/shared_data_manager.py         # Data sharing system - use but do not modify
utils/auth_manager.py                # Authentication system - use but do not modify
utils/pipeline_logger.py             # Logging system - use but do not modify
config/dashboard_config.json         # Dashboard configuration - only add, never remove
static/js/dashboard_controller.js    # Dashboard controller - only use existing hooks
static/js/data_store.js              # Data store - use API, do not modify implementation
static/js/event_bus.js               # Event system - use API, do not modify implementation
templates/dashboard.html             # Main dashboard template - only modify designated sections
```

### 2.2 Completed Analysis Components

The following components are **COMPLETE** and must not be modified:

```
conversion_advisor.py                # Gas station conversion analysis - COMPLETE
templates/conversion_advisor.html    # Conversion advisor template - COMPLETE
time_series_forecasting.py           # Forecasting functionality - COMPLETE
HPC_integration_part1.py             # Data pipeline part 1 - COMPLETE
HPC_integration_part2.py             # Data pipeline part 2 - COMPLETE
HPC_integration_part3.py             # Data pipeline part 3 - COMPLETE
```

### 2.3 Data Processing Pipeline

The data processing pipeline is complete and fully functional. **DO NOT:**
- Modify the ETL process
- Change data validation rules
- Alter the data integration flow
- Modify the output format of integrated datasets

### 2.4 Dashboard Structure

The base dashboard structure is established. **DO NOT:**
- Change the navigation system
- Modify the layout framework
- Alter the component loading mechanism
- Change the authentication mechanism

## 3. EXTENSIBLE AREAS - IMPLEMENTATION GUIDANCE

### 3.1 Adding the EV Charging Pattern Analysis Component

**DO:**
- Create a new file `ev_charging_analysis.py` in the root directory
- Implement the specified analysis functions
- Generate visualizations to `output/charging_patterns/`
- Create a new template `templates/charging_patterns.html`
- Add a new route to `enhanced_dashboard.py` for the component
- Register the component in `config/dashboard_components.json`

**DO NOT:**
- Create additional analysis scripts beyond `ev_charging_analysis.py`
- Modify existing datasets - use them as read-only inputs
- Create new data processing pipelines - use the existing pipeline

**SPECIFIC IMPLEMENTATION REQUIREMENTS:**
1. `ev_charging_analysis.py` must include these functions:
   - `analyze_time_patterns(data)` - For temporal analysis
   - `analyze_station_utilization(data)` - For utilization analysis
   - `analyze_energy_delivery(data)` - For energy volume analysis
   - `analyze_session_duration(data)` - For session length analysis
   - `analyze_user_behavior(data)` - For user clustering
   - `generate_visualizations(output_dir)` - To create all visualizations
   - `run_analysis()` - Main entry point for CLI usage

2. The Flask route in `enhanced_dashboard.py` must follow this pattern:
   ```python
   @app.route('/charging-patterns')
   def charging_patterns():
       # Analysis logic or import from ev_charging_analysis.py
       return render_template('charging_patterns.html', data=analysis_data)
   ```

3. The template should extend the base template:
   ```html
   {% extends "base.html" %}
   {% block content %}
     <!-- Charging patterns specific content -->
   {% endblock %}
   ```

### 3.2 Dashboard Integration

**DO:**
- Add a new card to the dashboard home in the designated section:
  ```html
  <!-- BEGIN EXTENSIBLE SECTION: DASHBOARD CARDS -->
  <!-- Your new card here -->
  <!-- END EXTENSIBLE SECTION: DASHBOARD CARDS -->
  ```
- Register your component in `config/dashboard_components.json`:
  ```json
  {
    "id": "charging_patterns",
    "name": "EV Charging Patterns",
    "route": "/charging-patterns",
    "icon": "chart-line",
    "permission": "analyst"
  }
  ```
- Subscribe to relevant data streams:
  ```javascript
  // In your component's JS file
  EventBus.subscribe('ev_charging_data_updated', function(data) {
    // Update your component's view
  });
  ```

**DO NOT:**
- Modify the dashboard card layout system
- Change the navigation generation mechanism
- Alter the component loading framework
- Modify permission structures

### 3.3 API Extensions

**DO:**
- Add new API endpoints in a structured way:
  ```python
  @app.route('/api/v1/charging-patterns/summary', methods=['GET'])
  def charging_patterns_summary_api():
      # Return JSON summary data
      return jsonify(get_charging_patterns_summary())
  ```
- Document new API endpoints in code comments
- Use the existing authentication mechanisms:
  ```python
  @app.route('/api/v1/charging-patterns/detailed', methods=['GET'])
  @requires_auth(['analyst', 'admin'])  # Use existing decorator
  def charging_patterns_detailed_api():
      # Return detailed data
      return jsonify(get_charging_patterns_detailed())
  ```

**DO NOT:**
- Create parallel API structures
- Bypass the API gateway
- Implement custom authentication
- Create redundant endpoints for existing functionality

## 4. INTEGRATION WITH EXISTING DATA

### 4.1 Using Shared Datasets

**DO:**
- Access existing datasets through the shared data manager:
  ```python
  from utils.shared_data_manager import get_data
  
  def analyze_charging_patterns():
      ev_data = get_data('ev_charging_patterns')
      station_data = get_data('station_data_dataverse')
      # Perform analysis...
  ```
- Subscribe to data updates:
  ```python
  from utils.shared_data_manager import subscribe
  
  subscribe('ev_charging_patterns', on_charging_data_updated)
  ```

**DO NOT:**
- Create duplicate copies of datasets
- Implement custom data loading mechanisms
- Store intermediate datasets outside the established structure
- Modify existing datasets directly

### 4.2 Producing Output Artifacts

**DO:**
- Store visualization files in the designated directory:
  ```python
  def generate_visualizations():
      output_dir = 'output/charging_patterns/'
      os.makedirs(output_dir, exist_ok=True)
      # Generate and save visualizations...
  ```
- Follow established naming conventions:
  ```
  output/charging_patterns/hourly_usage.png
  output/charging_patterns/daily_patterns.png
  output/charging_patterns/station_comparison.png
  output/charging_patterns/user_segments.png
  ```

**DO NOT:**
- Store outputs in non-standard locations
- Use inconsistent naming patterns
- Create visualization formats incompatible with the dashboard
- Generate excessive numbers of output files

## 5. CODE STYLE AND STANDARDS

### 5.1 Python Standards

**DO:**
- Follow PEP 8 style guidelines
- Use docstrings for all functions and classes:
  ```python
  def analyze_time_patterns(data):
      """
      Analyze temporal patterns in charging data.
      
      Args:
          data (pandas.DataFrame): Charging session data with timestamps
          
      Returns:
          dict: Dictionary containing temporal pattern analysis results
      """
      # Implementation...
  ```
- Implement proper error handling:
  ```python
  try:
      # Operation that might fail
  except SpecificException as e:
      logging.error(f"Specific error occurred: {e}")
      # Handle the error appropriately
  ```
- Use type hints:
  ```python
  def analyze_station_utilization(data: pd.DataFrame) -> Dict[str, Any]:
      # Implementation...
  ```

**DO NOT:**
- Use global variables
- Write functions longer than 50 lines
- Use non-descriptive variable names
- Skip error handling

### 5.2 JavaScript Standards

**DO:**
- Follow the existing patterns in dashboard JavaScript:
  ```javascript
  // Namespace your components
  const ChargingPatterns = {
    init: function() {
      // Initialization code
    },
    updateView: function(data) {
      // Update the visualization
    }
  };
  
  // Initialize on document ready
  $(document).ready(function() {
    ChargingPatterns.init();
  });
  ```
- Use the event bus for communication:
  ```javascript
  EventBus.publish('charging_patterns_updated', newData);
  ```

**DO NOT:**
- Use global functions
- Modify existing JavaScript objects
- Use different UI frameworks than what's already in use
- Implement custom AJAX mechanisms instead of using the provided ones

### 5.3 HTML/CSS Standards

**DO:**
- Extend existing templates:
  ```html
  {% extends "base.html" %}
  {% block title %}Charging Patterns Analysis{% endblock %}
  {% block content %}
    <!-- Component-specific content -->
  {% endblock %}
  ```
- Use the established CSS classes and variables:
  ```html
  <div class="dashboard-card">
    <h2 class="card-title">Charging Patterns</h2>
    <div class="card-content">
      <!-- Content -->
    </div>
  </div>
  ```

**DO NOT:**
- Create new base templates
- Use inline styles
- Implement custom CSS frameworks
- Override global styles

## 6. GPT-4o INTEGRATION COMPLIANCE

### 6.1 Using the GPT-4o API

**DO:**
- Use the established integration mechanism:
  ```python
  from utils.gpt4o_integration import query_model
  
  def get_ai_insights(data):
      prompt = format_prompt_for_charging_insights(data)
      return query_model(prompt, temperature=0.3)
  ```
- Use the predefined system prompts:
  ```python
  from utils.gpt4o_integration import load_system_prompt
  
  system_prompt = load_system_prompt('charging_analysis')
  ```

**DO NOT:**
- Implement separate OpenAI API calls
- Create custom prompt management systems
- Bypass rate limiting mechanisms
- Store API keys in code

### 6.2 Extending AI Features

**DO:**
- Add new system prompts in the designated directory:
  ```
  config/system_prompts/charging_patterns_analysis.txt
  ```
- Register new AI features in the configuration:
  ```json
  {
    "feature_id": "charging_insights",
    "prompt_file": "charging_patterns_analysis.txt",
    "required_data": ["ev_charging_patterns"],
    "default_temperature": 0.3
  }
  ```

**DO NOT:**
- Create ad-hoc prompts in code
- Hardcode model parameters
- Bypass the conversation management system
- Implement custom streaming mechanisms

## 7. TESTING REQUIREMENTS

### 7.1 Must-Have Tests

**DO:**
- Write unit tests for all new functions:
  ```python
  def test_analyze_time_patterns():
      test_data = pd.DataFrame({
          'start_time': ['2023-01-01 08:00:00', '2023-01-01 12:00:00'],
          'end_time': ['2023-01-01 10:00:00', '2023-01-01 14:00:00'],
          'energy_delivered': [10.5, 15.2],
          'station_id': ['S001', 'S002'],
          'user_id': ['U001', 'U002']
      })
      result = analyze_time_patterns(test_data)
      assert 'hourly_distribution' in result
      assert len(result['hourly_distribution']) == 24
  ```
- Test integration with the dashboard:
  ```python
  def test_charging_patterns_route():
      client = app.test_client()
      response = client.get('/charging-patterns')
      assert response.status_code == 200
      assert b'Charging Patterns Analysis' in response.data
  ```

**DO NOT:**
- Skip testing critical functionality
- Assume existing components will integrate automatically
- Write tests that modify production data
- Create tests with external dependencies

### 7.2 Regression Testing

**DO:**
- Run existing test suite before and after changes:
  ```bash
  python -m pytest tests/
  ```
- Verify dashboard functionality manually:
  1. Start the dashboard
  2. Navigate to each existing component
  3. Confirm all visualizations and features work
  4. Test the new component alongside existing ones

**DO NOT:**
- Disable existing tests
- Skip regression testing
- Assume backward compatibility
- Submit code with failing tests

## 8. FILE-BY-FILE MODIFICATION GUIDANCE

### 8.1 New Files to Create

You **MUST** create these files:

1. `ev_charging_analysis.py` - Main analysis script
2. `templates/charging_patterns.html` - Dashboard template
3. `static/js/charging_patterns.js` - Frontend JavaScript
4. `tests/test_ev_charging_analysis.py` - Unit tests

### 8.2 Files You May Modify (ONLY in specified ways)

1. `enhanced_dashboard.py`
   - **ONLY** add a new route for charging patterns
   - **DO NOT** modify existing routes
   - **DO NOT** change application configuration

2. `templates/dashboard.html`
   - **ONLY** add a new card in the designated extensible section
   - **DO NOT** modify the layout structure
   - **DO NOT** change existing cards

3. `config/dashboard_components.json`
   - **ONLY** add a new component entry
   - **DO NOT** modify existing component entries
   - **DO NOT** change the file structure

4. `static/css/dashboard_styles.css`
   - **ONLY** add new classes specific to your component
   - **DO NOT** modify existing CSS classes
   - **DO NOT** change global styles

### 8.3 Files You MUST NOT Modify

1. **Data Processing Pipeline**:
   - `HPC_integration_part1.py`
   - `HPC_integration_part2.py`
   - `HPC_integration_part3.py`
   - `data_validation_rules.py`

2. **Existing Analysis Components**:
   - `conversion_advisor.py`
   - `time_series_forecasting.py`
   - `hpc_pricing_rl.py`

3. **Core Dashboard Framework**:
   - `static/js/dashboard_controller.js`
   - `static/js/data_store.js`
   - `static/js/event_bus.js`
   - `utils/shared_data_manager.py`
   - `utils/auth_manager.py`
   - `utils/pipeline_logger.py`

4. **Existing Templates**:
   - `templates/base.html`
   - `templates/conversion_advisor.html`
   - `templates/forecasting.html`

5. **Configuration Files**:
   - `config/hpc_cost_params.yaml`
   - `config/forecast_models.yaml`
   - `config/data_sources.json`

## 9. IMPLEMENTATION SEQUENCE

Follow this precise sequence of implementation steps:

1. **Data Exploration and Analysis**
   - First examine the structure of `ev_charging_patterns.csv`
   - Understand the schema and relationships
   - Plan the analysis approach based on requirements

2. **Core Analysis Functions**
   - Implement the time-based pattern analysis
   - Implement the station utilization analysis
   - Implement the energy delivery analysis
   - Implement the session duration analysis
   - Implement the user behavior analysis

3. **Visualization Generation**
   - Create visualization functions for each analysis
   - Generate output files to `output/charging_patterns/`
   - Ensure visualizations are consistent with dashboard style

4. **Dashboard Template**
   - Create the `charging_patterns.html` template
   - Structure it to display all visualizations
   - Implement interactive elements if required

5. **Dashboard Integration**
   - Add the route to `enhanced_dashboard.py`
   - Register the component in `config/dashboard_components.json`
   - Add a card to the dashboard home page

6. **Frontend Interactivity**
   - Implement JavaScript for interactive features
   - Connect to data streams via the event bus
   - Implement any client-side filtering or analysis

7. **Testing**
   - Write unit tests for analysis functions
   - Test dashboard integration
   - Perform regression testing on existing components

8. **Documentation**
   - Document the analysis approach and functions
   - Update user documentation if needed
   - Document API endpoints and usage

## 10. SUMMARY OF CRITICAL RULES

1. **NEVER replace existing functionality** - Only extend and enhance
2. **NEVER modify core files** - Use only designated extension points
3. **ALWAYS follow existing patterns** - Maintain consistency with the codebase
4. **ALWAYS test thoroughly** - Ensure both new and existing features work
5. **ALWAYS use established APIs** - Don't create parallel systems
6. **ONLY modify files you are explicitly permitted to change**
7. **ONLY add new functionality through defined extension mechanisms**
8. **IMPLEMENT EXACTLY what is required** - No more, no less

These rules are **MANDATORY** and must be followed without exception. Any deviation risks breaking the existing functionality of the system, which is unacceptable.

## 11. FINAL VERIFICATION CHECKLIST

Before considering implementation complete, verify that:

- [ ] Analysis script is created and functioning
- [ ] Visualizations are generated in the correct location
- [ ] Dashboard template is created properly
- [ ] Route is added to the Flask application
- [ ] Component is registered in configuration
- [ ] No existing functionality is broken
- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation is complete
- [ ] No unauthorized files were modified

Follow these rules and guidelines precisely to ensure successful integration of the new component while preserving existing functionality. 