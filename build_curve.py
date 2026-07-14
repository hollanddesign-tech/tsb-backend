import json
from pull_trades import pull_trades, get_prop_value


def build_curve(pages):
    trades = []
    for page in pages:
        props = page["properties"]
        date = get_prop_value(props.get("Date", {}))
        r_multiple = get_prop_value(props.get("R Multiple", {}))
        name = get_prop_value(props.get("Name", {}))

        if date is None or r_multiple is None:
            continue
        trades.append({"date": date, "r_multiple": r_multiple, "name": name})

    trades.sort(key=lambda t: t["date"])

    cumulative_r = 0
    curve = []
    for i, t in enumerate(trades, start=1):
        cumulative_r += t["r_multiple"]
        curve.append({
            "trade_number": i,
            "trade": t["name"],
            "r_multiple": round(t["r_multiple"], 2),
            "cumulative_r": round(cumulative_r, 2),
        })

    return curve


def main():
    pages = pull_trades()
    result = build_curve(pages)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
