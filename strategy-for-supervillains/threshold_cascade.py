"""Mark Granovetter's threshold model of a riot, after Chapter 24.

Each person in a crowd has a threshold: how many others must already be
rioting before they'll join. Someone with a threshold of 0 starts on their
own. The program adds people in rounds: everyone whose threshold has been met
joins, which may meet more thresholds, until nobody else will move.

Part 1 is the chapter's pair of crowds (and Figure 24.1). Crowd A has one
person at each threshold from 0 to 99, and the whole crowd riots. Crowd B is
the same except that the person with a threshold of 1 now has a threshold of
2, and only the instigator moves.

Part 2 draws crowds whose thresholds are scattered around an average, as
real crowds' would be, and shows how the result jumps from a handful of people
to almost everyone as the scatter changes, which is why identical-looking
crowds can behave so differently and why revolutions are so hard to predict.

Needs only Python 3. Run it with:
    python threshold_cascade.py
    python threshold_cascade.py --thresholds 0,1,1,3,3,5,8   # try your own crowd
"""
import argparse
import random


def cascade(thresholds):
    """Return how many people end up rioting, and how many joined in each round."""
    rioting, rounds = 0, []
    remaining = sorted(thresholds)
    while True:
        joining = sum(1 for t in remaining if t <= rioting)
        if joining == 0:
            return rioting, rounds
        remaining = [t for t in remaining if t > rioting]
        rioting += joining
        rounds.append(joining)


def two_crowds():
    print("Part 1: Granovetter's two crowds of 100\n")
    a = list(range(100))
    b = list(range(100)); b[1] = 2
    for name, crowd, note in [("Crowd A", a, "thresholds 0, 1, 2, ... 99"),
                              ("Crowd B", b, "the same, except the person at 1 is now at 2")]:
        total, rounds = cascade(crowd)
        print(f"  {name} ({note}): {total} of 100 riot, after {len(rounds)} round(s)")
    print("\n  One person's threshold moved by one, and the result went from a riot to a lone instigator,")
    print("  whom the newspapers will describe as a lunatic in a crowd of peaceful citizens.\n")


def scattered(mean, spread, size=100):
    return [max(0, round(random.gauss(mean, spread))) for _ in range(size)]


def sweep(mean, trials):
    print(f"Part 2: crowds of 100 with thresholds scattered around an average of {mean}\n")
    print("  scatter   average number who riot   (each row: {} crowds)".format(trials))
    for spread in (2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 25, 30):
        total = sum(cascade(scattered(mean, spread))[0] for _ in range(trials)) / trials
        print(f"  {spread:7}   {total:5.1f}  {'#' * round(total / 2)}")
    print("\n  When everyone's threshold is close to the average, nobody starts, and nothing happens.")
    print("  Add enough people at the low end (more scatter), and the chain can run all the way up.")
    print("  The jump in between is where small differences between crowds decide everything.")


def main():
    p = argparse.ArgumentParser(description="Granovetter's threshold model (Chapter 24).")
    p.add_argument("--thresholds", help="your own crowd, as comma-separated numbers")
    p.add_argument("--mean", type=float, default=25, help="average threshold for Part 2 (default 25)")
    p.add_argument("--trials", type=int, default=500, help="crowds per row in Part 2 (default 500)")
    p.add_argument("--seed", type=int, default=1978)
    args = p.parse_args()
    random.seed(args.seed)
    if args.thresholds:
        crowd = [int(x) for x in args.thresholds.split(",")]
        total, rounds = cascade(crowd)
        print(f"{total} of {len(crowd)} riot; joined per round: {rounds or [0]}")
        return
    two_crowds()
    sweep(args.mean, args.trials)


if __name__ == "__main__":
    main()
