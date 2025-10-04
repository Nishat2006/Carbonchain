@echo off
REM Aptos Smart Contract Deployment Script for Windows
REM This script deploys the carbon credit contract to Aptos blockchain

echo =========================================
echo   Carbon Credit Contract Deployment
echo =========================================
echo.

REM Check if Aptos CLI is installed
where aptos >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Aptos CLI not found!
    echo 📥 Install from: https://aptos.dev/cli-tools/aptos-cli-tool/install-aptos-cli
    echo.
    echo Quick install for Windows:
    echo   Download from: https://github.com/aptos-labs/aptos-core/releases
    echo   Or use: iwr "https://aptos.dev/scripts/install_cli.py" -useb ^| iex
    pause
    exit /b 1
)

echo ✅ Aptos CLI found
echo.

REM Check if initialized
if not exist ".aptos\config.yaml" (
    echo 🔧 Initializing Aptos account...
    aptos init --network testnet
    echo.
)

REM Compile the contract
echo 📦 Compiling Move contract...
aptos move compile --named-addresses carbon_registry=default
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Compilation failed!
    pause
    exit /b 1
)
echo ✅ Compilation successful
echo.

REM Run tests
echo 🧪 Running tests...
aptos move test
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Tests failed, but continuing...
)
echo.

REM Deploy to testnet
echo 🚀 Deploying to Aptos testnet...
aptos move publish --named-addresses carbon_registry=default --assume-yes

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =========================================
    echo ✅ DEPLOYMENT SUCCESSFUL!
    echo =========================================
    echo.
    echo 📝 Next steps:
    echo 1. Copy your account address from .aptos\config.yaml
    echo 2. Update backend\.env with:
    echo    APTOS_MODULE_ADDRESS=^<your_address^>
    echo 3. Fund your account from faucet:
    echo    aptos account fund-with-faucet --account default
    echo 4. Test the contract:
    echo    test_contract.bat
    echo.
) else (
    echo ❌ Deployment failed!
    pause
    exit /b 1
)

pause
