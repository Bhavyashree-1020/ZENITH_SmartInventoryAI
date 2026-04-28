
# 📊 StockSense AI - Smart Inventory & Demand Prediction System

 **Smart inventory management system **  
 -Predict demand, prevent stockouts, and reduce waste using machine learning


## 🎯 Overview

**StockSense AI** solves a critical business problem: **inventory mismanagement** costs retailers billions annually in stockouts and waste.

### The Problem
| Issue | Impact |
|-------|--------|
| Stockouts | Lost sales, angry customers |
| Overstocking | Wasted money, expired products |
| Manual guessing | Inefficient, inconsistent |

### Our Solution
- 🔮 **AI predicts** future demand with 85%+ accuracy
- 🚨 **Real-time alerts** prevent stockouts
- 💰 **Cost savings** calculated automatically
- 📊 **Interactive dashboard** for easy decision making

---

## ✨ Features

### 🏠 7-Step Interactive Dashboard

| Step | Feature | What It Does |
|------|---------|--------------|
| 1 | **Setup** | Configure product, stock, forecast period |
| 2 | **Overview** | View KPIs, risk level, savings |
| 3 | **Forecast** | AI demand predictions with confidence bands |
| 4 | **Inventory** | Stock health, EOQ, reorder points |
| 5 | **Insights** | AI recommendations & trend analysis |
| 6 | **Simulate** | Test "what-if" scenarios |
| 7 | **Report** | Download CSV reports |

### 🔥 Key Capabilities

```

✅ Random Forest demand forecasting
✅ Multi-product comparison
✅ Audio alerts for critical stockouts
✅ CSV report generation
✅ What-if simulation
✅ Stock burn-down analysis
✅ Real-time savings calculator
✅ 80% confidence intervals

### Screenshots

**Dashboard Overview**


┌─────────────────────────────────────────────────────────────┐
│  📊 Smart Inventory & Demand Prediction System              │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ Demand   │ │ Stock    │ │ Reorder  │ │ Risk     │       │
│  │ 1,214    │ │ 150      │ │ 1,246    │ │ HIGH     │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│                                                             │
│  🚨 CRITICAL STOCKOUT ALERT                                 │
│  Milk will stockout in 1 days. Order 1,246 units NOW.      │
│                                                             │
│  📈 Demand Forecast Chart                                   │
│  [Historical Data ───] [Forecast - - -]                    │
│                                                             │
│  💰 Total Savings: ₹1,238 per week                         │
└─────────────────────────────────────────────────────────────┘


## 📊 Dataset Format

### Required CSV Structure

Place `smart_inventory_dataset.csv` in the project folder:

```csv
date,store,dept,product,weekly_sales,stock,category
2024-01-07,1,1,Aspirin,125,450,Medicine
2024-01-14,1,1,Aspirin,118,332,Medicine
2024-01-21,1,1,Aspirin,95,237,Medicine
2024-01-28,1,1,Aspirin,142,95,Medicine
```

Column Specifications

Column Type Required Description
date Date ✅ Yes Transaction/Week date
store Integer ✅ Yes Store identifier
dept Integer ✅ Yes Department ID
product String ✅ Yes Product name
weekly_sales Integer ✅ Yes Units sold per week
stock Integer ✅ Yes Current inventory


🚀 Installation

Prerequisites

· Python 3.8 or higher
· pip package manager

Step-by-Step Setup

```bash
# 1. Clone the repository
git clone https://github.com/Bhavyashree-1020/StockSense-AI.git
cd StockSense-AI

# 2. Install dependencies
pip install -r requirements.txt

# 3. Place your CSV file
# Copy smart_inventory_dataset.csv to this folder

# 4. Run the application
streamlit run streamlit.py
```

requirements.txt

```txt
streamlit==1.28.0
pandas==2.1.0
numpy==1.24.0
plotly==5.17.0
scikit-learn==1.3.0
```

---

📖 Usage Guide

Quick Start Workflow

1. Launch the app → streamlit run streamlit.py
2. Select product from sidebar dropdown
3. Set current stock level
4. Choose forecast weeks (1-12 weeks)
5. Navigate through 7 steps using sidebar buttons

Understanding the Alerts

Alert Color Risk Level Days Until Stockout Action Required
🔴 Red High < 3 days ORDER IMMEDIATELY
🟠 Orange Medium 3-10 days Plan reorder this week
🟢 Green Low 10 days Routine monitoring

What Each Metric Means

Metric Definition Business Impact
Total Demand Predicted sales over forecast period How much to prepare
Current Stock Units in inventory Current position
Reorder Quantity Units to order What to buy
Days Until Stockout When stock runs out Urgency level
Safety Stock Buffer for uncertainty Risk protection
EOQ Economic Order Quantity Cost optimization
Model MAE Prediction accuracy (± units) Trust in forecast

---

🛠️ Tech Stack

Component Technology Purpose
Frontend Streamlit Interactive dashboard
ML Model Random Forest (scikit-learn) Demand prediction
Charts Plotly Interactive visualizations
Data Processing Pandas, NumPy Data manipulation
Audio Alerts Web Audio API Sound notifications

---

📁 Project Structure

```
StockSense-AI/
│
├── streamlit.py                 # Main application (1218 lines)
├── smart_inventory_dataset.csv  # Your data file
├── requirements.txt             # Python dependencies
├── README.md                    # Documentation
├── LICENSE                      # MIT License
├── .gitignore                   # Git ignore file

---

