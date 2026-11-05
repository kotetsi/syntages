// Αλλαγή μερίδων: ξαναϋπολογίζει ποσότητες και κόστος από τα δεδομένα της σελίδας
(function () {
  var el = document.getElementById("recipe-data");
  if (!el) return;
  var d = JSON.parse(el.textContent);
  var serv = d.servings;
  var eur = function (v) { return v.toLocaleString("el-GR", { style: "currency", currency: "EUR" }); };
  var half = function (n) { var r = Math.round(n * 2) / 2; return r % 1 ? r.toLocaleString("el-GR", { minimumFractionDigits: 1 }) : String(r); };
  function qty(i, f) {
    if (i.show) return half(i.show[0] * f) + " " + i.show[1];
    var unit = i.unit === "l" ? "ml" : "g";
    var q = i.qty * f;
    q = q >= 100 ? Math.round(q / 10) * 10 : Math.max(1, Math.round(q));
    if (q >= 1000) return (q / 1000).toLocaleString("el-GR", { maximumFractionDigits: 2 }) + (unit === "ml" ? " l" : " kg");
    return q + " " + unit;
  }
  var rows = document.querySelectorAll("#ing li");
  function draw() {
    var f = serv / d.servings, total = 0;
    d.ingredients.forEach(function (i, n) {
      var c = i.cost * f; total += c;
      rows[n].querySelector(".amt").textContent = qty(i, f);
      rows[n].querySelector(".ic").textContent = eur(c);
    });
    document.getElementById("sv").textContent = serv + " μερίδες";
    document.getElementById("tsv").textContent = "για " + serv;
    document.getElementById("tot").textContent = eur(total);
    document.getElementById("pp").textContent = eur(total / serv);
  }
  document.getElementById("minus").addEventListener("click", function () { if (serv > 1) { serv--; draw(); } });
  document.getElementById("plus").addEventListener("click", function () { if (serv < 20) { serv++; draw(); } });
  draw();
})();

// Φίλτρα κατηγοριών στην αρχική
(function () {
  var chips = document.querySelectorAll(".chip[data-c]");
  if (!chips.length) return;
  chips.forEach(function (b) {
    b.addEventListener("click", function () {
      var c = b.dataset.c;
      chips.forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      document.querySelectorAll(".card[data-cats]").forEach(function (card) {
        card.hidden = !(c === "Όλες" || card.dataset.cats.split("|").indexOf(c) > -1);
      });
    });
  });
})();
