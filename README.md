# Hotel Management Project

## 📌 Project Overview
This project is a **hotel management system** built with **Python** and **PyQt6** for the graphical user interface (GUI). It uses **SQLite3** as the database.

## ⚡ Setup Instructions
To set up and run this project, follow the steps below.

###   **1. Clone the Repository**
```sh
git clone https://github.com/svutheareak/hotel-management.git
cd hotel-management
```

###   **2. Run the Setup Script**
The setup script will:
- Create a **virtual environment** (`venv`).
- Install required dependencies.

Run the following command:
```sh
chmod +x setup.sh  # Give execution permission (Only needed once)
./setup.sh
```

If error reportlab can't install Run the following command:
```sh
pip install --force-reinstall reportlab
```

###   **3. Activate the Virtual Environment**
- **For macOS/Linux:**
  ```sh
  source venv/bin/activate
  ```

###   **4. Verify Installation**
After activating the virtual environment, check if PyQt6 is installed:
```sh
python -c "import PyQt6.QtWidgets; print('PyQt6 is installed and working!')"
```
If you see `PyQt6 is installed and working!`, everything is set up correctly. 🎉

###   **5. Run the Application**
Start the hotel management system by running:
```sh
python hotel.py
```

###   **6. Run the Application login**
Start the hotel management system login USER Admin:
```sh
username: admin ,
password: admin123
```

## 🛠 Troubleshooting
If you encounter issues:
- Make sure you're using **Python 3.8+** (`python --version`).
- Ensure the virtual environment is **activated** before running commands.
- If dependencies fail, try:
  ```sh
  pip install -r requirements.txt
  ```
- If VS Code doesn't detect imports, select the correct **Python Interpreter** (`Ctrl + Shift + P` → `Python: Select Interpreter`).

## 🚀 Happy Coding!

