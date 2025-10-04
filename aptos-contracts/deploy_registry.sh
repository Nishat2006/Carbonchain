#!/bin/bash

# Deploy Carbon Registry to Aptos Testnet
# This script compiles and deploys the enhanced registry contract

echo "========================================="
echo "  Carbon Registry Deployment"
echo "========================================="
echo ""

# Check Aptos CLI
if ! command -v aptos &> /dev/null; then
    echo "❌ Aptos CLI not found!"
    echo "Install: curl -fsSL \"https://aptos.dev/scripts/install_cli.py\" | python3"
    exit 1
fi

echo "✅ Aptos CLI found"
echo ""

# Initialize if needed
if [ ! -f ".aptos/config.yaml" ]; then
    echo "🔧 Initializing Aptos account..."
    aptos init --network testnet
    echo ""
fi

# Get account address
ACCOUNT=$(aptos config show-profiles --profile default 2>/dev/null | grep "account" | awk '{print $2}')
echo "📋 Account: $ACCOUNT"
echo ""

# Fund account
echo "💰 Funding account from faucet..."
aptos account fund-with-faucet --account default --amount 100000000
echo ""

# Compile
echo "📦 Compiling contract..."
aptos move compile --named-addresses carbon_registry=default
if [ $? -ne 0 ]; then
    echo "❌ Compilation failed!"
    exit 1
fi
echo "✅ Compilation successful"
echo ""

# Test
echo "🧪 Running tests..."
aptos move test
echo ""

# Deploy
echo "🚀 Deploying to testnet..."
aptos move publish --named-addresses carbon_registry=default --assume-yes

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "✅ DEPLOYMENT SUCCESSFUL!"
    echo "========================================="
    echo ""
    echo "📋 Contract Details:"
    echo "   Module: carbon_registry::registry"
    echo "   Address: $ACCOUNT"
    echo "   Network: Testnet"
    echo ""
    echo "📝 Next Steps:"
    echo "1. Initialize registry:"
    echo "   aptos move run --function-id '$ACCOUNT::registry::initialize'"
    echo ""
    echo "2. Update frontend config:"
    echo "   REACT_APP_CONTRACT_ADDRESS=$ACCOUNT"
    echo ""
    echo "3. Update backend .env:"
    echo "   APTOS_MODULE_ADDRESS=$ACCOUNT"
    echo ""
    echo "4. View on explorer:"
    echo "   https://explorer.aptoslabs.com/account/$ACCOUNT?network=testnet"
    echo ""
else
    echo "❌ Deployment failed!"
    exit 1
fi
