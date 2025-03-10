
# Check if Python3 is installed
if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 is not installed. Please install Python 3.x first."
    exit 1
fi

echo "  Python3 detected!"

# Check if the virtual environment already exists
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
else
    echo "  Virtual environment already exists."
fi

# Activate the virtual environment (Detect OS)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "  Virtual environment activated."

# Upgrade pip
echo "  Upgrading pip..."
pip install --upgrade pip

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found! Creating one..."
    echo -e "PyQt6\npillow\nreportlab" > requirements.txt
fi

# Install dependencies
echo "  Installing dependencies..."
pip install -r requirements.txt

echo "  Setup complete! Run 'source venv/bin/activate' to activate the environment."
