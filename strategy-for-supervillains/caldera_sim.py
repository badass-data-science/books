"""A bot simulation of *Caldera*, the book's wargame (Appendix E).

Computer players ("bots") play thousands of games of *Caldera* against each
other, with and without the optional Pillars and Rival, and the program
reports who wins and how. It's a sanity check on the rules, not a model of
anything real, and not a substitute for playing with people: the bots are
crude, so the numbers say where a rule is lopsided against simple play, not
how you and your friends will play.

The Incumbent bots: hard (sweeps), hearts (governs and patrols), mixed,
responsive (patrols, then sweeps, where Cells have raided), and oracle, which
cheats by seeing the hidden Cells, to show the best any Incumbent could do.
The Insurgent bots: raid, politics (rallies and organizes), mixed, and smart.

Where the rules in Appendix E are silent or ambiguous, the program makes an
assumption and prints it. The last few tables try house rules that change how
raiding works; try your own by editing the Game class.

Needs only Python 3. Run it with:
    python caldera_sim.py                 # about 25 seconds
    python caldera_sim.py --games 500     # quicker, rougher
"""
import argparse
import collections
import random

N = 7            # islands, in a ring
ROUNDS = 12
START_PATIENCE, START_SUPPLY, UPKEEP = 20, 10, 3
START_GARRISONS, START_CELLS = 12, 4
RIVAL_START, RIVAL_TARGET = 6, 20

ASSUMPTIONS = [
    "Move isn't in the Resolve order; the Incumbent's Moves resolve with its Resupply, Patrol, and Govern (before Sweeps), and the Insurgent's with its other actions, last.",
    "Friction (a 1) cancels an action but its cost is still paid: a failed Govern still costs 2 Supply, and a failed Sweep still costs 1 Patience.",
    "Suspected has no effect in the rules, so it only informs the bots (an Incumbent may choose to Patrol or Sweep where Cells have raided).",
    "The Rival's price has no currency in the rules (neither side holds Tokens), so sales are free; the Rival earns only its 1 a round plus 1 per Patience lost.",
    "The Rival may make one sale to each side a round (\"Nothing stops the Rival from selling to both\").",
    "The Rival's win (\"neither side has yet won by the end of Round 12\") can never happen as written, since the Incumbent wins at the end if the Insurgent hasn't. It's read here as \"nobody won at once, before the end of Round 12.\"",
    "The Pillars move Support after the Insurgent's actions and before the end-of-round win check; their offers aren't modeled.",
]


def d6(rng):
    return rng.randint(1, 6)


def neighbors(i):
    return [(i - 1) % N, (i + 1) % N]


class Game:
    def __init__(self, rng, inc, ins, pillars=False, rival=False, suspected_rule=False,
                 raid_risk=0, patience=START_PATIENCE, raid_supply=True):
        self.rng, self.inc_style, self.ins_style = rng, inc, ins
        self.pillars, self.rival = pillars, rival
        self.suspected_rule = suspected_rule   # house rule: a Sweep on a Suspected island hits on 2+
        self.raid_risk = raid_risk             # house rule: raiding a garrisoned island loses the Cell on a roll of raid_risk or less
        self.raid_supply = raid_supply         # house rule (when False): a Raid costs Patience only, not Supply
        self.support = [0] * N
        self.garrison = [0] * N
        for k in range(START_GARRISONS):          # spread openly: 2,2,2,2,2,1,1
            self.garrison[k % N] += 1
        self.cells = [0] * N
        for _ in range(START_CELLS):             # hidden, scattered
            self.cells[rng.randrange(N)] += 1
        self.patience, self.supply = patience, START_SUPPLY
        self.tokens = RIVAL_START
        self.suspected = set()
        self.sales = collections.Counter()

    # -- bots -------------------------------------------------------------------
    def garrisoned(self):
        return [i for i in range(N) if self.garrison[i] > 0] or [0]

    def incumbent_plan(self):
        rng, s = self.rng, self.support
        g = self.garrisoned()
        plan = []
        style = self.inc_style
        for k in range(2):
            if self.supply < 4 and rng.random() < .7:
                plan.append(("resupply", None)); continue
            sus = [i for i in g if i in self.suspected]
            if style == "hard":
                plan.append(("sweep", rng.choice(sus or g)))
            elif style == "hearts":
                if self.supply >= 2 and rng.random() < .7:
                    plan.append(("govern", max(g, key=lambda i: (s[i], rng.random()))))
                else:
                    plan.append(("patrol", rng.choice(g)))
            elif style == "mixed":
                x = rng.random()
                if x < .4: plan.append(("patrol", rng.choice(g)))
                elif x < .65: plan.append(("sweep", rng.choice(sus or g)))
                else: plan.append(("govern", max(g, key=lambda i: (s[i], rng.random()))))
            elif style == "oracle":  # cheats: sees the hidden Cells (an upper bound, not a player)
                hot = sorted(range(N), key=lambda i: (-self.cells[i], rng.random()))
                target = hot[k] if self.cells[hot[k]] else hot[0]
                if self.garrison[target]:
                    plan.append(("sweep", target))
                elif self.supply >= 2:
                    plan.append(("govern", max(g, key=lambda i: (s[i], rng.random()))))
                else:
                    plan.append(("resupply", None))
            else:  # "responsive": answer raids where they happen, govern the rest
                if k == 0 and sus:
                    target = rng.choice(sus)
                    if self.garrison[target]:
                        plan.append(("patrol", target)); continue
                    plan.append(("move", target)); continue
                if k == 1 and plan and plan[0][0] == "patrol":
                    plan.append(("sweep", plan[0][1])); continue
                if self.supply >= 2:
                    plan.append(("govern", max(g, key=lambda i: (s[i], rng.random()))))
                else:
                    plan.append(("resupply", None))
        return plan

    def insurgent_plan(self):
        rng, s, c = self.rng, self.support, self.cells
        cells = [i for i in range(N) if c[i] > 0]
        plan = []
        if not cells:
            return plan
        style = self.ins_style
        for _ in range(2):
            if style == "raid":
                plan.append(("raid", rng.choice(cells)))
            elif style == "politics":
                org = [i for i in cells if s[i] >= 0]
                if org and rng.random() < .5: plan.append(("organize", rng.choice(org)))
                else: plan.append(("rally", rng.choice(cells)))
            elif style == "mixed":
                x = rng.random()
                if x < .35: plan.append(("rally", rng.choice(cells)))
                elif x < .65: plan.append(("organize", rng.choice(cells)))
                else: plan.append(("raid", rng.choice(cells)))
            else:  # "smart": raid only where no Garrison can Sweep, organize where allowed, rally toward 4 islands
                safe = [i for i in cells if self.garrison[i] == 0]
                org = [i for i in cells if s[i] >= 0]
                lean = sum(1 for x in s if x >= 1)
                if sum(c) < 4 and org:
                    plan.append(("organize", rng.choice(org)))
                elif lean < 4 and rng.random() < .6:
                    plan.append(("rally", min(cells, key=lambda i: (s[i] >= 1, -s[i], rng.random()))))
                elif safe:
                    plan.append(("raid", rng.choice(safe)))
                else:
                    plan.append(("move", rng.choice(cells)))
        return plan

    def rival_sells(self):
        """Prolong the game: prop up whichever side is closer to winning at once."""
        if not self.rival:
            return
        if self.patience <= 8 or self.supply < UPKEEP:
            self.supply += 2; self.sales["supply"] += 1
        if sum(self.cells) <= 2:
            self.cells[self.rng.randrange(N)] += 1; self.sales["cell"] += 1

    def pillars_move(self):
        """Keep every island off +2 and -2, and keep the Insurgent alive enough to matter."""
        if not self.pillars:
            return
        s = self.support
        for _ in range(2):
            extreme = [i for i in range(N) if abs(s[i]) == 2]
            if extreme:
                i = self.rng.choice(extreme); s[i] -= 1 if s[i] > 0 else -1
            elif sum(self.cells) < 3:
                blocked = [i for i in range(N) if self.cells[i] and s[i] < 0]
                if blocked:
                    i = self.rng.choice(blocked); s[i] += 1

    # -- a round ----------------------------------------------------------------
    def play(self):
        rng = self.rng
        for rnd in range(1, ROUNDS + 1):
            lost_before = self.patience
            # 1. Upkeep
            if self.supply >= UPKEEP:
                self.supply -= UPKEEP
            else:
                self.patience -= UPKEEP - self.supply; self.supply = 0
            # 2. Plan
            inc, ins = self.incumbent_plan(), self.insurgent_plan()
            # Rival sells after the plans are revealed, before Friction
            self.rival_sells()
            # 3. Friction: a 1 cancels the action (costs still paid)
            inc = [(a, t, d6(rng) != 1) for a, t in inc]
            ins = [(a, t, d6(rng) != 1) for a, t in ins]
            swept = {t for a, t, ok in inc if a == "sweep"}
            # 4. Resolve: Resupply, Patrol, Govern, Move; then Sweeps; then the Insurgent
            revealed = set()
            for a, t, ok in inc:
                if a == "govern":
                    if self.supply < 2:
                        continue          # can't pay, so it doesn't happen
                    self.supply -= 2      # paid even if Friction cancels it
                if not ok:
                    continue
                if a == "resupply":
                    self.supply += 3
                elif a == "patrol" and self.cells[t] and d6(rng) >= 3:
                    revealed.add(t)
                elif a == "govern":
                    self.support[t] = max(-2, self.support[t] - 1)
                elif a == "move":
                    src = sorted(range(N), key=lambda i: -self.garrison[i])
                    moved = 0
                    for i in src:
                        if moved == 3: break
                        if t in neighbors(i) and self.garrison[i] > 1:
                            self.garrison[i] -= 1; self.garrison[t] += 1; moved += 1
            for a, t, ok in inc:
                if a != "sweep":
                    continue
                self.patience -= 1
                if not ok:
                    continue
                easy = t in revealed or (self.suspected_rule and t in self.suspected)
                if self.cells[t] and d6(rng) >= (2 if easy else 4):
                    self.cells[t] -= 1
                self.support[t] = min(2, self.support[t] + 1)
                if d6(rng) <= 2:
                    self.cells[t] += 1
            for a, t, ok in ins:
                if not ok or self.cells[t] == 0:
                    continue
                if a == "rally":
                    self.support[t] = min(2, self.support[t] + 1)
                elif a == "organize" and self.support[t] >= 0:
                    self.cells[t] += 1
                elif a == "raid":
                    self.suspected.add(t)
                    if t in swept:
                        self.cells[t] -= 1
                    elif self.raid_risk and self.garrison[t] and d6(rng) <= self.raid_risk:
                        self.cells[t] -= 1
                    else:
                        self.patience -= 1
                        if self.raid_supply:
                            self.supply = max(0, self.supply - 1)
                        if self.support[t] < 1:
                            self.support[t] = max(-2, self.support[t] - 1)
                elif a == "move":
                    self.cells[t] -= 1; self.cells[self.rng.choice(neighbors(t))] += 1
            self.pillars_move()
            if self.rival:
                self.tokens += 1 + max(0, lost_before - self.patience)
            # instant wins
            if self.patience <= 0:
                return self.result("insurgent", "patience", rnd)
            if sum(self.cells) == 0:
                return self.result("incumbent", "no cells", rnd)
        if sum(1 for x in self.support if x >= 1) >= 4:
            return self.result("insurgent", "islands", ROUNDS)
        return self.result("incumbent", "held", ROUNDS)

    def result(self, winner, how, rnd):
        pillars_win = (self.pillars and rnd == ROUNDS and self.patience >= 8
                       and all(abs(x) < 2 for x in self.support) and sum(self.cells) >= 3)
        rival_win = self.rival and rnd == ROUNDS and how in ("islands", "held") and self.tokens >= RIVAL_TARGET
        return dict(winner=winner, how=how, rounds=rnd, pillars=pillars_win, rival=rival_win,
                    sales=sum(self.sales.values()))


INCUMBENTS = ["hard", "hearts", "mixed", "responsive", "oracle"]
INSURGENTS = ["raid", "politics", "mixed", "smart"]


def run(games, seed, **opts):
    rng = random.Random(seed)
    table = {}
    for a in INCUMBENTS:
        for b in INSURGENTS:
            tally = collections.Counter(); hows = collections.Counter(); rounds = 0
            for _ in range(games):
                r = Game(rng, a, b, **opts).play()
                tally[r["winner"]] += 1; hows[r["how"]] += 1; rounds += r["rounds"]
                tally["pillars"] += r["pillars"]; tally["rival"] += r["rival"]; tally["sales"] += r["sales"]
            table[a, b] = (tally, hows, rounds / games)
    return table


def report(games, seed):
    print(f"Caldera bot simulation: {games} games per matchup, seed {seed}.\n")
    print("Assumptions where Appendix E is silent or ambiguous:")
    for k, a in enumerate(ASSUMPTIONS, 1):
        print(f"  {k}. {a}")
    print("\nIncumbent bots: hard (sweeps), hearts (governs and patrols), mixed, responsive (patrols then sweeps where Cells raided),"
          " and oracle, which cheats by seeing the hidden Cells, as an upper bound on what any Incumbent could do.")
    print("Insurgent bots: raid, politics (rally and organize), mixed, and smart (organizes to keep Cells, rallies toward four islands, raids only where no Garrison can sweep).")
    for title, opts in [("Two players", {}), ("With the Pillars", {"pillars": True}),
                        ("With the Rival", {"rival": True}), ("All four", {"pillars": True, "rival": True}),
                        ("House rule: a Sweep on a Suspected island hits on 2+", {"suspected_rule": True}),
                        ("House rule: raiding an island with a Garrison loses the Cell on a 1", {"raid_risk": 1}),
                        ("House rule: raiding an island with a Garrison loses the Cell on a 1-2", {"raid_risk": 2}),
                        ("House rule: raiding an island with a Garrison loses the Cell on a 1-3", {"raid_risk": 3}),
                        ("House rule: a Raid costs Patience only, not Supply", {"raid_supply": False}),
                        ("House rule: Patience starts at 30", {"patience": 30}),
                        ("House rule: Suspected 2+, and raiding a Garrison loses the Cell on a 1-2", {"suspected_rule": True, "raid_risk": 2})]:
        table = run(games, seed, **opts)
        print(f"\n== {title} ==")
        head = "Incumbent \\ Insurgent".ljust(22) + "".join(b.rjust(12) for b in INSURGENTS)
        print(head + "   (Insurgent win %)")
        for a in INCUMBENTS:
            print(a.ljust(22) + "".join(f"{100 * table[a, b][0]['insurgent'] / games:11.0f}%" for b in INSURGENTS))
        if opts.get("pillars"):
            print("Pillars win %:".ljust(22) + "".join("" for _ in INSURGENTS))
            for a in INCUMBENTS:
                print(("  " + a).ljust(22) + "".join(f"{100 * table[a, b][0]['pillars'] / games:11.0f}%" for b in INSURGENTS))
        if opts.get("rival"):
            print("Rival win %:")
            for a in INCUMBENTS:
                print(("  " + a).ljust(22) + "".join(f"{100 * table[a, b][0]['rival'] / games:11.0f}%" for b in INSURGENTS))
        hows = collections.Counter()
        for v in table.values():
            hows.update(v[1])
        total = sum(hows.values())
        print("How games ended:", ", ".join(f"{k} {100 * v / total:.0f}%" for k, v in hows.most_common()))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--games", type=int, default=3000)
    p.add_argument("--seed", type=int, default=2026)
    args = p.parse_args()
    report(args.games, args.seed)
