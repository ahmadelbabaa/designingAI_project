#!/bin/bash

# Script to create .env file with OpenAI credentials
echo "Creating .env file with OpenAI credentials..."

cat > .env << EOL
# OpenAI API Configuration
OPENAI_API_TYPE=azure
OPENAI_API_KEY=24046116ca6b413e8c8ba19e25c7f44d
OPENAI_API_BASE=https://mx250220204441as.openai.azure.com/
OPENAI_API_VERSION=2025-01-01-preview
OPENAI_DEPLOYMENT_NAME=gpt-4o-mlops-hpc
EOL

echo "Done! Created .env file with OpenAI credentials."
echo "Make sure to install python-dotenv by running: pip install python-dotenv" 