# Lughati AI — Arabic Grammar & Rewriting Assistant

A lightweight web application for Arabic grammar correction, text rewriting, and translation. Built with FastAPI (backend) and vanilla JavaScript (frontend).

## Features

- **Grammar Fix**: Correct grammar, spelling, and sentence structure in Modern Standard Arabic
- **Professional Arabic**: Rewrite text in formal, business-appropriate Arabic
- **Emirati Dialect**: Convert text to natural Emirati Arabic
- **Academic Tone**: Rewrite in formal academic style
- **Marketing Tone**: Create engaging, persuasive marketing copy
- **Translation**: Translate between English and Arabic (both directions)
- **Hybrid Monetization**: Free tier with server key OR bring your own API key for unlimited use
- **Strong Security**: Server keys never exposed; BYO keys stored locally in browser
- **Abuse Protection**: Rate limiting, daily caps, and text length limits

## Project Structure

```
project_root/
├── back_end/
│   ├── app.py            # FastAPI application and routes
│   ├── model.py          # AI/prompt logic per mode
│   └── config.py         # Configuration and environment variables
│
├── front_end/
│   ├── index.html        # Main UI
│   ├── styles.css        # Styling
│   └── script.js         # Frontend logic and API calls
│
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone or navigate to the project directory**

2. **Create a virtual environment (recommended)**

   ```bash
   python -m venv venv
   ```

   **Activate the virtual environment:**

   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables (required for free tier)**

   **Important**: To enable the free tier (5 requests/day per IP), you must set `OPENAI_API_KEY`. Users can also provide their own key in the frontend for unlimited use.

   To set the server-side key:

   - On Windows (PowerShell):
     ```powershell
     $env:OPENAI_API_KEY="your_api_key_here"
     ```

   - On Windows (CMD):
     ```cmd
     set OPENAI_API_KEY=your_api_key_here
     ```

   - On macOS/Linux:
     ```bash
     export OPENAI_API_KEY=your_api_key_here
     ```

   **Security Note**: The server key is NEVER exposed to the frontend, never embedded in HTML/JS, and never logged. It only exists server-side.

   Optional environment variables:
   - `OPENAI_MODEL` - Model to use (default: `gpt-4o-mini`)
   - `API_TIMEOUT` - Request timeout in seconds (default: `60`)

## Running the Application

### Start the Server

From the project root directory, run:

```bash
uvicorn back_end.app:app --reload
```

The server will start at `http://127.0.0.1:8000` (or `http://localhost:8000`).

### Access the Application

1. **Open your web browser** and navigate to:
   ```
   http://127.0.0.1:8000
   ```
   or
   ```
   http://localhost:8000
   ```

2. The frontend will be served automatically by FastAPI.

### Available Endpoints

- `http://127.0.0.1:8000/` - Main application (frontend)
- `http://127.0.0.1:8000/health` - Health check endpoint
- `http://127.0.0.1:8000/api/generate` - POST endpoint for text processing
- `http://127.0.0.1:8000/api/modes` - GET endpoint to list available modes
- `http://127.0.0.1:8000/docs` - Interactive API documentation (Swagger UI)

### Test the Application

1. Open `http://127.0.0.1:8000` in your browser
2. **Choose your usage mode**:
   - **Free Tier**: Use the app without providing a key (5 requests/day, uses server key)
   - **BYO Key**: Enter your OpenAI API key for unlimited use (your billing)
3. Enter some Arabic or English text in the input area (max 2500 characters)
4. Select a mode from the dropdown
5. Click "Fix / Rewrite"
6. View the result in the output area
7. Use the "Copy" button to copy the result

### Hybrid Monetization Model

The application uses a hybrid monetization approach:

#### Free Tier (Server-Paid Usage)

- **5 requests per day per IP address** (uses server's `OPENAI_API_KEY`)
- **10 requests per 10 minutes** rate limit (applies to everyone)
- **2500 character maximum** per request (applies to everyone)
- If daily limit is reached, users see: "Daily free limit reached. Add your own OpenAI key for unlimited usage (your billing) or subscribe to unlock more."

#### Bring Your Own API Key (BYO Key)

- **Unlimited daily requests** when you provide your own OpenAI API key (daily cap bypassed)
- **Rate limit still applies**: 10 requests per 10 minutes (prevents abuse)
- **Your billing**: All API costs go to your OpenAI account
- **Privacy**: Your key is stored locally in your browser (localStorage: `lughati_openai_key`)
- **Security**: Your key is sent only in the `X-OPENAI-KEY` header and never logged on the server
- **No server cost**: When you use your own key, the server incurs no OpenAI API costs

#### How It Works

1. **Free users** (no BYO key):
   - Server checks if `OPENAI_API_KEY` is set
   - If not set, returns error: "Server is not configured. Please add your own OpenAI key to continue."
   - If set, tracks daily usage per IP (5 requests/day)
   - Uses server key for API calls

2. **BYO key users**:
   - User enters key in frontend → stored in browser localStorage
   - Key sent as `X-OPENAI-KEY` header with each request
   - Server detects BYO key and bypasses daily cap (5/day limit)
   - Rate limit still applies (10 per 10 minutes) to prevent abuse
   - Server uses user's key for that request
   - No server cost for API calls

### Security

**Server Key Protection:**
- Server `OPENAI_API_KEY` is read ONLY from environment variable
- Never returned to client, never embedded in HTML/JS, never logged
- Only used server-side for free tier requests

**BYO Key Protection:**
- Stored locally in browser localStorage (never on server)
- Sent only in request header `X-OPENAI-KEY`
- Backend never logs the `X-OPENAI-KEY` header value
- Only passed directly to OpenAI API client

**General Security:**
- User text content is never logged (only length and IP for abuse tracking)
- API keys are never included in logs or error messages
- Rate limiting and daily caps prevent abuse

## API Endpoints

### `POST /api/generate`

Process text based on the selected mode.

**Request Body:**
```json
{
  "text": "Your text here",
  "mode": "grammar_fix"
}
```

**Response:**
```json
{
  "result": "Processed text result"
}
```

**Available Modes:**
- `grammar_fix` - Grammar Fix (Standard Arabic)
- `professional_arabic` - Rewrite – Professional Arabic
- `emirati_dialect` - Rewrite – Emirati Dialect
- `academic_tone` - Rewrite – Academic Tone
- `marketing_tone` - Rewrite – Marketing Tone
- `translate_en_ar` - Translate EN → AR
- `translate_ar_en` - Translate AR → EN

### `GET /api/modes`

Get a list of all available modes.

### `GET /health`

Health check endpoint. Returns `{"status": "ok"}`.

### `GET /`

Serves the frontend application (index.html).

## Configuration

### Environment Variables

- `OPENAI_API_KEY` (required for free tier): Server-side OpenAI API key for free tier usage
- `OPENAI_MODEL` (optional): Model to use (default: `gpt-4o-mini`)
- `API_TIMEOUT` (optional): Request timeout in seconds (default: `60`)

### Abuse Protection & Limits

The application includes multiple layers of protection:

**Universal Limits (apply to everyone):**
- **Text Length Limit**: Maximum 2500 characters per request
- **Rate Limiting**: 10 requests per 10 minutes per IP address

**Free Tier Limits (no BYO key):**
- **Daily Cap**: 5 requests per day per IP address
- Resets at midnight (based on server date)
- Tracked in-memory (resets on server restart)
- **BYO key bypasses daily cap** but still respects rate limit

**Logging:**
- Blocked requests are logged with IP and reason
- User text content is NEVER logged
- API keys are NEVER logged

**Where to Change Limits:**

Edit these constants in `back_end/app.py`:
- `MAX_TEXT_LENGTH = 2500` - Maximum input text length
- `RATE_LIMIT_MAX_REQUESTS = 10` - Requests per time window
- `RATE_LIMIT_WINDOW_SECONDS = 600` - Time window in seconds (10 minutes)
- `FREE_TIER_DAILY_LIMIT = 5` - Daily free tier limit per IP

### Customizing Prompts

Edit the `MODE_PROMPTS` dictionary in `back_end/model.py` to customize the system prompts for each mode.

## Troubleshooting

### "Server is not configured" error

- The server's `OPENAI_API_KEY` environment variable is not set
- Either set the environment variable OR provide your own key in the frontend
- This error appears when trying to use free tier without server key configured

### "Daily free limit reached" error

- You've used all 5 free requests for today (free tier, no BYO key)
- Options:
  1. **Add your own OpenAI API key** for unlimited daily use (your billing, no daily cap)
  2. Wait until tomorrow (resets at midnight)
  3. Use a different IP address (limit is per IP)
- **Note**: With BYO key, daily cap is bypassed but rate limit (10 per 10 min) still applies

### Rate limit errors

If you see "Rate limit exceeded. Try again later.":
- You've made more than 10 requests in the last 10 minutes
- Wait a few minutes before trying again
- Rate limits are per IP address and apply to everyone (free and BYO key users)

### Text too long error

- Maximum text length is 2500 characters
- Split your text into smaller chunks if needed

### API key errors

- If using BYO key: Make sure you've entered your API key and clicked "Save"
- The key must start with `sk-` and be a valid OpenAI API key
- Check that your key hasn't expired or been revoked

### Frontend not loading

- Ensure the server is running: `uvicorn back_end.app:app --reload`
- Check that you're accessing `http://127.0.0.1:8000` or `http://localhost:8000`
- Check browser console for detailed error messages
- Verify that the `front_end` folder exists and contains `index.html`, `styles.css`, and `script.js`

## Future Enhancements

- User authentication and accounts
- History of processed texts
- Custom mode creation
- Batch processing
- API rate limiting
- Monetization features

## License

This project is provided as-is for development purposes.


