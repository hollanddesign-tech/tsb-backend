"""
A small local web server that serves your equity curve as JSON over HTTP.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import requests

from build_equity_curve import pull_trades, build_equity_curve, STARTING_BALANCE
from build_win_loss import build_win_loss

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/equity-curve")
def get_equity_curve():
    pages = pull_trades()
    curve = build_equity_curve(pages)

    summary = {}
    if curve:
        final = curve[-1]
        max_dd = min(c["drawdown"] for c in curve)
        summary = {
            "starting_balance": STARTING_BALANCE,
            "final_equity": final["equity"],
            "max_drawdown": max_dd,
        }

    return {"summary": summary, "points": curve}


CRYPTO_SYMBOLS = ["BTCUSDT", "ETHUSDT"]


@app.get("/ticker")
def get_ticker():
    results = []
    for symbol in CRYPTO_SYMBOLS:
        try:
            resp = requests.get(
                "https://api.binance.com/api/v3/ticker/24hr",
                params={"symbol": symbol},
                timeout=5,
            )
            resp.raise_for_status()
            data = resp.json()
            results.append({
                "symbol": symbol,
                "price": float(data["lastPrice"]),
                "change_pct": float(data["priceChangePercent"]),
            })
        except Exception as e:
            results.append({"symbol": symbol, "error": str(e)})

    return {"ticker": results}


@app.get("/win-loss")
def get_win_loss():
    pages = pull_trades()
    return build_win_loss(pages)


@app.get("/")
def root():
    return {"status": "ok", "message": "TSB backend is running. Try /equity-curve"}


@app.get("/chart")
def get_chart():
    return FileResponse("chart.html")


@app.get("/ticker-widget")
def get_ticker_widget():
    return FileResponse("ticker.html")


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
