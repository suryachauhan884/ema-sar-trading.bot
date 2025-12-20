// ==================================================
// TradeWin LIVE Signal Auto Refresh (FINAL FIXED)
// ==================================================

const API_URL = "/api/binary/signal";
const REFRESH_INTERVAL = 30000; // 30 seconds

async function fetchSignal() {
  try {
    const response = await fetch(API_URL, { cache: "no-store" });
    if (!response.ok) throw new Error("API error");

    const data = await response.json();

    // Safe setter
    const setText = (id, value) => {
      const el = document.getElementById(id);
      if (el && value !== undefined) el.innerText = value;
    };

    setText("pair", data.pair || "EUR/USD");
    setText("timeframe", data.timeframe || "1 Min");
    setText("signal", data.signal || "WAIT");
    setText("confidence", data.confidence ? data.confidence + "%" : "--");
    setText("strategy", data.strategy || "EMA + SAR");
    setText("status", data.status || "LIVE");

    // Signal color
    const signalBox = document.getElementById("signal");
    if (signalBox) {
      if (data.signal === "BUY") {
        signalBox.style.color = "#00ff88";
      } else if (data.signal === "SELL") {
        signalBox.style.color = "#ff4444";
      } else {
        signalBox.style.color = "#ffaa00";
      }

      // Pulse animation
      signalBox.style.opacity = "0.4";
      setTimeout(() => (signalBox.style.opacity = "1"), 200);
    }

    console.log("✅ Signal updated:", data);

  } catch (error) {
    console.error("❌ Error fetching signal:", error);

    const statusEl = document.getElementById("status");
    if (statusEl) statusEl.innerText = "OFFLINE";
  }
}

// Initial fetch
fetchSignal();

// Auto refresh
setInterval(fetchSignal, REFRESH_INTERVAL);
