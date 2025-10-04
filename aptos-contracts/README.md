# Carbon Credit Registry - Aptos Smart Contracts

## Overview
Move smart contracts for managing carbon credits, GeoNFTs, and tokenization on Aptos blockchain.

## Features
- ✅ Carbon Credit Project Management
- ✅ GeoNFT (Location-bound NFT) Minting
- ✅ Credit Transfer & Retirement
- ✅ Verification Status Tracking
- ✅ Event Emission for Tracking

## Setup

### Install Aptos CLI
```bash
# Windows (PowerShell)
iwr "https://aptos.dev/scripts/install_cli.py" -useb | iex

# Or download from: https://github.com/aptos-labs/aptos-core/releases
```

### Initialize Aptos Account
```bash
aptos init
```

### Compile Contract
```bash
cd aptos-contracts
aptos move compile
```

### Deploy to Testnet
```bash
aptos move publish --named-addresses carbon_registry=default
```

## Contract Functions

### Initialize Registry
```bash
aptos move run --function-id 'default::carbon_credit::initialize'
```

### Create Project
```bash
aptos move run \
  --function-id 'default::carbon_credit::create_project' \
  --args address:0x... string:"MANGROVE-001" string:"New Delhi" u64:28613900 u64:77209000 u64:120 u64:230 u64:4500 u64:2024
```

### Mint GeoNFT
```bash
aptos move run \
  --function-id 'default::carbon_credit::mint_geonft' \
  --args address:0x... string:"GEO-001" string:"MANGROVE-001" string:"ipfs://..."
```

## Integration with Backend

The Python backend uses `aptos-sdk` to interact with these contracts.
See `backend/services/aptos_integration.py` for implementation.

## Testing

```bash
aptos move test
```
