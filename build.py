#!/usr/bin/env python3
"""Χτίζει το site από τα αρχεία της φακέλου data/ στη φάκελο _site/.

Νέα συνταγή: πρόσθεσε ένα αρχείο data/recipes/<slug>.json.
Νέα τιμή υλικού: άλλαξε το data/prices.json — το κόστος όλων των συνταγών ξαναϋπολογίζεται.
Εκτέλεση: python3 build.py
"""
import json, shutil, html, sys, hashlib
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
site = json.loads((ROOT / "data/site.json").read_text(encoding="utf-8"))
prices_doc = json.loads((ROOT / "data/prices.json").read_text(encoding="utf-8"))
PRICES = prices_doc["items"]
UPDATED = prices_doc["_updated"]
BASE = site.get("base_url", "").rstrip("/")  # π.χ. https://www.domain.gr — κενό μέχρι να μπει domain
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Literata:opsz,wght@7..72,500;7..72,700'
         '&family=Commissioner:wght@400;500;600&display=swap">')
e = lambda s: html.escape(str(s), quote=True)
VER = hashlib.md5((ROOT / "assets/style.css").read_bytes() + (ROOT / "assets/recipe.js").read_bytes()).hexdigest()[:8]


def eur(v):
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} €"


def half(n):
    r = round(n * 2) / 2
    return str(int(r)) if r == int(r) else f"{r:.1f}".replace(".", ",")


def qty(i, f=1.0):
    if i.get("show"):
        return f"{half(i['show'][0] * f)} {i['show'][1]}"
    if PRICES[i["item"]]["unit"] == "τεμ":
        return f"{half(i['qty'] * f)} τεμ."
    unit = "ml" if PRICES[i["item"]]["unit"] == "l" else "g"
    q = i["qty"] * f
    q = round(q / 10) * 10 if q >= 100 else max(1, round(q))
    if q >= 1000:
        v = f"{q / 1000:.2f}".rstrip("0").rstrip(".").replace(".", ",")
        return f"{v} {'l' if unit == 'ml' else 'kg'}"
    return f"{q} {unit}"


def ing_cost(i):
    if i["item"] not in PRICES:
        sys.exit(f"Λείπει τιμή για το υλικό '{i['item']}' στο data/prices.json")
    x = PRICES[i["item"]]
    return x["price"] * i["qty"] if x["unit"] == "τεμ" else x["price"] * i["qty"] / 1000


def load_recipes():
    rs = []
    for p in sorted((ROOT / "data/recipes").glob("*.json")):
        r = json.loads(p.read_text(encoding="utf-8"))
        r["total"] = sum(ing_cost(i) for i in r["ingredients"])
        r["per"] = r["total"] / r["servings"]
        rs.append(r)
    return rs


def page(title, desc, body, root, path, extra_head=""):
    canon = f'<link rel="canonical" href="{BASE}/{path}">' if BASE else ""
    return f"""<!doctype html>
<html lang="{site['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
{canon}
{FONTS}
<link rel="stylesheet" href="{root}assets/style.css?v={VER}">
{extra_head}
</head>
<body>
<div class="wrap">
  <header class="site">
    <a class="brand" href="{root}">{e(site['name'])}</a>
    <nav><a href="{root}">Συνταγές</a><a href="{root}times/">Τιμές υλικών</a></nav>
  </header>
  <main>
{body}
  </main>
  <footer class="site">© {e(site['name'])} · Οι τιμές υλικών ενημερώθηκαν: {e(UPDATED)}</footer>
</div>
<script src="{root}assets/recipe.js?v={VER}" defer></script>
</body>
</html>
"""


def img_url(r, root):
    u = r.get("image", "")
    return u if u.startswith("http") else f"{root}{u}"


def photo(r, root, label, credit=False):
    if r.get("image"):
        c = r.get("image_credit")
        cap = (f'<figcaption>Φωτογραφία: <a href="{e(c["url"])}" rel="nofollow noopener" target="_blank">{e(c["name"])}</a> / {e(c["source"])}</figcaption>'
               if credit and c else "")
        lazy = "" if credit else ' loading="lazy"'
        return f'<figure class="photo has-img"><img src="{e(img_url(r, root))}" alt="{e(r["title"])}"{lazy}>{cap}</figure>'
    return f'<div class="photo noimg"><span>{e(r["title"])}</span></div>'


def build_home(rs):
    cats = ["Όλες"] + sorted({c for r in rs for c in r["categories"]}, key=lambda c: c)
    chips = "".join(f'<button class="chip" aria-pressed="{"true" if c == "Όλες" else "false"}" data-c="{e(c)}">{e(c)}</button>' for c in cats)
    cards = "".join(f"""
      <a class="card" href="syntages/{r['slug']}/" data-cats="{e('|'.join(r['categories']))}" data-search="{e((r['title'] + ' ' + ' '.join(i['text'] for i in r['ingredients'])).lower())}">
        {photo(r, '', 'Φωτογραφία: ' + r['title'])}
        <h3>{e(r['title'])}</h3>
        <div class="meta"><span class="cost-pill">{eur(r['per'])} <small>/ {r.get('serving_label', ['', 'μερίδα'])[1]}</small></span><span>{r['prep'] + r['cook']}′</span><span>{e(r['difficulty'])}</span></div>
      </a>""" for r in rs)
    body = f"""
    <p class="eyebrow">Ελληνικές συνταγές με κόστος</p>
    <h1>Μαγείρεμα σπιτικό, με τον λογαριασμό μπροστά σου</h1>
    <p class="lead">Κάθε συνταγή δείχνει πόσο κοστίζει η μερίδα με τις τρέχουσες τιμές των υλικών στο σουπερμάρκετ.</p>
    <div class="search"><label for="q" class="eyebrow">Αναζήτηση</label><input id="q" type="search" placeholder="π.χ. φακές, κοτόπουλο, σπανάκι" autocomplete="off"></div>
    <div class="filters" role="group" aria-label="Κατηγορίες">{chips}</div>
    <p class="note" id="count">{len(rs)} συνταγές</p>
    <div class="grid">{cards}</div>"""
    (OUT / "index.html").write_text(page(f"{site['name']} · {site['tagline']}", site["tagline"], body, "", ""), encoding="utf-8")


def schema(r, path):
    s = {"@context": "https://schema.org", "@type": "Recipe", "name": r["title"], "description": r["intro"],
         "recipeCategory": r["categories"][0], "recipeCuisine": "Ελληνική", "keywords": ", ".join(r["categories"]),
         "recipeYield": f"{r['servings']} {r.get('serving_label', ['μερίδες'])[0]}",
         "prepTime": f"PT{r['prep']}M", "cookTime": f"PT{r['cook']}M", "totalTime": f"PT{r['prep'] + r['cook']}M",
         "estimatedCost": {"@type": "MonetaryAmount", "currency": "EUR", "value": f"{r['total']:.2f}"},
         "recipeIngredient": [f"{qty(i)} {i['text']}" for i in r["ingredients"]],
         "recipeInstructions": [{"@type": "HowToStep", "text": t} for t in r["steps"]],
         "author": {"@type": "Organization", "name": site["name"]}}
    if r.get("image"):
        u = r["image"]
        if u.startswith("http"):
            s["image"] = [u]
        elif BASE:
            s["image"] = [f"{BASE}/{u}"]
    if BASE:
        s["url"] = f"{BASE}/{path}"
    return s


def build_recipe(r):
    path = f"syntages/{r['slug']}/"
    root = "../../"
    SL = r.get("serving_label", ["μερίδες", "μερίδα"])
    items = "".join(f'<li><span><span class="amt">{qty(i)}</span> {e(i["text"])}</span><span class="ic">{eur(ing_cost(i))}</span></li>'
                    for i in r["ingredients"])
    data = {"servings": r["servings"], "label": SL[0], "ingredients": [
        {"qty": i["qty"], "show": i.get("show"), "unit": PRICES[i["item"]]["unit"], "cost": ing_cost(i)} for i in r["ingredients"]]}
    body = f"""
    <a href="{root}" class="crumb">← Όλες οι συνταγές</a>
    <div class="r-head" style="margin-top:14px">
      <div>
        <p class="eyebrow">{' · '.join(e(c) for c in r['categories'])}</p>
        <h1>{e(r['title'])}</h1>
        <p class="lead">{e(r['intro'])}</p>
        <div class="facts">
          <div><span>Προετοιμασία</span><b>{r['prep']}′</b></div>
          <div><span>Μαγείρεμα</span><b>{r['cook']}′</b></div>
          <div><span>Δυσκολία</span><b>{e(r['difficulty'])}</b></div>
          <div><span>Ανά {SL[1]}</span><b id="pp">{eur(r['per'])}</b></div>
        </div>
        <a class="jump" href="#syntagi">Πήγαινε στη συνταγή ↓</a>
      </div>
      {photo(r, root, 'Κεντρική φωτογραφία πιάτου', credit=True)}
    </div>
    <div class="body" id="syntagi">
      <aside class="panel">
        <h2>Υλικά</h2>
        <div class="servings">
          <button id="minus" type="button" aria-label="Λιγότερες μερίδες">−</button>
          <output id="sv" aria-live="polite">{r['servings']} {SL[0]}</output>
          <button id="plus" type="button" aria-label="Περισσότερες μερίδες">+</button>
        </div>
        <ul class="ing" id="ing">{items}</ul>
        <div class="total"><span>Σύνολο <span id="tsv">για {r['servings']}</span></span><strong id="tot">{eur(r['total'])}</strong></div>
        <p class="note">Τιμές: {e(UPDATED)}. <a href="{root}times/">Δες τον πίνακα τιμών</a>.</p>
      </aside>
      <section>
        <h2>Εκτέλεση</h2>
        <ol class="steps">{''.join(f'<li><p>{e(s)}</p></li>' for s in r['steps'])}</ol>
        <div class="tips"><h3>Συμβουλές και διατήρηση</h3><ul>{''.join(f'<li>{e(t)}</li>' for t in r['tips'])}</ul></div>
      </section>
    </div>
    <script type="application/json" id="recipe-data">{json.dumps(data, ensure_ascii=False)}</script>"""
    ld = f'<script type="application/ld+json">{json.dumps(schema(r, path), ensure_ascii=False)}</script>'
    desc = f"{r['intro']} Κόστος περίπου {eur(r['per'])} τη μερίδα."
    d = OUT / path
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(page(f"{r['title']} · {site['name']}", desc, body, root, path, ld), encoding="utf-8")


UNIT_LABEL = {"l": "λίτρο", "kg": "κιλό", "τεμ": "τεμάχιο"}


def build_prices(rs):
    rows = "".join(
        f'<tr><td>{e(x["name"])}</td><td class="n">{eur(x["price"])}</td><td>ανά {UNIT_LABEL[x["unit"]]}</td><td class="prod">{e(x.get("product", "ενδεικτική τιμή"))}</td>'
        f'<td class="n">{sum(1 for r in rs if any(i["item"] == k for i in r["ingredients"]))}</td></tr>'
        for k, x in sorted(PRICES.items(), key=lambda kv: kv[1]["name"]))
    body = f"""
    <p class="eyebrow">Βάση υπολογισμού</p>
    <h1>Τιμές υλικών</h1>
    <p class="lead">Από αυτόν τον πίνακα υπολογίζεται το κόστος κάθε συνταγής. Όταν αλλάζει μια τιμή, ενημερώνονται όλες οι συνταγές που χρησιμοποιούν το υλικό.</p>
    {f'<div class="banner">{e(prices_doc["_note"])}</div>' if prices_doc.get("_note") else ''}
    <div class="tablewrap"><table><thead><tr><th>Υλικό</th><th class="n">Τιμή</th><th>Μονάδα</th><th>Προϊόν αναφοράς</th><th class="n">Συνταγές</th></tr></thead>
    <tbody>{rows}</tbody></table></div>
    <p class="note">Ενημέρωση: {e(UPDATED)}</p>"""
    d = OUT / "times"
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(page(f"Τιμές υλικών · {site['name']}", "Οι τιμές υλικών με τις οποίες υπολογίζεται το κόστος των συνταγών.", body, "../", "times/"), encoding="utf-8")


def build_seo(rs):
    if BASE:
        urls = [""] + ["times/"] + [f"syntages/{r['slug']}/" for r in rs]
        sm = "".join(f"<url><loc>{BASE}/{u}</loc></url>" for u in urls)
        (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>', encoding="utf-8")
        (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
        host = BASE.split("://", 1)[-1].split("/")[0]
        if not host.endswith("github.io"):
            (OUT / "CNAME").write_text(host + "\n", encoding="utf-8")
    else:
        (OUT / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    if (ROOT / "images").exists():
        shutil.copytree(ROOT / "images", OUT / "images")
    (OUT / ".nojekyll").write_text("")
    rs = load_recipes()
    build_home(rs)
    for r in rs:
        build_recipe(r)
    build_prices(rs)
    build_seo(rs)
    print(f"OK: {len(rs)} συνταγές → {OUT}")


if __name__ == "__main__":
    main()
