"""A Colonel Blotto tournament, after Chapter 11's Play-It.

Each side secretly divides 100 points among five islands. Whoever puts more
points on an island wins it (a tie splits it), and whoever wins more islands
wins the game. The French mathematician Emile Borel described the game in
1921.

The tournament plays a few named plans against each other, many times over,
with each plan's numbers shuffled across the islands every game, since an
opponent doesn't know which island you'll put your weight on. Then it shows
the point the Play-It makes: there's no best plan, because for any plan you
pick, the program can build one that beats it, and then one that beats that.

Needs only Python 3. Run it with:
    python colonel_blotto.py
    python colonel_blotto.py --plan 30,30,30,5,5      # find a counter to your own plan
"""
import argparse
import itertools
import random

ISLANDS, POINTS = 5, 100

PLANS = {
    "even (20 each)": (20, 20, 20, 20, 20),
    "three strong": (34, 33, 33, 0, 0),
    "four strong": (25, 25, 25, 25, 0),
    "lopsided": (40, 30, 20, 10, 0),
    "three and a feint": (30, 30, 30, 9, 1),
    "two and change": (35, 35, 10, 10, 10),
}


def islands_won(a, b):
    """Islands won by plan a against plan b, counting a tie as half."""
    return sum(1 if x > y else 0.5 if x == y else 0 for x, y in zip(a, b))


def result(a, b):
    """1 if a wins, 0.5 for a draw, 0 if a loses."""
    w = islands_won(a, b)
    return 1 if w > ISLANDS / 2 else 0.5 if w == ISLANDS / 2 else 0


def shuffled(plan):
    p = list(plan)
    random.shuffle(p)
    return p


def tournament(games):
    names = list(PLANS)
    table = {}
    for a, b in itertools.product(names, names):
        table[a, b] = sum(result(shuffled(PLANS[a]), shuffled(PLANS[b])) for _ in range(games)) / games
    print(f"Each plan against each, {games} games apiece, islands shuffled every game.")
    print("Share of games won by the row's plan (draws count half):\n")
    width = max(len(n) for n in names)
    print(" " * (width + 2) + "".join(f"{k + 1:>7}" for k in range(len(names))))
    for k, a in enumerate(names):
        row = "".join(f"{100 * table[a, b]:6.0f}%" for b in names)
        avg = sum(table[a, b] for b in names if b != a) / (len(names) - 1)
        print(f"{k + 1}. {a:<{width}}{row}    average {100 * avg:3.0f}%")
    print("\n(The columns are numbered as the rows are.)")


def counter(plan):
    """A plan that beats `plan` when it knows where the points are: win the three cheapest islands by a point."""
    order = sorted(range(ISLANDS), key=lambda i: plan[i])
    reply = [0] * ISLANDS
    for i in order[:3]:
        reply[i] = plan[i] + 1
    spare = POINTS - sum(reply)
    if spare < 0:
        return None
    for i in order[3:]:          # spend the rest where it might steal a fourth island
        reply[i] += spare // 2
    reply[order[-1]] += POINTS - sum(reply)
    return reply


def chain(plan, steps=4):
    print("\nNo plan is safe from an opponent who knows it. Starting from", list(plan))
    current = list(plan)
    for k in range(steps):
        reply = counter(current)
        if reply is None:
            print("  (no three-island counter exists for this plan)")
            return
        print(f"  {list(reply)} beats it, winning {islands_won(reply, current):g} islands of 5")
        current = reply
    print("...and so on. Once you know the plan, you can beat it, which is why the plan has to stay")
    print("unpredictable. You're not doing arithmetic anymore. You're playing your opponent.")


def main():
    p = argparse.ArgumentParser(description="Colonel Blotto tournament (Chapter 11).")
    p.add_argument("--games", type=int, default=4000, help="games per pairing (default 4000)")
    p.add_argument("--plan", help="your own plan: five numbers adding to 100, such as 30,30,30,5,5")
    p.add_argument("--seed", type=int, default=1921)
    args = p.parse_args()
    random.seed(args.seed)
    if args.plan:
        plan = [int(x) for x in args.plan.split(",")]
        if len(plan) != ISLANDS or sum(plan) != POINTS or min(plan) < 0:
            p.error("a plan is five whole numbers, none negative, adding to 100")
        chain(plan)
        return
    tournament(args.games)
    chain(PLANS["even (20 each)"])


if __name__ == "__main__":
    main()
