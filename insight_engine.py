
from typing import List, Dict
import pandas as pd

Insight = Dict[str, str]

def unit_price_variance(df: pd.DataFrame) -> List[Insight]:
    output = []
    grouped = df.groupby('Item Number')

    for item, group in grouped:
        if group['CY WAP USD (Fiscal)'].nunique() > 1:
            price_range = group['CY WAP USD (Fiscal)'].max() / max(group['CY WAP USD (Fiscal)'].min(), 0.01)
            if price_range > 1.5:
                insight_text = f"Item {item} has a {price_range:.1f}x price spread across suppliers."
                output.append({
                    "type": "Unit Price Variance",
                    "item": item,
                    "metric": f"{price_range:.1f}x spread",
                    "impact": "Moderate",
                    "insight_text": insight_text,
                    "recommended_action": "Standardize pricing or renegotiate contracts"
                })
    return output

def supplier_concentration(df: pd.DataFrame) -> List[Insight]:
    output = []
    supplier_spend = df.groupby("Supplier Name")["CY WAP * CY QTY"].sum()
    total = supplier_spend.sum()

    for supplier, spend in supplier_spend.items():
        share = spend / total
        if share > 0.4:
            output.append({
                "type": "Supplier Overdependence",
                "supplier": supplier,
                "metric": f"{share:.0%} of total spend",
                "impact": "High",
                "insight_text": f"{supplier} accounts for {share:.0%} of total spend — potential risk.",
                "recommended_action": "Evaluate diversification or dual-sourcing."
            })
    return output

def missed_volume_discount(df: pd.DataFrame) -> List[Insight]:
    output = []
    volume_data = df.groupby('Item Number')['CY Quantity (Fiscal)'].sum()
    for item, total_qty in volume_data.items():
        if total_qty > 10000:
            output.append({
                "type": "Missed Volume Discount",
                "item": item,
                "metric": f"{int(total_qty)} units purchased",
                "impact": "Moderate",
                "insight_text": f"Item {item} exceeds 10,000 units purchased — missed bulk discount opportunity.",
                "recommended_action": "Consolidate volume and renegotiate pricing."
            })
    return output

def run_all_insights(df: pd.DataFrame) -> List[Insight]:
    insights = []
    insights += unit_price_variance(df)
    insights += supplier_concentration(df)
    insights += missed_volume_discount(df)
    return insights
