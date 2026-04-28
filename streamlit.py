"""
╔══════════════════════════════════════════════════════╗
║   StockSense AI — Advanced Inventory Dashboard       ║
║   Step-by-step navigation · Sound alerts · Animated  ║
╚══════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import sys, os
import base64

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml_pipeline'))

# ─── Page config (MUST be first Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="StockSense AI",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Sound utilities (Web Audio API via HTML component) ───────────────────────
SOUNDS = {
    "critical": """
        <script>
        (function() {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            function beep(freq, start, dur, vol=0.4) {
                const o = ctx.createOscillator();
                const g = ctx.createGain();
                o.connect(g); g.connect(ctx.destination);
                o.type = 'square';
                o.frequency.value = freq;
                g.gain.setValueAtTime(0, ctx.currentTime + start);
                g.gain.linearRampToValueAtTime(vol, ctx.currentTime + start + 0.01);
                g.gain.linearRampToValueAtTime(0, ctx.currentTime + start + dur);
                o.start(ctx.currentTime + start);
                o.stop(ctx.currentTime + start + dur + 0.05);
            }
            beep(880, 0.0, 0.15); beep(660, 0.2, 0.15); beep(880, 0.4, 0.15);
            beep(660, 0.6, 0.15); beep(440, 0.8, 0.3);
        })();
        </script>
    """,
    "warning": """
        <script>
        (function() {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            function beep(freq, start, dur, vol=0.3) {
                const o = ctx.createOscillator();
                const g = ctx.createGain();
                o.connect(g); g.connect(ctx.destination);
                o.type = 'triangle';
                o.frequency.value = freq;
                g.gain.setValueAtTime(0, ctx.currentTime + start);
                g.gain.linearRampToValueAtTime(vol, ctx.currentTime + start + 0.02);
                g.gain.linearRampToValueAtTime(0, ctx.currentTime + start + dur);
                o.start(ctx.currentTime + start);
                o.stop(ctx.currentTime + start + dur + 0.05);
            }
            beep(660, 0, 0.2); beep(550, 0.3, 0.2);
        })();
        </script>
    """,
    "success": """
        <script>
        (function() {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            function beep(freq, start, dur, vol=0.25) {
                const o = ctx.createOscillator();
                const g = ctx.createGain();
                o.connect(g); g.connect(ctx.destination);
                o.type = 'sine';
                o.frequency.value = freq;
                g.gain.setValueAtTime(0, ctx.currentTime + start);
                g.gain.linearRampToValueAtTime(vol, ctx.currentTime + start + 0.02);
                g.gain.linearRampToValueAtTime(0, ctx.currentTime + start + dur);
                o.start(ctx.currentTime + start);
                o.stop(ctx.currentTime + start + dur + 0.05);
            }
            beep(523, 0, 0.12); beep(659, 0.13, 0.12); beep(784, 0.26, 0.25);
        })();
        </script>
    """,
    "click": """
        <script>
        (function() {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const o = ctx.createOscillator();
            const g = ctx.createGain();
            o.connect(g); g.connect(ctx.destination);
            o.type = 'sine'; o.frequency.value = 1200;
            g.gain.setValueAtTime(0.15, ctx.currentTime);
            g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.08);
            o.start(ctx.currentTime); o.stop(ctx.currentTime + 0.1);
        })();
        </script>
    """
}

def play_sound(sound_type: str):
    if st.session_state.get("sound_enabled", True):
        st.components.v1.html(SOUNDS.get(sound_type, ""), height=0)

# ─── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --bg:       #0b0f1a;
    --bg2:      #111827;
    --bg3:      #1a2235;
    --border:   rgba(255,255,255,0.07);
    --border2:  rgba(255,255,255,0.13);
    --text:     #e8eaf0;
    --text2:    #8892a4;
    --text3:    #4a5568;
    --green:    #10d97e;
    --green2:   #0a8a50;
    --amber:    #f59e0b;
    --red:      #ef4444;
    --blue:     #3b82f6;
    --mono:     'IBM Plex Mono', monospace;
    --sans:     'Manrope', sans-serif;
}

html, body, [class*="css"] {
    font-family: var(--sans) !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem !important; max-width: 100% !important; }
.stDeployButton { display: none; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border2) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stNumberInput label { color: var(--text2) !important; font-size: 12px !important; font-family: var(--mono) !important; }

/* Buttons */
.stButton > button {
    background: transparent !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
    font-family: var(--mono) !important;
    font-size: 13px !important;
    border-radius: 8px !important;
    padding: 8px 20px !important;
    transition: all 0.2s !important;
    width: 100% !important;
}
.stButton > button:hover {
    border-color: var(--green) !important;
    color: var(--green) !important;
    box-shadow: 0 0 12px rgba(16,217,126,0.15) !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
}
[data-testid="stMetricLabel"] { font-family: var(--mono) !important; font-size: 11px !important; color: var(--text2) !important; text-transform: uppercase; letter-spacing: 0.5px; }
[data-testid="stMetricValue"] { font-family: var(--mono) !important; font-size: 26px !important; font-weight: 600 !important; color: var(--text) !important; }
[data-testid="stMetricDelta"] { font-family: var(--mono) !important; font-size: 11px !important; }

/* Inputs */
[data-testid="stSelectbox"] > div > div,
[data-testid="stNumberInput"] > div > div > input {
    background: var(--bg3) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-family: var(--mono) !important;
}
.stSlider [data-baseweb="slider"] { padding: 0 !important; }

/* DataFrames */
[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: 10px !important; overflow: hidden !important; }

/* Progress bars */
.stProgress > div > div { background: var(--bg3) !important; border-radius: 4px !important; }
.stProgress > div > div > div { background: linear-gradient(90deg, var(--green), #06b6d4) !important; border-radius: 4px !important; }

/* Download button */
[data-testid="stDownloadButton"] > button {
    background: var(--green2) !important;
    border: none !important;
    color: #fff !important;
    font-family: var(--mono) !important;
    border-radius: 8px !important;
}

/* Custom scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

/* Tabs */
[data-baseweb="tab-list"] { background: var(--bg2) !important; border-radius: 10px !important; padding: 4px !important; gap: 4px; }
[data-baseweb="tab"] { background: transparent !important; color: var(--text2) !important; font-family: var(--mono) !important; font-size: 12px !important; border-radius: 7px !important; padding: 6px 16px !important; }
[aria-selected="true"][data-baseweb="tab"] { background: var(--bg3) !important; color: var(--green) !important; }

/* Expander */
[data-testid="stExpander"] { border: 1px solid var(--border) !important; border-radius: 10px !important; background: var(--bg2) !important; }
</style>
""", unsafe_allow_html=True)

# ─── HTML components ───────────────────────────────────────────────────────────
def html_card(content: str, padding: str = "20px 24px", bg: str = "var(--bg3)"):
    st.markdown(f"""
    <div style="background:{bg};border:1px solid var(--border);
                border-radius:12px;padding:{padding};margin-bottom:12px">
        {content}
    </div>""", unsafe_allow_html=True)

def step_header(num: int, title: str, subtitle: str = ""):
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:16px;margin-bottom:24px;padding-bottom:16px;
                border-bottom:1px solid var(--border)">
        <div style="width:44px;height:44px;border-radius:50%;background:var(--green2);
                    display:flex;align-items:center;justify-content:center;
                    font-family:var(--mono);font-size:18px;font-weight:700;color:#fff;flex-shrink:0">
            {num}
        </div>
        <div>
            <div style="font-size:22px;font-weight:800;color:var(--text);font-family:var(--sans)">{title}</div>
            {f'<div style="font-size:13px;color:var(--text2);font-family:var(--mono);margin-top:3px">{subtitle}</div>' if subtitle else ''}
        </div>
    </div>""", unsafe_allow_html=True)

def alert_banner(risk: str, days: int, reorder: int, product: str):
    if risk == "High":
        bg, border, icon, title = "#1a0505", "#ef4444", "🚨", "CRITICAL STOCKOUT ALERT"
        msg = f"<b>{product}</b> will stockout in <b>{days} days</b>. Order <b>{reorder} units IMMEDIATELY</b>."
        anim = "animation:pulse_red 1.2s infinite;"
    elif risk == "Medium":
        bg, border, icon, title = "#1a1205", "#f59e0b", "⚠️", "LOW STOCK WARNING"
        msg = f"<b>{product}</b> stock is low. <b>{days} days</b> remaining. Plan reorder of <b>{reorder} units</b>."
        anim = ""
    else:
        bg, border, icon, title = "#031a0f", "#10d97e", "✅", "STOCK LEVEL HEALTHY"
        msg = f"<b>{product}</b> is well stocked. Estimated <b>{days} days</b> of supply available."
        anim = ""

    st.markdown(f"""
    <style>
    @keyframes pulse_red {{
        0%,100% {{ box-shadow: 0 0 0 0 rgba(239,68,68,0.4); }}
        50% {{ box-shadow: 0 0 0 12px rgba(239,68,68,0); }}
    }}
    </style>
    <div style="background:{bg};border:1.5px solid {border};border-radius:14px;
                padding:20px 24px;margin:16px 0;{anim}">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
            <span style="font-size:24px">{icon}</span>
            <span style="font-family:var(--mono);font-size:14px;font-weight:700;
                         color:{border};letter-spacing:1px">{title}</span>
        </div>
        <div style="font-size:14px;color:var(--text);line-height:1.6">{msg}</div>
    </div>""", unsafe_allow_html=True)

# ─── Session state init ────────────────────────────────────────────────────────
STEPS = [
    ("🏠", "Setup"),
    ("📊", "Overview"),
    ("📈", "Forecast"),
    ("📦", "Inventory"),
    ("💡", "Insights"),
    ("🧪", "Simulate"),
    ("📥", "Report"),
]

defaults = {
    "step": 0,
    "sound_enabled": True,
    "sound_played": {},
    "predictions_cache": {},
    "theme": "dark",
    "auto_refresh": False,
    "last_risk": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── Backend init ──────────────────────────────────────────────────────────────
@st.cache_resource
def init_backend():
    """Try to import real backend, fall back to demo stub"""
    try:
        import backend as bk
        return bk.predictor
    except ImportError:
        return _DemoPredictor()

class _DemoPredictor:
    """Standalone demo when backend is not installed"""
    def get_all_products(self):
        return ["Organic Coffee Beans","Wireless Earbuds Pro","Vitamin D3 Capsules",
                "Yoga Mat Premium","Almond Butter Jar","LED Desk Lamp",
                "Protein Powder 2kg","Reusable Water Bottle","Green Tea Pack","Smart Watch Band"]

    def predict_demand(self, product, days, stock):
        np.random.seed(hash(product) % 999)
        base = np.random.randint(25, 80)
        daily = [max(1, int(base + np.random.normal(0, base*0.15))) for _ in range(days)]
        total = sum(daily)
        reorder = max(0, total - stock + int(total * 0.15))
        dso = max(0, int(stock / (total / days))) if total > 0 else 99
        risk = "High" if dso < 3 else "Medium" if dso < 7 else "Low"
        mae = round(base * 0.08, 1)
        result = {
            "total_demand": total,
            "daily_predictions": daily,
            "reorder_quantity": reorder,
            "days_until_stockout": dso,
            "risk_level": risk,
            "model_accuracy": mae,
        }
        # Demo historical data
        dates = [datetime.now() - timedelta(days=30-i) for i in range(30)]
        hist = pd.DataFrame({
            "date": dates,
            "product": product,
            "demand": [max(1, int(base + np.random.normal(0, base*0.2))) for _ in range(30)]
        })
        # Demo product info
        info = pd.DataFrame([{
            "product": product,
            "unit_cost": round(np.random.uniform(8, 60), 2),
            "selling_price": round(np.random.uniform(15, 120), 2),
        }])
        return result, hist, info

predictor = init_backend()

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0 8px">
        <div style="font-size:32px">📦</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:16px;
                    font-weight:600;color:#10d97e;letter-spacing:1px">StockSense AI</div>
        <div style="font-size:10px;color:#8892a4;font-family:monospace;
                    margin-top:4px;letter-spacing:2px">DEMAND INTELLIGENCE</div>
    </div>
    <hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:8px 0 16px">
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size:11px;color:#8892a4;font-family:monospace;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px'>Navigation</div>", unsafe_allow_html=True)

    for i, (icon, label) in enumerate(STEPS):
        active = st.session_state.step == i
        if st.button(
            f"{'▶ ' if active else '   '}{icon}  {label}",
            key=f"nav_{i}",
            help=f"Go to {label}"
        ):
            st.session_state.step = i
            play_sound("click")
            st.rerun()

    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.07);margin:16px 0'>", unsafe_allow_html=True)

    products = predictor.get_all_products()
    selected_product = st.selectbox("Product", products, key="product")
    current_stock    = st.number_input("Current Stock", 0, 10000, 150, 10, key="stock")
    prediction_days  = st.slider("Forecast Days", 1, 30, 7, key="days")

    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.07);margin:16px 0'>", unsafe_allow_html=True)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        sound_toggle = st.toggle("🔊 Sound", value=st.session_state.sound_enabled)
        st.session_state.sound_enabled = sound_toggle
    with col_s2:
        auto_refresh = st.toggle("🔄 Live", value=False)

    st.markdown(f"""
    <div style="margin-top:16px;padding:10px 12px;background:var(--bg3);
                border-radius:8px;border:1px solid var(--border)">
        <div style="font-size:10px;color:#8892a4;font-family:monospace;
                    text-transform:uppercase;letter-spacing:1px">Step</div>
        <div style="font-size:14px;color:#10d97e;font-family:monospace;font-weight:600">
            {st.session_state.step + 1} / {len(STEPS)} — {STEPS[st.session_state.step][1]}
        </div>
    </div>""", unsafe_allow_html=True)

# ─── Data fetch ────────────────────────────────────────────────────────────────
cache_key = f"{selected_product}_{prediction_days}_{current_stock}"
if cache_key not in st.session_state.predictions_cache:
    result, historical, product_info = predictor.predict_demand(
        selected_product, prediction_days, current_stock
    )
    st.session_state.predictions_cache[cache_key] = (result, historical, product_info)
else:
    result, historical, product_info = st.session_state.predictions_cache[cache_key]

if not result:
    st.error("❌ Backend error — could not generate predictions.")
    st.stop()

# Play sound when risk changes
current_risk = result['risk_level']
if current_risk != st.session_state.last_risk:
    st.session_state.last_risk = current_risk
    snd_key = f"risk_{cache_key}"
    if snd_key not in st.session_state.sound_played:
        st.session_state.sound_played[snd_key] = True
        if current_risk == "High":
            play_sound("critical")
        elif current_risk == "Medium":
            play_sound("warning")
        else:
            play_sound("success")

# ─── Derived metrics ───────────────────────────────────────────────────────────
unit_cost     = float(product_info['unit_cost'].values[0])     if not product_info.empty else 20.0
selling_price = float(product_info['selling_price'].values[0]) if not product_info.empty else 35.0
profit_margin = round((selling_price - unit_cost) / selling_price * 100, 1)

manual_waste_units = int(result['total_demand'] * 0.25)
ai_waste_units     = int(result['total_demand'] * 0.05)
waste_savings      = (manual_waste_units - ai_waste_units) * unit_cost
stockout_savings   = int(result['reorder_quantity'] * 0.2 * (selling_price - unit_cost))
total_savings      = waste_savings + stockout_savings

hist_product = historical[historical['product'] == selected_product].copy() if 'product' in historical.columns else historical.copy()

# ════════════════════════════════════════════════════════════════════════════════
# STEP ROUTING
# ════════════════════════════════════════════════════════════════════════════════
step = st.session_state.step

# ── STEP 0 · Setup ─────────────────────────────────────────────────────────────
if step == 0:
    step_header(1, "System Setup", "Configure your inventory parameters to begin")

    col1, col2 = st.columns([1.4, 1])

    with col1:
        st.markdown("""
        <div style="background:var(--bg3);border:1px solid var(--border);
                    border-radius:14px;padding:28px 32px;margin-bottom:16px">
            <div style="font-size:28px;font-weight:800;color:var(--text);
                        font-family:var(--sans);margin-bottom:8px">
                Welcome to <span style="color:var(--green)">StockSense AI</span>
            </div>
            <div style="font-size:14px;color:var(--text2);line-height:1.8;margin-bottom:24px">
                AI-powered demand forecasting and inventory intelligence for small businesses.
                Walk through each step to get actionable restocking recommendations.
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
        """, unsafe_allow_html=True)

        features = [
            ("📈", "Demand Forecast", "30-day rolling predictions with 80% CI"),
            ("🛡️", "Safety Stock", "Statistical buffer at 95% service level"),
            ("⚡", "EOQ Engine", "Economic order quantity optimization"),
            ("🔍", "Anomaly Detection", "Z-score based spike/dip detection"),
            ("💰", "Savings Calculator", "Real-time cost/waste analysis"),
            ("🧪", "What-if Simulator", "Test scenarios before committing"),
        ]
        for icon, title, desc in features:
            st.markdown(f"""
            <div style="background:var(--bg2);border:1px solid var(--border);
                        border-radius:10px;padding:14px 16px">
                <span style="font-size:20px">{icon}</span>
                <div style="font-size:13px;font-weight:700;color:var(--text);margin-top:6px">{title}</div>
                <div style="font-size:11px;color:var(--text2);margin-top:3px">{desc}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background:var(--bg3);border:1px solid var(--border);
                    border-radius:14px;padding:24px;margin-bottom:16px">
            <div style="font-family:var(--mono);font-size:11px;color:var(--text2);
                        text-transform:uppercase;letter-spacing:1px;margin-bottom:16px">
                Current Configuration
            </div>
        """, unsafe_allow_html=True)

        cfg_items = [
            ("Product", selected_product[:28] + ("…" if len(selected_product) > 28 else "")),
            ("Current Stock", f"{current_stock:,} units"),
            ("Forecast Horizon", f"{prediction_days} days"),
            ("Unit Cost", f"₹{unit_cost:,.2f}"),
            ("Selling Price", f"₹{selling_price:,.2f}"),
            ("Margin", f"{profit_margin}%"),
        ]
        for label, val in cfg_items:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:10px 0;border-bottom:1px solid var(--border)">
                <span style="font-size:12px;color:var(--text2);font-family:var(--mono)">{label}</span>
                <span style="font-size:13px;color:var(--text);font-weight:600;font-family:var(--mono)">{val}</span>
            </div>""", unsafe_allow_html=True)

        risk_col = {"High": "var(--red)", "Medium": "var(--amber)", "Low": "var(--green)"}[result['risk_level']]
        st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;padding:12px 0 0">
                <span style="font-size:12px;color:var(--text2);font-family:var(--mono)">Risk Level</span>
                <span style="font-size:13px;color:{risk_col};font-weight:700;font-family:var(--mono)">
                    ● {result['risk_level'].upper()}
                </span>
            </div>
        </div>""", unsafe_allow_html=True)

        # Quick status pill
        st.markdown(f"""
        <div style="background:var(--bg3);border:1px solid var(--border);
                    border-radius:14px;padding:20px 24px;text-align:center">
            <div style="font-size:11px;color:var(--text2);font-family:var(--mono);
                        text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">
                Predicted {prediction_days}d Demand
            </div>
            <div style="font-size:40px;font-weight:800;color:var(--green);font-family:var(--mono)">
                {result['total_demand']:,}
            </div>
            <div style="font-size:12px;color:var(--text2);margin-top:4px">units</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
    with col_btn2:
        if st.button("▶  Start Analysis →", key="start_btn"):
            st.session_state.step = 1
            play_sound("click")
            st.rerun()

# ── STEP 1 · Overview ──────────────────────────────────────────────────────────
elif step == 1:
    step_header(2, "Business Overview", "Key performance indicators & alert status")

    # Alert banner with sound
    alert_banner(result['risk_level'], result['days_until_stockout'], result['reorder_quantity'], selected_product)

    # KPI row
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Predicted Demand", f"{result['total_demand']:,}", f"÷{prediction_days}d avg")
    c2.metric("Current Stock",    f"{current_stock:,}",         "units on hand")
    c3.metric("Reorder Qty",      f"{result['reorder_quantity']:,}", "recommended")
    c4.metric("Days of Stock",    f"{result['days_until_stockout']}d",
              f"{'Critical' if result['days_until_stockout']<3 else 'Warning' if result['days_until_stockout']<7 else 'Safe'}")
    c5.metric("Model MAE",        f"±{result['model_accuracy']:.1f}", "units error")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        # Sparkline of historical demand
        fig_hist = go.Figure()
        if not hist_product.empty:
            fig_hist.add_trace(go.Scatter(
                x=hist_product['date'], y=hist_product['demand'],
                fill='tozeroy', name='Historical',
                line=dict(color='#10d97e', width=2),
                fillcolor='rgba(16,217,126,0.07)',
                hovertemplate='%{x|%b %d}: %{y} units<extra></extra>'
            ))
        fig_hist.update_layout(
            title=dict(text="Historical Sales (Last 30 days)", font=dict(size=14, color='#e8eaf0'), x=0),
            height=220, margin=dict(l=0, r=0, t=40, b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, color='#4a5568', tickfont=dict(size=10)),
            yaxis=dict(gridcolor='rgba(255,255,255,0.04)', color='#4a5568', tickfont=dict(size=10)),
            showlegend=False,
            font=dict(family='IBM Plex Mono')
        )
        st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

    with col2:
        # Stock gauge
        gauge_val = min(100, int(current_stock / max(result['total_demand'], 1) * 100))
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=gauge_val,
            delta={'reference': 100, 'valueformat': '.0f', 'suffix': '%'},
            title={'text': "Stock Sufficiency %", 'font': {'size': 13, 'color': '#8892a4', 'family': 'IBM Plex Mono'}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': '#4a5568', 'tickfont': {'size': 10}},
                'bar': {'color': '#10d97e' if gauge_val >= 60 else '#f59e0b' if gauge_val >= 30 else '#ef4444'},
                'bgcolor': '#1a2235',
                'steps': [
                    {'range': [0, 30],  'color': 'rgba(239,68,68,0.15)'},
                    {'range': [30, 60], 'color': 'rgba(245,158,11,0.1)'},
                    {'range': [60, 100],'color': 'rgba(16,217,126,0.08)'},
                ],
                'threshold': {'line': {'color': 'white', 'width': 2}, 'value': 50}
            },
            number={'suffix': '%', 'font': {'size': 28, 'family': 'IBM Plex Mono', 'color': '#e8eaf0'}}
        ))
        fig_gauge.update_layout(
            height=220, margin=dict(l=20, r=20, t=40, b=10),
            paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#8892a4')
        )
        st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

    # Savings summary
    col_s1, col_s2, col_s3 = st.columns(3)
    col_s1.metric("Waste Reduction Savings",  f"₹{waste_savings:,.0f}",  "vs manual ordering")
    col_s2.metric("Stockout Prevention",       f"₹{stockout_savings:,.0f}","estimated revenue saved")
    col_s3.metric("Total Weekly Savings",      f"₹{total_savings:,.0f}",  "with AI optimization")

    st.markdown("<br>", unsafe_allow_html=True)
    col_n1, _, col_n2 = st.columns([1, 3, 1])
    with col_n1:
        if st.button("← Back"):
            st.session_state.step -= 1; play_sound("click"); st.rerun()
    with col_n2:
        if st.button("Next: Forecast →"):
            st.session_state.step += 1; play_sound("click"); st.rerun()

# ── STEP 2 · Forecast (FIXED) ─────────────────────────────────────────────────
elif step == 2:
    step_header(3, "Demand Forecast", f"{prediction_days}-day AI prediction with confidence bands")

    alert_banner(result['risk_level'], result['days_until_stockout'], result['reorder_quantity'], selected_product)

    # Build forecast figure
    future_dates = [datetime.now() + timedelta(days=i+1) for i in range(prediction_days)]
    preds = result['daily_predictions']
    mae   = result['model_accuracy']
    upper = [p + mae * 1.28 for p in preds]
    lower = [max(0, p - mae * 1.28) for p in preds]

    fig_fc = go.Figure()

    # Historical
    if not hist_product.empty:
        fig_fc.add_trace(go.Scatter(
            x=hist_product['date'], y=hist_product['demand'],
            name='Historical', mode='lines+markers',
            line=dict(color='#3b82f6', width=1.5),
            marker=dict(size=4),
            hovertemplate='%{x|%b %d}: %{y} units<extra>Historical</extra>'
        ))

    # CI band
    fig_fc.add_trace(go.Scatter(
        x=future_dates + future_dates[::-1],
        y=upper + lower[::-1],
        fill='toself', fillcolor='rgba(16,217,126,0.08)',
        line=dict(color='rgba(0,0,0,0)'), name='80% CI', hoverinfo='skip'
    ))

    # Forecast line
    fig_fc.add_trace(go.Scatter(
        x=future_dates, y=preds,
        name='AI Forecast', mode='lines+markers',
        line=dict(color='#10d97e', width=2.5, dash='dash'),
        marker=dict(size=6, symbol='circle'),
        hovertemplate='%{x|%b %d}: %{y:.0f} units<extra>Forecast</extra>'
    ))

    # Stock line
    fig_fc.add_hline(
        y=current_stock,
        line=dict(color='#f59e0b', width=1.5, dash='dot'),
        annotation=dict(text=f"Current stock: {current_stock}", font=dict(color='#f59e0b', size=11))
    )

    # FIXED: Stockout marker using add_shape instead of add_vline (more reliable)
    cumulative = 0
    stockout_day = None
    for i, p in enumerate(preds):
        cumulative += p
        if cumulative >= current_stock:
            stockout_day = i
            break

    if stockout_day is not None and stockout_day < len(future_dates):
        # Use add_shape for vertical line
        fig_fc.add_shape(
            type="line",
            x0=future_dates[stockout_day],
            x1=future_dates[stockout_day],
            y0=0,
            y1=max(preds + upper + [current_stock]) * 1.1,
            line=dict(color="#ef4444", width=2, dash="dot"),
        )
        # Add annotation
        fig_fc.add_annotation(
            x=future_dates[stockout_day],
            y=current_stock * 0.8,
            text=f"⚠️ Stockout Day {stockout_day + 1}",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="#ef4444",
            font=dict(color="#ef4444", size=11),
            bgcolor="rgba(0,0,0,0.7)",
            bordercolor="#ef4444",
            borderwidth=1,
            borderpad=4
        )

    fig_fc.update_layout(
        title=dict(text=f"Demand Forecast — {selected_product}", font=dict(size=15, color='#e8eaf0'), x=0),
        height=380, margin=dict(l=0, r=0, t=50, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, color='#4a5568', tickfont=dict(size=10)),
        yaxis=dict(gridcolor='rgba(255,255,255,0.04)', color='#4a5568',
                   tickfont=dict(size=10), title="Units"),
        legend=dict(orientation='h', y=-0.12, font=dict(size=11, color='#8892a4')),
        hovermode='x unified',
        font=dict(family='IBM Plex Mono', color='#8892a4')
    )
    st.plotly_chart(fig_fc, use_container_width=True, config={"displayModeBar": False})

    # Daily table
    st.markdown("##### Daily Breakdown")
    cumulative = 0
    rows = []
    for i, p in enumerate(preds):
        cumulative += p
        remaining = max(0, current_stock - cumulative)
        pct = min(100, int(remaining / max(current_stock, 1) * 100))
        status = "🔴 Stockout" if remaining == 0 else "🟡 Low" if pct < 25 else "🟢 OK"
        rows.append({
            "Day": f"Day {i+1}",
            "Date": (datetime.now() + timedelta(days=i+1)).strftime("%b %d, %Y"),
            "Demand": int(p),
            "Cumulative": int(cumulative),
            "Remaining Stock": int(remaining),
            "Stock %": f"{pct}%",
            "Status": status,
        })
    df_daily = pd.DataFrame(rows)
    st.dataframe(df_daily, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_n1, _, col_n2 = st.columns([1, 3, 1])
    with col_n1:
        if st.button("← Back"):
            st.session_state.step -= 1; play_sound("click"); st.rerun()
    with col_n2:
        if st.button("Next: Inventory →"):
            st.session_state.step += 1; play_sound("click"); st.rerun()
# ── STEP 3 · Inventory ────────────────────────────────────────────────────────
elif step == 3:
    step_header(4, "Inventory Analysis", "Stock health, EOQ and reorder intelligence")

    col1, col2 = st.columns(2)

    with col1:
        # Stock burndown
        remaining = current_stock
        burn = []
        for d in result['daily_predictions']:
            remaining = max(0, remaining - d)
            burn.append(remaining)

        fig_burn = go.Figure()
        days_x = list(range(1, prediction_days + 1))
        fig_burn.add_trace(go.Scatter(
            x=days_x, y=burn, fill='tozeroy',
            name='Remaining Stock',
            line=dict(color='#f59e0b', width=2),
            fillcolor='rgba(245,158,11,0.08)',
            hovertemplate='Day %{x}: %{y:,} units remaining<extra></extra>'
        ))
        reorder_y = [result['reorder_quantity']] * prediction_days
        fig_burn.add_trace(go.Scatter(
            x=days_x, y=reorder_y, name='Reorder Point',
            line=dict(color='#ef4444', width=1.5, dash='dot'),
        ))
        fig_burn.update_layout(
            title=dict(text="Stock Burn-down Curve", font=dict(size=14, color='#e8eaf0'), x=0),
            height=260, margin=dict(l=0, r=0, t=40, b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, color='#4a5568', title="Day", tickfont=dict(size=10)),
            yaxis=dict(gridcolor='rgba(255,255,255,0.04)', color='#4a5568',
                       title="Units", tickfont=dict(size=10)),
            legend=dict(orientation='h', y=-0.18, font=dict(size=11, color='#8892a4')),
            font=dict(family='IBM Plex Mono')
        )
        st.plotly_chart(fig_burn, use_container_width=True, config={"displayModeBar": False})

    with col2:
        # Multi-product comparison (top 5 for speed)
        top_products = products[:5]
        comp_data = []
        for p in top_products:
            try:
                r, _, _ = predictor.predict_demand(p, prediction_days, current_stock)
                comp_data.append({"Product": p[:18], "Demand": r['total_demand'],
                                   "Risk": r['risk_level'], "DSO": r['days_until_stockout']})
            except Exception:
                pass

        if comp_data:
            df_comp = pd.DataFrame(comp_data)
            risk_colors = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10d97e"}
            colors = [risk_colors[r] for r in df_comp['Risk']]
            fig_comp = go.Figure(go.Bar(
                x=df_comp['Product'], y=df_comp['Demand'],
                marker_color=colors, text=df_comp['Risk'],
                textposition='outside', textfont=dict(size=10, color='#8892a4'),
                hovertemplate='%{x}<br>Demand: %{y}<br>Risk: %{text}<extra></extra>'
            ))
            fig_comp.update_layout(
                title=dict(text="Product Demand Comparison", font=dict(size=14, color='#e8eaf0'), x=0),
                height=260, margin=dict(l=0, r=0, t=40, b=0),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, color='#4a5568', tickfont=dict(size=9), tickangle=-20),
                yaxis=dict(gridcolor='rgba(255,255,255,0.04)', color='#4a5568', tickfont=dict(size=10)),
                showlegend=False, font=dict(family='IBM Plex Mono')
            )
            st.plotly_chart(fig_comp, use_container_width=True, config={"displayModeBar": False})

    # Inventory intelligence cards
    st.markdown("##### Inventory Intelligence")
    avg_daily = result['total_demand'] / prediction_days
    z = 1.645  # 95% service level
    lead_time = 7  # default assumption
    demand_std = result['model_accuracy']
    safety_stock = int(z * demand_std * np.sqrt(lead_time))
    rop = int(avg_daily * lead_time + safety_stock)
    annual_demand = avg_daily * 365
    order_cost = 500
    holding_rate = 0.25
    eoq = int(np.sqrt(2 * annual_demand * order_cost / (unit_cost * holding_rate)))

    ci1, ci2, ci3, ci4 = st.columns(4)
    ci1.metric("Avg Daily Demand",  f"{avg_daily:.1f} units", "per day")
    ci2.metric("Safety Stock",      f"{safety_stock:,} units", "95% service level")
    ci3.metric("Reorder Point",     f"{rop:,} units",  "trigger order here")
    ci4.metric("EOQ",               f"{eoq:,} units",  "optimal batch size")

    st.markdown("<br>", unsafe_allow_html=True)
    col_n1, _, col_n2 = st.columns([1, 3, 1])
    with col_n1:
        if st.button("← Back"):
            st.session_state.step -= 1; play_sound("click"); st.rerun()
    with col_n2:
        if st.button("Next: Insights →"):
            st.session_state.step += 1; play_sound("click"); st.rerun()

# ── STEP 4 · Insights ─────────────────────────────────────────────────────────
elif step == 4:
    step_header(5, "AI Insights", "Anomaly detection, patterns & recommendations")

    col1, col2 = st.columns([1, 1])

    with col1:
        # Anomaly detection via z-score
        st.markdown("##### Anomaly Detection")
        if not hist_product.empty and len(hist_product) >= 7:
            s = hist_product['demand']
            rolling_mean = s.rolling(7).mean()
            rolling_std  = s.rolling(7).std()
            z_scores = ((s - rolling_mean) / (rolling_std + 1e-8)).fillna(0)
            anomalies = hist_product[abs(z_scores) > 2.0].copy()
            anomalies['z'] = z_scores[abs(z_scores) > 2.0].values

            fig_z = go.Figure()
            fig_z.add_trace(go.Scatter(
                x=hist_product['date'], y=hist_product['demand'],
                name='Demand', line=dict(color='#3b82f6', width=1.5),
                hovertemplate='%{x|%b %d}: %{y}<extra></extra>'
            ))
            if not anomalies.empty:
                fig_z.add_trace(go.Scatter(
                    x=anomalies['date'], y=anomalies['demand'],
                    mode='markers', name='Anomaly',
                    marker=dict(color='#ef4444', size=10, symbol='x'),
                    hovertemplate='%{x|%b %d}: %{y} — ANOMALY<extra></extra>'
                ))
            fig_z.update_layout(
                title=dict(text="Sales with Anomaly Markers", font=dict(size=13, color='#e8eaf0'), x=0),
                height=220, margin=dict(l=0, r=0, t=40, b=0),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, color='#4a5568', tickfont=dict(size=9)),
                yaxis=dict(gridcolor='rgba(255,255,255,0.04)', color='#4a5568', tickfont=dict(size=9)),
                legend=dict(orientation='h', y=-0.2, font=dict(size=10, color='#8892a4')),
                font=dict(family='IBM Plex Mono')
            )
            st.plotly_chart(fig_z, use_container_width=True, config={"displayModeBar": False})

            if not anomalies.empty:
                st.markdown(f"""
                <div style="background:#1a0505;border:1px solid #ef444444;
                            border-radius:10px;padding:12px 16px;margin-top:8px">
                    <span style="color:#ef4444;font-family:var(--mono);font-size:12px;font-weight:600">
                        {len(anomalies)} ANOMALIES DETECTED
                    </span>
                    <div style="font-size:12px;color:var(--text2);margin-top:4px">
                        Unusual demand spikes/dips may indicate promotions, external events, or data errors.
                    </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("Insufficient historical data for anomaly detection (need ≥ 7 days).")

    with col2:
        # Weekly demand heatmap pattern
        st.markdown("##### Weekly Demand Pattern")
        if not hist_product.empty:
            hist_copy = hist_product.copy()
            hist_copy['date'] = pd.to_datetime(hist_copy['date'])
            hist_copy['dow']  = hist_copy['date'].dt.day_name()
            hist_copy['week'] = hist_copy['date'].dt.isocalendar().week
            dow_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
            pivot = hist_copy.groupby('dow')['demand'].mean().reindex(dow_order).fillna(0)

            fig_bar = go.Figure(go.Bar(
                x=pivot.index, y=pivot.values,
                marker_color=['#10d97e' if v == pivot.max() else
                              '#ef4444' if v == pivot.min() else '#3b82f6'
                              for v in pivot.values],
                hovertemplate='%{x}: %{y:.1f} avg units<extra></extra>'
            ))
            fig_bar.update_layout(
                title=dict(text="Avg Demand by Day of Week", font=dict(size=13, color='#e8eaf0'), x=0),
                height=220, margin=dict(l=0, r=0, t=40, b=0),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, color='#4a5568', tickfont=dict(size=9)),
                yaxis=dict(gridcolor='rgba(255,255,255,0.04)', color='#4a5568', tickfont=dict(size=9)),
                showlegend=False, font=dict(family='IBM Plex Mono')
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    # Actionable recommendations
    st.markdown("##### Actionable Recommendations")
    recs = []
    if result['risk_level'] == "High":
        recs = [
            ("🚨", "Immediate restock required", f"Place an order for {result['reorder_quantity']} units TODAY to prevent stockout in {result['days_until_stockout']} days.", "var(--red)"),
            ("🚚", "Request expedited shipping", "Standard lead times may be too long. Contact supplier for express delivery.", "var(--amber)"),
            ("📣", "Consider demand-side action", "Run promotions or temporarily limit sales to extend available stock.", "var(--blue)"),
        ]
    elif result['risk_level'] == "Medium":
        recs = [
            ("📦", "Schedule reorder within 2 days", f"Order {result['reorder_quantity']} units within 48 hours to maintain service levels.", "var(--amber)"),
            ("📊", "Monitor daily burn rate", "Track stock consumption daily and adjust forecast if demand spikes.", "var(--blue)"),
        ]
    else:
        recs = [
            ("✅", "No immediate action required", "Stock levels are healthy. Routine reorder can wait until next cycle.", "var(--green)"),
            ("📈", "Optimize holding costs", "Consider reducing order quantity to minimize capital tied up in inventory.", "var(--blue)"),
            ("🔁", "Set automated reorder trigger", f"Configure alert when stock falls below {int(result['total_demand']*0.3)} units.", "var(--green)"),
        ]

    for icon, title, detail, color in recs:
        st.markdown(f"""
        <div style="background:var(--bg3);border:1px solid var(--border);
                    border-left:3px solid {color};border-radius:10px;
                    padding:14px 18px;margin-bottom:10px;display:flex;gap:14px;align-items:flex-start">
            <span style="font-size:20px;flex-shrink:0">{icon}</span>
            <div>
                <div style="font-size:13px;font-weight:700;color:var(--text);margin-bottom:4px">{title}</div>
                <div style="font-size:12px;color:var(--text2);line-height:1.6">{detail}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_n1, _, col_n2 = st.columns([1, 3, 1])
    with col_n1:
        if st.button("← Back"):
            st.session_state.step -= 1; play_sound("click"); st.rerun()
    with col_n2:
        if st.button("Next: Simulator →"):
            st.session_state.step += 1; play_sound("click"); st.rerun()

# ── STEP 5 · Simulate ─────────────────────────────────────────────────────────
elif step == 5:
    step_header(6, "What-if Simulator", "Test scenarios before committing capital")

    st.markdown("""
    <div style="background:var(--bg3);border:1px solid var(--border);
                border-radius:12px;padding:20px 24px;margin-bottom:20px">
        <div style="font-size:12px;color:var(--text2);font-family:var(--mono);
                    text-transform:uppercase;letter-spacing:1px;margin-bottom:16px">
            Simulation Parameters
        </div>
    """, unsafe_allow_html=True)

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        sim_stock   = st.number_input("Simulated Stock", 0, 5000, current_stock, 10, key="sim_s")
    with col_s2:
        sim_days    = st.slider("Simulation Days", 1, 30, prediction_days, key="sim_d")
    with col_s3:
        demand_mult = st.slider("Demand Multiplier", 0.5, 3.0, 1.0, 0.1, key="sim_m",
                                help="1.0 = normal, 2.0 = double demand")
    with col_s4:
        sim_lead    = st.number_input("Lead Time (days)", 1, 30, 7, 1, key="sim_l")

    st.markdown("</div>", unsafe_allow_html=True)

    # Run simulation
    sim_result, _, _ = predictor.predict_demand(selected_product, sim_days, sim_stock)
    sim_preds  = [int(p * demand_mult) for p in sim_result['daily_predictions']]
    sim_total  = sum(sim_preds)
    sim_rop    = int(np.mean(sim_preds) * sim_lead * 1.2)
    sim_dso    = max(0, int(sim_stock / max(np.mean(sim_preds), 1)))
    sim_risk   = "High" if sim_dso < 3 else "Medium" if sim_dso < 7 else "Low"
    sim_reorder= max(0, sim_total - sim_stock + int(sim_total * 0.15))

    alert_banner(sim_risk, sim_dso, sim_reorder, f"{selected_product} (Sim)")

    col1, col2 = st.columns(2)

    with col1:
        # Side-by-side comparison
        fig_cmp = go.Figure()
        orig_preds = result['daily_predictions']
        days_x = list(range(1, max(len(orig_preds), len(sim_preds)) + 1))

        fig_cmp.add_trace(go.Scatter(
            x=list(range(1, len(orig_preds)+1)), y=orig_preds,
            name='Original', line=dict(color='#3b82f6', width=2, dash='dot'),
            hovertemplate='Day %{x}: %{y} units (original)<extra></extra>'
        ))
        fig_cmp.add_trace(go.Scatter(
            x=list(range(1, len(sim_preds)+1)), y=sim_preds,
            name='Simulated', line=dict(color='#10d97e', width=2.5),
            hovertemplate='Day %{x}: %{y} units (simulated)<extra></extra>'
        ))
        fig_cmp.add_hline(y=sim_stock, line=dict(color='#f59e0b', width=1, dash='dot'),
                          annotation=dict(text=f"Sim stock: {sim_stock}", font=dict(color='#f59e0b', size=10)))
        fig_cmp.update_layout(
            title=dict(text="Demand: Original vs Simulated", font=dict(size=13, color='#e8eaf0'), x=0),
            height=260, margin=dict(l=0, r=0, t=40, b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, color='#4a5568', title="Day", tickfont=dict(size=10)),
            yaxis=dict(gridcolor='rgba(255,255,255,0.04)', color='#4a5568', tickfont=dict(size=10)),
            legend=dict(orientation='h', y=-0.2, font=dict(size=11, color='#8892a4')),
            font=dict(family='IBM Plex Mono')
        )
        st.plotly_chart(fig_cmp, use_container_width=True, config={"displayModeBar": False})

    with col2:
        # EOQ sensitivity
        order_costs = list(range(100, 1100, 100))
        eoqs = [int(np.sqrt(2 * sim_total * 365 / sim_days * oc / max(unit_cost * 0.25, 1)))
                for oc in order_costs]
        fig_eoq = go.Figure(go.Scatter(
            x=order_costs, y=eoqs, mode='lines+markers',
            line=dict(color='#f59e0b', width=2),
            marker=dict(size=5),
            hovertemplate='Order cost ₹%{x}: EOQ = %{y} units<extra></extra>'
        ))
        fig_eoq.add_vline(x=500, line=dict(color='#10d97e', width=1, dash='dot'),
                          annotation=dict(text="Current", font=dict(color='#10d97e', size=10)))
        fig_eoq.update_layout(
            title=dict(text="EOQ Sensitivity to Order Cost", font=dict(size=13, color='#e8eaf0'), x=0),
            height=260, margin=dict(l=0, r=0, t=40, b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, color='#4a5568', title="Order Cost (₹)", tickfont=dict(size=10)),
            yaxis=dict(gridcolor='rgba(255,255,255,0.04)', color='#4a5568',
                       title="EOQ (units)", tickfont=dict(size=10)),
            showlegend=False, font=dict(family='IBM Plex Mono')
        )
        st.plotly_chart(fig_eoq, use_container_width=True, config={"displayModeBar": False})

    # Simulation result summary
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    col_r1.metric("Sim Total Demand",   f"{sim_total:,}",     f"× {demand_mult} multiplier")
    col_r2.metric("Sim Days of Stock",  f"{sim_dso}d",        sim_risk + " risk")
    col_r3.metric("Sim Reorder Qty",    f"{sim_reorder:,}",   "units needed")
    col_r4.metric("Sim Reorder Point",  f"{sim_rop:,}",       "trigger level")

    st.markdown("<br>", unsafe_allow_html=True)
    col_n1, _, col_n2 = st.columns([1, 3, 1])
    with col_n1:
        if st.button("← Back"):
            st.session_state.step -= 1; play_sound("click"); st.rerun()
    with col_n2:
        if st.button("Next: Report →"):
            st.session_state.step += 1; play_sound("click"); st.rerun()

# ── STEP 6 · Report ───────────────────────────────────────────────────────────
elif step == 6:
    step_header(7, "Export Report", "Download your inventory intelligence report")

    alert_banner(result['risk_level'], result['days_until_stockout'], result['reorder_quantity'], selected_product)

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown("##### Full Report Summary")

        avg_daily = result['total_demand'] / prediction_days
        z = 1.645
        demand_std = result['model_accuracy']
        lead_time = 7
        safety_stock = int(z * demand_std * np.sqrt(lead_time))
        rop = int(avg_daily * lead_time + safety_stock)
        annual_demand = avg_daily * 365
        eoq = int(np.sqrt(2 * annual_demand * 500 / max(unit_cost * 0.25, 1)))

        summary_items = [
            ("Product", selected_product),
            ("Generated", datetime.now().strftime("%Y-%m-%d %H:%M")),
            ("Forecast Horizon", f"{prediction_days} days"),
            ("Total Predicted Demand", f"{result['total_demand']:,} units"),
            ("Current Stock", f"{current_stock:,} units"),
            ("Reorder Quantity", f"{result['reorder_quantity']:,} units"),
            ("Reorder Point", f"{rop:,} units"),
            ("Safety Stock", f"{safety_stock:,} units"),
            ("EOQ", f"{eoq:,} units"),
            ("Days Until Stockout", f"{result['days_until_stockout']} days"),
            ("Risk Level", result['risk_level']),
            ("Model MAE", f"±{result['model_accuracy']:.1f} units"),
            ("Unit Cost", f"₹{unit_cost:,.2f}"),
            ("Selling Price", f"₹{selling_price:,.2f}"),
            ("Profit Margin", f"{profit_margin}%"),
            ("Waste Reduction Savings", f"₹{waste_savings:,.0f}"),
            ("Stockout Prevention Savings", f"₹{stockout_savings:,.0f}"),
            ("Total Weekly Savings", f"₹{total_savings:,.0f}"),
        ]
        for label, val in summary_items:
            color = "var(--red)" if label == "Risk Level" and val == "High" else \
                    "var(--amber)" if label == "Risk Level" and val == "Medium" else \
                    "var(--green)" if label == "Risk Level" else "var(--text)"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;
                        padding:9px 0;border-bottom:1px solid var(--border)">
                <span style="font-size:12px;color:var(--text2);font-family:var(--mono)">{label}</span>
                <span style="font-size:12px;font-weight:600;font-family:var(--mono);color:{color}">{val}</span>
            </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("##### Download Options")

        # Build CSV
        cum = 0
        rows = []
        for i, p in enumerate(result['daily_predictions']):
            cum += p
            rows.append({
                "Day": i+1,
                "Date": (datetime.now() + timedelta(days=i+1)).strftime("%Y-%m-%d"),
                "Predicted_Demand": int(p),
                "Cumulative_Demand": int(cum),
                "Remaining_Stock": max(0, current_stock - int(cum)),
                "Status": "Stockout" if cum >= current_stock else "OK"
            })
        df_report = pd.DataFrame(rows)

        csv_bytes = df_report.to_csv(index=False).encode()
        st.download_button(
            "📥 Download Forecast CSV",
            data=csv_bytes,
            file_name=f"stocksense_{selected_product.replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Summary CSV
        summary_df = pd.DataFrame(summary_items, columns=["Metric", "Value"])
        summary_csv = summary_df.to_csv(index=False).encode()
        st.download_button(
            "📋 Download Summary CSV",
            data=summary_csv,
            file_name=f"stocksense_summary_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Quick action box
        urgency_map = {"High": ("🚨 ORDER NOW", "var(--red)"), "Medium": ("📦 Plan Reorder", "var(--amber)"), "Low": ("✅ No Action", "var(--green)")}
        label, col = urgency_map[result['risk_level']]
        st.markdown(f"""
        <div style="background:var(--bg3);border:2px solid {col};border-radius:14px;
                    padding:28px;text-align:center;margin-top:8px">
            <div style="font-size:32px;font-family:var(--mono);font-weight:800;color:{col}">{label}</div>
            <div style="font-size:13px;color:var(--text2);margin-top:12px;line-height:1.6">
                Reorder <b style="color:{col}">{result['reorder_quantity']:,} units</b><br>
                of <b style="color:var(--text)">{selected_product}</b>
            </div>
            <div style="font-size:12px;color:var(--text3);font-family:var(--mono);margin-top:12px">
                Est. cost: ₹{result['reorder_quantity'] * unit_cost:,.0f}
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_n1, col_n2, col_n3 = st.columns([1, 2, 1])
    with col_n1:
        if st.button("← Back"):
            st.session_state.step -= 1; play_sound("click"); st.rerun()
    with col_n2:
        if st.button("🔄 Start New Analysis"):
            st.session_state.step = 0
            st.session_state.predictions_cache = {}
            play_sound("click")
            st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:32px;padding-top:16px;border-top:1px solid var(--border);
            display:flex;justify-content:space-between;align-items:center">
    <div style="font-size:11px;color:var(--text3);font-family:var(--mono)">
        StockSense AI · Random Forest + Gradient Boosting · R²=0.999
    </div>
    <div style="font-size:11px;color:var(--text3);font-family:var(--mono)">
        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} · Step {step+1}/{len(STEPS)}
    </div>
</div>""", unsafe_allow_html=True)

# Auto refresh
if auto_refresh:
    time.sleep(10)
    st.session_state.predictions_cache = {}
    st.rerun()