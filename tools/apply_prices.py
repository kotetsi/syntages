#!/usr/bin/env python3
"""Εφαρμόζει τις τιμές που επέστρεψε το tools/fetch_prices.js στο data/prices.json.

Χρήση: python3 tools/apply_prices.py fetched.json "6 Νοεμβρίου 2026"
Κρατάει την παλιά τιμή όταν το προϊόν δεν βρέθηκε ή η αλλαγή είναι ύποπτα μεγάλη (>60%),
και τυπώνει αναφορά με όλες τις αλλαγές.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
fetched = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
date = sys.argv[2]
MAP = json.loads((ROOT / "tools/price_map.json").read_text(encoding="utf-8"))
pp = ROOT / "data/prices.json"
P = json.loads(pp.read_text(encoding="utf-8"))
changed, kept, flagged = [], [], []
for k, m in MAP.items():
    item = P["items"].get(k)
    f = fetched.get(k, {})
    if not item:
        continue
    base = f.get("per_piece") if m["mode"] == "piece" else f.get("per_kg")
    if not f.get("found") or base is None:
        kept.append(f"{item['name']}: δεν βρέθηκε το προϊόν αναφοράς, κρατήθηκε {item['price']:.2f} €")
        continue
    new = round(base * m["factor"], 2)
    old = item["price"]
    if old and abs(new - old) / old > 0.6:
        flagged.append(f"{item['name']}: {old:.2f} → {new:.2f} € (μεγάλη αλλαγή, ΔΕΝ εφαρμόστηκε)")
        continue
    item["product"] = f.get("title") or item.get("product", "")
    if new != old:
        changed.append(f"{item['name']}: {old:.2f} → {new:.2f} €")
        item["price"] = new
P["_updated"] = date
P["_note"] = (f"Τιμές από το e-shop του Σκλαβενίτη (sklavenitis.gr), ενημέρωση {date}. "
              "Για κάθε υλικό παίρνουμε ένα συνηθισμένο προϊόν της καθημερινής αγοράς, όχι το ακριβότερο ή προσφορά.")
pp.write_text(json.dumps(P, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"Αλλαγές: {len(changed)}")
for s in changed + flagged + kept:
    print(" -", s)
