# AI News Summarizer Bot for KakaoTalk

This project is a fully automated bot that scrapes the latest news based on a specific query, uses the Google Gemini API to summarize it, and sends the summary to you via KakaoTalk. The entire process is scheduled to run automatically using GitHub Actions.

## ✨ Features

- **Dynamic News Scraping**: Fetches the latest news headlines from Google News for any given query.
- **AI-Powered Summarization**: Leverages the Google Gemini API to generate concise, readable summaries of the news.
- **Automated KakaoTalk Delivery**: Sends the formatted summary directly to you using KakaoTalk's "Message to Me" API.
- **Scheduled Automation**: Uses GitHub Actions for serverless, scheduled execution, requiring no dedicated server.

## ⚙️ How It Works

The workflow is straightforward and automated:

1.  **Scheduled Trigger**: A GitHub Actions workflow, defined by a `cron` schedule, kicks off the process at a specified time.
2.  **Scrape News**: The Python script (`summarizer.py`) scrapes the latest news headlines from Google News.
3.  **Summarize with AI**: The collected headlines are passed to the Gemini Pro API, which returns a coherent summary.
4.  **Send Notification**: The script (`kakao_sender.py`) uses the KakaoTalk API to send the AI-generated summary as a message to your personal chat.

---

## 🚀 Setup and Installation

Follow these steps to get the project running.

### Prerequisites

- Python 3.8 or higher
- A GitHub account

### Step 1: Clone the Repository

First, clone this repository to your local machine.

```bash
git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name
```

### Step 2: Install Dependencies

This project uses several Python packages. You can install them all using `pip`.

First, create a `requirements.txt` file in your project root with the following content:

```text
requests
beautifulsoup4
python-dotenv
google-generativeai
```

Now, install the dependencies:

```bash
pip install -r requirements.txt
```

### Step 3: Get API Keys and Tokens

You need to acquire credentials from both Google and Kakao.

#### 1. Google Gemini API Key

- Go to **Google AI Studio**.
- Log in with your Google account.
- Click **Create API key** to generate a new key.
- Copy this key. You will use it as `GEMINI_API_KEY`.

#### 2. KakaoTalk API Credentials

This is a multi-step process to get a key that allows the script to send messages on your behalf.

1.  **Create a Kakao App**: Go to the [Kakao Developers](https://developers.kakao.com/) portal, create a new application, and get the **REST API Key**.

2.  **Set Redirect URI**: In your app settings under **Platform**, set the Redirect URI to `https://example.com/oauth`.

3.  **Enable Kakao Login**: Go to **Product Settings > Kakao Login** and turn it on. Under **Consent Items**, find and set "KakaoTalk message sending (to me)" to "Required Consent".

4.  **Get Authorization Code (One-time only)**: Paste the following URL into your browser, replacing `{YOUR_REST_API_KEY}` with your key.

    ```
    https://kauth.kakao.com/oauth/authorize?client_id={YOUR_REST_API_KEY}&redirect_uri=https://example.com/oauth&response_type=code&scope=talk_message
    ```

    After logging in and consenting, the URL in your browser will contain a `code`. Copy this code.

5.  **Get Refresh Token (One-time only)**: Use the code you just received to get a long-lived Refresh Token. Run the following `curl` command in your terminal, replacing the placeholders.

    ```bash
    curl -X POST "https://kauth.kakao.com/oauth/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "grant_type=authorization_code" \
    -d "client_id={YOUR_REST_API_KEY}" \
    -d "redirect_uri=https://example.com/oauth" \
    -d "code={THE_CODE_FROM_PREVIOUS_STEP}"
    ```

    The JSON response will contain a `refresh_token`. Copy this value.

### Step 4: Configure Environment Variables

#### For Local Testing

For testing on your local machine, create a `.env` file in the root of the project.

```
# .env file
GEMINI_API_KEY="your_gemini_api_key_here"
KAKAO_REST_API_KEY="your_kakao_rest_api_key_here"
KAKAO_REFRESH_TOKEN="your_kakao_refresh_token_here"
```

**Important**: Add `.env` to your `.gitignore` file to prevent committing sensitive keys.

#### For GitHub Actions (Production)

For the automated workflow, you must use GitHub Repository Secrets.

1.  In your GitHub repository, go to **Settings > Secrets and variables > Actions**.
2.  Click **New repository secret** and add the following three secrets:
    -   `GEMINI_API_KEY`
    -   `KAKAO_REST_API_KEY`
    -   `KAKAO_REFRESH_TOKEN`

## ▶️ Usage

### Running Locally

You can test the script directly from your terminal. Make sure your `.env` file is set up correctly.

```bash
python scheduler/news/ai/summarizer.py "AI trends"
```

Replace `"AI trends"` with any query you want.

### Automated Workflow

The automation is handled by the `.github/workflows/daily-news.yml` file. By default, it runs on a schedule. You can customize the schedule by editing the `cron` value in the YAML file. The times are in UTC.

```yaml
# .github/workflows/daily-news.yml

name: Daily AI News Summary

on:
  schedule:
    # Runs at 21:30 UTC (6:30 AM KST) and 09:00 UTC (6:00 PM KST)
    - cron: '30 21 * * *'
    - cron: '0 9 * * *'
  workflow_dispatch: # Allows manual runs from the Actions tab

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run summarizer and send to Kakao
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          KAKAO_REST_API_KEY: ${{ secrets.KAKAO_REST_API_KEY }}
          KAKAO_REFRESH_TOKEN: ${{ secrets.KAKAO_REFRESH_TOKEN }}
        run: |
          python scheduler/news/ai/summarizer.py "AI latest trends"
```

Once you push this file to your repository, the bot will start running on the defined schedule.