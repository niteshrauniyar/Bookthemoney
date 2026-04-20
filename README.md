# NEPSE FloorSheet Intelligence — Institutional Detection System

A production-grade Streamlit application for detecting big players (institutional activity) using floorsheet data, market data, and advanced analytics.

---

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Run the App

```bash
streamlit run app.py
```

---

## 📋 Features

### Data Input
- **Auto-simulation**: Instantly generates realistic NEPSE market + floorsheet data
- **Excel upload**: Upload `.xlsx` / `.csv` floorsheet and market data
- **Flexible column mapping**: Auto-detects and normalizes column names
- **Error-proof**: Never crashes on missing/messy data

### Analysis Modules

| Module | Description |
|--------|-------------|
| Broker Net Flow | Net buy/sell per broker, dominance detection |
| Order Flow ACF | Autocorrelation for order splitting detection |
| Trade Size Analysis | Large trade detection, institutional flags |
| Metaorder Detection | Sequential pattern detection, suspicion scoring |
| Volume Profile | POC, Value Area High/Low computation |
| Amihud Illiquidity | Illiquidity ratio, spike detection |
| Kyle's Lambda | Price impact per unit of signed volume |
| Network Analysis | Broker centrality, co-activity graphs |
| Trader Clustering | Institutional vs. retail segmentation |
| Behavioral Detection | Stealth accumulation, distribution, obfuscation |
| Smart Money Score | Composite -10 to +10 score with confidence |

---

## 📄 Floorsheet Excel Format

Expected columns (flexible naming):

| Column | Aliases |
|--------|---------|
| SN | S.N., No, # |
| Contract No | Contract, Transaction No |
| Stock Symbol | Scrip, Ticker, Stock |
| Buyer Broker No | Buyer, BuyerBroker |
| Seller Broker No | Seller, SellerBroker |
| Quantity | Qty, Shares, Volume |
| Rate | Price, LTP, Trade Price |
| Amount | Turnover, Value, Trade Amount |

---

## 🎯 Smart Money Score

| Score | Direction | Interpretation |
|-------|-----------|----------------|
| +4 to +10 | Bullish | Strong institutional accumulation |
| +1.5 to +4 | Mild Bullish | Possible accumulation |
| -1.5 to +1.5 | Neutral | No clear direction |
| -4 to -1.5 | Mild Bearish | Possible distribution |
| -10 to -4 | Bearish | Institutional distribution |

---

## 🏗 Architecture

```
app.py
├── Data Generation (generate_market_data, generate_floorsheet)
├── Normalization Layer (normalize_floorsheet, normalize_market_data)
├── Analysis Modules
│   ├── broker_net_flow()
│   ├── acf_analysis()
│   ├── trade_size_analysis()
│   ├── metaorder_detection()
│   ├── volume_profile()
│   ├── amihud_illiquidity()
│   ├── kyle_lambda()
│   ├── network_analysis()
│   ├── clustering_analysis()
│   └── behavioral_detection()
├── Scoring (smart_money_score)
├── Charts (Plotly, dark theme)
└── Dashboard UI (Streamlit)
```

---

## 📊 Output Exports

- `smart_money_scores.csv` — Full score table
- `{SYMBOL}_broker_flow.csv` — Broker net flow per stock
- `{SYMBOL}_metaorders.csv` — Detected metaorders
- `{SYMBOL}_clusters.csv` — Trader cluster assignments
