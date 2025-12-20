// ==================================================
// TradeWin LIVE Signal Auto Refresh
// ==================================================

const API_URL = "/api/binary/signal";
const REFRESH_INTERVAL = 60000; // 60 seconds

async function fetchSignal() {
    try {
        const response = await fetch(API_URL);
        const data = await response.json();

        document.getElementById("pair").innerText = data.pair;
        document.getElementById("timeframe").innerText = data.timeframe;
        document.getElementById("signal").innerText = data.signal;
        document.getElementById("confidence").innerText = data.confidence + "%";
        document.getElementById("strategy").innerText = data.strategy;
        document.getElementById("status").innerText = data.status;

        // Color signal
        const signalBox = document.getElementById("signal");
        if (data.signal === "BUY") {
            signalBox.style.color = "#00ff88";
        } else if (data.signal === "SELL") {
            signalBox.style.color = "#ff4d4d";
        } else {
            signalBox.style.color = "#ffaa00";
        }

        console.log("Signal updated:", data);

    } catch (error) {
        console.error("Error fetching signal:", error);
        document.getElementById("status").innerText = "DISCONNECTED";
    }
}

// Initial fetch
fetchSignal();

// Auto refresh every minute
setInterval(fetchSignal, REFRESH_INTERVAL);
