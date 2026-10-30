"""Chapter 17's PySD example, as printed in the book.

Needs PySD (pip install pysd). Run it from this directory, so it can find
quantified-supply-chain.xmile:
    python chapter_17_pysd.py
PySD translates the model to quantified-supply-chain.py beside the XMILE file.
"""
import pysd

# Load Chapter 16's supply-chain model from its XMILE file
# (a Vensim .mdl file loads the same way, with pysd.read_vensim)
model = pysd.read_xmile("quantified-supply-chain.xmile")

# Run it forward, exactly as the simulation software would,
# but now as a plain pandas DataFrame our Heroine can query
results = model.run()

print(results[["Refined Villainium On Hand", "Warhead Stockpile"]].head(9))
