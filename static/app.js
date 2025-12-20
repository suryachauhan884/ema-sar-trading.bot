let binaryWidget, angelWidget;
let countdown = 60;

// ================= TABS =================
function showTab(tab) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById(tab).classList.add('active');
}

// ================= COUNTDOWN =================
setInterval(() => {
  countdown--;
  if (countdown <= 0) countdown = 60;
  document.getElementById("countdown").innerText = countdown;
}, 1000);

// ================= BINARY CHART =================
function loadBinaryChart() {
  if (binaryWidget) binaryWidget.remove();

  binaryWidget = new TradingView.widget({
    autosize: true,
    symbol: "FX:EURUSD",
    interval: "1",
    timezone: "Asia/Kolkata",
    theme: "dark",
    style: "1",
    hide_top_toolbar: false,
    allow_symbol_change: false,
    container_id: "tv-binary",
    studies: [
      "EMA@tv-basicstudies",
      "ParabolicSAR@tv-basicstudies"
    ]
  });
}

loadBinaryChart();

// 🔄 Telegram live fix
setInterval(loadBinaryChart, 60000);

// ================= STOCK CHART =================
function loadAngelChart() {
  if (angelWidget) angelWidget.remove();

  angelWidget = new TradingView.widget({
    autosize: true,
    symbol: "NSE:RELIANCE",
    interval: "5",
    timezone: "Asia/Kolkata",
    theme: "dark",
    container_id: "tv-angel"
  });
}

loadAngelChart();
setInterval(loadAngelChart, 120000);

// ================= SIGNAL FETCH =================
async function getSignal() {
  document.getElementById("signal").innerText = "Analyzing...";

  try {
    const res = await fetch("/api/binary/signal");
    const data = await res.json();

    document.getElementById("signal").innerHTML =
      data.signal === "BUY"
        ? "🟢 BUY ↑"
        : "🔴 SELL ↓";

  } catch {
    document.getElementById("signal").innerText = "Error";
  }
}
