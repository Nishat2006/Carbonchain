"""
Binance API Integration for Real-Time Carbon Credit Pricing
Uses Binance API to get cryptocurrency prices and apply to carbon credits
"""
import requests
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import os

class BinancePriceService:
    """Service to fetch real-time prices from Binance and calculate carbon credit values"""
    
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.base_carbon_price = 45.0  # Base price in USD
        self.price_cache = {}
        self.last_update = None
        
    async def get_crypto_price(self, symbol: str = "BTCUSDT") -> Optional[float]:
        """Get current cryptocurrency price from Binance"""
        try:
            url = f"{self.base_url}/ticker/price"
            params = {"symbol": symbol}
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            price = float(data.get("price", 0))
            
            self.price_cache[symbol] = price
            self.last_update = datetime.utcnow()
            
            return price
        except Exception as e:
            print(f"❌ Failed to fetch {symbol} price: {e}")
            return self.price_cache.get(symbol)
    
    async def get_multiple_prices(self, symbols: list = None) -> Dict[str, float]:
        """Get multiple cryptocurrency prices"""
        if symbols is None:
            symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "APTUSDT"]
        
        try:
            url = f"{self.base_url}/ticker/price"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            all_prices = response.json()
            
            result = {}
            for item in all_prices:
                if item["symbol"] in symbols:
                    result[item["symbol"]] = float(item["price"])
            
            self.price_cache.update(result)
            self.last_update = datetime.utcnow()
            
            return result
        except Exception as e:
            print(f"❌ Failed to fetch prices: {e}")
            return self.price_cache
    
    async def get_market_stats(self) -> Dict[str, Any]:
        """Get 24h market statistics"""
        try:
            url = f"{self.base_url}/ticker/24hr"
            params = {"symbol": "BTCUSDT"}
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "symbol": data.get("symbol"),
                "price": float(data.get("lastPrice", 0)),
                "price_change": float(data.get("priceChange", 0)),
                "price_change_percent": float(data.get("priceChangePercent", 0)),
                "high_24h": float(data.get("highPrice", 0)),
                "low_24h": float(data.get("lowPrice", 0)),
                "volume_24h": float(data.get("volume", 0)),
            }
        except Exception as e:
            print(f"❌ Failed to fetch market stats: {e}")
            return {}
    
    def calculate_carbon_price_with_crypto(self, crypto_price: float, crypto_change_percent: float) -> float:
        """
        Calculate carbon credit price based on REAL crypto market volatility
        Uses actual Binance price movements to create realistic market dynamics
        """
        # Apply crypto volatility to carbon price (20% correlation)
        # This creates realistic market-driven price movements
        carbon_adjustment = crypto_change_percent * 0.2
        
        # Calculate new carbon price based on real market data
        new_carbon_price = self.base_carbon_price * (1 + carbon_adjustment / 100)
        
        # Ensure price stays within reasonable bounds (±40% from base)
        min_price = self.base_carbon_price * 0.6  # 40% down
        max_price = self.base_carbon_price * 1.4  # 40% up
        new_carbon_price = max(min_price, min(max_price, new_carbon_price))
        
        return round(new_carbon_price, 2)
    
    async def get_carbon_market_data(self) -> Dict[str, Any]:
        """Get comprehensive carbon market data with REAL-TIME crypto influence from Binance"""
        # Get REAL crypto prices from Binance
        crypto_prices = await self.get_multiple_prices()
        btc_stats = await self.get_market_stats()
        
        # Extract REAL market data
        btc_price = btc_stats.get("price", crypto_prices.get("BTCUSDT", 45000.0))
        btc_change_percent = btc_stats.get("price_change_percent", 0)
        btc_high_24h = btc_stats.get("high_24h", btc_price * 1.02)
        btc_low_24h = btc_stats.get("low_24h", btc_price * 0.98)
        btc_volume = btc_stats.get("volume_24h", 0)
        
        # Calculate carbon price using REAL BTC volatility
        carbon_price = self.calculate_carbon_price_with_crypto(btc_price, btc_change_percent)
        
        # Carbon price change mirrors crypto (20% correlation)
        carbon_change_percent = btc_change_percent * 0.2
        carbon_change_24h = carbon_price * (carbon_change_percent / 100)
        
        # Calculate realistic high/low based on actual BTC volatility
        btc_volatility = ((btc_high_24h - btc_low_24h) / btc_price) * 100
        carbon_volatility = btc_volatility * 0.2  # 20% of crypto volatility
        
        carbon_high_24h = carbon_price * (1 + carbon_volatility / 200)
        carbon_low_24h = carbon_price * (1 - carbon_volatility / 200)
        
        # Determine market sentiment based on REAL data
        if btc_change_percent > 2:
            sentiment = "Strongly Bullish"
            demand = "Very High"
        elif btc_change_percent > 0.5:
            sentiment = "Bullish"
            demand = "High"
        elif btc_change_percent < -2:
            sentiment = "Strongly Bearish"
            demand = "Very Low"
        elif btc_change_percent < -0.5:
            sentiment = "Bearish"
            demand = "Low"
        else:
            sentiment = "Neutral"
            demand = "Medium"
        
        # Calculate volume correlation
        carbon_volume = 12450.0 * (1 + btc_change_percent / 100)
        
        return {
            "current_price": carbon_price,
            "price_change_24h": round(carbon_change_24h, 2),
            "price_change_percent": round(carbon_change_percent, 2),
            "high_24h": round(carbon_high_24h, 2),
            "low_24h": round(carbon_low_24h, 2),
            "volume_24h": round(carbon_volume, 2),
            "market_cap": round(carbon_price * 50000, 2),
            "market_sentiment": sentiment,
            "demand_level": demand,
            "volatility_24h": round(carbon_volatility, 2),
            "crypto_influence": {
                "btc_price": round(btc_price, 2),
                "btc_change": round(btc_change_percent, 2),
                "btc_high_24h": round(btc_high_24h, 2),
                "btc_low_24h": round(btc_low_24h, 2),
                "btc_volume": round(btc_volume, 2),
                "eth_price": round(crypto_prices.get("ETHUSDT", 0), 2),
                "bnb_price": round(crypto_prices.get("BNBUSDT", 0), 2),
                "apt_price": round(crypto_prices.get("APTUSDT", 0), 4),
            },
            "data_source": "Binance Real-Time API",
            "last_updated": datetime.utcnow().isoformat(),
        }
    
    async def get_price_history(self, symbol: str = "BTCUSDT", interval: str = "1h", limit: int = 24) -> list:
        """Get historical price data (klines)"""
        try:
            url = f"{self.base_url}/klines"
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            # Format data
            history = []
            for candle in data:
                history.append({
                    "timestamp": candle[0],
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": float(candle[5]),
                })
            
            return history
        except Exception as e:
            print(f"❌ Failed to fetch price history: {e}")
            return []
    
    async def calculate_portfolio_value(self, carbon_credits: float) -> Dict[str, Any]:
        """Calculate portfolio value with real-time pricing"""
        market_data = await self.get_carbon_market_data()
        current_price = market_data["current_price"]
        
        total_value = carbon_credits * current_price
        change_24h = (carbon_credits * current_price * market_data["price_change_percent"]) / 100
        
        return {
            "carbon_credits": carbon_credits,
            "current_price": current_price,
            "total_value": round(total_value, 2),
            "change_24h": round(change_24h, 2),
            "change_percent": market_data["price_change_percent"],
            "market_data": market_data,
        }


# Global instance
_price_service = None

def get_price_service() -> BinancePriceService:
    """Get or create price service instance"""
    global _price_service
    if _price_service is None:
        _price_service = BinancePriceService()
    return _price_service


# Background price updater
async def start_price_updater(interval: int = 60):
    """Background task to update prices periodically"""
    service = get_price_service()
    
    print("🔄 Starting price updater...")
    print(f"   Update interval: {interval}s")
    
    while True:
        try:
            await service.get_carbon_market_data()
            print(f"✅ Prices updated at {datetime.utcnow().isoformat()}")
        except Exception as e:
            print(f"❌ Price update failed: {e}")
        
        await asyncio.sleep(interval)


if __name__ == "__main__":
    # Test the service
    async def test():
        service = get_price_service()
        
        print("Testing Binance Price Service")
        print("=" * 50)
        
        # Test crypto prices
        print("\n1. Crypto Prices:")
        prices = await service.get_multiple_prices()
        for symbol, price in prices.items():
            print(f"   {symbol}: ${price:,.2f}")
        
        # Test market stats
        print("\n2. BTC Market Stats:")
        stats = await service.get_market_stats()
        print(f"   Price: ${stats.get('price', 0):,.2f}")
        print(f"   24h Change: {stats.get('price_change_percent', 0):.2f}%")
        
        # Test carbon market data
        print("\n3. Carbon Market Data:")
        carbon_data = await service.get_carbon_market_data()
        print(f"   Carbon Price: ${carbon_data['current_price']}")
        print(f"   24h Change: {carbon_data['price_change_percent']}%")
        print(f"   Sentiment: {carbon_data['market_sentiment']}")
        print(f"   Demand: {carbon_data['demand_level']}")
        
        # Test portfolio value
        print("\n4. Portfolio Value (2.3 credits):")
        portfolio = await service.calculate_portfolio_value(2.3)
        print(f"   Total Value: ${portfolio['total_value']}")
        print(f"   24h Change: ${portfolio['change_24h']} ({portfolio['change_percent']}%)")
    
    asyncio.run(test())
