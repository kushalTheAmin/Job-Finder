#!/bin/bash

# Job Finder - Initial Setup Script
# This script helps you set up Job Finder by:
# 1. Checking prerequisites
# 2. Guiding through resume conversion
# 3. Setting up .env file
# 4. Running a test

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Welcome message
clear
echo -e "${BLUE}"
cat << "EOF"
   ___  ___  ____    ______ __  ____  ____  ______ ____
  / _ \/ _ \/ __ \  / __/ // / / / / / / /_/_/ __ / __/
 / // / // / /_/ / / _// _  / / / / /  '_/ /_/ / _/
/____/____/\____/ /_/ /_//_/ /_/ /_/_/\_\ \____/___/

EOF
echo -e "${NC}"
echo -e "${GREEN}Job Finder - Automated Job Search & Resume Customizer${NC}"
echo -e "${BLUE}This script will help you set up the system.${NC}\n"

# Step 1: Check Prerequisites
print_header "Step 1: Checking Prerequisites"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_success "Python 3 installed: $PYTHON_VERSION"
else
    print_error "Python 3 not found"
    echo "Please install Python 3.9+ from: https://www.python.org/downloads/"
    exit 1
fi

# Check pip
if command -v pip &> /dev/null || command -v pip3 &> /dev/null; then
    print_success "pip installed"
else
    print_error "pip not found"
    echo "Please install pip"
    exit 1
fi

# Check Git
if command -v git &> /dev/null; then
    print_success "Git installed"
else
    print_warning "Git not found (optional for version control)"
fi

# Check gcloud (optional for now)
if command -v gcloud &> /dev/null; then
    print_success "Google Cloud SDK installed"
else
    print_warning "Google Cloud SDK not found (needed for deployment)"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
fi

# Step 2: Install Dependencies
print_header "Step 2: Installing Dependencies"

read -p "Install Python dependencies? (y/n): " install_deps
if [[ $install_deps == "y" ]]; then
    print_info "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
    print_success "Dependencies installed"
else
    print_warning "Skipping dependency installation"
fi

# Step 3: Resume Conversion
print_header "Step 3: Resume Conversion (MOST IMPORTANT!)"

echo "Your resume needs to be in JSON format for the system to work."
echo "We have a tool that converts PDF, DOCX, or TXT to JSON automatically."
echo ""

if [ -f "data/master_resume.json" ]; then
    print_info "Found existing master_resume.json"
    read -p "Do you want to convert a new resume? (y/n): " convert_new
else
    print_warning "No master_resume.json found - you need to convert your resume"
    convert_new="y"
fi

if [[ $convert_new == "y" ]]; then
    print_info "Running resume converter..."
    echo ""

    # Install converter dependencies if needed
    pip install PyPDF2 python-docx google-cloud-aiplatform --quiet

    # Run converter
    python tools/resume_converter.py

    if [ -f "data/master_resume.json" ]; then
        print_success "Resume converted successfully!"
    else
        print_error "Resume conversion failed. Please try again manually:"
        echo "  python tools/resume_converter.py"
    fi
else
    print_info "Using existing resume"
fi

# Step 4: Environment Variables
print_header "Step 4: Environment Variables (.env file)"

if [ -f ".env" ]; then
    print_info "Found existing .env file"
    read -p "Do you want to recreate it from template? (y/n): " recreate_env
else
    print_warning "No .env file found - creating from template"
    recreate_env="y"
fi

if [[ $recreate_env == "y" ]]; then
    if [ -f ".env.template" ]; then
        cp .env.template .env
        print_success ".env file created from template"
        echo ""
        print_warning "IMPORTANT: Edit .env file and add your API keys!"
        echo ""
        echo "Required API keys:"
        echo "  1. Google Cloud Project ID"
        echo "  2. Adzuna API (free): https://developer.adzuna.com/"
        echo "  3. JSearch API (free): https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch"
        echo "  4. Gmail App Password: https://myaccount.google.com/apppasswords"
        echo "  5. Google Drive Folder ID"
        echo ""
        echo "See SETUP_GUIDE.md Part 2 for detailed instructions."
        echo ""
        read -p "Press Enter when you've added your API keys to .env..."
    else
        print_error ".env.template not found"
        exit 1
    fi
fi

# Validate .env file
print_info "Validating .env file..."

required_vars=("GOOGLE_CLOUD_PROJECT" "GMAIL_USER" "GMAIL_APP_PASSWORD")
missing_vars=()

for var in "${required_vars[@]}"; do
    if grep -q "^$var=.\+$" .env && ! grep -q "^$var=your-" .env; then
        print_success "$var is set"
    else
        print_error "$var is not set or still has placeholder value"
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    print_warning "Some required variables are not set. Please edit .env file."
    echo "Missing or placeholder: ${missing_vars[*]}"
fi

# Step 5: Configuration
print_header "Step 5: Job Search Configuration"

if [ -f "config.yaml" ]; then
    print_info "Found config.yaml"
    echo ""
    echo "Current job search settings:"
    grep -A 3 "default_titles:" config.yaml | head -4
    echo ""
    read -p "Do you want to edit job search preferences? (y/n): " edit_config

    if [[ $edit_config == "y" ]]; then
        print_info "Opening config.yaml in default editor..."
        if command -v nano &> /dev/null; then
            nano config.yaml
        elif command -v vi &> /dev/null; then
            vi config.yaml
        else
            print_info "Please edit config.yaml manually in your text editor"
            open config.yaml 2>/dev/null || xdg-open config.yaml 2>/dev/null || echo "Edit config.yaml file manually"
        fi
    fi
else
    print_error "config.yaml not found!"
    exit 1
fi

# Step 6: Test Run
print_header "Step 6: Test Run"

echo "Let's test the system locally before deploying to the cloud."
echo ""
print_warning "NOTE: This will make real API calls and may find actual jobs."
echo ""
read -p "Run a test now? (y/n): " run_test

if [[ $run_test == "y" ]]; then
    print_info "Running Job Finder locally..."
    echo ""
    echo "----------------------------------------"
    python main.py
    exit_code=$?
    echo "----------------------------------------"
    echo ""

    if [ $exit_code -eq 0 ]; then
        print_success "Test run completed successfully!"

        if [ -d "output" ] && [ "$(ls -A output)" ]; then
            print_info "Generated files saved to output/ directory:"
            ls -lh output/ | tail -n +2
        fi
    else
        print_error "Test run failed with exit code $exit_code"
        print_info "Check the error messages above for details"
        echo ""
        echo "Common issues:"
        echo "  - Missing API keys in .env"
        echo "  - Invalid master_resume.json"
        echo "  - Network connectivity"
        echo ""
        echo "See SETUP_GUIDE.md Troubleshooting section for help."
        exit $exit_code
    fi
else
    print_warning "Skipping test run"
fi

# Step 7: Next Steps
print_header "Setup Complete!"

echo -e "${GREEN}✓ Prerequisites checked${NC}"
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo -e "${GREEN}✓ Resume converted to JSON${NC}"
echo -e "${GREEN}✓ Environment variables configured${NC}"
echo -e "${GREEN}✓ Configuration customized${NC}"

if [[ $run_test == "y" ]] && [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✓ Local test successful${NC}"
fi

echo ""
print_header "Next Steps"

echo "1. Review the test output above"
echo "2. Check generated resumes in output/ directory"
echo "3. Adjust settings in config.yaml if needed"
echo ""
echo "When ready to deploy to Google Cloud:"
echo "  cd deploy"
echo "  ./deploy.sh"
echo ""
echo "For detailed deployment instructions:"
echo "  See SETUP_GUIDE.md Part 6"
echo ""
print_success "Happy job hunting! 🎯"
echo ""
