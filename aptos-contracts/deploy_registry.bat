@echo off
REM Deploy Carbon Registry to Aptos Testnet (Windows)

echo =========================================
echo   Carbon Registry Deployment
echo =========================================
echo.

REM Check Aptos CLI
where aptos >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Aptos CLI not found!
    echo Install: iwr "https://aptos.dev/scripts/install_cli.py" -useb ^| iex
    pause
    exit /b 1
)

echo ✅ Aptos CLI found
echo.

REM Initialize if needed
if not exist ".aptos\config.yaml" (
    echo 🔧 Initializing Aptos account...
    aptos init --network testnet
    echo.
)

REM Fund account
echo 💰 Funding account from faucet...
aptos account fund-with-faucet --account default --amount 100000000
echo.

REM Compile
echo 📦 Compiling contract...
aptos move compile --named-addresses carbon_registry=default
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Compilation failed!
    pause
    exit /b 1
)
echo ✅ Compilation successful
echo.

REM Test
echo 🧪 Running tests...
aptos move test
echo.

REM Deploy
echo 🚀 Deploying to testnet...
aptos move publish --named-addresses carbon_registry=default --assume-yes

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =========================================
    echo ✅ DEPLOYMENT SUCCESSFUL!
    echo =========================================
    echo.
    
    REM Get account address
    for /f "tokens=2" %%a in ('aptos config show-profiles --profile default ^| findstr "account"') do set ACCOUNT=%%a
    
    echo 📋 Contract Details:
    echo    Module: carbon_registry::registry
    echo    Address: %ACCOUNT%
    echo    Network: Testnet
    echo.
    echo 📝 Next Steps:
    echo 1. Initialize registry:
    echo    aptos move run --function-id '%ACCOUNT%::registry::initialize'
    echo.
    echo 2. Update frontend config:
    echo    REACT_APP_CONTRACT_ADDRESS=%ACCOUNT%
    echo.
    echo 3. Update backend .env:
    echo    APTOS_MODULE_ADDRESS=%ACCOUNT%
    echo.
    echo 4. View on explorer:
    echo    https://explorer.aptoslabs.com/account/%ACCOUNT%?network=testnet
    echo.
) else (
    echo ❌ Deployment failed!
    pause
    exit /b 1
)

pause
