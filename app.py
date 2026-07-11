from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from build_equity_curve import pull_trades, build_equity_curve, STARTING_BALANCE

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


@app.get("/")
def root():
    return {"status": "ok", "message": "TSB backend is running. Try /equity-curve"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
