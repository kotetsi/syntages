// Τρέχει μέσα σε σελίδα του sklavenitis.gr (ίδιο origin), π.χ. ως:
//   <περιεχόμενο αυτού του αρχείου>
//   await fetchPrices(<περιεχόμενο του tools/price_map.json>)
// Επιστρέφει JSON με την τιμή ανά κιλό/λίτρο
// και ανά τεμάχιο για κάθε προϊόν αναφοράς (βρίσκεται με το SKU του).
async function fetchPrices(MAP) {
  const T = e => e ? e.textContent.replace(/\s+/g, ' ').trim() : '';
  const num = s => parseFloat(s.replace('.', '').replace(',', '.'));
  const out = {};
  for (const [k, m] of Object.entries(MAP)) {
    try {
      const h = await fetch('/apotelesmata-anazitisis/?Query=' + encodeURIComponent(m.query)).then(r => r.text());
      const d = new DOMParser().parseFromString(h, 'text/html');
      const p = [...d.querySelectorAll('.product[class*=prGa]')].find(x => {
        try { return JSON.parse(x.getAttribute('data-item')).ProductSKU === m.sku; } catch (e) { return false; }
      });
      if (!p) { out[k] = { found: false }; continue; }
      const pr = T(p.querySelector('.product_prices'));
      const kg = pr.match(/([\d.,]+) €\/(κιλό|λίτρο)/);
      const pc = pr.match(/([\d.,]+) €\/(τεμ|συσκ)/);
      out[k] = { found: true, title: T(p.querySelector('.product__title')), raw: pr,
                 per_kg: kg ? num(kg[1]) : null, per_piece: pc ? num(pc[1]) : null };
    } catch (e) { out[k] = { found: false, error: String(e) }; }
  }
  return JSON.stringify(out);
}
