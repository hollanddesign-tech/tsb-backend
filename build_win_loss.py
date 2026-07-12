import json
from pull_trades import pull_trades, get_prop_value


def build_win_loss(pages):
    wins = 0
    losses = 0
    breakeven = 0

    for page in pages:
        props = page["properties"]
        outcome = get_prop_value(props.get("Outcome", {}))

        if outcome == "Win":
            wins += 1
        elif outcome == "Loss":
            losses += 1
        elif outcome == "Breakeven":
            breakeven += 1

    total_decided = wins + losses
    win_rate = round((wins / total_decided) * 100, 1) if total_decided > 0 else 0

    return {
        "wins": wins,
        "losses": losses,
        "breakeven": breakeven,
        "win_rate": win_rate,
    }


def main():
    pages = pull_trades()
    result = build_win_loss(pages)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
