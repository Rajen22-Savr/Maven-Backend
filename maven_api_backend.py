
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from io import BytesIO
from typing import List, Dict

from insight_engine import run_all_insights

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InsightResponse(BaseModel):
    top_suppliers: List[Dict]
    outliers: List[Dict]
    actions: List[Dict]
    dynamic_insights: List[Dict]

@app.post("/upload/", response_model=InsightResponse)
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_excel(BytesIO(contents), sheet_name='Sheet1')
    df["Potential Savings"] = df["CY Quantity (Fiscal)"] * df["CY vs PY WAP USD (Fiscal)"]

    top_suppliers = (
        df.groupby("Supplier Name")["Potential Savings"]
        .sum()
        .sort_values(ascending=False)
        .head(3)
        .reset_index()
        .to_dict(orient="records")
    )

    outliers = (
        df.assign(abs_change=abs(df["CY vs PY WAP USD (Fiscal)"]))
        .sort_values("abs_change", ascending=False)
        .head(3)[["Supplier Name", "Item Name", "CY vs PY WAP USD (Fiscal)"]]
        .to_dict(orient="records")
    )

    actions = [
        {
            "type": "Renegotiate Pricing",
            "supplier": top_suppliers[0]["Supplier Name"],
            "savings": f"${top_suppliers[0]['Potential Savings']:,.0f}"
        },
        {
            "type": "Consolidate Tail Spend",
            "note": "3+ suppliers under $10K spend"
        },
        {
            "type": "Rationalize Overlapping Materials",
            "note": "Multiple suppliers provide similar materials"
        }
    ]

    dynamic_insights = run_all_insights(df)

    return InsightResponse(
        top_suppliers=top_suppliers,
        outliers=outliers,
        actions=actions,
        dynamic_insights=dynamic_insights
    )
