#!/bin/bash

# Zep Temporal Knowledge Graph Evaluation Setup Script
# This script automates the setup process for running the Zep evaluation

set -e  # Exit on any error

echo "🚀 Zep Temporal Knowledge Graph Evaluation Setup"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    print_error "Please run this script from the OpenDeepSearch project root directory"
    exit 1
fi

# Step 1: Check Python version
print_status "Checking Python version..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    print_success "Python $python_version is compatible (requires $required_version+)"
else
    print_error "Python $python_version is too old. Please upgrade to Python $required_version or higher"
    exit 1
fi

# Step 2: Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Step 3: Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Step 4: Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Step 5: Install dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Step 6: Install Zep Cloud
print_status "Installing Zep Cloud..."
pip install zep-cloud
print_success "Zep Cloud installed"

# Step 7: Check for .env file
if [ ! -f ".env" ]; then
    print_warning "No .env file found. Creating template..."
    cat > .env << EOF
# Zep Cloud Configuration
ZEP_API_KEY=your_zep_api_key_here
ZEP_BASE_URL=https://api.getzep.com

# LiteLLM Configuration (for evaluation)
LITELLM_MODEL=gemini/gemini-1.5-flash
EOF
    print_warning "Please edit .env file and add your Zep API key"
    print_warning "Get your API key from: https://www.getzep.com/"
else
    print_success ".env file exists"
fi

# Step 8: Check if Zep API key is configured
if [ -f ".env" ]; then
    if grep -q "your_zep_api_key_here" .env; then
        print_warning "Zep API key not configured in .env file"
        print_warning "Please edit .env and replace 'your_zep_api_key_here' with your actual API key"
    else
        print_success "Zep API key appears to be configured"
    fi
fi

# Step 9: Check if SEC data exists
if [ ! -f "temporal_evaluation/datasets/sec_filings_enhanced.json" ]; then
    print_warning "SEC filing dataset not found"
    print_warning "You may need to generate the dataset first"
    print_status "Checking if dataset generation script exists..."
    
    if [ -f "temporal_evaluation/create_all_datasets.py" ]; then
        print_status "Found dataset generation script. Running it..."
        cd temporal_evaluation
        python create_all_datasets.py
        cd ..
        print_success "Dataset generation completed"
    else
        print_error "Dataset generation script not found"
        print_error "Please ensure the SEC filing dataset exists at: temporal_evaluation/datasets/sec_filings_enhanced.json"
    fi
else
    print_success "SEC filing dataset found"
fi

# Step 10: Test basic setup
print_status "Testing basic setup..."
cd temporal_evaluation/zep

# Test if we can import the required modules
python3 -c "
import sys
sys.path.insert(0, 'tools')
try:
    from zep_temporal_kg_tool import ZepTemporalKGTool
    print('✅ Zep tool import successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

cd ../..

print_success "Basic setup test completed"

# Step 11: Final instructions
echo ""
echo "🎉 Setup completed successfully!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your Zep API key"
echo "2. Run: cd temporal_evaluation/zep"
echo "3. Run: python load_sec_data_to_zep.py"
echo "4. Run: python test_basic_zep.py"
echo "5. Run: python run_zep_evaluation.py"
echo ""
echo "For detailed instructions, see: ZEP_SETUP_GUIDE.md"
echo ""
echo "To activate the virtual environment in the future:"
echo "  source venv/bin/activate"
echo ""

# Check if user wants to proceed with data loading
read -p "Would you like to proceed with loading SEC data into Zep? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Proceeding with SEC data loading..."
    cd temporal_evaluation/zep
    python load_sec_data_to_zep.py
    cd ../..
    print_success "SEC data loading completed"
    
    read -p "Would you like to run the basic Zep test? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Running basic Zep test..."
        cd temporal_evaluation/zep
        python test_basic_zep.py
        cd ../..
        print_success "Basic Zep test completed"
    fi
fi

print_success "Setup script completed!"
print_status "You can now run the full evaluation when ready" 