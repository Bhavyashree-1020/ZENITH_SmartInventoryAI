def predict_demand(month, weekday, stock):
    # Simple logic-based prediction (for prototype)
    demand = (month * 5) + (weekday * 3) + 20
    
    reorder = demand - stock
    
    return demand, max(0, reorder)