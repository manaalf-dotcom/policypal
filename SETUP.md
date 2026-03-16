# Setup Guide — PolicyPal

## Prerequisites

- Python 3.9 or higher
- An OpenAI API key ([get one here](https://platform.openai.com/api-keys))
- Git

---

## Local Installation

**1. Clone the repo**
```bash
git clone https://github.com/your-username/PolicyPal
cd PolicyPal
```

**2. Create a virtual environment**
```bash
python -m venv .venv

# Mac/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your API key**

Create the Streamlit secrets folder and file:
```bash
mkdir .streamlit
```

Then create `.streamlit/secrets.toml` with this content:
```toml
OPENAI_API_KEY = "sk-your-key-here"
```

> ⚠️ Never commit this file. It's already in `.gitignore`.

**5. Run the app**
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`

---

## Deploying to Streamlit Cloud (Public URL)

1. Push your repo to GitHub (make sure `secrets.toml` is NOT included)
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **"New app"**
4. Select your repo → branch `main` → main file `app.py`
5. Click **"Advanced settings"** → paste into the Secrets box:
   ```
   OPENAI_API_KEY = "sk-your-key-here"
   ```
6. Click **Deploy**

Your public URL will be `https://your-app-name.streamlit.app` — ready to share in about 2 minutes.

---

## Requirements

```
openai>=1.0.0
streamlit>=1.32.0
pdfplumber>=0.10.0
plotly>=5.18.0
tiktoken>=0.6.0
numpy>=1.24.0
scipy>=1.11.0
```
