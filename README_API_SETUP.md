# API Credentials Setup

This document explains how to set up API credentials for the Gas Station Conversion Advisor.

## OpenAI API Configuration

The application uses Azure OpenAI services for generating personalized recommendations. Follow these steps to set up the environment:

1. **Install the required dependencies**:
   ```
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:

   You can create a `.env` file in the root directory using the provided script:
   ```
   ./create_env.sh
   ```

   Or manually create a `.env` file with the following content:
   ```
   OPENAI_API_TYPE=azure
   OPENAI_API_KEY=your_api_key
   OPENAI_API_BASE=your_api_base_url
   OPENAI_API_VERSION=your_api_version
   OPENAI_DEPLOYMENT_NAME=your_deployment_name
   ```

3. **Security Best Practices**:
   
   - Never commit your `.env` file to version control
   - The `.gitignore` file is configured to exclude `.env` files
   - For production deployments, use a secure secrets management solution rather than `.env` files
   - Periodically rotate API keys

## Running the Application

1. Start the static file server:
   ```
   cd output && python3 -m http.server 8000
   ```

2. In another terminal, run the Flask application:
   ```
   python3 enhanced_dashboard.py
   ```

3. Visit http://localhost:5000/ in your browser

## Troubleshooting

If you encounter errors related to API authentication:

1. Make sure your `.env` file is in the correct location (project root)
2. Verify that the API credentials are correct
3. Check if the Azure OpenAI service is available
4. Verify your API key has the necessary permissions 