"""
Discord webhook integration for trading bot notifications.

Sends trading day summaries including wallet total and stock positions.
"""
import os
import json
import logging
from decimal import Decimal
from typing import Dict, Optional
import requests

logger = logging.getLogger(__name__)


def send_discord_webhook(webhook_url: str, content: str, username: Optional[str] = None) -> bool:
    """Send a message to Discord via webhook.
    
    Args:
        webhook_url: Discord webhook URL
        content: Message content to send
        username: Optional username for the webhook
    
    Returns:
        True if message sent successfully, False otherwise
    """
    if not webhook_url:
        logger.warning("Discord webhook URL not provided")
        return False
    
    payload = {
        "content": content
    }
    
    if username:
        payload["username"] = username
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 204:
            logger.info("Discord webhook message sent successfully")
            return True
        else:
            logger.error("Discord webhook failed with status %d: %s", 
                        response.status_code, response.text)
            return False
            
    except requests.exceptions.RequestException as e:
        logger.exception("Failed to send Discord webhook: %s", e)
        return False


def format_wallet_summary(wallet_total: Decimal, positions: Dict[str, Decimal]) -> str:
    """Format wallet and positions summary for Discord.
    
    Args:
        wallet_total: Total wallet value
        positions: Dictionary of symbol -> shares owned
    
    Returns:
        Formatted message string
    """
    message = f"**Trading Day Summary** 📊\n\n"
    message += f"Current Wallet Total: **${wallet_total:,.2f}**\n\n"
    
    if positions:
        message += "**Stocks Owned:**\n"
        for symbol, shares in positions.items():
            if shares > 0:
                shares_str = f"{shares:,.2f}" if shares != shares.to_integral_value() else f"{int(shares):,}"
                message += f"• {symbol}: {shares_str} shares\n"
    else:
        message += "**No stocks currently owned**\n"
    
    return message


def send_trading_day_summary(webhook_url: str, wallet_total: Decimal, 
                           positions: Dict[str, Decimal], day_type: str = "start") -> bool:
    """Send trading day summary to Discord.
    
    Args:
        webhook_url: Discord webhook URL
        wallet_total: Total wallet value
        positions: Dictionary of symbol -> shares owned
        day_type: Either "start" or "end" of trading day
    
    Returns:
        True if message sent successfully, False otherwise
    """
    if not webhook_url:
        return False
    
    # Create header based on day type
    if day_type.lower() == "start":
        header = "🌅 **TRADING DAY STARTED**\n"
    elif day_type.lower() == "end":
        header = "🌙 **TRADING DAY ENDED**\n"
    else:
        header = "📈 **TRADING UPDATE**\n"
    
    # Format the summary
    summary = format_wallet_summary(wallet_total, positions)
    
    # Combine header and summary
    message = header + summary
    
    return send_discord_webhook(
        webhook_url=webhook_url,
        content=message,
        username="Trading Bot"
    )


def send_trade_notification(webhook_url: str, action: str, symbol: str, 
                          quantity: Decimal, price: Optional[Decimal] = None) -> bool:
    """Send individual trade notification to Discord.
    
    Args:
        webhook_url: Discord webhook URL
        action: "BUY" or "SELL"
        symbol: Stock symbol
        quantity: Number of shares
        price: Price per share (optional)
    
    Returns:
        True if message sent successfully, False otherwise
    """
    if not webhook_url:
        return False
    
    # Format quantity
    qty_str = f"{quantity:,.2f}" if quantity != quantity.to_integral_value() else f"{int(quantity):,}"
    
    # Create message based on action
    if action.upper() == "BUY":
        emoji = "🟢"
        action_text = "BOUGHT"
    elif action.upper() == "SELL":
        emoji = "🔴"
        action_text = "SOLD"
    else:
        emoji = "ℹ️"
        action_text = action.upper()
    
    message = f"{emoji} **{action_text}** {qty_str} shares of **{symbol}**"
    
    if price is not None:
        message += f" at **${price:.2f}** per share"
        total_value = quantity * price
        message += f" (Total: **${total_value:,.2f}**)"
    
    return send_discord_webhook(
        webhook_url=webhook_url,
        content=message,
        username="Trading Bot"
    )


def get_discord_webhook_url() -> Optional[str]:
    """Get Discord webhook URL from environment variables.
    
    Returns:
        Discord webhook URL or None if not configured
    """
    return os.environ.get("DISCORD_WEBHOOK_URL")


def send_error_notification(webhook_url: str, title: str, error_message: str) -> bool:
    """Send an error notification to Discord.
    
    Args:
        webhook_url: Discord webhook URL
        title: Error title/summary
        error_message: Detailed error message
    
    Returns:
        True if notification sent successfully, False otherwise
    """
    # Truncate long error messages for Discord
    if len(error_message) > 1000:
        error_message = error_message[:997] + "..."
    
    message = f"🚨 **{title}**\n```\n{error_message}\n```"
    
    return send_discord_webhook(
        webhook_url=webhook_url,
        content=message,
        username="Trading Bot Alert"
    )