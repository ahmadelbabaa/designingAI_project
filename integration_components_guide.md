# HPC Prediction Analysis - Comprehensive Integration Guide

This document provides an in-depth guide for the integration components of the HPC Prediction Analysis project, including technical implementation details, API configurations, and dashboard integration specifications.

## 1. EV Charging Pattern Analysis

**Purpose:** Analyze charging behavior patterns from historical data to identify usage trends, peak times, and user behaviors.

**Core Files:**
- `ev_charging_patterns.csv` - Primary dataset containing charging session data
- `ev_charging_analysis.py` - New file to be implemented that will perform the analysis
- `output/charging_patterns/` - Directory where analysis visualizations will be stored
- `templates/charging_patterns.html` - Template file for displaying analysis in the dashboard

**Data Format Details:**
- `ev_charging_patterns.csv` structure:
  - Contains columns for session_id, station_id, start_time, end_time, energy_delivered, user_id
  - Timestamps are in ISO format (YYYY-MM-DD HH:MM:SS)
  - Energy values are in kWh

**Required Analysis:**
1. Time-based patterns (hourly, daily, weekly)
2. Station utilization rates
3. Energy delivery volumes
4. Session duration analysis
5. User behavior clustering

**Visualization Requirements:**
- Interactive time-series charts
- Heatmaps for utilization periods
- Station comparison charts
- User behavior segmentation visualizations

**Integration Points:**
- Add a new Flask route in `enhanced_dashboard.py`: `/charging-patterns`
- Create a dashboard card in `templates/dashboard.html` that links to the detailed analysis
- Ensure all visualizations follow the project's established D3.js and Plotly conventions

## 2. Station Conversion Analysis

**Purpose:** Evaluate the feasibility and ROI of converting gas stations to EV charging stations.

**Core Files:**
- `conversion_advisor.py` - Contains the existing logic for conversion analysis
- `gas_stations.csv` and `gas_stations.json` - Datasets with gas station information
- `output/conversion_advisor/` - Directory containing conversion visualization outputs
- `templates/conversion_advisor.html` - Dashboard template for conversion analysis
- `config/conversion_parameters.json` - Contains ROI calculation parameters

**Implementation Details:**
- The analysis uses a multi-factor ROI model defined in `conversion_advisor.py:calculate_roi()`
- Geospatial analysis is performed using GeoPandas (not TomTom API as previously planned)
- Projections use Monte Carlo simulation with 1000 iterations per station
- Time horizon for ROI calculations is configurable in `config/conversion_parameters.json`

**API Integration (Internal):**
- ROI calculations exposed via internal API endpoint: `/api/v1/conversion-roi`
- Station data accessible via: `/api/v1/stations`
- API authentication handled through Flask session cookies

**Visualization Components:**
- Interactive ROI calculator with adjustable parameters
- Map visualization showing station locations and potential conversion candidates
- Comparison charts for different conversion scenarios

## 3. Time Series Forecasting

**Purpose:** Predict future charging demand and usage patterns for planning capacity.

**Core Files:**
- `time_series_forecasting.py` - Contains forecasting models and visualization generation
- Various `GS-XXXX_forecast_data.csv` files in the `data/` directory - Individual station forecast data
- `forecast_summary.json` and `forecast_trends.json` - Aggregated forecast results
- `output/forecasts/` - Directory containing forecast visualization outputs
- `config/forecast_models.yaml` - Configuration for ARIMA, Prophet, and LSTM models

**Model Implementation:**
- Primary forecasting uses Prophet model (implementation in `time_series_forecasting.py:run_prophet_model()`)
- ARIMA models serve as verification/comparison (implementation in `time_series_forecasting.py:run_arima_model()`)
- Model selection logic in `time_series_forecasting.py:select_best_model()`
- Model evaluation metrics stored in `data/model_performance_metrics.json`

**Integration with Dashboard:**
- Real-time forecast updates implemented using AJAX requests to `/api/v1/forecasts`
- Interactive forecast adjustment with confidence intervals
- Forecast data cached in Redis (configuration in `config/cache_config.json`)
- Visualization components use Plotly.js with custom wrapper functions

## 4. HPC Integration Pipeline

**Purpose:** Process, combine, and prepare data from multiple sources for cohesive analysis.

**Core Files:**
- `HPC_integration_part1.py` - Initial data setup and Kaggle data downloading
- `HPC_integration_part2.py` - Data processing and transformation
- `HPC_integration_part3.py` - Final data integration and preparation
- `hpc_usage_master.csv` - The integrated dataset resulting from the pipeline
- `config/hpc_cost_params.yaml` - Configuration parameters for cost calculations
- `config/data_sources.json` - Configuration for data source locations and credentials

**Pipeline Implementation:**
- ETL pipeline implemented in three sequential scripts to handle:
  1. Data acquisition and validation (`part1`)
  2. Cleaning, normalization, and feature engineering (`part2`)
  3. Integration, aggregation, and final dataset creation (`part3`)
- Custom data validation rules in `data_validation_rules.py`
- Error handling and logging in `utils/pipeline_logger.py`

**Data Flow Specifications:**
- Raw data ingestion → Validation → Cleaning → Transformation → Feature Engineering → Integration
- Logging occurs at each stage with detailed reporting
- Data quality metrics calculated and stored in `data/quality_metrics.json`

**Configuration Management:**
- Data source configurations in `config/data_sources.json`
- Cost parameters in `config/hpc_cost_params.yaml`
- Pipeline execution parameters in `config/pipeline_config.yaml`

## 5. GPT-4o Integration

**Purpose:** Leverage GPT-4o for natural language interactions with the dashboard and advanced data insights.

**Core Files:**
- `gpt4o_integration.py` - Main integration script for GPT-4o API
- `templates/ai_insights.html` - Template for AI-generated insights
- `static/js/gpt4o_interface.js` - Frontend JavaScript for AI interaction
- `config/openai_config.json` - OpenAI API configuration (keys stored in environment variables)

**Integration Implementation:**
- OpenAI API integration using the official Python library
- API key managed through environment variables (`OPENAI_API_KEY`)
- System prompts stored in `config/system_prompts/` directory
- Conversation history managed in `utils/conversation_manager.py`

**Features Implemented:**
1. Natural language querying of dashboard data
2. AI-generated insights based on current analytics
3. Anomaly explanation and detection
4. Recommendation generation for optimization strategies
5. Q&A interface for business users

**API Endpoints:**
- `/api/v1/ai/query` - For direct data questions
- `/api/v1/ai/insights` - For automated insight generation
- `/api/v1/ai/recommendations` - For business recommendations

**Model Configuration:**
- Default model: `gpt-4o`
- Temperature: 0.3 for data analysis, 0.7 for recommendations
- Max tokens: 2048
- Rate limiting implemented in `utils/rate_limiter.py`
- Caching strategy for common queries in `utils/ai_response_cache.py`

## 6. Unified Dashboard Integration

**Purpose:** Combine all analysis components into a cohesive, interactive dashboard interface.

**Core Files:**
- `enhanced_dashboard.py` - Main Flask application
- `templates/dashboard.html` - Main dashboard template
- `templates/components/` - Directory with modular dashboard components
- `static/js/dashboard_controller.js` - Central JavaScript for dashboard functionality
- `static/css/dashboard_styles.css` - Dashboard styling
- `config/dashboard_config.json` - Dashboard layout and component configuration

**Dashboard Architecture:**
- Component-based architecture with independent visualization modules
- Shared data layer to minimize redundant API calls
- Responsive layout using CSS Grid and Flexbox
- State management handled through browser localStorage and sessionStorage

**Integration Implementation:**
1. **Component Registration System:**
   - Dashboard components register via `register_component()` in `enhanced_dashboard.py`
   - Component config in `config/dashboard_components.json`
   - Dynamic loading mechanism in `static/js/component_loader.js`

2. **Data Layer Integration:**
   - Centralized data store in `static/js/data_store.js`
   - API gateway in `api_gateway.py` providing unified access point
   - Data refreshing handled by background workers (`utils/background_processor.py`)

3. **Navigation and Layout:**
   - Side navigation dynamically generated from component registry
   - Layout persistence using localStorage
   - User preference storage in `user_preferences.json`

4. **Authentication and User Management:**
   - Role-based access control in `utils/auth_manager.py`
   - Component visibility filtered by user role
   - Session management in `session_handler.py`

**Integration Requirements:**
1. New components must implement:
   - A Flask route (`/component-name`)
   - A template file (`templates/component-name.html`)
   - Registration in `config/dashboard_components.json`
   - Any required API endpoints (`/api/v1/component-name/*`)

2. Visualization standards:
   - Use project visualization libraries (D3.js, Plotly)
   - Follow color scheme in `static/css/variables.css`
   - Implement responsive breakpoints for all visualizations

## 7. Cross-Component Data Sharing

**Purpose:** Enable seamless data sharing between analysis components.

**Implementation:**
- Central data repository in `data/shared/`
- Shared data access API in `utils/shared_data_manager.py`
- Cross-component event system in `static/js/event_bus.js`
- Configuration for cross-component dependencies in `config/component_dependencies.json`

**API Structure:**
- GET data: `shared_data_manager.get_data(dataset_name, filters)`
- SET data: `shared_data_manager.set_data(dataset_name, data, metadata)`
- SUBSCRIBE: `shared_data_manager.subscribe(dataset_name, callback)`

**Data Exchange Format:**
- All shared data uses standardized JSON schema defined in `schemas/`
- Schema validation performed by `utils/schema_validator.py`
- Data transformations for cross-component compatibility in `utils/data_transformer.py`

## 8. Development and Integration Process

When implementing a new component or extending an existing one:

1. **Study Existing Components:**
   - Review code organization in similar components
   - Note API usage patterns
   - Identify shared utilities and libraries

2. **Folder Structure:**
   - Script: `/` (root directory)
   - Template: `templates/`
   - Static assets: `static/component_name/`
   - Configuration: `config/component_name/`
   - Output: `output/component_name/`

3. **Implementation Sequence:**
   1. Create data processing logic with test cases
   2. Develop visualization components
   3. Build template file and CSS
   4. Add Flask routes to dashboard
   5. Register component in configuration
   6. Add API endpoints if needed
   7. Implement cross-component communication

4. **Testing Requirements:**
   - Unit tests in `tests/unit/component_name/`
   - Integration tests in `tests/integration/component_name/`
   - Performance benchmarks in `tests/performance/`

5. **Documentation:**
   - Code documentation with docstrings
   - API documentation in `docs/api/`
   - User documentation in `docs/user/`

This comprehensive integration approach ensures each component works independently but also functions as part of the larger system, with standardized data exchange, consistent visualization approaches, and unified user experience. 