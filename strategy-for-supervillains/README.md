# Code from *Strategy for Supervillains*

These small programs accompany *Strategy for Supervillains: War, Revolution, and the Art of Outthinking Opponents Who Think Back* by Lady Napalm. The book doesn't need them: everything in it works with a pen, a coin, a die, and a friend. They're here for readers who'd like to play a game ten thousand times instead of five, or change a rule and see what happens.

Each program needs only Python 3, with nothing else to install, and each prints its results as text. Run them from inside this folder.

## Files

- **`iterated_prisoners_dilemma.py`** (Chapter 4, "Play-It — Trenches"): a round-robin tournament of strategies for the repeated Prisoner's Dilemma, in the spirit of Robert Axelrod's, with the Play-It's scores. It runs twice: ten rounds that everyone knows are coming, and a game that could end after any round. Add `--noise 0.05` to make some moves go wrong by mistake.
- **`colonel_blotto.py`** (Chapter 11, "Play-It — Blotto"): six ways of dividing 100 points among five islands, each played against the others thousands of times, followed by a chain of plans, each beating the one before. Add `--plan 30,30,30,5,5` to watch the program find a counter to your own plan.
- **`threshold_cascade.py`** (Chapter 24): Mark Granovetter's threshold model of a riot. It reproduces the chapter's two nearly identical crowds (Figure 24.1), one of which riots while the other doesn't, then shows how the outcome jumps as a crowd's thresholds spread out. Add `--thresholds 0,1,1,3,3,5,8` to try a crowd of your own.
- **`caldera_sim.py`** (Appendix E): computer players play the book's wargame, *Caldera*, thousands of times, with and without the optional Pillars and Rival, and the program reports who wins and how. It prints the assumptions it makes where the rules are silent, and its last tables try house rules that change how raiding works. It takes about 25 seconds.

```
python iterated_prisoners_dilemma.py
python colonel_blotto.py
python threshold_cascade.py
python caldera_sim.py
```

Every program takes a `--seed`, so a run can be repeated exactly, and `--help` lists its other options.

## A warning, in the book's spirit

These are toys. The bots are simple, the games are smaller than any real contest, and a number printed to one decimal place is not a forecast. Chapter 36 has the longer version: a model is good at raising questions and poor at answering them. If one of these programs surprises you, the useful next step is to ask why, and then to go and play the game with people.
