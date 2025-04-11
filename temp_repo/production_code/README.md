# Options AI Assistant

Options AI Assistant is a comprehensive platform for options traders that combines a powerful options price calculator with an intelligent Discord bot. The platform helps traders understand their options positions and make informed decisions through natural language interactions.

## Key Features

1. **Options Calculator**
   - Estimate future option values based on target stock prices
   - Calculate Greeks (Delta, Gamma, Theta, Vega)
   - Visualize potential profit/loss

2. **Technical Analysis**
   - Get support-based stop loss recommendations
   - Identify key support and resistance levels

3. **Unusual Activity Detection**
   - Identify potential market-moving options activity
   - Track unusual volume and open interest

4. **Discord Bot Integration**
   - Interact with the options calculator through natural language
   - Get real-time option price estimates and stop loss recommendations
   - Configure bot access permissions by server and channel

## System Architecture

The platform consists of two main components:

1. **Streamlit Web Interface**
   - Administrative dashboard for bot configuration
   - Interactive options calculator
   - Visualization of technical analysis

2. **Discord Bot**
   - Natural language processing for options queries
   - Real-time market data integration
   - Permission-based access control

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Required packages (see `pyproject.toml`)
- Discord Bot Token

### Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env` file:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   ```

### Running the Application

1. Start the Streamlit web interface:
   ```
   streamlit run app.py --server.port 5000
   ```

2. Start the Discord bot:
   ```
   python run_bot.py
   ```

## Discord Bot Usage

The Discord bot responds to natural language queries about options. It can:

- Estimate option prices based on target stock prices
- Recommend stop loss levels based on technical analysis
- Identify unusual options activity

### Example Queries

- "What's the price of AAPL $200 calls expiring next month?"
- "Stop loss for TSLA $250 puts expiring April 15th?"
- "Show me unusual activity for AMD options"

## File Structure

- `app.py` - Main Streamlit application
- `run_bot.py` - Discord bot launcher
- `discord_bot.py` - Discord bot implementation
- `option_calculator.py` - Options pricing algorithms
- `technical_analysis.py` - Technical analysis functions
- `unusual_activity.py` - Unusual options activity detection
- `utils.py` - Utility functions
- `pages/` - Streamlit pages for the web interface
- `utils/` - Helper modules

## Configuration

### Discord Bot Configuration

Bot permissions can be configured through the Streamlit web interface under "Discord Bot Configuration". This allows setting which channels the bot can respond in.

### Environment Variables

- `DISCORD_TOKEN` - Discord bot authentication token

## License

This project is proprietary and confidential.

## Acknowledgements

- [yfinance](https://github.com/ranaroussi/yfinance) for market data
- [Discord.py](https://github.com/Rapptz/discord.py) for Discord integration
- [Streamlit](https://streamlit.io/) for the web interface