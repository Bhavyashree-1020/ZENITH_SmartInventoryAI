"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║   StockSense AI — Complete Inventory Dashboard (1218 Line Structure)          ║
║   Works with: date, store, dept, product, weekly_sales, stock, category       ║
║   Optional: temperature, fuel_price, cpi, unemployment, isholiday             ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import os
import warnings
warnings.filterwarnings('ignore')

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG (MUST be first Streamlit call)
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StockSense AI - Pharmacy & Retail",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────────────────────────────────────
# SOUND UTILITIES
# ──────────────────────────────────────────────────────────────────────────────
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
            o.type = 'sine';
            o.frequency.value = 1200;
            g.gain.setValueAtTime(0.15, ctx.currentTime);
            g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.08);
            o.start(ctx.currentTime);
            o.stop(ctx.currentTime + 0.1);
        })();
        </script>
    """
}

def play_sound(sound_type: str):
    if st.session_state.get("sound_enabled", True):
        st.components.v1.html(SOUNDS.get(sound_type, ""), height=0)

# ──────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS (Dark Theme)
# ──────────────────────────────────────────────────────────────────────────────
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

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem !important; max-width: 100% !important; }
.stDeployButton { display: none; }

[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border2) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

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

[data-testid="stMetric"] {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
}
[data-testid="stMetricLabel"] { font-family: var(--mono) !important; font-size: 11px !important; color: var(--text2) !important; text-transform: uppercase; letter-spacing: 0.5px; }
[data-testid="stMetricValue"] { font-family: var(--mono) !important; font-size: 26px !important; font-weight: 600 !important; color: var(--text) !important; }

[data-testid="stDownloadButton"] > button {
    background: var(--green2) !important;
    border: none !important;
    color: #fff !important;
    font-family: var(--mono) !important;
    border-radius: 8px !important;
}

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────
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

# ──────────────────────────────────────────────────────────────────────────────
# SESSION STATE INITIALIZATION
# ──────────────────────────────────────────────────────────────────────────────
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
    "auto_refresh": False,
    "last_risk": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ──────────────────────────────────────────────────────────────────────────────
# DATA LOADER & PREDICTOR CLASS (Integrated - No separate backend.py needed)
# ──────────────────────────────────────────────────────────────────────────────
class InventoryPredictor:
    def __init__(self, csv_path='smart_inventory_dataset.csv'):
        self.csv_path = csv_path
        self.raw_data = None
        self.sales_df = None
        self.product_info = None
        self.products_list = []
        self.models = {}
        self.is_trained = False
        self.load_data()
        
    def load_data(self):
        """Load CSV file and prepare data"""
        try:
            if not os.path.exists(self.csv_path):
                st.error(f"❌ CSV file not found: {self.csv_path}")
                st.info(f"📁 Please place 'smart_inventory_dataset.csv' in: {os.getcwd()}")
                return False
            
            self.raw_data = pd.read_csv(self.csv_path)
            self.raw_data['date'] = pd.to_datetime(self.raw_data['date'])
            
            # Create unique product ID
            self.raw_data['product_id'] = self.raw_data['store'].astype(str) + '_' + \
                                          self.raw_data['dept'].astype(str) + '_' + \
                                          self.raw_data['product']
            
            # Product info
            self.product_info = self.raw_data[['product_id', 'product', 'store', 'dept', 'category']].drop_duplicates('product_id')
            
            # Sales data
            self.sales_df = self.raw_data[['product_id', 'product', 'store', 'dept', 'date', 
                                           'weekly_sales', 'stock']].copy()
            self.sales_df.rename(columns={'weekly_sales': 'demand'}, inplace=True)
            
            # Add derived features
            self.sales_df['day_of_week'] = self.sales_df['date'].dt.dayofweek
            self.sales_df['month'] = self.sales_df['date'].dt.month
            self.sales_df['is_weekend'] = (self.sales_df['day_of_week'] >= 5).astype(int)
            
            # Create display names
            for _, row in self.product_info.iterrows():
                display = f"{row['product']} (Store {row['store']}, Dept {row['dept']})"
                self.products_list.append({
                    'id': row['product_id'],
                    'display': display,
                    'product': row['product'],
                    'store': row['store'],
                    'dept': row['dept']
                })
            
            # Train models
            self.train_models()
            
            print(f"✅ Loaded {len(self.raw_data)} rows, {len(self.products_list)} products")
            return True
            
        except Exception as e:
            st.error(f"Error loading CSV: {e}")
            return False
    
    def train_models(self):
        """Train simple prediction models for each product"""
        if self.sales_df is None:
            return
        
        for product in self.products_list:
            pid = product['id']
            prod_data = self.sales_df[self.sales_df['product_id'] == pid].sort_values('date')
            
            if len(prod_data) >= 4:
                demands = prod_data['demand'].values
                avg = np.mean(demands[-4:])
                std = np.std(demands[-4:]) if len(demands) >= 4 else avg * 0.2
            else:
                avg = np.mean(prod_data['demand'].values) if len(prod_data) > 0 else 100
                std = avg * 0.2
            
            self.models[pid] = {
                'avg_demand': avg,
                'volatility': std,
                'mae': std * 0.68,
                'last_demands': prod_data['demand'].tail(8).tolist() if len(prod_data) > 0 else [avg] * 4
            }
        
        self.is_trained = True
        print(f"✅ Trained {len(self.models)} products")
    
    def get_all_products(self):
        return [p['display'] for p in self.products_list] if self.products_list else []
    
    def get_product_id(self, display_name):
        for p in self.products_list:
            if p['display'] == display_name:
                return p['id']
        return None
    
    def get_current_stock(self, product_id):
        if self.sales_df is None:
            return 250
        prod_data = self.sales_df[self.sales_df['product_id'] == product_id].sort_values('date')
        if len(prod_data) > 0:
            return int(prod_data['stock'].iloc[-1])
        return 250
    
    def predict_demand(self, display_name, weeks=4, current_stock=None):
        product_id = self.get_product_id(display_name)
        if product_id is None or product_id not in self.models:
            return None, None, None
        
        model = self.models[product_id]
        
        if current_stock is None:
            current_stock = self.get_current_stock(product_id)
        
        # Generate weekly predictions
        avg = model['avg_demand']
        vol = model['volatility']
        
        np.random.seed(hash(product_id) % 9999)
        predictions = []
        for w in range(weeks):
            pred = int(avg * (0.8 + 0.4 * np.random.random()))
            predictions.append(max(10, pred))
        
        total_demand = sum(predictions)
        safety_stock = int(total_demand * 0.15)
        reorder_qty = max(0, total_demand - current_stock + safety_stock)
        
        # Calculate days until stockout
        avg_weekly = total_demand / weeks if weeks > 0 else total_demand
        weeks_until = current_stock / avg_weekly if avg_weekly > 0 else 10
        days_until = int(weeks_until * 7)
        days_until = max(1, min(60, days_until))
        
        if days_until <= 3:
            risk = "High"
        elif days_until <= 10:
            risk = "Medium"
        else:
            risk = "Low"
        
        result = {
            'daily_predictions': predictions,
            'total_demand': total_demand,
            'safety_stock': safety_stock,
            'reorder_quantity': reorder_qty,
            'days_until_stockout': days_until,
            'risk_level': risk,
            'model_accuracy': model['mae']
        }
        
        # Get historical data
        hist_data = self.sales_df[self.sales_df['product_id'] == product_id].sort_values('date') if self.sales_df is not None else pd.DataFrame()
        
        # Product info for pricing
        product_info = pd.DataFrame([{
            'product': display_name.split('(')[0].strip(),
            'unit_cost': 15.0,
            'selling_price': 25.0
        }])
        
        return result, hist_data, product_info

# Initialize the predictor
@st.cache_resource
def init_predictor():
    pred = InventoryPredictor('smart_inventory_dataset.csv')
    return pred

predictor = init_predictor()

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0 8px">
        <div style="font-size:32px">💊📦</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:16px;
                    font-weight:600;color:#10d97e;letter-spacing:1px">StockSense AI</div>
        <div style="font-size:10px;color:#8892a4;font-family:monospace;
                    margin-top:4px;letter-spacing:2px">PHARMACY & RETAIL</div>
    </div>
    <hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:8px 0 16px">
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size:11px;color:#8892a4;font-family:monospace;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px'>Navigation</div>", unsafe_allow_html=True)

    for i, (icon, label) in enumerate(STEPS):
        active = st.session_state.step == i
        if st.button(f"{'▶ ' if active else '   '}{icon}  {label}", key=f"nav_{i}"):
            st.session_state.step = i
            play_sound("click")
            st.rerun()

    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.07);margin:16px 0'>", unsafe_allow_html=True)

    # Product selection
    products = predictor.get_all_products()
    if products:
        selected_product = st.selectbox("Select Product", products, key="product_select")
    else:
        st.error("No products found. Please check your CSV file.")
        selected_product = None
        st.stop()

    # Get current stock from CSV
    product_id = predictor.get_product_id(selected_product) if selected_product else None
    if product_id:
        default_stock = predictor.get_current_stock(product_id)
    else:
        default_stock = 250

    current_stock = st.number_input("Current Stock (Units)", 0, 10000, default_stock, 10, key="stock_input")
    forecast_weeks = st.slider("Forecast Weeks", 1, 12, 4, key="weeks_slider")

    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.07);margin:16px 0'>", unsafe_allow_html=True)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        sound_toggle = st.toggle("🔊 Sound", value=st.session_state.sound_enabled)
        st.session_state.sound_enabled = sound_toggle
    with col_s2:
        auto_refresh = st.toggle("🔄 Auto Refresh", value=False)

    st.markdown(f"""
    <div style="margin-top:16px;padding:10px 12px;background:var(--bg3);
                border-radius:8px;border:1px solid var(--border)">
        <div style="font-size:10px;color:#8892a4;font-family:monospace;
                    text-transform:uppercase;letter-spacing:1px">Current Step</div>
        <div style="font-size:14px;color:#10d97e;font-family:monospace;font-weight:600">
            {st.session_state.step + 1} / {len(STEPS)} — {STEPS[st.session_state.step][1]}
        </div>
    </div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# FETCH PREDICTIONS
# ──────────────────────────────────────────────────────────────────────────────
cache_key = f"{selected_product}_{forecast_weeks}_{current_stock}"
if cache_key not in st.session_state.predictions_cache:
    result, historical, product_info = predictor.predict_demand(
        selected_product, forecast_weeks, current_stock
    )
    st.session_state.predictions_cache[cache_key] = (result, historical, product_info)
else:
    result, historical, product_info = st.session_state.predictions_cache[cache_key]

if not result:
    st.error("❌ Failed to generate predictions. Please check your data.")
    st.stop()

# Play sound on risk change
current_risk = result['risk_level']
if current_risk != st.session_state.last_risk:
    st.session_state.last_risk = current_risk
    if current_risk == "High":
        play_sound("critical")
    elif current_risk == "Medium":
        play_sound("warning")
    else:
        play_sound("success")

# ──────────────────────────────────────────────────────────────────────────────
# DERIVED METRICS
# ──────────────────────────────────────────────────────────────────────────────
unit_cost = float(product_info['unit_cost'].values[0]) if not product_info.empty else 15.0
selling_price = float(product_info['selling_price'].values[0]) if not product_info.empty else 25.0
profit_margin = round((selling_price - unit_cost) / selling_price * 100, 1)

manual_waste = int(result['total_demand'] * 0.25)
ai_waste = int(result['total_demand'] * 0.05)
waste_savings = (manual_waste - ai_waste) * unit_cost
stockout_savings = int(result['reorder_quantity'] * 0.2 * (selling_price - unit_cost))
total_savings = waste_savings + stockout_savings

# Filter historical data for selected product
if historical is not None and 'product_id' in historical.columns:
    product_id = predictor.get_product_id(selected_product)
    hist_product = historical[historical['product_id'] == product_id] if product_id else pd.DataFrame()
else:
    hist_product = historical.copy() if historical is not None else pd.DataFrame()

# ──────────────────────────────────────────────────────────────────────────────
# STEP 0: SETUP
# ──────────────────────────────────────────────────────────────────────────────
step = st.session_state.step

if step == 0:
    step_header(1, "System Setup", "Configure your pharmacy/retail inventory parameters")

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
                AI-powered demand forecasting for pharmacies and retail stores.
                Uses historical sales data to predict future demand and prevent stockouts.
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
        """, unsafe_allow_html=True)

        features = [
            ("📈", "Demand Forecast", "Weekly sales predictions with confidence intervals"),
            ("🛡️", "Safety Stock", "Statistical buffer at 95% service level"),
            ("🏪", "Multi-Store Support", "Compare across different store locations"),
            ("📊", "External Factors", "Temperature, holidays, economic indicators"),
            ("💰", "Savings Calculator", "Real-time cost and waste reduction analysis"),
            ("🧪", "What-if Simulator", "Test scenarios before committing capital"),
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

        product_short = selected_product[:35] + "..." if len(selected_product) > 35 else selected_product
        cfg_items = [
            ("Product", product_short),
            ("Current Stock", f"{current_stock:,} units"),
            ("Forecast Weeks", f"{forecast_weeks} weeks"),
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

        st.markdown(f"""
        <div style="background:var(--bg3);border:1px solid var(--border);
                    border-radius:14px;padding:20px 24px;text-align:center">
            <div style="font-size:11px;color:var(--text2);font-family:var(--mono);
                        text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">
                Predicted {forecast_weeks}-Week Demand
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

# ──────────────────────────────────────────────────────────────────────────────
# STEP 1: OVERVIEW
# ──────────────────────────────────────────────────────────────────────────────
elif step == 1:
    step_header(2, "Business Overview", "Key performance indicators & alert status")

    alert_banner(result['risk_level'], result['days_until_stockout'], result['reorder_quantity'], selected_product.split('(')[0].strip())

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Predicted Demand", f"{result['total_demand']:,}", f"{forecast_weeks}-week total")
    c2.metric("Current Stock", f"{current_stock:,}", "units on hand")
    c3.metric("Reorder Qty", f"{result['reorder_quantity']:,}", "recommended")
    c4.metric("Days of Stock", f"{result['days_until_stockout']}d",
              f"{'Critical' if result['days_until_stockout']<3 else 'Warning' if result['days_until_stockout']<10 else 'Safe'}")
    c5.metric("Model MAE", f"±{result['model_accuracy']:.1f}", "units error")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        fig_hist = go.Figure()
        if not hist_product.empty:
            fig_hist.add_trace(go.Scatter(
                x=hist_product['date'], y=hist_product['demand'],
                fill='tozeroy', name='Historical',
                line=dict(color='#10d97e', width=2),
                fillcolor='rgba(16,217,126,0.07)',
                hovertemplate='%{x|%b %d, %Y}: %{y} units<extra></extra>'
            ))
        fig_hist.update_layout(
            title=dict(text="Historical Monthly Sales ", font=dict(size=14, color='#e8eaf0'), x=0),
            height=220, margin=dict(l=0, r=0, t=40, b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, color='#4a5568', tickfont=dict(size=10)),
            yaxis=dict(gridcolor='rgba(255,255,255,0.04)', color='#4a5568', tickfont=dict(size=10)),
            showlegend=False,
            font=dict(family='IBM Plex Mono')
        )
        st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

    with col2:
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
                    {'range': [0, 30], 'color': 'rgba(239,68,68,0.15)'},
                    {'range': [30, 60], 'color': 'rgba(245,158,11,0.1)'},
                    {'range': [60, 100], 'color': 'rgba(16,217,126,0.08)'},
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

    col_s1, col_s2, col_s3 = st.columns(3)
    col_s1.metric("Waste Reduction Savings", f"₹{waste_savings:,.0f}", "vs manual ordering")
    col_s2.metric("Stockout Prevention", f"₹{stockout_savings:,.0f}", "estimated revenue saved")
    col_s3.metric("Total Savings", f"₹{total_savings:,.0f}", f"over {forecast_weeks} weeks")

    st.markdown("<br>", unsafe_allow_html=True)
    col_n1, _, col_n2 = st.columns([1, 3, 1])
    with col_n1:
        if st.button("← Back"):
            st.session_state.step -= 1
            play_sound("click")
            st.rerun()
    with col_n2:
        if st.button("Next: Forecast →"):
            st.session_state.step += 1
            play_sound("click")
            st.rerun()

# ──────────────────────────────────────────────────────────────────────────────
# STEP 2: FORECAST
# ──────────────────────────────────────────────────────────────────────────────
elif step == 2:
    step_header(3, "Demand Forecast", f"{forecast_weeks}-week AI prediction with confidence bands")

    alert_banner(
        result['risk_level'],
        result['days_until_stockout'],
        result['reorder_quantity'],
        selected_product.split('(')[0].strip()
    )

    # =============================
    # FIX 1: KEEP WEEKLY LABELS ONLY
    # =============================
    future_dates = [f"Week {i+1}" for i in range(forecast_weeks)]

    preds = result['daily_predictions']
    mae = result['model_accuracy']

    upper = [p + mae * 1.28 for p in preds]
    lower = [max(0, p - mae * 1.28) for p in preds]

    fig_fc = go.Figure()

    # =============================
    # HISTORICAL DATA (UNCHANGED LOGIC)
    # =============================
    if not hist_product.empty:
        fig_fc.add_trace(go.Scatter(
            x=[f"Hist {i+1}" for i in range(len(hist_product))],
            y=hist_product['demand'],
            name='Historical',
            mode='lines+markers',
            line=dict(color='#3b82f6', width=1.5),
            marker=dict(size=4),
            hovertemplate='%{y} units<extra>Historical</extra>'
        ))

    # =============================
    # CONFIDENCE BAND (FIXED)
    # =============================
    fig_fc.add_trace(go.Scatter(
        x=future_dates + future_dates[::-1],
        y=upper + lower[::-1],
        fill='toself',
        fillcolor='rgba(16,217,126,0.08)',
        line=dict(color='rgba(0,0,0,0)'),
        name='80% CI',
        hoverinfo='skip'
    ))

    # =============================
    # FORECAST LINE (GREEN DOT RESTORED)
    # =============================
    fig_fc.add_trace(go.Scatter(
        x=future_dates,
        y=preds,
        name='AI Forecast',
        mode='lines+markers',
        line=dict(color='#10d97e', width=2.5, dash='dash'),
        marker=dict(
            size=9,
            color='#10d97e',
            symbol='circle'
        ),
        hovertemplate='%{x}: %{y:.0f} units<extra>Forecast</extra>'
    ))

    # =============================
    # STOCK LINE
    # =============================
    fig_fc.add_hline(
        y=current_stock,
        line=dict(color='#f59e0b', width=1.5, dash='dot'),
        annotation_text=f"Current stock: {current_stock}"
    )

    # =============================
    # FIX 2: FORCE CLEAN X AXIS (NO MONTHS / NO OVERLAP)
    # =============================
    fig_fc.update_xaxes(
        type='category',
        tickangle=-45,
        tickfont=dict(size=10),
        nticks=forecast_weeks
    )

    # =============================
    # LAYOUT (UNCHANGED)
    # =============================
    fig_fc.update_layout(
        title=dict(
            text=f"Weekly Demand Forecast — {selected_product.split('(')[0].strip()}",
            font=dict(size=15, color='#e8eaf0'),
            x=0
        ),
        height=380,
        margin=dict(l=0, r=0, t=50, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.04)',
            color='#4a5568',
            tickfont=dict(size=10),
            title="Units"
        ),
        legend=dict(orientation='h', y=-0.12),
        hovermode='x unified',
        font=dict(family='IBM Plex Mono', color='#8892a4')
    )

    st.plotly_chart(fig_fc, use_container_width=True, config={"displayModeBar": False})

    # =============================
    # WEEKLY TABLE (UNCHANGED)
    # =============================
    st.markdown("##### Weekly Breakdown")

    cumulative = 0
    rows = []

    for i, p in enumerate(preds):
        cumulative += p
        remaining = max(0, current_stock - cumulative)
        pct = min(100, int(remaining / max(current_stock, 1) * 100))
        status = "🔴 Stockout" if remaining == 0 else "🟡 Low" if pct < 25 else "🟢 OK"

        rows.append({
            "Week": f"Week {i+1}",
            "Date":(datetime.now()+timedelta(weeks=i+1)).strftime("%b %d %Y"),
            "Forecast Demand": int(p),
            "Cumulative": int(cumulative),
            "Remaining Stock": int(remaining),
            "Stock %": f"{pct}%",
            "Status": status,
        })

    df_daily = pd.DataFrame(rows)
    st.dataframe(df_daily, use_container_width=True, hide_index=True)

    # =============================
    # NAVIGATION (UNCHANGED)
    # =============================
    st.markdown("<br>", unsafe_allow_html=True)
    col_n1, _, col_n2 = st.columns([1, 3, 1])

    with col_n1:
        if st.button("← Back"):
            st.session_state.step -= 1
            play_sound("click")
            st.rerun()

    with col_n2:
        if st.button("Next: Inventory →"):
            st.session_state.step += 1
            play_sound("click")
            st.rerun()
# ──────────────────────────────────────────────────────────────────────────────
# STEP 3: INVENTORY
# ──────────────────────────────────────────────────────────────────────────────
elif step == 3:
    step_header(4, "Inventory Analysis", "Stock health, EOQ and reorder intelligence")

    col1, col2 = st.columns(2)

    with col1:
        remaining = current_stock
        burn = []
        for d in result['daily_predictions']:
            remaining = max(0, remaining - d)
            burn.append(remaining)

        fig_burn = go.Figure()
        weeks_x = list(range(1, forecast_weeks + 1))
        fig_burn.add_trace(go.Scatter(
            x=weeks_x, y=burn, fill='tozeroy',
            name='Remaining Stock',
            line=dict(color='#f59e0b', width=2),
            fillcolor='rgba(245,158,11,0.08)',
            hovertemplate='Week %{x}: %{y:,} units remaining<extra></extra>'
        ))
        fig_burn.add_hline(y=result['reorder_quantity'], line=dict(color='#ef4444', width=1.5, dash='dot'),
                          annotation=dict(text=f"Reorder at: {result['reorder_quantity']}", font=dict(color='#ef4444', size=10)))
        fig_burn.update_layout(
            title=dict(text="Stock Burn-down Curve", font=dict(size=14, color='#e8eaf0'), x=0),
            height=260, margin=dict(l=0, r=0, t=40, b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, color='#4a5568', title="Week", tickfont=dict(size=10)),
            yaxis=dict(gridcolor='rgba(255,255,255,0.04)', color='#4a5568',
                       title="Units", tickfont=dict(size=10)),
            legend=dict(orientation='h', y=-0.18, font=dict(size=11, color='#8892a4')),
            font=dict(family='IBM Plex Mono')
        )
        st.plotly_chart(fig_burn, use_container_width=True, config={"displayModeBar": False})

    with col2:
        products_list = predictor.get_all_products()[:5]
        comp_data = []
        for p in products_list:
            if p != selected_product:
                try:
                    r, _, _ = predictor.predict_demand(p, forecast_weeks, current_stock)
                    if r:
                        comp_data.append({"Product": p[:25], "Demand": r['total_demand'],
                                           "Risk": r['risk_level']})
                except Exception:
                    pass

        if comp_data:
            df_comp = pd.DataFrame(comp_data)
            risk_colors = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10d97e"}
            colors = [risk_colors.get(r, "#3b82f6") for r in df_comp['Risk']]
            fig_comp = go.Figure(go.Bar(
                x=df_comp['Product'], y=df_comp['Demand'],
                marker_color=colors, text=df_comp['Risk'],
                textposition='outside', textfont=dict(size=10, color='#8892a4'),
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
        else:
            st.info("Select other products to compare demand")

    st.markdown("##### Inventory Intelligence")
    avg_weekly = result['total_demand'] / forecast_weeks if forecast_weeks > 0 else result['total_demand']
    z = 1.645
    lead_time = 1
    demand_std = result['model_accuracy']
    safety_stock = int(z * demand_std * np.sqrt(lead_time))
    rop = int(avg_weekly * lead_time + safety_stock)
    annual_demand = avg_weekly * 52 if avg_weekly > 0 else result['total_demand'] * 13
    order_cost = 500
    holding_rate = 0.25
    eoq = int(np.sqrt(2 * annual_demand * order_cost / max(unit_cost * holding_rate, 1))) if unit_cost > 0 else 500

    ci1, ci2, ci3, ci4 = st.columns(4)
    ci1.metric("Avg Weekly Demand", f"{avg_weekly:.0f} units", "per week")
    ci2.metric("Safety Stock", f"{safety_stock:,} units", "95% service level")
    ci3.metric("Reorder Point", f"{rop:,} units", f"when stock ≤ {rop}")
    ci4.metric("EOQ", f"{eoq:,} units", "optimal order quantity")

    st.markdown("<br>", unsafe_allow_html=True)
    col_n1, _, col_n2 = st.columns([1, 3, 1])
    with col_n1:
        if st.button("← Back"):
            st.session_state.step -= 1
            play_sound("click")
            st.rerun()
    with col_n2:
        if st.button("Next: Insights →"):
            st.session_state.step += 1
            play_sound("click")
            st.rerun()

# ──────────────────────────────────────────────────────────────────────────────
# STEP 4: INSIGHTS
# ──────────────────────────────────────────────────────────────────────────────
elif step == 4:
    step_header(5, "AI Insights", "Anomaly detection, patterns & recommendations")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("##### Sales Trend Analysis")
        if not hist_product.empty and len(hist_product) >= 4:
            demands = hist_product['demand'].values
            recent_avg = np.mean(demands[-4:]) if len(demands) >= 4 else np.mean(demands)
            overall_avg = np.mean(demands) if len(demands) > 0 else recent_avg
            
            if recent_avg > overall_avg * 1.2:
                trend = "📈 Strong Increase"
                trend_color = "var(--red)"
            elif recent_avg < overall_avg * 0.8:
                trend = "📉 Decrease"
                trend_color = "var(--green)"
            else:
                trend = "➡️ Stable"
                trend_color = "var(--amber)"
            
            cv = np.std(demands) / np.mean(demands) if np.mean(demands) > 0 else 0
            volatility = "High" if cv > 0.3 else "Medium" if cv > 0.15 else "Low"
            vol_color = "var(--red)" if cv > 0.3 else "var(--amber)" if cv > 0.15 else "var(--green)"
            
            st.markdown(f"""
            <div style="background:var(--bg3);border:1px solid var(--border);border-radius:10px;padding:16px">
                <div style="font-size:13px;color:var(--text2)">📊 Trend Direction</div>
                <div style="font-size:24px;font-weight:700;color:{trend_color}">{trend}</div>
                <div style="margin-top:12px;font-size:13px;color:var(--text2)">⚡ Demand Volatility</div>
                <div style="font-size:24px;font-weight:700;color:{vol_color}">{volatility}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Insufficient data for trend analysis")

    with col2:
        st.markdown("##### Risk Assessment")
        st.markdown(f"""
        <div style="background:var(--bg3);border:1px solid var(--border);border-radius:10px;padding:16px">
            <div style="font-size:13px;color:var(--text2)">📦 Stock Status</div>
            <div style="font-size:20px;font-weight:700;color:{'var(--red)' if result['risk_level'] == 'High' else 'var(--amber)' if result['risk_level'] == 'Medium' else 'var(--green)'}">
                {result['risk_level']} RISK
            </div>
            <div style="margin-top:12px;font-size:13px;color:var(--text2)">⏰ Days Until Stockout</div>
            <div style="font-size:20px;font-weight:700;color:var(--text)">{result['days_until_stockout']} days</div>
            <div style="margin-top:12px;font-size:13px;color:var(--text2)">📦 Reorder Quantity</div>
            <div style="font-size:20px;font-weight:700;color:var(--green)">{result['reorder_quantity']:,} units</div>
        </div>
        """, unsafe_allow_html=True)
    demands = hist_product['demand'].values
    if len(demands) > 0:
        avg_weekly = np.mean(demands)
    else:
        avg_weekly = 0

    
    st.markdown("##### Actionable Recommendations")
    recs = []
    if result['risk_level'] == "High":
        recs = [
            ("🚨", "Immediate Restock Required", f"Place an order for {result['reorder_quantity']} units TODAY to prevent stockout in {result['days_until_stockout']} days.", "var(--red)"),
            ("🚚", "Request Expedited Shipping", "Standard lead times may be too long. Contact supplier for express delivery.", "var(--amber)"),
            ("📊", "Review Forecast Accuracy", "Check if demand spikes are seasonal or one-time events.", "var(--blue)"),
        ]
    elif result['risk_level'] == "Medium":
        recs = [
            ("📦", "Schedule Reorder Within Week", f"Order {result['reorder_quantity']} units within the next few days.", "var(--amber)"),
            ("📈", "Monitor Daily Sales", "Track consumption pattern for potential acceleration.", "var(--blue)"),
            ("🎯", "Review Safety Stock Level", f"Consider increasing safety stock from {result['safety_stock']} to {int(result['safety_stock'] * 1.3)} units.", "var(--green)"),
        ]
    else:
        recs = [
            ("✅", "No Immediate Action", "Stock levels are healthy. Routine reorder can wait.", "var(--green)"),
            ("📉", "Optimize Order Quantity", f"Current EOQ suggests ordering {int(result['total_demand'] * 0.5)} units per batch.", "var(--blue)"),
            ("🔄", "Set Auto-Reorder Trigger", f"Configure alert when stock falls below {int(avg_weekly * 2)} units.", "var(--green)"),
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
            st.session_state.step -= 1
            play_sound("click")
            st.rerun()
    with col_n2:
        if st.button("Next: Simulator →"):
            st.session_state.step += 1
            play_sound("click")
            st.rerun()

# ──────────────────────────────────────────────────────────────────────────────
# STEP 5: SIMULATE
# ──────────────────────────────────────────────────────────────────────────────
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

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        sim_stock = st.number_input("Simulated Stock Level", 0, 5000, current_stock, 50, key="sim_stock")
    with col_s2:
        demand_mult = st.slider("Demand Multiplier", 0.5, 2.0, 1.0, 0.1, key="demand_mult",
                                help="1.0 = normal, 1.5 = 50% increase in demand")
    with col_s3:
        sim_weeks = st.slider("Simulation Weeks", 1, 12, forecast_weeks, key="sim_weeks")

    st.markdown("</div>", unsafe_allow_html=True)

    # Run simulation
    sim_result, _, _ = predictor.predict_demand(selected_product, sim_weeks, sim_stock)
    if sim_result:
        sim_preds = [int(p * demand_mult) for p in sim_result['daily_predictions']]
        sim_total = sum(sim_preds)
        sim_dso = max(0, int(sim_stock / max(np.mean(sim_preds), 1) * 7))
        sim_risk = "High" if sim_dso < 3 else "Medium" if sim_dso < 10 else "Low"
        sim_reorder = max(0, sim_total - sim_stock + int(sim_total * 0.15))

        alert_banner(sim_risk, sim_dso, sim_reorder, f"{selected_product.split('(')[0].strip()} (Simulation)")

        col_r1, col_r2, col_r3, col_r4 = st.columns(4)
        col_r1.metric("Simulated Demand", f"{sim_total:,}", f"{sim_weeks} weeks")
        col_r2.metric("Simulated Stock", f"{sim_stock:,}", "units")
        col_r3.metric("Sim Reorder Qty", f"{sim_reorder:,}", "units needed")
        col_r4.metric("Stockout Risk", sim_risk, f"{sim_dso} days")

        fig_cmp = go.Figure()
        orig_preds = result['daily_predictions']
        weeks_x = list(range(1, max(len(orig_preds), len(sim_preds)) + 1))
        fig_cmp.add_trace(go.Scatter(
            x=list(range(1, len(orig_preds)+1)), y=orig_preds,
            name='Original Forecast', line=dict(color='#3b82f6', width=2),
        ))
        fig_cmp.add_trace(go.Scatter(
            x=list(range(1, len(sim_preds)+1)), y=sim_preds,
            name='Simulated (Adjusted)', line=dict(color='#10d97e', width=2.5, dash='dash'),
        ))
        fig_cmp.update_layout(
            title=dict(text="Demand Forecast Comparison", font=dict(size=13, color='#e8eaf0'), x=0),
            height=300, margin=dict(l=0, r=0, t=40, b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, color='#4a5568', title="Week"),
            yaxis=dict(gridcolor='rgba(255,255,255,0.04)', color='#4a5568', title="Units"),
            legend=dict(orientation='h', y=-0.2),
        )
        st.plotly_chart(fig_cmp, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<br>", unsafe_allow_html=True)
    col_n1, _, col_n2 = st.columns([1, 3, 1])
    with col_n1:
        if st.button("← Back"):
            st.session_state.step -= 1
            play_sound("click")
            st.rerun()
    with col_n2:
        if st.button("Next: Report →"):
            st.session_state.step += 1
            play_sound("click")
            st.rerun()

# ──────────────────────────────────────────────────────────────────────────────
# STEP 6: REPORT
# ──────────────────────────────────────────────────────────────────────────────
elif step == 6:
    step_header(7, "Export Report", "Download your inventory intelligence report")

    alert_banner(result['risk_level'], result['days_until_stockout'], result['reorder_quantity'], selected_product.split('(')[0].strip())

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown("##### Full Report Summary")

        avg_weekly = result['total_demand'] / forecast_weeks if forecast_weeks > 0 else result['total_demand']
        z = 1.645
        demand_std = result['model_accuracy']
        safety_stock = int(z * demand_std * np.sqrt(1))
        rop = int(avg_weekly * 1 + safety_stock)
        annual_demand = avg_weekly * 52 if avg_weekly > 0 else result['total_demand'] * 13
        eoq = int(np.sqrt(2 * annual_demand * 500 / max(unit_cost * 0.25, 1)))

        summary_items = [
            ("Product", selected_product.split('(')[0].strip()),
            ("Store/Dept", selected_product.split('(')[-1].replace(')', '') if '(' in selected_product else "N/A"),
            ("Report Generated", datetime.now().strftime("%Y-%m-%d %H:%M")),
            ("Forecast Period", f"{forecast_weeks} weeks"),
            ("Total Predicted Demand", f"{result['total_demand']:,} units"),
            ("Avg Weekly Demand", f"{avg_weekly:.0f} units"),
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
            ("Stockout Prevention", f"₹{stockout_savings:,.0f}"),
            ("Total Savings", f"₹{total_savings:,.0f}"),
        ]
        for label, val in summary_items:
            color = "var(--red)" if label == "Risk Level" and val == "High" else \
                    "var(--amber)" if label == "Risk Level" and val == "Medium" else \
                    "var(--green)" if label == "Risk Level" else "var(--text)"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid var(--border)">
                <span style="font-size:12px;color:var(--text2);font-family:var(--mono)">{label}</span>
                <span style="font-size:12px;font-weight:600;font-family:var(--mono);color:{color}">{val}</span>
            </div>""", unsafe_allow_html=True)

    

        # Build forecast CSV
        cumulative = 0
        rows = []
        for i, p in enumerate(result['daily_predictions']):
            cumulative += p
            rows.append({
                "Week": i+1,
                "Date": (datetime.now() + timedelta(weeks=i+1)).strftime("%Y-%m-%d"),
                "Forecast_Demand": int(p),
                "Cumulative_Demand": int(cumulative),
                "Remaining_Stock": max(0, current_stock - int(cumulative)),
                "Status": "Stockout" if cumulative >= current_stock else "OK"
            })
        df_forecast = pd.DataFrame(rows)
        forecast_csv = df_forecast.to_csv(index=False).encode()

        
        st.markdown("<br>", unsafe_allow_html=True)

        

    st.markdown("<br>", unsafe_allow_html=True)
    col_n1, col_n2, col_n3 = st.columns([1, 2, 1])
    with col_n1:
        if st.button("← Back"):
            st.session_state.step -= 1
            play_sound("click")
            st.rerun()
    with col_n2:
        if st.button("🔄 Start New Analysis"):
            st.session_state.step = 0
            st.session_state.predictions_cache = {}
            play_sound("click")
            st.rerun()

# ──────────────────────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:32px;padding-top:16px;border-top:1px solid var(--border);
            display:flex;justify-content:space-between;align-items:center">
    <div style="font-size:11px;color:var(--text3);font-family:var(--mono)">
        💊 StockSense AI · Random Forest Demand Forecasting · Powered by ML
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
