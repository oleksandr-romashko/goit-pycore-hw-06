@echo off

:: Step 1: Create a virtual environment if not already created
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
) else (
    echo Virtual environment already exists.
)

:: Step 2: Activate the virtual environment
echo Activating the virtual environment...
call .\.venv\Scripts\activate.bat

:: Step 3: Install required packages from requirements.txt (if it exists)
if exist "requirements.txt" (
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
) else (
    echo No requirements.txt found.
)

:: Step 4: Set the PYTHONPATH
echo Setting PYTHONPATH...
set PYTHONPATH=.\src;%PYTHONPATH%

:: Optional: Inform the user about the environment setup
echo Virtual environment set up and PYTHONPATH configured.
