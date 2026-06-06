#set page(
  paper: "a4",
  header: align(
    right + horizon,
    context document.title,
  ),
  numbering: "1",
  columns: 2,
)

#set text(
  size: 9pt,
)

#set par(justify: false)

#show title: set text(size: 17pt)
#show title: set align(center)

#place(
  top + center,
  float: true,
  scope: "parent",
  clearance: 2em,
)[
  #title[
    Using RDF 1.2 to Simplify The Encoding of Wikidata Statements
  ]

  #grid(
    columns: (2fr),
    align(center)[
      Niklas Lindström \
      National Library of Sweden \
      #link("mailto:niklas.lindstrom@kb.se")
    ],
  )

  #align(center)[
    #set par(justify: false)
    *Abstract* \
    It is possible to simplify the RDF-encoded Wikidata statement model without losing information. This can be done by leveraging triple reifiers and annotations as specified in RDF 1.2.
  ]
]

#show raw.where(block: true): it => block(
  fill: rgb("ddd"),
  inset: 8pt,
  radius: 5pt,
  text(0.75em, it)
)

== Prelude

The following prefix declarations are assumed throughout this document:
```turtle
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
PREFIX pqv: <http://www.wikidata.org/prop/qualifier/value/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdref: <http://www.wikidata.org/reference/>
PREFIX wds: <http://www.wikidata.org/entity/statement/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
```

== Statements as Reifiers

In Wikidata #footnote[https://www.wikidata.org/], the RDF-encoded descriptions about an entity contain detailed statements (context nodes for "snak" assertions/key-value pairs), such as:
```turtle
wd:Q102071
  p:P373 wds:q102071-DD501184-4DDD-4F5A-8E1A-003222D87635 .

wds:q102071-DD501184-4DDD-4F5A-8E1A-003222D87635
  a wikibase:Statement, wikibase:BestRank ;
  wikibase:rank wikibase:NormalRank ;
  ps:P373 "Tove Jansson" ;
  prov:wasDerivedFrom
    wdref:fa278ebfc458360e5aed63d5058cca83c46134f1 .
```
Each such statement has a corresponding simple assertion, like:
```turtle
wd:Q102071 wdt:P373 "Tove Jansson" .
```

By using *RDF 1.2#footnote[https://www.w3.org/TR/rdf12-concepts/] annotations*, the  simplified triple can instead be directly associated with the corresponding detailed statement:
```turtle
wd:Q102071 wdt:P373 "Tove Jansson"
    ~ wds:q102071-DD501184-4DDD-4F5A-8E1A-003222D87635 .

wds:q102071-DD501184-4DDD-4F5A-8E1A-003222D87635
  a wikibase:Statement, wikibase:BestRank ;
  wikibase:rank wikibase:NormalRank ;
  prov:wasDerivedFrom
    wdref:fa278ebfc458360e5aed63d5058cca83c46134f1 .
```
This represents the same amount of information, structured and expressed a bit differently, in order to leverage the more compact Turtle 1.2#footnote[https://www.w3.org/TR/rdf12-turtle/] annotation syntax.

The annotation itself is actually a shorthand for two triples:
```turtle
wd:Q102071 wdt:P373 "Tove Jansson" .

wds:q102071-DD501184-4DDD-4F5A-8E1A-003222D87635
  rdf:reifies <<( wd:Q102071 wdt:P373 "Tove Jansson" )>> .
```
where the latter is a *reifying triple*, connecting the Statement resource to the proposition (i.e., the propositional meaning) denoted by the first triple.

Note that the statement predicate-value `ps:P373 "Tove Jansson"` was omitted in the reduced example, since the reifying relation to the proposition itself captures this information (along with the subject).

It should also be noted that if a triple is not asserted (its propositional meaning is not considered to be a known truth), the reifying triple can still be used without the corresponding asserted triple. There is a shorthand for that form as well:

```turtle
<< wd:Q102071 wdt:P373 "Tove Jansson"
   ~ wds:q102071-DD501184-4DDD-4F5A-8E1A-003222D87635 >> .
```

== Multiple Reifiers of One Statement

There are many cases where multiple distinct qualified statements are related to one simplified, direct statement. Consider the Academy Award for Best Actress, given to Elisabeth Taylor in 1961 and 1967, respectively:
```turtle
wd:Q34851
  wdt:P166 wd:Q103618 ;
  p:P166 wds:Q34851-9A17B21E-99CC-4AB2-9C8A-7B859CF5FB89 ,
    wds:Q34851-916BCB92-388B-4431-A480-529E319CA72D .

wds:Q34851-9A17B21E-99CC-4AB2-9C8A-7B859CF5FB89
  a wikibase:Statement , wikibase:BestRank ;
  wikibase:rank wikibase:NormalRank ;
  prov:wasDerivedFrom
    wdref:a1e319a3623b741c0f0a06f0a8c49b09484b4c16 ;
  pq:P1686 wd:Q652069 ;
  pq:P585 "1961-04-17T00:00:00Z"^^xsd:dateTime ;
  pq:P805 wd:Q917071 ;
  pqv:P585 wdv:a3e73d0bebb80f81d7e82e5b15153137 ;
  ps:P166 wd:Q103618 .

wds:Q34851-916BCB92-388B-4431-A480-529E319CA72D
  a wikibase:Statement , wikibase:BestRank ;
  wikibase:rank wikibase:NormalRank ;
  prov:wasDerivedFrom
    wdref:0bd21561fed8da57859baf4bd22f39a8d8dc1889 ;
  pq:P1686 wd:Q325643 ;
  pq:P585 "1967-04-10T00:00:00Z"^^xsd:dateTime ;
  pq:P805 wd:Q167214 ;
  pqv:P585 wdv:9b6b996289afab5e4c2f37f48c3e74f5 ;
  ps:P166 wd:Q103618 .
```

Since, likewise, there can be multiple reifiers of the same triple in RDF 1.2, the first description block in the previous example can be simplified as:
```turtle
wd:Q34851 wdt:P166 wd:Q103618
      ~ wds:Q34851-9A17B21E-99CC-4AB2-9C8A-7B859CF5FB89
      ~ wds:Q34851-916BCB92-388B-4431-A480-529E319CA72D .
```
(along with omitting the corresponding `ps:P166 wd:Q103618` from the statement nodes).

== Reduce Using SPARQL Update

The following simple SPARQL 1.2#footnote[https://www.w3.org/TR/sparql12-update/] update can be used to turn data into the previously described annotation form:
```sparql
PREFIX wikibase: <http://wikiba.se/ontology#>

delete {
  ?x ?p ?stmt .
  ?stmt ?stp ?dv .
}
insert {
  << ?x ?dp ?dv ~ ?stmt >> .
}
where {
  ?x ?dp ?dv .
  ?x ?p ?stmt .
  ?stmt ?stp ?dv .
  ?wp
    wikibase:claim ?p ;
    wikibase:directClaim ?dp ;
    wikibase:statementProperty ?stp .
}
```

== On Qualifiers and References

In the wikidata model, each statement can have multiple *qualifiers* and *references*.

For example, in the following information about one of the award statements:
```turtle
wds:Q34851-9A17B21E-99CC-4AB2-9C8A-7B859CF5FB89
  pq:P585 "1961-04-17T00:00:00Z"^^xsd:dateTime .
```
the `pq:P585` property is used to provide a "point in time". Not for when the statement was made in Wikidata, but as a circumstantial qualifier of when the award was given to Elisabeth Taylor. With the current model, one can assume that references associated with a statement also, in full on in part, are related to such particular qualifiying aspects of that statement.

It could be valuable to distinguish the qualifying structure as a distinct reifier. This would make the nature of the reifier more clear, as an *event* or *situation* underlying the simple proposition (the latter being an abstract relationship induced by the more concrete circumstance).

Here is a possible remodelling, using the underlying temporal event of each award as a reifier of the simple award relationship; and also using the reference entities themselves as reifiers of both the simple statement, and of the particulars of each qualification:

```turtle
wd:Q34851 wdt:P166 wd:Q103618
    {| a prov:InstantaneousEvent ;
      pq:P1686 wd:Q652069
          ~ wdref:a1e319a3623b741c0f0a06f0a8c49b09484b4c16 ;
      pq:P805 wd:Q917071
          ~ wdref:a1e319a3623b741c0f0a06f0a8c49b09484b4c16 ;
      pq:P585 "1961-04-17T00:00:00Z"^^xsd:dateTime
          ~ wdref:a1e319a3623b741c0f0a06f0a8c49b09484b4c16
    |}
    {| a prov:InstantaneousEvent ;
      pq:P1686 wd:Q325643 ;
          ~ wdref:0bd21561fed8da57859baf4bd22f39a8d8dc1889 ;
      pq:P585 "1967-04-10T00:00:00Z"^^xsd:dateTime ;
          ~ wdref:0bd21561fed8da57859baf4bd22f39a8d8dc1889 ;
      pq:P805 wd:Q167214 ;
          ~ wdref:0bd21561fed8da57859baf4bd22f39a8d8dc1889
    |}
    ~ wdref:a1e319a3623b741c0f0a06f0a8c49b09484b4c16
    ~ wdref:0bd21561fed8da57859baf4bd22f39a8d8dc1889 .
```
This illustrates a flattening into multiple refiers, where each reference can also be a reifier of multiple statements, including the qualified statements about each corresponding event.

It is an open question whether this variant increases precision and utility, and/or increases the burden of consuming and maintaining these facts.

== Preferring Datatypes Over Qualified Values

Another kind of qualification used by Wikidata are the basic datatyped literals accompanied by detailed descriptions of such values. For example, date/time values described with precision, timezone and/or calendar model:
```turtle
wds:Q34851-9A17B21E-99CC-4AB2-9C8A-7B859CF5FB89
  pq:P585 "1961-04-17T00:00:00Z"^^xsd:dateTime ;
  pqv:P585 wdv:a3e73d0bebb80f81d7e82e5b15153137 .

wdv:a3e73d0bebb80f81d7e82e5b15153137 a wikibase:TimeValue ;
  wikibase:timeCalendarModel wd:Q1985727 ;
  wikibase:timePrecision "11"^^xsd:integer ;
  wikibase:timeTimezone "0"^^xsd:integer ;
  wikibase:timeValue "1961-04-17T00:00:00Z"^^xsd:dateTime .
```
However, since the XSD datatypes#footnote[https://www.w3.org/TR/xmlschema11-2/] for dates and times already encode these details, the previous expression can reasonably be turned into just:
```turtle
wds:Q34851-9A17B21E-99CC-4AB2-9C8A-7B859CF5FB89
  pq:P585 "1961-04-17"^^xsd:date .
```
without losing any precision, since `"1961-04-17"^^xsd:date` encodes the same amount of information (including being a date in the proleptic Gregorian calendar model#footnote[https://www.wikidata.org/wiki/Q1985727]).

== Further Exploration

To implement the proposals of this paper, SPARQL may be used (as shown). Another approach is to transform the native Wikidata JSON format to RDF. It is possible to define a JSON-LD context for this purpose, but due to various idiosyncrasies and repetition of properties, it may be cumbersome to maintain a "zero edit" context for this purpose. Another way is by mapping the data programmatically. An example implementation#footnote[https://github.com/Kungbib/wikidatalab] of these ideas has been written, and can be used for further evaluation of approaches and usefulness of the results.
