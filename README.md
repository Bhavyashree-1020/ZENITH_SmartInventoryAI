# ZENITH_SmartInventoryAI
AI-powered demand forecasting an smart restocking engine for  businesses — predicts stockouts before they happen

# 📦 Smart Inventory & Demand Prediction System

An AI-powered system that predicts product demand using machine learning and helps optimize inventory levels for retail and pharmacy businesses.

---

## 🚀 Features

- 📊 Real-time demand prediction
- 📦 Inventory stock alert system
- 📈 Data analytics dashboard
- 🧠 Machine learning-based forecasting
- 🏪 Supports retail & pharmacy datasets

---

## 🧠 Problem Statement

Retailers and pharmacies often face:
- Overstocking (waste & loss)
- Stockouts (lost sales)
- Poor demand forecasting

This system solves it using Machine Learning.

---

## 📂 Dataset Used

- stores.csv
- features.csv
- sales.csv / train.csv

After merging:
- Store-level sales data
- External factors (weather, CPI, fuel price, holidays)

---

## ⚙️ Tech Stack

- Python
- Pandas, NumPy
- Scikit-learn
- Streamlit
- Matplotlib

---

## 🤖 Machine Learning Model

- Algorithm: Random Forest Regressor
- Input Features:
  - Store
  - Dept
  - Temperature
  - Fuel Price
  - CPI
  - Unemployment
  - IsHoliday

- Output:
  - Weekly Sales Prediction (Demand)

---

## 📊 System Modules

### 1. Dashboard
- Dataset overview
- Sales distribution graph

### 2. Demand Prediction
- User input-based prediction
- Stock alert system

### 3. Analytics
- Top stores by sales
- Department-wise performance

---

## 🛠️ Installation

```bash
pip install pandas numpy scikit-learn streamlit matplotlib