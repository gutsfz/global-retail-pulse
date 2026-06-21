# Global Retail Pulse — E-commerce Sales & Customer Analytics

## Project Overview

This project analyses two years of transactional data (2009–2011) from a UK-based online retailer to surface actionable business insights around revenue trends, product performance, and customer behaviour. The end goal is a self-contained analytics pipeline — from raw Excel files through a PostgreSQL data store to an interactive dashboard — that could realistically support decisions in pricing, inventory management, and retention marketing. The dataset is the publicly available **Online Retail II** dataset published by the UCI Machine Learning Repository.

## Tech Stack

| Layer | Tool |
|---|---|
| Ingestion | Python 3.11 + pandas |
| Storage | PostgreSQL 15 (local) |
| Transformation | pandas (cleaning, RFM, aggregates) |
| SQL analysis | Plain `.sql` files, psycopg2 |
| Visualisation | Tableau Public (primary) / Plotly + Streamlit (lightweight alternative) |
| Version control | Git |

---

## Dataset

### What it is

**Online Retail II** — UCI Machine Learning Repository  
~1 million rows of invoice-level e-commerce transactions for a UK gift retailer, covering 01/12/2009 to 09/12/2011. Columns include invoice number, stock code, description, quantity, invoice date, unit price, customer ID, and country.

### How to download

The dataset requires a manual download (no direct script-accessible URL):

**Option A — UCI ML Repository (recommended)**

1. Go to: [https://archive.ics.uci.edu/dataset/502/online+retail+ii](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
2. Click **Download** — you may need to accept a terms-of-use form.
3. Extract the ZIP. You will get a file named `online_retail_II.xlsx` (or similar).

**Option B — Kaggle**

1. Log in to [https://www.kaggle.com](https://www.kaggle.com) (free account required).
2. Search for **"Online Retail II UCI"** or navigate directly to the dataset page.
3. Click **Download** and extract the ZIP.

### Where to place the file

Move (or copy) the downloaded file into this repository:

```
data/raw/online_retail_II.xlsx
```

The `data/raw/` directory is excluded from version control via `.gitignore`. The `.gitkeep` file inside it is the only thing committed — it just ensures Git tracks the empty folder.

---

## Local Setup — PostgreSQL on Windows

### Prerequisites

- Python 3.10+ (verify with `python --version` in PowerShell)
- PostgreSQL 15+ installed locally ([download here](https://www.postgresql.org/download/windows/))
- The `psql` CLI added to your PATH (the PostgreSQL installer offers this option)

### 1. Create the database

You can do this either via the command line or via pgAdmin. Pick whichever feels more comfortable.

#### Option A — Command line (psql)

Open PowerShell and run:

```powershell
# Connect to the default postgres superuser
psql -U postgres

# Inside the psql prompt, create the database and a dedicated user
CREATE DATABASE global_retail_pulse;
CREATE USER grp_user WITH PASSWORD 'your_strong_password';
GRANT ALL PRIVILEGES ON DATABASE global_retail_pulse TO grp_user;
\q
```

Or create the database in one shot without entering the prompt:

```powershell
createdb -U postgres global_retail_pulse
```

#### Option B — pgAdmin (GUI)

1. Open **pgAdmin 4** from the Start menu.
2. In the left panel, expand **Servers → PostgreSQL 15 → Databases**.
3. Right-click **Databases** → **Create → Database…**
4. Set the name to `global_retail_pulse`, click **Save**.
5. To create a dedicated user: expand **Login/Group Roles** → right-click → **Create → Login/Group Role…** Fill in the name and password under the **General** and **Definition** tabs, then grant permissions under **Privileges**.

### 2. Configure your environment

Copy the example env file and fill in your credentials:

```powershell
copy .env.example .env
```

Open `.env` in any text editor and update the values:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=global_retail_pulse
DB_USER=grp_user
DB_PASSWORD=your_strong_password
```

> **Security note:** `.env` is listed in `.gitignore` and will never be committed to version control. Only `.env.example` (with placeholder values) is tracked.

### 3. Install Python dependencies

Create a virtual environment and install the pinned requirements:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> If PowerShell blocks script execution, run:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 4. Test the connection

After filling in `.env`, run this one-liner to verify the connection:

```powershell
python -c "
import psycopg2, os
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
)
print('Connection successful:', conn.get_dsn_parameters())
conn.close()
"
```

A successful output looks like:

```
Connection successful: {'dbname': 'global_retail_pulse', 'user': 'grp_user', 'host': 'localhost', ...}
```

> **SQLite alternative:** If PostgreSQL becomes an obstacle, a SQLite-backed version of the pipeline is documented as a fallback option. Ask about it in the issues section of this repo.

---

## How to Run

_Step-by-step run instructions will be added in Phase 3, once the pipeline scripts are implemented._

---

## Project Structure

```
global-retail-pulse/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
├── data/
│   ├── raw/              # Place downloaded dataset here (git-ignored)
│   └── processed/        # Pipeline outputs (git-ignored)
├── sql/
│   ├── schema.sql        # Table definitions
│   └── analysis_queries.sql
├── src/
│   ├── db.py             # PostgreSQL connection factory
│   ├── extract.py        # Raw data ingestion
│   ├── transform.py      # Cleaning + RFM + aggregates
│   └── load.py           # Bulk insert to PostgreSQL
├── notebooks/
│   └── 01_exploratory_analysis.ipynb
├── dashboard/
│   └── README.md
└── docs/
    └── architecture.md
```

---

## License

MIT — see [LICENSE](LICENSE).
