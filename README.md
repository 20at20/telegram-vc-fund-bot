# Telegram VC Fund Metrics Bot

An intelligent Telegram bot that helps VC fund team members query fund performance metrics and portfolio information using natural language.

## Features

- 📊 **Fund Metrics**: Query fund-level metrics (TVPI, DPI, IRR, MOIC, etc.)
- 🏢 **Portfolio Rankings**: Get top N companies by various criteria
- 📋 **Portfolio Lists**: Filter companies by sector, stage, or other attributes
- 🔍 **Company Details**: Get detailed information about specific portfolio companies
- 💬 **Conversation Memory**: Remembers last 5 messages for contextual follow-up questions
- 🔐 **Secure**: Whitelist-based authorization and rate limiting
- ⚡ **Fast**: 5-minute caching for quick responses

## Architecture

```
User Question → Telegram Bot → OpenAI (Query Analysis)
                    ↓
            Google Sheets (Data Source)
                    ↓
            Pandas (Data Processing)
                    ↓
            OpenAI (Response Generation)
                    ↓
            Telegram Response
```

## Prerequisites

- Python 3.11+
- Node.js 18+ (for MCP servers)
- Telegram Bot Token
- OpenAI API Key
- Google Cloud Service Account with Sheets API access

## Quick Start

### 1. Clone and Install

```bash
git clone <your-repo-url>
cd telegram-vc-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env and fill in your credentials
nano .env
```

Required variables:
- `TELEGRAM_BOT_TOKEN`: Get from @BotFather on Telegram
- `ALLOWED_TELEGRAM_IDS`: Comma-separated list of authorized user IDs
- `OPENAI_API_KEY`: Get from platform.openai.com
- `FUND_METRICS_SHEET_ID` & `PORTFOLIO_SHEET_ID`: Your Google Sheet IDs
- `FUND_METRICS_RANGE` & `PORTFOLIO_RANGE`: Cell ranges (e.g., "Sheet1!A1:Z100")

### 3. Setup Google Sheets Access

#### Option A: Using Setup Script
```bash
python scripts/setup_google_auth.py
```

#### Option B: Manual Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable Google Sheets API
4. Create a Service Account
5. Download the JSON credentials file
6. Save it to `config/credentials/google_service_account.json`
7. Share your Google Sheets with the service account email (found in the JSON file)

### 4. Get Your Telegram User ID

Send a message to [@userinfobot](https://t.me/userinfobot) on Telegram to get your user ID.

Add it to the `ALLOWED_TELEGRAM_IDS` in your `.env` file.

### 5. Run the Bot

```bash
python src/main.py
```

You should see:
```
✅ Bot started successfully and is now polling for messages
```

### 6. Test the Bot

Open Telegram and search for your bot, then send:
```
/start
```

Try a query:
```
What's our current TVPI?
```

## Deployment to Railway.app

### Prerequisites
- GitHub account
- Railway.app account (sign up at railway.app)

### Step-by-Step Deployment

#### 1. Push to GitHub

```bash
git add .
git commit -m "Initial commit: VC Fund Bot"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

#### 2. Create Railway Project

1. Go to [railway.app](https://railway.app) and login with GitHub
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `telegram-vc-bot` repository

#### 3. Configure Environment Variables

In Railway dashboard, go to "Variables" tab and add:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
ALLOWED_TELEGRAM_IDS=[123456789,987654321]
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview
FUND_METRICS_SHEET_ID=your_sheet_id
FUND_METRICS_RANGE=Fund Performance!A1:Z100
PORTFOLIO_SHEET_ID=your_sheet_id
PORTFOLIO_RANGE=Portfolio!A1:Z100
CACHE_TTL_SECONDS=300
RATE_LIMIT_PER_USER=20
LOG_LEVEL=INFO
```

For Google Service Account:
- Variable name: `GOOGLE_SERVICE_ACCOUNT_JSON`
- Value: Paste the entire content of your `google_service_account.json` file

#### 4. Deploy

Railway will automatically build and deploy. Watch the logs to ensure it starts successfully.

#### 5. Enable Auto-Deploy

In Railway project settings, ensure "Auto-Deploy" is enabled. Now every push to `main` will automatically redeploy the bot.

### Cost Estimation

**Railway:** ~$5-10/month
**OpenAI API:** ~$20-50/month (50-100 queries/day with GPT-4 Turbo)
**Total:** ~$25-60/month

## Usage Examples

### Fund Metrics
```
What's our current TVPI?
Show me the latest IRR
What's the DPI this quarter?
```

### Portfolio Rankings
```
Top 5 companies by investment amount
Show me the top 10 companies
Give me the best performing companies
```

### Portfolio Lists
```
List all fintech companies
Show companies in Series A stage
What companies are in healthcare?
```

### Company Details
```
Tell me about Acme Corp
Show details for TechStart
```

### Follow-up Questions (using conversation memory)
```
User: "Show me top 5 companies"
Bot: [lists 5 companies]
User: "Tell me more about #3"
Bot: [provides details about the 3rd company]
```

## Commands

- `/start` - Start the bot and see welcome message
- `/help` - Show help and usage examples
- `/clear` - Clear conversation history

## Project Structure

```
telegram-vc-bot/
├── config/
│   ├── settings.py          # Configuration management
│   └── credentials/         # Google credentials (gitignored)
├── src/
│   ├── bot/
│   │   ├── handlers.py      # Telegram command handlers
│   │   └── middleware.py    # Authorization & rate limiting
│   ├── services/
│   │   ├── mcp_client.py    # MCP integration
│   │   ├── memory_service.py   # Conversation memory
│   │   ├── sheets_service.py   # Google Sheets access
│   │   ├── openai_service.py   # OpenAI integration
│   │   ├── query_analyzer.py   # Intent parsing
│   │   ├── data_processor.py   # Data manipulation
│   │   └── response_generator.py # Response formatting
│   ├── models/
│   │   ├── query.py         # Query intent models
│   │   ├── fund_metrics.py  # Fund data models
│   │   └── portfolio.py     # Portfolio models
│   ├── utils/
│   │   ├── logger.py        # Logging setup
│   │   ├── cache.py         # Caching utilities
│   │   └── validators.py    # Input validation
│   └── main.py             # Application entry point
├── tests/                   # Test files
├── scripts/
│   ├── setup_google_auth.py # Setup helper
│   └── test_connections.py  # Connection tester
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

## Configuration

### Google Sheets Structure

#### Fund Metrics Sheet
Expected columns (customize in your sheets):
- Quarter/Period
- TVPI
- DPI
- IRR
- MOIC
- (any other metrics you track)

#### Portfolio Sheet
Expected columns:
- Company Name
- Investment Date
- Investment Amount
- Sector
- Stage
- Valuation
- Status
- (any other fields you track)

**Note:** The bot is flexible with column names. Just ensure you provide the correct column names when setting up.

## Troubleshooting

### Bot doesn't respond
- Check that environment variables are set correctly
- Verify bot token is valid: `curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe`
- Check Railway logs for errors

### Google Sheets access denied
- Ensure sheets are shared with service account email
- Verify service account has Sheets API enabled
- Check credentials file path is correct

### OpenAI errors
- Verify API key is valid
- Ensure you have GPT-4 access (or change to gpt-3.5-turbo in settings)
- Check API quota/billing

### Rate limiting issues
- Adjust `RATE_LIMIT_PER_USER` in environment variables
- Current default: 20 queries per hour

## Security Best Practices

✅ **Do:**
- Keep `.env` file private (never commit to git)
- Use read-only access for Google Sheets service account
- Regularly rotate API keys
- Monitor unauthorized access attempts in logs
- Keep authorized user list up to date

❌ **Don't:**
- Share your bot token publicly
- Commit credentials to version control
- Give write access to sheets service account
- Ignore rate limiting warnings

## Development

### Running Tests

```bash
pytest tests/
```

### Running Locally with Hot Reload

```bash
# Install watchdog
pip install watchdog

# Use nodemon or similar
nodemon --exec python src/main.py
```

### Clearing Cache

The bot caches Google Sheets data for 5 minutes. To clear cache during development, restart the bot.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check this README
2. Review the [implementation plan](/Users/andrewtymovskyi/.claude/plans/replicated-noodling-mist.md)
3. Check Railway logs for errors
4. Open an issue on GitHub

## Roadmap

Future enhancements:
- [ ] Data visualizations (charts sent as images)
- [ ] Scheduled reports (daily/weekly summaries)
- [ ] Multi-language support
- [ ] Voice message support
- [ ] Export data to PDF/Excel
- [ ] Custom alerts for metric thresholds

---

Built with ❤️ using Python, OpenAI, and Telegram Bot API
