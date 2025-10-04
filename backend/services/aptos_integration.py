"""
Real Aptos blockchain integration using aptos-sdk
"""
from aptos_sdk.client import RestClient, FaucetClient
from aptos_sdk.account import Account
from aptos_sdk.transactions import EntryFunction, TransactionArgument, TransactionPayload
from aptos_sdk.type_tag import TypeTag, StructTag
from aptos_sdk.bcs import Serializer
import os
from typing import Dict, Any, Optional
from datetime import datetime


class AptosBlockchainService:
    """Service for interacting with Aptos blockchain"""
    
    def __init__(self):
        # Use testnet by default
        self.node_url = os.getenv("APTOS_NODE_URL", "https://fullnode.testnet.aptoslabs.com/v1")
        self.faucet_url = os.getenv("APTOS_FAUCET_URL", "https://faucet.testnet.aptoslabs.com")
        
        self.client = RestClient(self.node_url)
        self.faucet_client = FaucetClient(self.faucet_url, self.client)
        
        # Load or create account
        self.account = self._load_or_create_account()
        self.module_address = self.account.address()
        
    def _load_or_create_account(self) -> Account:
        """Load existing account or create new one"""
        private_key = os.getenv("APTOS_PRIVATE_KEY")
        
        if private_key:
            # Load from environment
            return Account.load_key(private_key)
        else:
            # Create new account
            account = Account.generate()
            print(f"Created new Aptos account: {account.address()}")
            print(f"Private key: {account.private_key}")
            print("Save this private key in your .env file!")
            
            # Fund account from faucet (testnet only)
            try:
                self.faucet_client.fund_account(account.address(), 100_000_000)  # 1 APT
                print("Account funded from faucet")
            except Exception as e:
                print(f"Could not fund account: {e}")
            
            return account
    
    async def initialize_registry(self) -> Dict[str, Any]:
        """Initialize the carbon credit registry"""
        try:
            # Build transaction payload
            payload = EntryFunction.natural(
                f"{self.module_address}::carbon_credit",
                "initialize",
                [],
                []
            )
            
            # Submit transaction
            signed_txn = self.client.create_bcs_signed_transaction(
                self.account,
                TransactionPayload(payload)
            )
            
            tx_hash = self.client.submit_bcs_transaction(signed_txn)
            self.client.wait_for_transaction(tx_hash)
            
            return {
                "success": True,
                "transaction_hash": tx_hash,
                "registry_address": str(self.module_address),
                "message": "Registry initialized successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_project(
        self,
        project_id: str,
        location: str,
        latitude: float,
        longitude: float,
        area: float,
        total_credits: float,
        unit_price: float,
        vintage_year: int
    ) -> Dict[str, Any]:
        """Create a carbon credit project on blockchain"""
        try:
            # Convert floats to integers (multiply by 1000000 for precision)
            lat_int = int(latitude * 1000000)
            lng_int = int(longitude * 1000000)
            area_int = int(area * 100)
            credits_int = int(total_credits * 100)
            price_int = int(unit_price * 100)
            
            # Build transaction payload
            payload = EntryFunction.natural(
                f"{self.module_address}::carbon_credit",
                "create_project",
                [],
                [
                    TransactionArgument(self.module_address, Serializer.struct),
                    TransactionArgument(project_id, Serializer.str),
                    TransactionArgument(location, Serializer.str),
                    TransactionArgument(lat_int, Serializer.u64),
                    TransactionArgument(lng_int, Serializer.u64),
                    TransactionArgument(area_int, Serializer.u64),
                    TransactionArgument(credits_int, Serializer.u64),
                    TransactionArgument(price_int, Serializer.u64),
                    TransactionArgument(vintage_year, Serializer.u64),
                ]
            )
            
            # Submit transaction
            signed_txn = self.client.create_bcs_signed_transaction(
                self.account,
                TransactionPayload(payload)
            )
            
            tx_hash = self.client.submit_bcs_transaction(signed_txn)
            self.client.wait_for_transaction(tx_hash)
            
            # Get transaction details
            tx_info = self.client.account_transaction(self.account.address(), tx_hash)
            
            return {
                "success": True,
                "transaction_hash": tx_hash,
                "project_id": project_id,
                "contract_address": str(self.module_address),
                "block_number": tx_info.get("version", 0),
                "gas_used": tx_info.get("gas_used", 0),
                "network_fee": int(tx_info.get("gas_used", 0)) * 100 / 1_000_000,  # Convert to APT
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def mint_geonft(
        self,
        nft_id: str,
        project_id: str,
        metadata_uri: str
    ) -> Dict[str, Any]:
        """Mint a GeoNFT for a project"""
        try:
            payload = EntryFunction.natural(
                f"{self.module_address}::carbon_credit",
                "mint_geonft",
                [],
                [
                    TransactionArgument(self.module_address, Serializer.struct),
                    TransactionArgument(nft_id, Serializer.str),
                    TransactionArgument(project_id, Serializer.str),
                    TransactionArgument(metadata_uri, Serializer.str),
                ]
            )
            
            signed_txn = self.client.create_bcs_signed_transaction(
                self.account,
                TransactionPayload(payload)
            )
            
            tx_hash = self.client.submit_bcs_transaction(signed_txn)
            self.client.wait_for_transaction(tx_hash)
            
            tx_info = self.client.account_transaction(self.account.address(), tx_hash)
            
            return {
                "success": True,
                "transaction_hash": tx_hash,
                "nft_id": nft_id,
                "project_id": project_id,
                "block_number": tx_info.get("version", 0),
                "gas_used": tx_info.get("gas_used", 0),
                "network_fee": int(tx_info.get("gas_used", 0)) * 100 / 1_000_000,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def transfer_credits(
        self,
        project_id: str,
        to_address: str,
        amount: float
    ) -> Dict[str, Any]:
        """Transfer carbon credits"""
        try:
            amount_int = int(amount * 100)
            
            payload = EntryFunction.natural(
                f"{self.module_address}::carbon_credit",
                "transfer_credits",
                [],
                [
                    TransactionArgument(self.module_address, Serializer.struct),
                    TransactionArgument(project_id, Serializer.str),
                    TransactionArgument(to_address, Serializer.struct),
                    TransactionArgument(amount_int, Serializer.u64),
                ]
            )
            
            signed_txn = self.client.create_bcs_signed_transaction(
                self.account,
                TransactionPayload(payload)
            )
            
            tx_hash = self.client.submit_bcs_transaction(signed_txn)
            self.client.wait_for_transaction(tx_hash)
            
            return {
                "success": True,
                "transaction_hash": tx_hash,
                "project_id": project_id,
                "amount": amount,
                "to_address": to_address
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def retire_credits(
        self,
        project_id: str,
        amount: float
    ) -> Dict[str, Any]:
        """Retire carbon credits"""
        try:
            amount_int = int(amount * 100)
            
            payload = EntryFunction.natural(
                f"{self.module_address}::carbon_credit",
                "retire_credits",
                [],
                [
                    TransactionArgument(self.module_address, Serializer.struct),
                    TransactionArgument(project_id, Serializer.str),
                    TransactionArgument(amount_int, Serializer.u64),
                ]
            )
            
            signed_txn = self.client.create_bcs_signed_transaction(
                self.account,
                TransactionPayload(payload)
            )
            
            tx_hash = self.client.submit_bcs_transaction(signed_txn)
            self.client.wait_for_transaction(tx_hash)
            
            return {
                "success": True,
                "transaction_hash": tx_hash,
                "project_id": project_id,
                "amount_retired": amount
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project details from blockchain"""
        try:
            # Call view function
            result = self.client.view_function(
                f"{self.module_address}::carbon_credit::get_project",
                [],
                [self.module_address, project_id]
            )
            return result
        except Exception as e:
            print(f"Error getting project: {e}")
            return None
    
    def get_account_balance(self) -> float:
        """Get account APT balance"""
        try:
            balance = self.client.account_balance(self.account.address())
            return balance / 100_000_000  # Convert to APT
        except Exception as e:
            print(f"Error getting balance: {e}")
            return 0.0


# Global instance
aptos_service = None

def get_aptos_service() -> AptosBlockchainService:
    """Get or create Aptos service instance"""
    global aptos_service
    if aptos_service is None:
        aptos_service = AptosBlockchainService()
    return aptos_service
