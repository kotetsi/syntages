# Συνταγές Μαγειρικής

Στατικό site συνταγών με αυτόματο κόστος ανά μερίδα.

- `data/recipes/*.json` — μία συνταγή ανά αρχείο
- `data/prices.json` — τιμές υλικών (ανά κιλό ή λίτρο)
- `data/site.json` — όνομα site και `base_url` (το domain, μόλις οριστεί)
- `images/` — φωτογραφίες συνταγών (πεδίο `image` στη συνταγή, π.χ. `images/fasolada.jpg`)
- `python3 build.py` — χτίζει το site στο `_site/`

Σε κάθε push στο `main` το GitHub Actions χτίζει και δημοσιεύει το site στο GitHub Pages.

## Καθημερινή ενημέρωση τιμών

1. Σε μια σελίδα του sklavenitis.gr εκτέλεσε το `tools/fetch_prices.js` και μετά
   `await fetchPrices(<περιεχόμενο του tools/price_map.json>)`. Αποθήκευσε το JSON που επιστρέφει.
2. `python3 tools/apply_prices.py <αρχείο>.json "<ημερομηνία>"` — ενημερώνει το `data/prices.json`
   (κρατάει την παλιά τιμή αν το προϊόν λείπει ή η αλλαγή ξεπερνά το 60%).
3. `python3 build.py`, commit και push.

Το `tools/price_map.json` ορίζει για κάθε υλικό την αναζήτηση, το SKU του προϊόντος αναφοράς και
πώς μετατρέπεται η τιμή (`kg`: τιμή ανά κιλό/λίτρο, `piece`: τιμή τεμαχίου, `factor`: πολλαπλασιαστής).
