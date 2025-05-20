@echo off
setlocal enabledelayedexpansion

echo ===================================
echo Balce Web Application Launcher
echo ===================================

REM 设置Python路径
set PYTHON_CMD=d:\miniconda3\python.exe
set CONDA_CMD=d:\miniconda3\Scripts\conda.exe
set CONDA_ACTIVATE=d:\miniconda3\Scripts\activate.bat

REM 激活conda环境
echo Activating Conda environment...
call "%CONDA_ACTIVATE%" base

REM 验证Python安装
echo.
echo Checking Python installation...
"%PYTHON_CMD%" --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not properly installed or accessible
    goto error
)

REM 验证必需的包
echo.
echo Checking required packages...
"%PYTHON_CMD%" -c "import streamlit; import balce; print('Streamlit version:', streamlit.__version__)"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Required packages are missing
    echo Installing missing packages...
    "%PYTHON_CMD%" -m pip install -e .
    "%PYTHON_CMD%" -m pip install streamlit
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install required packages
        goto error
    )
)

REM 检查应用文件
echo.
echo Checking application files...
if not exist balceapp\index.py (
    echo ERROR: Could not find balceapp\index.py
    echo Current directory: %CD%
    goto error
)

REM 启动应用
echo.
echo Starting Balce Web Application...
echo.
echo If the application doesn't start automatically, please:
echo 1. Check if you see any error messages
echo 2. Try running 'python -m streamlit run balceapp\index.py' in a command prompt
echo 3. Make sure all required packages are installed
echo.
echo Starting...
echo.

"%PYTHON_CMD%" -m streamlit run balceapp\index.py
if %ERRORLEVEL% NEQ 0 (
    goto error
)

goto end

:error
echo.
echo ===================================
echo ERROR: Application failed to start
echo ===================================
echo.
echo Troubleshooting steps:
echo 1. Make sure you're running this file from the correct directory
echo 2. Check if Python and Conda are properly installed
echo 3. Try running 'pip install -e .' to reinstall the package
echo 4. Try running 'pip install streamlit' to reinstall Streamlit
echo.
echo Current directory: %CD%
echo Python command: %PYTHON_CMD%
echo.

:end
echo.
echo Press any key to exit...
pause > nul
endlocal