# Code from *Systems Thinking for Supervillains*

These files accompany the book *Systems Thinking for Supervillains: Feedback, Causality, and Mental Models for the Age of Agentic AI* by Lady Napalm. They let you run the Python examples printed in the book for yourself, using the same system dynamics model the book builds.

## Files

- **`quantified-supply-chain.xmile`**: the Doomsday Device Supply Chain model from Chapter 16, in XMILE, the standard file format for system dynamics models. It has the supply chain's stocks, flows and constants, plus Chapter 10's feedback loop translated into stocks and flows. A few values the book never states are marked `PLACEHOLDER` in the file. Both Python scripts load this model.
- **`chapter_17_pysd.py`**: Chapter 17's example, exactly as printed apart from a short description at the top. It loads the model with PySD, runs it, and prints the first eight weeks of refined villainium on hand and the warhead stockpile.
- **`chapter_18_sobol.py`**: Chapter 18's Sobol sensitivity analysis. It tests whether the model's recommendation (expand assembly capacity rather than stop cutting corners) survives uncertainty in two of its guesses, and prints the S1, ST and S2 indices. Besides the printed code, it includes the `run_doomsday_model()` wrapper the book describes but doesn't show, along with the imports that wrapper needs and a filter for one PySD warning. It takes about a minute to run.

## Running the code

Install the libraries, then run each script from inside this directory, so it can find the model:

```
pip install pysd SALib
python chapter_17_pysd.py
python chapter_18_sobol.py
```

Each script prints the output shown in its chapter. Chapter 17's script needs only PySD.

PySD translates the model into Python the first time it loads it, so running either script also creates `quantified-supply-chain.py` and a `__pycache__` folder here. Both are generated files, and you can safely delete them.
