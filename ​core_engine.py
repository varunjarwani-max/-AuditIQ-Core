"""
AuditIQ — On-Premise Server Pipeline (Core Engine)
=========================================================
This script simulates AuditIQ's server-side architecture.

DEPLOYMENT MODEL: Client Server (On-Premise)
To ensure zero data exfiltration, AuditIQ is deployed directly 
on the client's internal servers. 

RESOURCE OPTIMIZATION: 
Enterprise servers for mid-market clients rarely have massive 
GPU clusters. To run Gemma 3.1 efficiently on a single-GPU server, 
we utilize a Sequential Batch Pipeline:
1. Load specialized Model 1 into Server VRAM.
2. Process the batch.
3. Unload to free VRAM for the next model.
"""

import random
from datetime import date, timedelta

# --- SERVER GPU NODE MANAGEMENT ---
def load_model_to_vram(model_name, size="3B"):
    print(f"🔄 [SERVER NODE] Allocating {model_name} ({size}) into GPU VRAM...")

def unload_model_from_vram(model_name):
    print(f"🗑️  [SERVER NODE] Deallocating {model_name} to free GPU compute.\n")

# --- DATA GENERATOR ---
def generate_fake_transactions(n=10):
    VENDORS = ["Acme Supplies", "Globex Traders", "Initech Services", "Wayne Holdings"]
    CATEGORIES = ["Office Supplies", "Consulting", "Equipment", "Software"]
    transactions = []
    
    for i in range(n):
        is_suspicious = random.random() < 0.2
        amount = round(random.uniform(50, 4000), 2)
        if is_suspicious:
            # Injecting heuristic anomalies for testing
            amount = random.choice([9999.00, 15000.00, 5099.00])
            
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
        
    # Manually inject a duplicate for testing Stage 1.5
    transactions.append({
        "id": "TXN9999",
        "date": str(date.today()),
        "vendor": "Acme Supplies",
        "category_hint": "Office Supplies",
        "amount": transactions[0]["amount"], # Duplicates the first transaction's amount
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
    amount = txn["amount"]
    score = 0.10
    flag = None
    
    # 1. High-value threshold check
    if amount > 8000:
        score = max(score, 0.75)
        flag = "HIGH_VALUE_THRESHOLD"
        
    # 2. Heuristic for suspicious round numbers (e.g., exactly $5000 or ending in .99)
    if amount % 1000 == 0 or amount % 100 == 99:
        score = max(score, 0.85)
        flag = "SUSPICIOUS_ROUND_NUMBER"
        
    return {"score": score, "flag": flag}

def model_deep_reasoning(txn):
    vendor = txn["vendor"]
    amount = txn["amount"]
    flag = txn["pipeline_data"].get("risk_flag")
    
    if flag == "SUSPICIOUS_ROUND_NUMBER":
        return f"CRITICAL: {vendor} transaction for ${amount} presents unusual trailing digits or ceiling limit. Potential manual override."
    elif flag == "HIGH_VALUE_THRESHOLD":
        return f"WARNING: {vendor} transaction for ${amount} exceeds standard materiality thresholds. Requires invoice verification."
    return "Standard verification required."

# --- SEQUENTIAL ORCHESTRATOR ---
def run_audiq_sequential_pipeline(batch):
    print("\n=== INITIATING AUDITIQ SERVER PIPELINE ===")
    print(f"Processing Batch Size: {len(batch)} transactions\n")

    # STAGE 1: Classification
    load_model_to_vram("Gemma-3.1-Account-Classifier")
    for txn in batch:
        txn["pipeline_data"]["account_type"] = model_account_classifier(txn)
    unload_model_from_vram("Gemma-3.1-Account-Classifier")

    # STAGE 1.5: Duplicate Detection (Hash Comparison)
    print("🔄 [SYSTEM] Running deterministic duplicate detection sweep...")
    seen_transactions = {}
    for txn in batch:
        # Create a unique hash based on vendor and exact amount
        txn_hash = f"{txn['vendor']}_{txn['amount']}"
        if txn_hash in seen_transactions:
            txn["pipeline_data"]["risk_score"] = 0.95
            txn["pipeline_data"]["risk_flag"] = "POTENTIAL_DUPLICATE"
        else:
            seen_transactions[txn_hash] = True
    print("✅  [SYSTEM] Duplicate sweep complete.\n")

    # STAGE 2: Risk Assessment
    load_model_to_vram("Gemma-3.1-Risk-Evaluator")
    for txn in batch:
        # Only evaluate if not already flagged as a duplicate
        if txn["pipeline_data"].get("risk_flag") != "POTENTIAL_DUPLICATE":
            risk = model_risk_evaluator(txn)
            txn["pipeline_data"]["risk_score"] = risk["score"]
            txn["pipeline_data"]["risk_flag"] = risk["flag"]
    unload_model_from_vram("Gemma-3.1-Risk-Evaluator")

    # FILTER: Only pass high-risk items to Stage 3
    high_risk_batch = [t for t in batch if t["pipeline_data"].get("risk_score", 0) > 0.70]
    
    # STAGE 3: Deep Reasoning (Heavy Compute)
    if high_risk_batch:
        load_model_to_vram("Gemma-3.1-Deep-Reasoning-Agent", size="9B")
        for txn in high_risk_batch:
            flag = txn["pipeline_data"]["risk_flag"]
            if flag == "POTENTIAL_DUPLICATE":
                txn["pipeline_data"]["audit_finding"] = f"CRITICAL: Exact match found for {txn['vendor']} at ${txn['amount']}. High risk of double-billing."
            else:
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
        print(f"Risk Flag: {item['pipeline_data']['risk_flag']}")
        print(f"Action: {item['pipeline_data']['audit_finding']}\n")
