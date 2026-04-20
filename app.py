"""
NEPSE FloorSheet Intelligence — Institutional Detection System
Production-grade Streamlit application for detecting big players
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
import io
import base64
from datetime import datetime, timedelta
import json

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NEPSE FloorSheet Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# CUSTOM CSS — DARK TERMINAL AESTHETIC
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

:root {
    --bg-primary: #080c12;
    --bg-secondary: #0d1420;
    --bg-card: #111827;
    --bg-card-hover: #162035;
    --accent-green: #00ff88;
    --accent-cyan: #00d4ff;
    --accent-red: #ff3d6e;
    --accent-amber: #ffb830;
    --accent-purple: #a855f7;
    --text-primary: #e2e8f0;
    --text-secondary: #64748b;
    --text-muted: #334155;
    --border: #1e293b;
    --border-glow: rgba(0, 255, 136, 0.3);
}

html, body, [class*="css"] {
    font-family: 'Space Mono', monospace;
    background-color: var(--bg-primary);
    color: var(--text-primary);
}

.stApp {
    background-color: var(--bg-primary);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] .stMarkdown {
    color: var(--text-secondary);
}

/* Headers */
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    color: var(--text-primary) !important;
}

/* Cards */
.intel-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
    margin: 8px 0;
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
}

.intel-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: var(--accent-green);
}

.intel-card.bearish::before {
    background: var(--accent-red);
}

.intel-card.neutral::before {
    background: var(--accent-amber);
}

/* Score badges */
.score-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
}

.score-bullish { background: rgba(0,255,136,0.15); color: var(--accent-green); border: 1px solid var(--accent-green); }
.score-bearish { background: rgba(255,61,110,0.15); color: var(--accent-red); border: 1px solid var(--accent-red); }
.score-neutral { background: rgba(255,184,48,0.15); color: var(--accent-amber); border: 1px solid var(--accent-amber); }

/* Metric boxes */
.metric-box {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 16px;
    text-align: center;
}

.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    font-weight: 800;
    color: var(--accent-cyan);
}

.metric-label {
    font-size: 11px;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
}

/* Header banner */
.header-banner {
    background: linear-gradient(135deg, #080c12 0%, #0d1e35 50%, #080c12 100%);
    border: 1px solid var(--border);
    border-top: 2px solid var(--accent-green);
    padding: 24px 32px;
    border-radius: 8px;
    margin-bottom: 24px;
}

.header-title {
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    font-weight: 800;
    color: var(--accent-green);
    letter-spacing: 2px;
    margin: 0;
}

.header-sub {
    font-size: 11px;
    color: var(--text-secondary);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 6px;
}

/* Tables */
.stDataFrame {
    border: 1px solid var(--border) !important;
}

/* Divider */
.section-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 24px 0;
}

/* Status pill */
.status-pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.status-live { background: rgba(0,255,136,0.2); color: var(--accent-green); }
.status-sim { background: rgba(255,184,48,0.2); color: var(--accent-amber); }

/* Flag tags */
.flag-tag {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 700;
    margin: 2px;
    background: rgba(168,85,247,0.15);
    color: var(--accent-purple);
    border: 1px solid rgba(168,85,247,0.4);
}

/* Hide streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display:none;}

/* Buttons */
.stButton > button {
    background: transparent;
    border: 1px solid var(--accent-cyan);
    color: var(--accent-cyan);
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    letter-spacing: 1px;
    border-radius: 4px;
    padding: 8px 20px;
    transition: all 0.2s;
}

.stButton > button:hover {
    background: var(--accent-cyan);
    color: var(--bg-primary);
}

/* Select boxes */
.stSelectbox > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: var(--bg-secondary);
    padding: 8px;
    border-radius: 8px;
    border: 1px solid var(--border);
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
    color: var(--text-secondary);
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    letter-spacing: 1px;
}

.stTabs [aria-selected="true"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--accent-green) !important;
    color: var(--accent-green) !important;
}

/* Progress bars */
.stProgress > div > div > div {
    background: var(--accent-green);
}

/* Warning/info boxes */
.stWarning {
    background: rgba(255,184,48,0.1) !important;
    border: 1px solid var(--accent-amber) !important;
}

.stInfo {
    background: rgba(0,212,255,0.1) !important;
    border: 1px solid var(--accent-cyan) !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# DATA GENERATION & SIMULATION
# ─────────────────────────────────────────────────────────────

NEPSE_SYMBOLS = [
    "NABIL", "NICA", "SCB", "PRVU", "MBL", "SBI", "ADBL", "HBL",
    "GBIME", "NBB", "HIDCL", "NHPC", "NEA", "CIT", "NIFRA",
    "SHIVM", "UPPER", "CHCL", "RURU", "API", "AKPL", "NPCL",
    "CHILIME", "BPCL", "NGPL", "UMHL", "DORDI", "SPDL", "BHL", "NMB"
]

BROKER_IDS = list(range(1, 61))

def generate_market_data(n_symbols=20, seed=42):
    """Generate realistic NEPSE-style market data"""
    np.random.seed(seed)
    syms = NEPSE_SYMBOLS[:n_symbols]
    data = []
    for sym in syms:
        base_price = np.random.uniform(200, 2000)
        open_p = base_price
        close_p = base_price * (1 + np.random.normal(0, 0.03))
        high_p = max(open_p, close_p) * (1 + np.random.uniform(0, 0.02))
        low_p = min(open_p, close_p) * (1 - np.random.uniform(0, 0.02))
        volume = int(np.random.lognormal(10, 1.5))
        avg_vol = int(volume * np.random.uniform(0.3, 1.8))
        turnover = volume * close_p
        pct_chg = (close_p - open_p) / open_p * 100
        data.append({
            "symbol": sym,
            "open": round(open_p, 2),
            "high": round(high_p, 2),
            "low": round(low_p, 2),
            "close": round(close_p, 2),
            "volume": volume,
            "avg_volume": avg_vol,
            "turnover": round(turnover, 2),
            "pct_change": round(pct_chg, 2),
            "vol_ratio": round(volume / avg_vol, 2),
        })
    return pd.DataFrame(data)


def rank_stocks(market_df, top_n=8):
    """Rank stocks using composite opportunity score"""
    df = market_df.copy()
    # Normalize each factor to 0-1
    df["vol_score"] = (df["vol_ratio"] - df["vol_ratio"].min()) / (df["vol_ratio"].max() - df["vol_ratio"].min() + 1e-9)
    df["move_score"] = df["pct_change"].abs() / (df["pct_change"].abs().max() + 1e-9)
    df["turn_score"] = (df["turnover"] - df["turnover"].min()) / (df["turnover"].max() - df["turnover"].min() + 1e-9)
    df["composite"] = 0.4 * df["vol_score"] + 0.35 * df["move_score"] + 0.25 * df["turn_score"]
    return df.nlargest(top_n, "composite").reset_index(drop=True)


def generate_floorsheet(symbol, n_trades=200, seed=None):
    """Generate realistic floorsheet data for a symbol"""
    if seed is None:
        seed = hash(symbol) % 10000
    np.random.seed(seed)

    base_price = np.random.uniform(200, 2000)
    trades = []

    # Simulate institutional buyers (2-3 dominant brokers)
    inst_buyers = np.random.choice(BROKER_IDS, size=3, replace=False).tolist()
    inst_sellers = np.random.choice([b for b in BROKER_IDS if b not in inst_buyers], size=2, replace=False).tolist()

    price = base_price
    for i in range(n_trades):
        # Price walk
        price = price * (1 + np.random.normal(0, 0.002))

        # Trade size: mix of large (institutional) and small (retail)
        if np.random.random() < 0.15:  # 15% large trades
            qty = int(np.random.lognormal(7, 0.5))
        else:
            qty = int(np.random.lognormal(4, 1))

        qty = max(10, qty)

        # Buyer/seller assignment with institutional bias
        if np.random.random() < 0.35:
            buyer = np.random.choice(inst_buyers)
        else:
            buyer = np.random.choice(BROKER_IDS)

        if np.random.random() < 0.25:
            seller = np.random.choice(inst_sellers)
        else:
            seller = np.random.choice(BROKER_IDS)

        if buyer == seller:
            seller = (seller % len(BROKER_IDS)) + 1

        amount = round(price * qty, 2)
        trades.append({
            "SN": i + 1,
            "Contract No": f"C{10000 + i}",
            "Stock Symbol": symbol,
            "Buyer Broker No": buyer,
            "Seller Broker No": seller,
            "Quantity": qty,
            "Rate": round(price, 2),
            "Amount": amount,
        })

    return pd.DataFrame(trades)


# ─────────────────────────────────────────────────────────────
# DATA NORMALIZATION
# ─────────────────────────────────────────────────────────────

COLUMN_MAP = {
    # symbol
    "stock symbol": "symbol", "stocksymbol": "symbol", "scrip": "symbol",
    "ticker": "symbol", "stock": "symbol",
    # buyer
    "buyer broker no": "buyer_broker", "buyerbroker": "buyer_broker",
    "buyer broker": "buyer_broker", "buyer": "buyer_broker",
    "buyerbrokerno": "buyer_broker",
    # seller
    "seller broker no": "seller_broker", "sellerbroker": "seller_broker",
    "seller broker": "seller_broker", "seller": "seller_broker",
    "sellerbrokerno": "seller_broker",
    # quantity
    "quantity": "quantity", "qty": "quantity", "shares": "quantity",
    "volume": "quantity",
    # rate
    "rate": "rate", "price": "rate", "ltp": "rate", "trade price": "rate",
    "tradeprice": "rate",
    # amount
    "amount": "amount", "turnover": "amount", "value": "amount",
    "trade amount": "amount", "tradeamount": "amount",
    # contract
    "contract no": "contract_no", "contractno": "contract_no",
    "contract": "contract_no", "transaction no": "contract_no",
    # sn
    "sn": "sn", "s.n.": "sn", "s.n": "sn", "no": "sn", "#": "sn",
}

MARKET_COL_MAP = {
    "pct_change": "pct_change", "percentchange": "pct_change",
    "change%": "pct_change", "% change": "pct_change",
    "changepercent": "pct_change", "chg%": "pct_change",
    "ltp": "close", "last": "close", "lastprice": "close",
    "closeprice": "close", "tradeprice": "close",
}


def normalize_floorsheet(df):
    """Robust floorsheet normalization — never crashes"""
    warnings_list = []
    df = df.copy()

    # Step 1: lowercase columns
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Step 2: map to standard names
    rename = {}
    for col in df.columns:
        if col in COLUMN_MAP:
            rename[col] = COLUMN_MAP[col]
    df.rename(columns=rename, inplace=True)

    # Step 3: ensure required columns exist
    required = {"symbol": "UNKNOWN", "buyer_broker": 0, "seller_broker": 0,
                 "quantity": 0, "rate": 0.0, "amount": 0.0}

    for col, default in required.items():
        if col not in df.columns:
            df[col] = default
            warnings_list.append(f"Column '{col}' missing — using default ({default})")

    # Step 4: numeric conversion
    for col in ["quantity", "rate", "amount", "buyer_broker", "seller_broker"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce").fillna(0)

    # Step 5: clean symbol
    df["symbol"] = df["symbol"].astype(str).str.strip().str.upper()
    df = df[df["symbol"] != "NAN"].copy()

    # Step 6: compute amount if missing
    mask = df["amount"] == 0
    if mask.any():
        df.loc[mask, "amount"] = df.loc[mask, "quantity"] * df.loc[mask, "rate"]

    return df, warnings_list


def normalize_market_data(df):
    """Normalize uploaded market data"""
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    for old, new in MARKET_COL_MAP.items():
        if old in df.columns and new not in df.columns:
            df.rename(columns={old: new}, inplace=True)

    # Compute pct_change if missing
    if "pct_change" not in df.columns:
        if "close" in df.columns and "open" in df.columns:
            df["pct_change"] = (
                (pd.to_numeric(df["close"], errors="coerce") -
                 pd.to_numeric(df["open"], errors="coerce")) /
                pd.to_numeric(df["open"], errors="coerce").replace(0, np.nan) * 100
            ).fillna(0)
        else:
            df["pct_change"] = 0

    for col in ["close", "open", "high", "low", "volume", "turnover", "pct_change"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce").fillna(0)

    return df


# ─────────────────────────────────────────────────────────────
# ANALYSIS MODULES
# ─────────────────────────────────────────────────────────────

def broker_net_flow(df):
    """Compute net buy/sell flow per broker"""
    buy = df.groupby("buyer_broker")["amount"].sum().rename("buy_amount")
    sell = df.groupby("seller_broker")["amount"].sum().rename("sell_amount")
    buy_qty = df.groupby("buyer_broker")["quantity"].sum().rename("buy_qty")
    sell_qty = df.groupby("seller_broker")["quantity"].sum().rename("sell_qty")

    flow = pd.concat([buy, sell, buy_qty, sell_qty], axis=1).fillna(0)
    flow.index.name = "broker"
    flow = flow.reset_index()
    flow["net_flow"] = flow["buy_amount"] - flow["sell_amount"]
    flow["net_qty"] = flow["buy_qty"] - flow["sell_qty"]
    flow["total_activity"] = flow["buy_amount"] + flow["sell_amount"]
    flow = flow[flow["total_activity"] > 0].sort_values("net_flow", ascending=False)
    return flow


def acf_analysis(df, n_lags=20):
    """Order flow autocorrelation"""
    if len(df) < 30:
        return np.zeros(n_lags), 0.0

    df_sorted = df.sort_values("sn") if "sn" in df.columns else df.copy()
    # Signed order flow: +1 buyer-initiated, -1 seller-initiated
    mid = df_sorted["rate"].rolling(3, min_periods=1).mean()
    sign = np.where(df_sorted["rate"] >= mid, 1, -1)
    qty_signed = df_sorted["quantity"].values * sign

    acf_vals = []
    mean_val = qty_signed.mean()
    var_val = ((qty_signed - mean_val) ** 2).mean()

    if var_val == 0:
        return np.zeros(n_lags), 0.0

    for lag in range(1, n_lags + 1):
        if lag >= len(qty_signed):
            acf_vals.append(0.0)
        else:
            cov = ((qty_signed[lag:] - mean_val) * (qty_signed[:-lag] - mean_val)).mean()
            acf_vals.append(cov / var_val)

    persistence = float(np.mean(np.abs(acf_vals[:5])))
    return np.array(acf_vals), persistence


def trade_size_analysis(df):
    """Detect large trades and institutional size clusters"""
    qty = df["quantity"].values
    if len(qty) == 0:
        return {}, []

    p75 = np.percentile(qty, 75)
    p90 = np.percentile(qty, 90)
    p99 = np.percentile(qty, 99)

    large_mask = qty >= p90
    inst_mask = qty >= p75

    stats = {
        "mean": float(np.mean(qty)),
        "median": float(np.median(qty)),
        "p75": float(p75),
        "p90": float(p90),
        "p99": float(p99),
        "large_count": int(large_mask.sum()),
        "large_pct": float(large_mask.mean() * 100),
        "large_volume_pct": float(df.loc[large_mask, "quantity"].sum() / (df["quantity"].sum() + 1e-9) * 100),
        "inst_volume_pct": float(df.loc[inst_mask, "quantity"].sum() / (df["quantity"].sum() + 1e-9) * 100),
    }

    # Size distribution
    bins = [0, p75, p90, p99, float("inf")]
    labels = ["Small", "Medium", "Large", "Mega"]
    df_copy = df.copy()
    df_copy["size_cat"] = pd.cut(df_copy["quantity"], bins=bins, labels=labels)
    dist = df_copy.groupby("size_cat", observed=False)["quantity"].agg(["count", "sum"]).reset_index()
    dist.columns = ["category", "count", "total_qty"]
    return stats, dist


def metaorder_detection(df):
    """Detect repeated institutional metaorders"""
    if len(df) < 20:
        return [], "LOW"

    # Find brokers with many sequential trades
    suspicious = []

    for broker in df["buyer_broker"].unique():
        broker_trades = df[df["buyer_broker"] == broker].sort_values("sn" if "sn" in df.columns else df.index.name or "amount")
        if len(broker_trades) < 5:
            continue

        qty = broker_trades["quantity"].values
        # Check for consistent trade sizes (metaorder splitting)
        cv = np.std(qty) / (np.mean(qty) + 1e-9)
        freq = len(broker_trades)
        total_qty = broker_trades["quantity"].sum()
        total_pct = total_qty / (df["quantity"].sum() + 1e-9) * 100

        if cv < 0.5 and freq >= 8:  # Low variance, high frequency
            suspicious.append({
                "broker": int(broker),
                "side": "BUY",
                "trades": freq,
                "total_qty": int(total_qty),
                "market_pct": round(total_pct, 1),
                "cv": round(cv, 3),
                "suspicion": "HIGH" if cv < 0.3 and freq >= 12 else "MODERATE"
            })

    suspicion_level = "HIGH" if any(s["suspicion"] == "HIGH" for s in suspicious) else \
                      "MODERATE" if suspicious else "LOW"

    return suspicious[:10], suspicion_level


def volume_profile(df):
    """Compute volume profile with POC"""
    if len(df) < 10:
        return {}, pd.DataFrame()

    price_min = df["rate"].min()
    price_max = df["rate"].max()

    if price_min == price_max:
        return {"poc": price_min, "vah": price_min, "val": price_min}, pd.DataFrame()

    n_bins = min(30, len(df) // 3)
    bins = np.linspace(price_min, price_max, n_bins + 1)
    labels = [(bins[i] + bins[i+1]) / 2 for i in range(n_bins)]

    df_copy = df.copy()
    df_copy["price_bin"] = pd.cut(df_copy["rate"], bins=bins, labels=labels)
    profile = df_copy.groupby("price_bin", observed=False)["quantity"].sum().reset_index()
    profile.columns = ["price", "volume"]
    profile["price"] = pd.to_numeric(profile["price"], errors="coerce")
    profile = profile.dropna()

    total_vol = profile["volume"].sum()
    poc_idx = profile["volume"].idxmax()
    poc = float(profile.loc[poc_idx, "price"])

    # Value area (70% of volume)
    profile_sorted = profile.sort_values("volume", ascending=False)
    cumvol = 0
    value_prices = []
    for _, row in profile_sorted.iterrows():
        cumvol += row["volume"]
        value_prices.append(row["price"])
        if cumvol >= 0.7 * total_vol:
            break

    vah = max(value_prices) if value_prices else poc
    val = min(value_prices) if value_prices else poc

    return {"poc": round(poc, 2), "vah": round(vah, 2), "val": round(val, 2)}, profile


def amihud_illiquidity(df, market_row):
    """Compute Amihud illiquidity ratio"""
    if len(df) < 5:
        return 0.0, []

    # Group by time buckets (simulate intraday buckets)
    n_buckets = min(20, len(df) // 5)
    df_copy = df.copy().reset_index(drop=True)
    df_copy["bucket"] = pd.cut(df_copy.index, bins=n_buckets, labels=False)

    bucket_stats = df_copy.groupby("bucket").agg(
        vol=("quantity", "sum"),
        price_first=("rate", "first"),
        price_last=("rate", "last")
    ).dropna()

    bucket_stats["ret"] = (bucket_stats["price_last"] - bucket_stats["price_first"]).abs() / \
                           (bucket_stats["price_first"] + 1e-9)
    bucket_stats["illiq"] = bucket_stats["ret"] / (bucket_stats["vol"] + 1e-9)

    illiq_series = bucket_stats["illiq"].values.tolist()
    avg_illiq = float(np.mean(illiq_series)) if illiq_series else 0.0

    return avg_illiq, illiq_series


def kyle_lambda(df):
    """Kyle's lambda: price impact of order flow"""
    if len(df) < 10:
        return 0.0

    # Signed volume (approximate)
    mid = df["rate"].rolling(5, min_periods=1).mean()
    sign = np.where(df["rate"] >= mid, 1, -1)
    signed_vol = df["quantity"].values * sign

    # Price changes
    price_changes = df["rate"].diff().fillna(0).values

    # Regression
    if np.std(signed_vol) > 0 and np.std(price_changes) > 0:
        cov = np.cov(price_changes, signed_vol)
        if cov.shape == (2, 2) and cov[1, 1] > 0:
            return float(cov[0, 1] / cov[1, 1])

    return 0.0


def network_analysis(df):
    """Broker network centrality analysis"""
    # Build broker-broker co-activity
    brokers = list(set(df["buyer_broker"].tolist() + df["seller_broker"].tolist()))
    brokers = [b for b in brokers if b > 0][:30]  # Top 30

    if len(brokers) < 3:
        return {}, pd.DataFrame()

    broker_idx = {b: i for i, b in enumerate(brokers)}
    n = len(brokers)
    adj = np.zeros((n, n))

    for _, row in df.iterrows():
        b = row["buyer_broker"]
        s = row["seller_broker"]
        if b in broker_idx and s in broker_idx:
            i, j = broker_idx[b], broker_idx[s]
            adj[i, j] += row["amount"]
            adj[j, i] += row["amount"]

    # Degree & strength centrality
    strength = adj.sum(axis=1)
    degree = (adj > 0).sum(axis=1)

    # Approximate s-coreness (iterative peeling)
    strength_norm = strength / (strength.max() + 1e-9)

    centrality_df = pd.DataFrame({
        "broker": brokers,
        "strength": strength,
        "degree": degree,
        "strength_norm": strength_norm,
    }).sort_values("strength", ascending=False)

    network_info = {
        "top_broker": int(centrality_df.iloc[0]["broker"]) if len(centrality_df) > 0 else 0,
        "concentration": float(strength[:3].sum() / (strength.sum() + 1e-9)),
        "n_active": int((strength > 0).sum()),
    }

    return network_info, centrality_df.head(15)


def clustering_analysis(df):
    """KMeans-style trader clustering"""
    # Build features per broker
    buy_data = df.groupby("buyer_broker").agg(
        buy_qty=("quantity", "sum"),
        buy_trades=("quantity", "count"),
        buy_avg_size=("quantity", "mean"),
        buy_amount=("amount", "sum")
    )
    sell_data = df.groupby("seller_broker").agg(
        sell_qty=("quantity", "sum"),
        sell_trades=("quantity", "count"),
        sell_avg_size=("quantity", "mean"),
        sell_amount=("amount", "sum")
    )

    features = buy_data.join(sell_data, how="outer").fillna(0)
    features["total_trades"] = features["buy_trades"] + features.get("sell_trades", pd.Series(0, index=features.index))
    features["net_qty"] = features["buy_qty"] - features.get("sell_qty", pd.Series(0, index=features.index))
    features["direction_consistency"] = features["net_qty"].abs() / (features["buy_qty"] + features.get("sell_qty", pd.Series(0, index=features.index)) + 1e-9)

    if len(features) < 4:
        features["cluster"] = 0
        features["cluster_label"] = "Unknown"
        return features

    # Manual 2-cluster kmeans (institutional = high avg size, high consistency)
    score = (
        (features["buy_avg_size"] / (features["buy_avg_size"].max() + 1e-9)) * 0.4 +
        (features["direction_consistency"]) * 0.4 +
        (features["total_trades"] / (features["total_trades"].max() + 1e-9)) * 0.2
    )

    threshold = score.quantile(0.6)
    features["cluster"] = (score >= threshold).astype(int)
    features["cluster_label"] = features["cluster"].map({1: "Institutional", 0: "Retail"})
    features["inst_score"] = score.round(3)
    return features


def behavioral_detection(df, flow_df, cluster_df):
    """Detect behavioral patterns"""
    flags = []

    if len(df) == 0:
        return flags

    # Top buyers
    top_buyers = flow_df.nlargest(3, "net_flow")

    for _, broker in top_buyers.iterrows():
        b = broker["broker"]
        b_trades = df[df["buyer_broker"] == b].sort_values("sn" if "sn" in df.columns else df.index.name or "amount")

        if len(b_trades) < 5:
            continue

        qty = b_trades["quantity"].values
        cv = np.std(qty) / (np.mean(qty) + 1e-9)
        total_pct = broker["net_flow"] / (flow_df["buy_amount"].sum() + 1e-9) * 100

        # Stealth accumulation: slow consistent buying
        if cv < 0.4 and total_pct > 10:
            flags.append({"broker": int(b), "flag": "Stealth Accumulation",
                          "detail": f"Broker {b}: consistent small trades, {total_pct:.1f}% net buy"})

        # Obfuscation: alternating buy sizes
        if len(qty) >= 10:
            alternating = np.sum(np.diff(np.sign(np.diff(qty))) != 0) / (len(qty) - 2)
            if alternating > 0.6:
                flags.append({"broker": int(b), "flag": "Obfuscation Pattern",
                              "detail": f"Broker {b}: alternating trade sizes detected"})

    # Distribution detection (top sellers)
    top_sellers = flow_df.nsmallest(2, "net_flow")
    for _, broker in top_sellers.iterrows():
        b = broker["broker"]
        if broker["net_flow"] < -broker["buy_amount"] * 0.3:
            flags.append({"broker": int(b), "flag": "Institutional Distribution",
                          "detail": f"Broker {b}: heavy net selling, possible distribution"})

    # Broker coordination
    if len(flow_df) >= 4:
        top_3_buy_pct = flow_df.nlargest(3, "buy_amount")["buy_amount"].sum() / (flow_df["buy_amount"].sum() + 1e-9)
        if top_3_buy_pct > 0.6:
            brokers_str = ", ".join(str(int(b)) for b in flow_df.nlargest(3, "buy_amount")["broker"])
            flags.append({"broker": 0, "flag": "Coordinated Activity",
                          "detail": f"Brokers {brokers_str} control {top_3_buy_pct*100:.0f}% of buy volume"})

    # Informed trading (large trades before price move)
    if "rate" in df.columns and len(df) > 20:
        first_half = df.iloc[:len(df)//2]
        second_half = df.iloc[len(df)//2:]
        price_move = (second_half["rate"].mean() - first_half["rate"].mean()) / (first_half["rate"].mean() + 1e-9)
        if abs(price_move) > 0.01:
            large_in_first = first_half[first_half["quantity"] > first_half["quantity"].quantile(0.85)]
            if len(large_in_first) > 3:
                flags.append({"broker": 0, "flag": "Possible Informed Trading",
                              "detail": f"Large trades preceded {price_move*100:.1f}% price move"})

    return flags[:8]


def smart_money_score(flow_df, persistence, size_stats, metaorders, net_info,
                      cluster_df, flags, illiq, kyle_lam):
    """Build composite smart money score -10 to +10"""

    score = 0.0
    components = {}

    # 1. Broker flow concentration (0-2)
    if len(flow_df) > 0:
        top_net = flow_df.iloc[0]["net_flow"] if len(flow_df) > 0 else 0
        total_amt = flow_df["buy_amount"].sum() + 1e-9
        flow_score = min(2.0, abs(top_net) / total_amt * 10)
        score += flow_score if top_net > 0 else -flow_score
        components["Broker Flow"] = round(flow_score if top_net > 0 else -flow_score, 2)

    # 2. ACF persistence (0-2)
    acf_score = min(2.0, persistence * 10)
    score += acf_score
    components["ACF Persistence"] = round(acf_score, 2)

    # 3. Trade size anomalies (0-1.5)
    if isinstance(size_stats, dict) and size_stats:
        large_pct = size_stats.get("large_volume_pct", 0)
        size_score = min(1.5, large_pct / 20)
        score += size_score
        components["Trade Size"] = round(size_score, 2)

    # 4. Metaorders (0-1.5)
    if isinstance(metaorders, list):
        if any(m["suspicion"] == "HIGH" for m in metaorders):
            score += 1.5
            components["Metaorders"] = 1.5
        elif metaorders:
            score += 0.8
            components["Metaorders"] = 0.8
        else:
            components["Metaorders"] = 0.0

    # 5. Network dominance (0-1)
    if net_info:
        conc = net_info.get("concentration", 0)
        net_score = min(1.0, conc * 2)
        score += net_score
        components["Network"] = round(net_score, 2)

    # 6. Clustering (0-1)
    if isinstance(cluster_df, pd.DataFrame) and len(cluster_df) > 0 and "cluster_label" in cluster_df.columns:
        inst_count = (cluster_df["cluster_label"] == "Institutional").sum()
        total = len(cluster_df)
        cluster_score = min(1.0, inst_count / total * 3)
        score += cluster_score
        components["Clustering"] = round(cluster_score, 2)

    # 7. Behavioral flags (0-1)
    if flags:
        flag_score = min(1.0, len(flags) * 0.25)
        score += flag_score
        components["Behavioral"] = round(flag_score, 2)

    # Clamp score
    score = max(-10, min(10, score))

    # Confidence
    active_components = sum(1 for v in components.values() if abs(v) > 0.1)
    confidence = min(95, 40 + active_components * 10)

    # Interpretation
    if score >= 4:
        interpretation = "BULLISH — Strong institutional accumulation"
        direction = "Bullish"
    elif score >= 1.5:
        interpretation = "MILD BULLISH — Possible accumulation"
        direction = "Mild Bullish"
    elif score <= -4:
        interpretation = "BEARISH — Institutional distribution"
        direction = "Bearish"
    elif score <= -1.5:
        interpretation = "MILD BEARISH — Possible distribution"
        direction = "Mild Bearish"
    else:
        interpretation = "NEUTRAL — No clear institutional direction"
        direction = "Neutral"

    return {
        "score": round(score, 2),
        "confidence": confidence,
        "interpretation": interpretation,
        "direction": direction,
        "components": components,
    }


# ─────────────────────────────────────────────────────────────
# CHART BUILDERS
# ─────────────────────────────────────────────────────────────

DARK_LAYOUT = dict(
    plot_bgcolor="#111827",
    paper_bgcolor="#111827",
    font=dict(family="Space Mono, monospace", color="#94a3b8", size=11),
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(gridcolor="#1e293b", linecolor="#1e293b"),
    yaxis=dict(gridcolor="#1e293b", linecolor="#1e293b"),
)


def chart_broker_flow(flow_df, top_n=15):
    fig = go.Figure()
    top = flow_df.head(top_n).copy()
    colors = ["#00ff88" if v >= 0 else "#ff3d6e" for v in top["net_flow"]]
    fig.add_trace(go.Bar(
        x=top["broker"].astype(str),
        y=top["net_flow"],
        marker_color=colors,
        name="Net Flow",
    ))
    fig.update_layout(
        **DARK_LAYOUT,
        title=dict(text="BROKER NET FLOW", font=dict(color="#00ff88", size=13)),
        xaxis_title="Broker ID",
        yaxis_title="Net Amount (NPR)",
        height=320,
    )
    return fig


def chart_acf(acf_vals, n_lags=20):
    lags = list(range(1, len(acf_vals) + 1))
    colors = ["#00d4ff" if v >= 0 else "#ff3d6e" for v in acf_vals]
    fig = go.Figure()
    fig.add_hline(y=0, line_color="#334155")
    fig.add_hline(y=0.2, line_dash="dash", line_color="#334155", opacity=0.5)
    fig.add_hline(y=-0.2, line_dash="dash", line_color="#334155", opacity=0.5)
    fig.add_trace(go.Bar(x=lags, y=acf_vals.tolist(), marker_color=colors, name="ACF"))
    fig.update_layout(
        **DARK_LAYOUT,
        title=dict(text="ORDER FLOW AUTOCORRELATION", font=dict(color="#00d4ff", size=13)),
        xaxis_title="Lag",
        yaxis_title="Autocorrelation",
        height=280,
    )
    return fig


def chart_volume_profile(profile_df, poc, vah, val):
    if profile_df.empty:
        return go.Figure()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=profile_df["price"].round(2).astype(str),
        x=profile_df["volume"],
        orientation="h",
        marker_color="#a855f7",
        name="Volume",
    ))
    fig.add_hline(y=str(round(poc, 2)), line_color="#ffb830", line_width=2,
                  annotation_text=f"POC {poc:.0f}", annotation_font_color="#ffb830")
    fig.update_layout(
        **DARK_LAYOUT,
        title=dict(text="VOLUME PROFILE", font=dict(color="#a855f7", size=13)),
        xaxis_title="Volume",
        yaxis_title="Price",
        height=340,
    )
    return fig


def chart_illiquidity(illiq_series):
    if not illiq_series:
        return go.Figure()
    fig = go.Figure()
    x = list(range(len(illiq_series)))
    fig.add_trace(go.Scatter(
        x=x, y=illiq_series,
        fill="tozeroy",
        fillcolor="rgba(255,184,48,0.1)",
        line=dict(color="#ffb830", width=2),
        name="Illiquidity",
    ))
    threshold = np.percentile(illiq_series, 80)
    fig.add_hline(y=threshold, line_dash="dash", line_color="#ff3d6e",
                  annotation_text="80th pctl", annotation_font_color="#ff3d6e")
    fig.update_layout(
        **DARK_LAYOUT,
        title=dict(text="AMIHUD ILLIQUIDITY SPIKES", font=dict(color="#ffb830", size=13)),
        xaxis_title="Time Bucket",
        yaxis_title="Illiquidity",
        height=280,
    )
    return fig


def chart_network(centrality_df):
    if centrality_df.empty:
        return go.Figure()

    top = centrality_df.head(12)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top["broker"].astype(str),
        y=top["strength_norm"],
        marker=dict(
            color=top["strength_norm"],
            colorscale=[[0, "#1e293b"], [0.5, "#00d4ff"], [1.0, "#00ff88"]],
            showscale=False,
        ),
        name="Strength",
    ))
    fig.update_layout(
        **DARK_LAYOUT,
        title=dict(text="BROKER NETWORK CENTRALITY", font=dict(color="#00d4ff", size=13)),
        xaxis_title="Broker ID",
        yaxis_title="Normalized Strength",
        height=280,
    )
    return fig


def chart_cluster_scatter(cluster_df):
    if cluster_df.empty or "cluster_label" not in cluster_df.columns:
        return go.Figure()

    color_map = {"Institutional": "#00ff88", "Retail": "#64748b"}
    fig = go.Figure()

    for label in ["Institutional", "Retail"]:
        subset = cluster_df[cluster_df["cluster_label"] == label]
        if subset.empty:
            continue
        fig.add_trace(go.Scatter(
            x=subset.get("buy_avg_size", pd.Series(dtype=float)),
            y=subset.get("direction_consistency", pd.Series(dtype=float)),
            mode="markers",
            name=label,
            marker=dict(
                color=color_map[label],
                size=10,
                opacity=0.8,
                line=dict(width=1, color="#080c12"),
            ),
            text=subset.index.astype(str),
            hovertemplate="Broker: %{text}<br>Avg Size: %{x:.0f}<br>Direction: %{y:.2f}",
        ))
    fig.update_layout(
        **DARK_LAYOUT,
        title=dict(text="TRADER CLUSTERING", font=dict(color="#a855f7", size=13)),
        xaxis_title="Avg Trade Size",
        yaxis_title="Direction Consistency",
        height=300,
    )
    return fig


# ─────────────────────────────────────────────────────────────
# EXPORT HELPERS
# ─────────────────────────────────────────────────────────────

def df_to_csv_download(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" style="color:#00d4ff;text-decoration:none;font-size:12px;">⬇ Download {filename}</a>'
    return href


# ─────────────────────────────────────────────────────────────
# FULL STOCK ANALYSIS
# ─────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def run_full_analysis(symbol, floorsheet_df, market_row_dict):
    """Run all analysis modules for a symbol"""
    df = floorsheet_df.copy()
    market_row = pd.Series(market_row_dict)

    results = {}

    # Modules
    flow_df = broker_net_flow(df)
    results["flow"] = flow_df

    acf_vals, persistence = acf_analysis(df)
    results["acf_vals"] = acf_vals
    results["persistence"] = persistence

    size_stats, size_dist = trade_size_analysis(df)
    results["size_stats"] = size_stats
    results["size_dist"] = size_dist

    metaorders, suspicion = metaorder_detection(df)
    results["metaorders"] = metaorders
    results["suspicion"] = suspicion

    vol_stats, vol_profile = volume_profile(df)
    results["vol_stats"] = vol_stats
    results["vol_profile"] = vol_profile

    illiq, illiq_series = amihud_illiquidity(df, market_row)
    results["illiq"] = illiq
    results["illiq_series"] = illiq_series

    kyle_lam = kyle_lambda(df)
    results["kyle_lambda"] = kyle_lam

    net_info, centrality_df = network_analysis(df)
    results["net_info"] = net_info
    results["centrality"] = centrality_df

    cluster_df = clustering_analysis(df)
    results["clusters"] = cluster_df

    flags = behavioral_detection(df, flow_df, cluster_df)
    results["flags"] = flags

    sms = smart_money_score(
        flow_df, persistence, size_stats, metaorders,
        net_info, cluster_df, flags, illiq, kyle_lam
    )
    results["sms"] = sms

    return results


# ─────────────────────────────────────────────────────────────
# RENDER STOCK DETAIL
# ─────────────────────────────────────────────────────────────

def render_stock_detail(symbol, results, market_row):
    sms = results["sms"]
    direction = sms["direction"]
    score = sms["score"]
    confidence = sms["confidence"]

    # Direction color
    dir_colors = {
        "Bullish": "#00ff88", "Mild Bullish": "#00ff88",
        "Bearish": "#ff3d6e", "Mild Bearish": "#ff3d6e",
        "Neutral": "#ffb830"
    }
    dir_color = dir_colors.get(direction, "#64748b")

    # Header
    st.markdown(f"""
    <div class="header-banner">
        <div class="header-title">◈ {symbol}</div>
        <div class="header-sub">FULL INSTITUTIONAL INTELLIGENCE REPORT</div>
        <div style="margin-top:12px;display:flex;gap:16px;flex-wrap:wrap;">
            <span style="color:{dir_color};font-size:22px;font-weight:800;font-family:'Syne',sans-serif;">
                Smart Money Score: {score:+.1f}
            </span>
            <span style="color:#64748b;font-size:14px;line-height:32px;">Confidence: {confidence}%</span>
            <span style="color:{dir_color};font-size:14px;line-height:32px;">{sms['interpretation']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Market snapshot
    col1, col2, col3, col4, col5 = st.columns(5)
    metrics = [
        ("LTP", f"NPR {market_row['close']:,.1f}", col1),
        ("Change", f"{market_row['pct_change']:+.2f}%", col2),
        ("Volume", f"{market_row['volume']:,}", col3),
        ("Turnover", f"NPR {market_row['turnover']/1e6:.1f}M", col4),
        ("Vol Ratio", f"{market_row['vol_ratio']:.2f}x", col5),
    ]
    for label, val, col in metrics:
        with col:
            color = "#00ff88" if "+" in str(val) or float(str(val).replace("NPR","").replace(",","").replace("%","").replace("x","").replace("M","").strip().split("+")[-1].split("-")[0]) >= 0 else "#ff3d6e"
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value" style="font-size:18px;color:{color};">{val}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 FLOW & ACF", "📐 VOLUME PROFILE", "💧 LIQUIDITY",
        "🕸 NETWORK", "🧠 BEHAVIORAL"
    ])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(chart_broker_flow(results["flow"]), use_container_width=True, key=f"flow_{symbol}")
        with c2:
            st.plotly_chart(chart_acf(results["acf_vals"]), use_container_width=True, key=f"acf_{symbol}")

        # Metaorders
        st.markdown("#### 🔍 METAORDER DETECTION")
        sus_level = results["suspicion"]
        sus_color = {"HIGH": "#ff3d6e", "MODERATE": "#ffb830", "LOW": "#64748b"}[sus_level]
        st.markdown(f'<span class="score-badge" style="background:rgba(0,0,0,0.3);color:{sus_color};border:1px solid {sus_color};">SUSPICION: {sus_level}</span>', unsafe_allow_html=True)

        if results["metaorders"]:
            meta_df = pd.DataFrame(results["metaorders"])
            st.dataframe(meta_df, use_container_width=True, hide_index=True)
        else:
            st.info("No significant metaorders detected")

        # Trade size
        st.markdown("#### 📏 TRADE SIZE ANALYSIS")
        ss = results["size_stats"]
        if isinstance(ss, dict) and ss:
            cols = st.columns(4)
            with cols[0]: st.metric("Large Trade %", f"{ss.get('large_pct',0):.1f}%")
            with cols[1]: st.metric("Inst. Volume %", f"{ss.get('inst_volume_pct',0):.1f}%")
            with cols[2]: st.metric("P90 Size", f"{ss.get('p90',0):,.0f}")
            with cols[3]: st.metric("Median Size", f"{ss.get('median',0):,.0f}")

    with tab2:
        vs = results["vol_stats"]
        vp = results["vol_profile"]

        if vs and not vp.empty:
            col1, col2, col3 = st.columns(3)
            col1.metric("POC (Point of Control)", f"NPR {vs.get('poc',0):,.1f}")
            col2.metric("Value Area High", f"NPR {vs.get('vah',0):,.1f}")
            col3.metric("Value Area Low", f"NPR {vs.get('val',0):,.1f}")
            st.plotly_chart(chart_volume_profile(vp, vs["poc"], vs["vah"], vs["val"]),
                           use_container_width=True, key=f"vp_{symbol}")
        else:
            st.info("Insufficient data for volume profile")

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 💧 AMIHUD ILLIQUIDITY")
            avg_illiq = results["illiq"]
            st.metric("Average Illiquidity", f"{avg_illiq:.6f}")
            if results["illiq_series"]:
                st.plotly_chart(chart_illiquidity(results["illiq_series"]),
                               use_container_width=True, key=f"illiq_{symbol}")
        with col2:
            st.markdown("#### ⚡ KYLE'S LAMBDA")
            kl = results["kyle_lambda"]
            kl_color = "#ff3d6e" if kl > 0 else "#00ff88"
            st.markdown(f"""
            <div class="metric-box" style="margin-top:20px;">
                <div class="metric-value" style="color:{kl_color};">{kl:.6f}</div>
                <div class="metric-label">Price Impact per Unit Volume</div>
            </div>""", unsafe_allow_html=True)
            st.markdown("""
            <div style="margin-top:16px;color:#64748b;font-size:11px;line-height:1.8;">
            Kyle's λ measures price impact per unit of signed volume.<br>
            Higher values → greater market impact → lower liquidity.
            </div>""", unsafe_allow_html=True)

    with tab4:
        ni = results["net_info"]
        cd = results["centrality"]

        if ni:
            col1, col2, col3 = st.columns(3)
            col1.metric("Top Broker", f"#{ni.get('top_broker',0)}")
            col2.metric("Top-3 Concentration", f"{ni.get('concentration',0)*100:.0f}%")
            col3.metric("Active Brokers", ni.get("n_active", 0))

        if not cd.empty:
            st.plotly_chart(chart_network(cd), use_container_width=True, key=f"net_{symbol}")
            st.dataframe(cd[["broker","strength","degree","strength_norm"]].head(10),
                        use_container_width=True, hide_index=True)

        # Clustering
        st.markdown("#### 🎯 TRADER CLUSTERING")
        clusters = results["clusters"]
        if isinstance(clusters, pd.DataFrame) and "cluster_label" in clusters.columns:
            st.plotly_chart(chart_cluster_scatter(clusters), use_container_width=True, key=f"clust_{symbol}")
            inst = clusters[clusters["cluster_label"] == "Institutional"]
            st.markdown(f"**{len(inst)} Institutional-classified traders** detected")

    with tab5:
        flags = results["flags"]
        st.markdown("#### 🚨 BEHAVIORAL FLAGS")

        if flags:
            for flag in flags:
                flag_name = flag["flag"]
                detail = flag["detail"]
                flag_colors = {
                    "Stealth Accumulation": "#00ff88",
                    "Institutional Distribution": "#ff3d6e",
                    "Coordinated Activity": "#ffb830",
                    "Obfuscation Pattern": "#a855f7",
                    "Possible Informed Trading": "#00d4ff",
                }
                color = flag_colors.get(flag_name, "#64748b")
                st.markdown(f"""
                <div class="intel-card" style="border-left-color:{color};">
                    <div style="color:{color};font-weight:700;font-size:13px;">◆ {flag_name}</div>
                    <div style="color:#94a3b8;font-size:12px;margin-top:6px;">{detail}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No significant behavioral anomalies detected")

        # Score breakdown
        st.markdown("#### 📊 SCORE COMPONENTS")
        components = sms["components"]
        if components:
            comp_df = pd.DataFrame(
                [(k, v) for k, v in components.items()],
                columns=["Component", "Score"]
            )
            fig_comp = go.Figure(go.Bar(
                x=comp_df["Component"],
                y=comp_df["Score"],
                marker_color=["#00ff88" if v >= 0 else "#ff3d6e" for v in comp_df["Score"]],
            ))
            fig_comp.update_layout(
                **DARK_LAYOUT,
                title=dict(text="SMART MONEY SCORE BREAKDOWN", font=dict(color="#e2e8f0", size=13)),
                height=260,
            )
            st.plotly_chart(fig_comp, use_container_width=True, key=f"score_{symbol}")

    # Exports
    st.markdown("---")
    st.markdown("#### ⬇ EXPORT DATA")
    col1, col2, col3 = st.columns(3)
    with col1:
        if not results["flow"].empty:
            st.markdown(df_to_csv_download(results["flow"], f"{symbol}_broker_flow.csv"), unsafe_allow_html=True)
    with col2:
        if results["metaorders"]:
            st.markdown(df_to_csv_download(pd.DataFrame(results["metaorders"]), f"{symbol}_metaorders.csv"), unsafe_allow_html=True)
    with col3:
        if isinstance(results["clusters"], pd.DataFrame) and len(results["clusters"]) > 0:
            export_df = results["clusters"].reset_index()
            if "broker" not in export_df.columns and "index" in export_df.columns:
                export_df.rename(columns={"index": "broker"}, inplace=True)
            st.markdown(df_to_csv_download(export_df, f"{symbol}_clusters.csv"), unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────

def main():
    # ── SIDEBAR ──────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style="padding:16px 0 8px 0;">
            <div style="font-family:'Syne',sans-serif;font-size:16px;font-weight:800;color:#00ff88;letter-spacing:2px;">
                NEPSE INTELLIGENCE
            </div>
            <div style="font-size:10px;color:#334155;letter-spacing:2px;margin-top:4px;">
                INSTITUTIONAL DETECTION
            </div>
        </div>
        <hr style="border-color:#1e293b;margin:12px 0;">
        """, unsafe_allow_html=True)

        st.markdown("#### 📡 DATA SOURCE")
        data_mode = st.radio(
            "Market Data",
            ["Simulated (Auto)", "Upload Excel"],
            label_visibility="collapsed"
        )

        uploaded_market = None
        uploaded_floor = None

        if data_mode == "Upload Excel":
            uploaded_market = st.file_uploader("Market Data (.xlsx/.csv)", type=["xlsx", "xls", "csv"], key="mkt")
            st.markdown("---")

        st.markdown("#### 📄 FLOORSHEET DATA")
        floor_mode = st.radio(
            "Floorsheet",
            ["Auto-Generate", "Upload Excel"],
            label_visibility="collapsed"
        )

        if floor_mode == "Upload Excel":
            uploaded_floor = st.file_uploader("Floorsheet (.xlsx/.csv)", type=["xlsx", "xls", "csv"], key="floor")

        st.markdown("---")
        st.markdown("#### ⚙️ SETTINGS")
        n_stocks = st.slider("Top Stocks to Analyze", 3, 10, 6)
        n_trades = st.slider("Trades per Simulation", 100, 500, 200, 50)

        st.markdown("---")
        refresh = st.button("🔄 REFRESH ANALYSIS", use_container_width=True)

        st.markdown("""
        <div style="margin-top:24px;padding:12px;background:#0d1420;border:1px solid #1e293b;border-radius:6px;">
            <div style="font-size:10px;color:#334155;line-height:1.8;">
                ◆ Amihud Illiquidity<br>
                ◆ Kyle's Lambda<br>
                ◆ Order Flow ACF<br>
                ◆ Network Centrality<br>
                ◆ Trader Clustering<br>
                ◆ Metaorder Detection<br>
                ◆ Behavioral Analysis
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── MAIN CONTENT ─────────────────────────────────────────

    # Header
    st.markdown("""
    <div class="header-banner">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
            <div>
                <div class="header-title">NEPSE FLOORSHEET INTELLIGENCE</div>
                <div class="header-sub">INSTITUTIONAL DETECTION SYSTEM — SMART MONEY ANALYTICS ENGINE</div>
            </div>
            <div style="text-align:right;">
                <span class="status-pill status-sim">● SIMULATION MODE</span>
                <div style="font-size:10px;color:#334155;margin-top:4px;">""" +
                datetime.now().strftime("%Y-%m-%d %H:%M") + """</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── LOAD MARKET DATA ─────────────────────────────────────
    global_warnings = []

    if data_mode == "Upload Excel" and uploaded_market is not None:
        try:
            if uploaded_market.name.endswith(".csv"):
                raw_df = pd.read_csv(uploaded_market)
            else:
                raw_df = pd.read_excel(uploaded_market)
            market_df = normalize_market_data(raw_df)
            if "symbol" not in market_df.columns:
                market_df["symbol"] = [f"STK{i}" for i in range(len(market_df))]
            for col in ["volume", "turnover", "close", "open", "pct_change"]:
                if col not in market_df.columns:
                    market_df[col] = 0
            market_df["vol_ratio"] = 1.0
            market_df["avg_volume"] = market_df["volume"]
            st.success(f"✓ Market data loaded: {len(market_df)} symbols")
        except Exception as e:
            st.warning(f"Market data load failed: {e}. Using simulation.")
            market_df = generate_market_data()
    else:
        market_df = generate_market_data()

    # Rank stocks
    top_stocks = rank_stocks(market_df, top_n=n_stocks)

    # ── MARKET SUMMARY ───────────────────────────────────────
    st.markdown("### 📊 MARKET OVERVIEW")

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.markdown(f"""<div class="metric-box">
            <div class="metric-value">{len(market_df)}</div>
            <div class="metric-label">Traded Symbols</div>
        </div>""", unsafe_allow_html=True)
    with col_m2:
        gainers = (market_df["pct_change"] > 0).sum()
        st.markdown(f"""<div class="metric-box">
            <div class="metric-value" style="color:#00ff88;">{gainers}</div>
            <div class="metric-label">Gainers</div>
        </div>""", unsafe_allow_html=True)
    with col_m3:
        losers = (market_df["pct_change"] < 0).sum()
        st.markdown(f"""<div class="metric-box">
            <div class="metric-value" style="color:#ff3d6e;">{losers}</div>
            <div class="metric-label">Losers</div>
        </div>""", unsafe_allow_html=True)
    with col_m4:
        total_turn = market_df["turnover"].sum()
        st.markdown(f"""<div class="metric-box">
            <div class="metric-value" style="font-size:20px;">NPR {total_turn/1e9:.1f}B</div>
            <div class="metric-label">Total Turnover</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Bull/Bear split
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("##### 🟢 TOP GAINERS")
        top_gain = market_df.nlargest(5, "pct_change")[["symbol", "close", "pct_change", "volume"]]
        st.dataframe(
            top_gain.style.format({"close": "{:.1f}", "pct_change": "{:+.2f}%", "volume": "{:,}"}),
            use_container_width=True, hide_index=True
        )
    with col_b:
        st.markdown("##### 🔴 TOP LOSERS")
        top_lose = market_df.nsmallest(5, "pct_change")[["symbol", "close", "pct_change", "volume"]]
        st.dataframe(
            top_lose.style.format({"close": "{:.1f}", "pct_change": "{:+.2f}%", "volume": "{:,}"}),
            use_container_width=True, hide_index=True
        )

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── RUN ANALYSIS ON TOP STOCKS ───────────────────────────
    st.markdown("### 🎯 TOP OPPORTUNITY STOCKS — FULL ANALYSIS")

    all_scores = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    floor_data_map = {}

    # Load or generate floorsheets
    if floor_mode == "Upload Excel" and uploaded_floor is not None:
        try:
            if uploaded_floor.name.endswith(".csv"):
                raw_floor = pd.read_csv(uploaded_floor)
            else:
                raw_floor = pd.read_excel(uploaded_floor)

            floor_norm, floor_warnings = normalize_floorsheet(raw_floor)

            for w in floor_warnings:
                global_warnings.append(w)

            # Show column mapping UI if needed
            if floor_warnings:
                with st.expander("⚠️ Column Mapping Warnings", expanded=False):
                    for w in floor_warnings:
                        st.warning(w)

            # Split by symbol if multiple
            if "symbol" in floor_norm.columns:
                for sym in floor_norm["symbol"].unique():
                    floor_data_map[sym] = floor_norm[floor_norm["symbol"] == sym].copy()
            else:
                # Apply to all top stocks
                for sym in top_stocks["symbol"]:
                    floor_data_map[sym] = floor_norm.copy()

            st.success(f"✓ Floorsheet loaded: {len(floor_norm)} trades, {len(floor_data_map)} symbols")
        except Exception as e:
            st.warning(f"Floorsheet load failed: {e}. Auto-generating.")
            for sym in top_stocks["symbol"]:
                floor_data_map[sym] = generate_floorsheet(sym, n_trades)
    else:
        for sym in top_stocks["symbol"]:
            floor_data_map[sym] = generate_floorsheet(sym, n_trades)

    # Run analysis
    results_map = {}
    for i, row in top_stocks.iterrows():
        sym = row["symbol"]
        progress_bar.progress((i + 1) / len(top_stocks))
        status_text.text(f"Analyzing {sym}...")

        fs = floor_data_map.get(sym, generate_floorsheet(sym, n_trades))

        # Ensure sn column
        if "sn" not in fs.columns:
            fs = fs.reset_index()
            fs.rename(columns={"index": "sn"}, inplace=True)

        market_row_dict = row.to_dict()

        try:
            res = run_full_analysis(sym, fs, market_row_dict)
            results_map[sym] = res
            sms = res["sms"]
            all_scores.append({
                "symbol": sym,
                "close": row["close"],
                "pct_change": row["pct_change"],
                "volume": row["volume"],
                "vol_ratio": row["vol_ratio"],
                "smart_money_score": sms["score"],
                "confidence": sms["confidence"],
                "direction": sms["direction"],
                "flags": ", ".join(f["flag"] for f in res["flags"]) if res["flags"] else "—",
                "suspicion": res["suspicion"],
            })
        except Exception as e:
            st.warning(f"Analysis failed for {sym}: {e}")

    progress_bar.empty()
    status_text.empty()

    # ── SMART MONEY SCORE TABLE ───────────────────────────────
    if all_scores:
        st.markdown("#### 📋 SMART MONEY SCORE DASHBOARD")
        score_df = pd.DataFrame(all_scores)

        def color_score(val):
            if val >= 4: return "color: #00ff88; font-weight: bold"
            elif val >= 1.5: return "color: #7fcc99"
            elif val <= -4: return "color: #ff3d6e; font-weight: bold"
            elif val <= -1.5: return "color: #cc8888"
            return "color: #ffb830"

        def color_dir(val):
            if "Bullish" in str(val): return "color: #00ff88"
            elif "Bearish" in str(val): return "color: #ff3d6e"
            return "color: #ffb830"

        styled = score_df.style\
            .applymap(color_score, subset=["smart_money_score"])\
            .applymap(color_dir, subset=["direction"])\
            .format({
                "close": "{:.1f}",
                "pct_change": "{:+.2f}%",
                "volume": "{:,}",
                "vol_ratio": "{:.2f}x",
                "smart_money_score": "{:+.2f}",
                "confidence": "{}%",
            })

        st.dataframe(styled, use_container_width=True, hide_index=True)
        st.markdown(df_to_csv_download(score_df, "smart_money_scores.csv"), unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── STOCK DRILL-DOWN ──────────────────────────────────────
    st.markdown("### 🔬 STOCK DRILL-DOWN ANALYSIS")

    if results_map:
        selected = st.selectbox(
            "Select stock for detailed analysis:",
            options=list(results_map.keys()),
            format_func=lambda s: f"{s}  (SMS: {results_map[s]['sms']['score']:+.1f}  |  {results_map[s]['sms']['direction']})"
        )

        if selected:
            sel_row = top_stocks[top_stocks["symbol"] == selected].iloc[0]
            render_stock_detail(selected, results_map[selected], sel_row)


if __name__ == "__main__":
    main()
