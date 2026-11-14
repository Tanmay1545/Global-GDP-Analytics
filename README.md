# 🌍 Global GDP Analytics Dashboard

🚀 **Live Demo:** [Open Dashboard](https://global-gdp-analytics-7b2wdkvmrfdcxcnrgug9aq.streamlit.app/)

💻 **GitHub Repository:** https://github.com/Tanmay1545/Global-GDP-Analytics

An interactive global economic analytics dashboard built using Python, PostgreSQL, SQL, Pandas, Plotly and Streamlit.

## 🚀 Project Overview

The Global GDP Analytics Dashboard transforms raw World Bank GDP data into meaningful economic insights using Python, SQL, PostgreSQL, and Streamlit.

## 🛠️ Technologies Used

- **Python** – Data processing and application development
- **Pandas** – Data cleaning and transformation
- **PostgreSQL** – Relational database storage
- **SQLAlchemy** – Python-to-database connectivity
- **SQL** – Data analysis, ranking, CTEs and window functions
- **Streamlit** – Interactive dashboard
- **Plotly** – Interactive charts and visualisations
- **PyCountry** – Country code validation for map visualisation

## 📊 Dashboard Features

- Economic overview with GDP KPIs
- Country-wise GDP comparison
- Historical GDP trend analysis
- Interactive world GDP map
- Country and year filters
- GDP data explorer with CSV export
- SQL-based GDP ranking and annual growth analysis

## 📂 Project Structure

```text
Global-GDP-Analytics/
│
├── app.py
├── load_to_postgres.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   └── gdp_data.csv
│
└── .streamlit/
    └── secrets.toml
```

*Note: Do not upload your secrets.toml file or database password to GitHub.*

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd Global-GDP-Analytics
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create a PostgreSQL database named `gdp_analytics`.

Create `.streamlit/secrets.toml` and configure:

```toml
[postgres]
host = "localhost"
port = 5432
database = "gdp_analytics"
username = "postgres"
password = "YOUR_PASSWORD"
```

### 5. Import the GDP dataset

Place the World Bank GDP CSV file inside the `data` folder and run:

```bash
python load_to_postgres.py
```

### 6. Run the dashboard

```bash
python -m streamlit run app.py
```

## 📈 SQL Concepts Demonstrated

- Common Table Expressions (CTEs)
- Aggregate functions
- GROUP BY and ORDER BY
- RANK() window function
- LAG() window function
- Year-over-year GDP growth calculations

## 📚 Data Source

World Bank Open Data – GDP (Current US$)

Indicator: `NY.GDP.MKTP.CD`

https://data.worldbank.org/indicator/NY.GDP.MKTP.CD

## 🎯 Project Objective

To demonstrate practical data analytics skills through data cleaning, database management, SQL querying, economic analysis, and interactive visualisation.

---

**Developed as a Data Analytics Portfolio Project.**