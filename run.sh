#!/bin/bash
# Convenience script to run the application with proper AWS credentials
#
# Usage:
#   ./run.sh                    # Use default AWS profile
#   AWS_PROFILE=maker ./run.sh  # Use specific profile

# Set AWS profile (override with environment variable)
export AWS_PROFILE=${AWS_PROFILE:-maker}
export AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}

echo "🚀 Starting Tank Application"
echo "AWS Profile: $AWS_PROFILE"
echo "AWS Region: $AWS_DEFAULT_REGION"
echo ""

# Run the application
python main.py

