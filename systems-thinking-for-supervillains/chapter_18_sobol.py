"""Chapter 18's Sobol analysis, as printed in the book, plus the wrapper the
book doesn't show.

The decision under test: expand assembly capacity by 10% (60 -> 66 tons/week)
or stop cutting corners on rushed ore (quality loss 0), both judged 26 weeks
into a six-week henchman shortage that takes 10 tons/week out of assembly in
weeks 2-7. run_doomsday_model() returns how many tons further ahead of schedule
expanding assembly leaves the stockpile.

Needs PySD and SALib (pip install pysd SALib). Run it from this directory, so
it can find quantified-supply-chain.xmile:
    python chapter_18_sobol.py
It runs the model 12,288 times (both options for each of 6,144 samples), which
takes about a minute. PySD translates the model to
quantified-supply-chain.py beside the XMILE file.
"""
from SALib.sample import sobol as sobol_sample
from SALib.analyze import sobol as sobol_analyze
import numpy as np
import pandas as pd
import pysd
import warnings

# PySD warns that the shortage replaces a constant with a time series, which is the point
warnings.filterwarnings("ignore", message="Replacing a constant value")

WEEKS = 26
TIMES = list(range(WEEKS + 1))
SHORTAGE_WEEKS, TONS_LOST = (2, 7), 10

model = pysd.read_xmile("quantified-supply-chain.xmile")


def shortfall(capacity, quality_loss, transit_time):
    """Tons behind schedule at week 26, given the assembly capacity outside the shortage."""
    hours = pd.Series(
        [capacity - (TONS_LOST if SHORTAGE_WEEKS[0] <= t <= SHORTAGE_WEEKS[1] else 0) for t in TIMES],
        index=TIMES,
    )
    model.reload()
    run = model.run(
        params={
            "Henchman Hours Capacity": hours,
            "Quality Loss From Corner Cutting": quality_loss,
            "Transit Time": transit_time,
        },
        final_time=WEEKS,
        return_columns=["Stockpile Shortfall"],
    )
    return float(run["Stockpile Shortfall"].iloc[-1])


def run_doomsday_model(quality_loss_from_corner_cutting, transit_time):
    """How many tons further ahead expanding assembly leaves the stockpile."""
    stop_cutting_corners = shortfall(60, 0.0, transit_time)
    expand_assembly = shortfall(66, quality_loss_from_corner_cutting, transit_time)
    return stop_cutting_corners - expand_assembly


problem = {
    "num_vars": 2,
    "names": ["quality_loss_from_corner_cutting", "transit_time"],
    "bounds": [[0.375, 0.625], [1.5, 2.5]],  # each guess, plus or minus 25%
}

# Sample the parameter space, then run the PySD model for each sample.
# run_doomsday_model() is the small wrapper above (the book doesn't show it):
# it sets the two parameters on the PySD model, runs both options through the
# shortage, and returns how many tons further ahead expanding assembly leaves
# the stockpile. Below zero, the recommendation has flipped.
param_values = sobol_sample.sample(problem, 1024, seed=42)
Y = np.array([
    run_doomsday_model(quality_loss_from_corner_cutting=p[0], transit_time=p[1])
    for p in param_values
])

Si = sobol_analyze.analyze(problem, Y, seed=42)
print("First-order (S1):", np.round(Si["S1"], 2))
print("Total-order (ST):", np.round(Si["ST"], 2))
print("Second-order (S2):", f"{Si['S2'][0, 1]:.2f}")
