# Συνταγές Μαγειρικής

Στατικό site συνταγών με αυτόματο κόστος ανά μερίδα.

- `data/recipes/*.json` — μία συνταγή ανά αρχείο
- `data/prices.json` — τιμές υλικών (ανά κιλό ή λίτρο)
- `data/site.json` — όνομα site και `base_url` (το domain, μόλις οριστεί)
- `images/` — φωτογραφίες συνταγών (πεδίο `image` στη συνταγή, π.χ. `images/fasolada.jpg`)
- `python3 build.py` — χτίζει το site στο `_site/`

Σε κάθε push στο `main` το GitHub Actions χτίζει και δημοσιεύει το site στο GitHub Pages.
