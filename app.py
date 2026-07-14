"""
A small local web server that serves your equity curve as JSON over HTTP.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import requests

from build_equity_curve import pull_trades, build_equity_curve, STARTING_BALANCE
from build_win_loss import build_win_loss
from build_monthly import build_monthly
from build_sessions import build_sessions
from build_setups import build_setups

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


CRYPTO_IDS = {
    "bitcoin": "BTCUSDT",
    "ethereum": "ETHUSDT",
    "binancecoin": "BNBUSDT",
    "solana": "SOLUSDT",
    "ripple": "XRPUSDT",
    "cardano": "ADAUSDT",
    "dogecoin": "DOGEUSDT",
    "avalanche-2": "AVAXUSDT",
    "polkadot": "DOTUSDT",
    "chainlink": "LINKUSDT",
    "tron": "TRXUSDT",
    "litecoin": "LTCUSDT",
    "polygon": "MATICUSDT",
    "shiba-inu": "SHIBUSDT",
    "uniswap": "UNIUSDT",
    "near": "NEARUSDT",
    "internet-computer": "ICPUSDT",
    "aptos": "APTUSDT",
    "stellar": "XLMUSDT",
    "cosmos": "ATOMUSDT",
}


@app.get("/ticker")
def get_ticker():
    results = []
    try:
        resp = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": ",".join(CRYPTO_IDS.keys()),
                "vs_currencies": "usd",
                "include_24hr_change": "true",
            },
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()

        for coin_id, symbol in CRYPTO_IDS.items():
            coin_data = data.get(coin_id, {})
            results.append({
                "symbol": symbol,
                "price": coin_data.get("usd", 0),
                "change_pct": coin_data.get("usd_24h_change", 0),
            })
    except Exception as e:
        results = [{"symbol": s, "error": str(e)} for s in CRYPTO_IDS.values()]

    return {"ticker": results}


@app.get("/win-loss")
def get_win_loss():
    pages = pull_trades()
    return build_win_loss(pages)

@app.get("/monthly-pnl")
def get_monthly_pnl():
    pages = pull_trades()
    return {"months": build_monthly(pages)}

@app.get("/sessions-pnl")
def get_sessions_pnl():
    pages = pull_trades()
    return {"sessions": build_sessions(pages)}

@app.get("/setups")
def get_setups():
    return {"setups": build_setups()}

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
