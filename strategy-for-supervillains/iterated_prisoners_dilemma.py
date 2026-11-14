"""An iterated Prisoner's Dilemma tournament, after Chapter 4's "Trenches."

Two players each choose, every round, to hold fire (cooperate) or shell the
enemy (defect). The scores are the Play-It's: both hold fire, 3 each; both
shell, 1 each; one shells while the other holds fire, 5 for the sheller and 0
for the other. Every strategy below plays every other (and a copy of itself),
in the spirit of Robert Axelrod's tournaments.

The tournament runs twice, as the Play-It does:
  Game one:  exactly ten rounds, and everyone knows it.
  Game two:  after each round, the game goes on with probability 0.9, so it
             lasts ten rounds on average, but nobody knows when it will stop.
Watch what the strategies that "know" the last round do with it, and what that
costs them when the end is uncertain: that's the shadow of the future.

Needs only Python 3. Run it with:
    python iterated_prisoners_dilemma.py
    python iterated_prisoners_dilemma.py --noise 0.05      # 5% of moves go wrong
"""
import argparse
import random

C, D = "hold fire", "shell"
PAYOFF = {(C, C): (3, 3), (D, D): (1, 1), (D, C): (5, 0), (C, D): (0, 5)}


# Each strategy sees its own past moves, the opponent's past moves, and, in
# Game one only, how many rounds remain (None when the end is unknown).
def tit_for_tat(mine, theirs, left):
    return theirs[-1] if theirs else C

def always_hold_fire(mine, theirs, left):
    return C

def always_shell(mine, theirs, left):
    return D

def grudger(mine, theirs, left):
    return D if D in theirs else C

def tit_for_two_tats(mine, theirs, left):
    return D if theirs[-2:] == [D, D] else C

def suspicious_tit_for_tat(mine, theirs, left):
    return theirs[-1] if theirs else D

def pavlov(mine, theirs, left):
    """Win-stay, lose-shift: repeat your move after a good result, switch after a bad one."""
    if not mine:
        return C
    good = PAYOFF[mine[-1], theirs[-1]][0] >= 3
    return mine[-1] if good else (D if mine[-1] == C else C)

def coin_flip(mine, theirs, left):
    return random.choice([C, D])

def tit_for_tat_but_shell_at_the_end(mine, theirs, left):
    """Tit for Tat, except that it shells in the last round when it knows which round that is."""
    if left == 1:
        return D
    return tit_for_tat(mine, theirs, left)


STRATEGIES = [tit_for_tat, always_hold_fire, always_shell, grudger, tit_for_two_tats,
              suspicious_tit_for_tat, pavlov, coin_flip, tit_for_tat_but_shell_at_the_end]


def play(a, b, rounds, known_end, noise):
    """Play one match. Returns each side's total score and the number of rounds played."""
    ma, mb, sa, sb = [], [], 0, 0
    r = 0
    while True:
        left = rounds - r if known_end else None
        x, y = a(ma, mb, left), b(mb, ma, left)
        if random.random() < noise:
            x = D if x == C else C
        if random.random() < noise:
            y = D if y == C else C
        pa, pb = PAYOFF[x, y]
        ma.append(x); mb.append(y); sa += pa; sb += pb
        r += 1
        if known_end and r == rounds:
            break
        if not known_end and random.random() > 0.9:
            break
    return sa, sb, r


def tournament(known_end, noise, repeats):
    """Round robin, each pairing played `repeats` times. Returns average points per round."""
    points = {s.__name__: 0 for s in STRATEGIES}
    rounds = {s.__name__: 0 for s in STRATEGIES}
    for i, a in enumerate(STRATEGIES):
        for b in STRATEGIES[i:]:
            for _ in range(repeats):
                sa, sb, r = play(a, b, 10, known_end, noise)
                points[a.__name__] += sa; rounds[a.__name__] += r
                if b is not a:
                    points[b.__name__] += sb; rounds[b.__name__] += r
    return {k: points[k] / rounds[k] for k in points}


def show(title, scores):
    print(f"\n{title}")
    print("  average points per round (3 = steady peace, 1 = steady war)")
    for name, score in sorted(scores.items(), key=lambda kv: -kv[1]):
        print(f"  {score:5.2f}  {'#' * round(score * 10):<50} {name.replace('_', ' ')}")


def main():
    p = argparse.ArgumentParser(description="Iterated Prisoner's Dilemma tournament (Chapter 4).")
    p.add_argument("--noise", type=float, default=0.0, help="chance that any one move goes wrong (default 0)")
    p.add_argument("--repeats", type=int, default=200, help="matches per pairing (default 200)")
    p.add_argument("--seed", type=int, default=1914, help="random seed, so runs can be repeated")
    args = p.parse_args()
    random.seed(args.seed)
    show("Game one: exactly ten rounds, and everyone knows it", tournament(True, args.noise, args.repeats))
    show("Game two: the end could come after any round", tournament(False, args.noise, args.repeats))
    print("\nThings to look for: Tit for Tat does well overall, though it never outscores the opponent")
    print("in front of it; knowing the last round is worth something only while the end is known;")
    print("and with --noise, shells fired by mistake punish the strategies that never forgive.")


if __name__ == "__main__":
    main()
