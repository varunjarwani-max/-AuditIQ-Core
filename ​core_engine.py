"""
AuditIQ — Sequential Multi-Model Pipeline (Core Engine)
=========================================================
This script simulates AuditIQ's core on-device architecture.

CRITICAL HARDWARE CONSTRAINT: 
To run entirely locally on a laptop without exceeding VRAM limits, 
we cannot load all AI models at once. 

Architecture: "One Model At A Time" (Batch Processing)
1. Load Model 1 into memory.
2. Run entire transaction batch through Model 1.
3. Unload Model 1 to free VRAM.
4. Load Model 2 into memory... and so on.

When deployed, these simulated functions will be replaced with 
quantized Gemma 3.1 models running via Apple MLX.
"""

import random
from datetime import date, timedelta

# --- MOCK VRAM MANAGEMENT ---
def load_model_to_vram(model_name, size="3B"):
    print(f"🔄 [SYSTEM] Loading {model_name} ({size}) into Unified Memory...")

def unload_model_from_vram(model_name):
    print(f"🗑️  [SYSTEM] Unloading {model_name} to free memory for next stage.\n")

# --- DATA GENERATOR ---
def generate_fake_transactions(n=10):
    VENDORS = ["Acme Supplies", "Globex Traders", "Initech Services", "Wayne Holdings"]
    CATEGORIES = ["Office Supplies", "Consulting", "Equipment", "Software"]
    transactions = []
    
    for i in range(n):
        is_suspicious = random.random() < 0.2
        amount = round(random.uniform(50, 4000), 2)
        if is_suspicious:
            amount = 9999.00
            
        transactions.append({
            "id": f"TXN{1000 + i}",
            "date": str(date.today() - timedelta(days=random.randint(0, 90))),
            "vendor": random.choice(VENDORS),
            "category_hint": random.choice(CATEGORIES),
            "amount": amount,
            "currency": "USD",
            "duplicate_of": None,
            "pipeline_data": {} 
        })
    return transactions

# --- PIPELINE MODELS ---
def model_account_classifier(txn):
    mapping = {"Office Supplies": "Operating Expense", "Consulting": "Operating Expense", "Equipment": "Capital Expense"}
    return mapping.get(txn["category_hint"], "Unclassified")

def model_risk_evaluator(txn):
    if txn["amount"] == 9999.00:
        return {"score": 0.90, "flag": "SUSPICIOUS_ROUND_NUMBER"}
    return {"score": 0.10, "flag": None}

def model_deep_reasoning(txn):
    vendor = txn["vendor"]
    amount = txn["amount"]
    flag = txn["pipeline_data"].get("risk_flag")
    
    if flag == "SUSPICIOUS_ROUND_NUMBER":
        return f"CRITICAL: {vendor} transaction for ${amount} hits exact ceiling ($9,999). Likely manual override to avoid procurement review."
    return "Standard verification required."

# --- SEQUENTIAL ORCHESTRATOR ---
def run_audiq_sequential_pipeline(batch):
    print("\n=== INITIATING AUDITIQ SEQUENTIAL PIPELINE ===")
    print(f"Processing Batch Size: {len(batch)} transactions\n")

    # STAGE 1: Classification
    load_model_to_vram("Gemma-3.1-Account-Classifier")
    for txn in batch:
        txn["pipeline_data"]["account_type"] = model_account_classifier(txn)
    unload_model_from_vram("Gemma-3.1-Account-Classifier")

    # STAGE 2: Risk Assessment
    load_model_to_vram("Gemma-3.1-Risk-Evaluator")
    for txn in batch:
        risk = model_risk_evaluator(txn)
        txn["pipeline_data"]["risk_score"] = risk["score"]
        txn["pipeline_data"]["risk_flag"] = risk["flag"]
    unload_model_from_vram("Gemma-3.1-Risk-Evaluator")

    # FILTER: Only pass high-risk items to Stage 3
    high_risk_batch = [t for t in batch if t["pipeline_data"]["risk_score"] > 0.70]
    
    # STAGE 3: Deep Reasoning
    if high_risk_batch:
        load_model_to_vram("Gemma-3.1-Deep-Reasoning-Agent", size="9B")
        for txn in high_risk_batch:
            txn["pipeline_data"]["audit_finding"] = model_deep_reasoning(txn)
        unload_model_from_vram("Gemma-3.1-Deep-Reasoning-Agent")

    return high_risk_batch

# --- EXECUTION ---
if __name__ == "__main__":
    raw_data = generate_fake_transactions(15)
    flagged_results = run_audiq_sequential_pipeline(raw_data)
    
    print("=== FINAL AUDIT REPORT (HIGH RISK ONLY) ===")
    for item in flagged_results:
        print(f"[{item['id']}] {item['vendor']} - ${item['amount']}")
        print(f"Action: {item['pipeline_data']['audit_finding']}\n")
