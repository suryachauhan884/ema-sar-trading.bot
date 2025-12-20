/*****************************
 TAB SWITCHING
*****************************/
function openTab(tabId) {
  document.querySelectorAll(".tab-content").forEach(tab => {
    tab.classList.remove("active");
  });

  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.classList.remove("active");
  });

  document.getElementById(tabId).classList.add("active");
  event.target.classList.add("active");
}

/*****************************
 OLYMP TRADE – BINARY CHART
*****************************/
const binaryChart = LightweightCharts.createChart(
  document.getElementById("binaryChart"),
  {
    layout: {
      background: { color: "#020617" },
      textColor: "#e5e7eb"
    },
    grid: {
      vertLines: { color: "#1f2937" },
      horzLines: { color: "#1f2937" }
    },
    timeScale: {
      timeVisible: true,
      secondsVisible: false
    }
  }
);

const binaryCandles = binaryChart.addCandlestickSeries({
  upColor: "#22c55e",
  downColor: "#ef4444",
  borderVisible: false,
  wickUpColor: "#22c55e",
  wickDownColor: "#ef4444"
});

// EMA LINES
const emaFastLine = binaryChart.addLineSeries({
  color: "#00ff9c",
  lineWidth: 2
});

const emaSlowLine = binaryChart.addLineSeries({
  color: "#ff4d4d",
  lineWidth: 2
});

/*****************************
 ANGEL ONE – STOCK CHART
*****************************/
const angelChart = LightweightCharts.createChart(
  document.getElementById("angelChart"),
  {
    layout: {
      background: { color: "#020617" },
      textColor: "#e5e7eb"
    },
    grid: {
      vertLines: { color: "#1f2937" },
      horzLines: { color: "#1f2937" }
    },
    timeScale: {
      timeVisible: true,
      secondsVisible: false
    }
  }
);

const angelCandles = angelChart.addCandlestickSeries({
  upColor: "#22c55e",
  downColor: "#ef4444",
  borderVisible: false,
  wickUpColor: "#22c55e",
  wickDownColor: "#ef4444"
});

// EMA FOR STOCKS
const stockEma9 = angelChart.addLineSeries({ color: "#38bdf8", lineWidth: 2 });
const stockEma21 = angelChart.addLineSeries({ color: "#facc15", lineWidth: 2 });
const stockEma50 = angelChart.addLineSeries({ color: "#f97316", lineWidth: 2 });

/*****************************
 LOAD OLYMP TRADE DATA
*****************************/
async function loadBinaryData() {
  const res = await fetch("/api/binary/candles");
  const data = await res.json();

  binaryCandles.setData(data.candles);
  emaFastLine.setData(data.ema_fast);
  emaSlowLine.setData(data.ema_slow);

  document.getElementById("binaryTrend").innerText = data.trend;
}

/*****************************
 LOAD ANGEL ONE DATA
*****************************/
async function loadAngelData() {
  const res = await fetch("/api/angel/candles");
  const data = await res.json();

  angelCandles.setData(data.candles);
  stockEma9.setData(data.ema9);
  stockEma21.setData(data.ema21);
  stockEma50.setData(data.ema50);

  document.getElementById("stockTrend").innerText = data.trend;
}

/*****************************
 GET BINARY SIGNAL
*****************************/
async function getBinarySignal() {
  const res = await fetch("/api/binary/signal");
  const data = await res.json();

  document.getElementById("binarySignal").innerText =
    data.signal + " (" + data.confidence + "%)";
}

/*****************************
 AUTO REFRESH
*****************************/
loadBinaryData();
loadAngelData();

setInterval(() => {
  loadBinaryData();
  loadAngelData();
}, 15000);