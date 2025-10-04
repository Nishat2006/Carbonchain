#!/bin/bash

# Aptos Smart Contract Deployment Script
# This script deploys the carbon credit contract to Aptos blockchain

echo "========================================="
echo "  Carbon Credit Contract Deployment"
echo "========================================="
echo ""

# Check if Aptos CLI is installed
if ! command -v aptos &> /dev/null; then
    echo "❌ Aptos CLI not found!"
    echo "📥 Install from: https://aptos.dev/cli-tools/aptos-cli-tool/install-aptos-cli"
    echo ""
    echo "Quick install:"
    echo "  curl -fsSL \"https://aptos.dev/scripts/install_cli.py\" | python3"
    exit 1
fi

echo "✅ Aptos CLI found"
echo ""

# Check if initialized
if [ ! -f ".aptos/config.yaml" ]; then
    echo "🔧 Initializing Aptos account..."
    aptos init --network testnet
    echo ""
fi

# Compile the contract
echo "📦 Compiling Move contract..."
aptos move compile --named-addresses carbon_registry=default
if [ $? -ne 0 ]; then
    echo "❌ Compilation failed!"
    exit 1
fi
echo "✅ Compilation successful"
echo ""

# Run tests
echo "🧪 Running tests..."
aptos move test
if [ $? -ne 0 ]; then
    echo "⚠️  Tests failed, but continuing..."
fi
echo ""

# Deploy to testnet
echo "🚀 Deploying to Aptos testnet..."
aptos move publish --named-addresses carbon_registry=default --assume-yes

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "✅ DEPLOYMENT SUCCESSFUL!"
    echo "========================================="
    echo ""
    echo "📝 Next steps:"
    echo "1. Copy your account address from .aptos/config.yaml"
    echo "2. Update backend/.env with:"
    echo "   APTOS_MODULE_ADDRESS=<your_address>"
    echo "3. Fund your account from faucet:"
    echo "   aptos account fund-with-faucet --account default"
    echo "4. Test the contract:"
    echo "   ./test_contract.sh"
    echo ""
else
    echo "❌ Deployment failed!"
    exit 1
fi
