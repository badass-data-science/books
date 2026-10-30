"""Chapter 23's Turtle and SPARQL examples, as printed in the book.

Needs rdflib (pip install rdflib). Run it from anywhere:
    python chapter_23_graphs.py
It prints each query's results: the mine's delivery time, the one agent nobody
reviews, and everything downstream of Omen.
"""
from rdflib import Graph

SUPPLY_CHAIN = """
@prefix : <http://secretlab.example/supply-chain#> .

:mine     :suppliesTo            :refinery .
:mine     :shippingDelayDays     14 .
:refinery :increasesDefectRateOf :assemblyLine .
"""

SLOW_SUPPLIERS = """
PREFIX : <http://secretlab.example/supply-chain#>

SELECT ?supplier ?customer ?days WHERE {
  ?supplier :suppliesTo        ?customer ;
            :shippingDelayDays ?days .
  FILTER (?days > 10)
}
"""

OPERATIONS = """
@prefix : <http://secretlab.example/operations#> .

:omen         a :Agent ;
              :actsOn        :deathRayRevenueForecast ;
              :reviewedBy    :ourHeroine .
:codingAgent  a :Agent ;
              :actsOn        :deathRayControlSoftware ;
              :reviewedBy    :reviewTeam .
:pricingAgent a :Agent ;
              :actsOn        :deathRayPrices ;
              :readsOutputOf :omen .
"""

UNREVIEWED_AGENTS = """
PREFIX : <http://secretlab.example/operations#>

SELECT ?agent ?target WHERE {
  ?agent a :Agent ;
         :actsOn ?target .
  FILTER NOT EXISTS { ?agent :reviewedBy ?anyone }
}
"""

# The chapter gives only this query's pattern; the rest is the usual wrapping
DOWNSTREAM_OF_OMEN = """
PREFIX : <http://secretlab.example/operations#>

SELECT ?downstream WHERE {
  ?downstream :readsOutputOf+ :omen
}
"""


def show(title, turtle, query):
    graph = Graph()
    graph.parse(data=turtle, format="turtle")
    print(title)
    for row in graph.query(query):
        # Keep only what follows the # in each name, so ":mine" prints as "mine"
        print("  ", *(str(value).split("#")[-1] for value in row))


show("Suppliers taking more than ten days:", SUPPLY_CHAIN, SLOW_SUPPLIERS)
show("Agents acting with nobody reviewing them:", OPERATIONS, UNREVIEWED_AGENTS)
show("Everything an Omen error would flow into:", OPERATIONS, DOWNSTREAM_OF_OMEN)
