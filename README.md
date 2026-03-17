# ExchangeAgg

End-to-end analytics platform processing live cryptocurrency data across exchanges while using PySpark/Dash for analysis and data visualizations.

## Features

- PySpark ETL pipeline transforms live cryptocurrency quotes into OHLC bars and cross-exchange spread metrics
- P50/P90/P99 API latency tracking across exchanges + rolling last 5m summary stats table 
- HTTP error rate monitoring/logging
- Rolling regression residuals, spreads, and volatility forecasts computed via PySpark to power cross-exchange analytics
- Interactive dashboards built with Plotly Dash
- Data quality safeguards including ETL state management, duplicate detection, and comprehensive logging
- Modular design to support the easy addition of new exchanges or currency pairs
- Multiprocessing orchestrator (main.py) coordinating API data collection, Spark analytics, and Dash dashboards


## Architecture

```mermaid
graph LR
    
    A[Data Collection<br/><br/>Exchange APIs,<br/>Bid/Ask, Latency, Status logging] --> B[PostgreSQL Storage<br/><br/>Create bars, Latency metrics, Quality checks<br/>]
    
    B --> C[SQL Aggregation<br/><br/>OHLC, P50/P90/P99<br/>distributions, etc.]
    
    C --> D[PySpark/Pandas<br/><br/>Analysis,<br/>Data validation]
    D --> E[Dash/Plotly<br/><br/>Flowing updates,<br/>Multi-chart layout<br/>]
    E --> F[Dashboard<br/><br/>Symbol filtering,<br/>Date ranges,<br/>Exchange selection,<br/>Cross-asset analytics]
    
    
    style A fill:#e1f5fe
    style F fill:#c8e6c9
    classDef title font-size:14px,font-weight:bold,color:#333
    class A,B,C,D,E,F title
```

## Quick Start (Local)
1. Clone the Repository
 ```bash
 git clone https://github.com/Chicago-tr/ExchangeAggregator.git
  ```
2. Install Dependencies
```bash
cd ExchangeAggregator
#Postgres
brew install postgresql@16
brew services start postgresql@16
createdb name_your_db

#Python deps
pip install -r python_service/requirements.txt

# TypeScript deps
cd typescript_service && npm install && cd ..
```
3. Set .env variables such as DB_URL and DB_NAME (.env.example lists whats needed)
   
4. Migrate database
```bash
npx drizzle-kit migrate
```

6. Run the platform
```bash
python main.py
```

## Screenshots
<img width="922" height="422" alt="homescreen" src="https://github.com/user-attachments/assets/620568d3-f2cf-48f4-83a5-51bdcfd16794" />

---

---

<img width="922" height="422" alt="regression_residuals" src="https://github.com/user-attachments/assets/f7e236b6-772d-4c4b-ba7d-16ce0ecc1cf0" />

---

---

<img width="922" height="422" alt="spread_zscore" src="https://github.com/user-attachments/assets/71c5d795-740d-45f3-bda8-65860d2f58f6" />

---

---

<img width="922" height="422" alt="forecast_stats" src="https://github.com/user-attachments/assets/72b2c5f1-ac91-4b33-b5ab-b4d64b47680a" />

---

---

<img width="922" height="422" alt="latency" src="https://github.com/user-attachments/assets/8879a920-693b-40ec-aba7-c212def2f71b" />

## Contributing
All contributions welcome, just fork the repo and open a pull request to ```main```.

