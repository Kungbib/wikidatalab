
## Intro

Wishlist for Wikibase:

1. Relate the wikibase Statement to the direct claim using RDF 1.2
2. Optional removal of redundancy from the RDF encoding
3. More granular provenance (revisions as reifiers of added and removed triples)

----

## Part 1

Assert that the wikibase Statement reifies the direct statement:
```sparql
insert {
  ?statement rdf:reifies <<( ?entity ?direct_property ?object )>> .
}
where {
  ?entity ?direct_property ?object .

  ?entity ?property ?statement .
  ?statement ?statement_property ?object .

  [ wikibase:claim ?property ;
    wikibase:directClaim ?direct_property ;
    wikibase:statementProperty ?statement_property ] .
}
```

----

## This Simplifies Queries

Example SPARQL query changes from:

```sparql
?entity #?direct_property ?o ;
  ?property [ a wikibase:Statement, wikibase:BestRank ;
       ?statement_property ?object ;
       prov:wasDerivedFrom ?wdref ] .

[ wikibase:claim ?property ;
  wikibase:directClaim ?direct_property ;
  wikibase:statementProperty ?statement_property ] .
```

to:

```sparql
?entity ?direct_property ?object {| a wikibase:Statement ; prov:wasDerivedFrom ?wdref |} .
```

----

## Unobtrusive Change

- No change to wikibase semantics
- Not breaking anything
* so we add content negotiation
* new dumps

----

### Content Negotiation

Announce that you accept RDF 1.2:

```sh
$ curl --header "accept: text/turtle; version=1.2" http://www.wikidata.org/entity/Q102071
```

----

### Example Data

From:

```turtle
wd:Q102071
    wdt:P1343 wd:Q136677319 ;
    p:P1343 [ a wikibase:Statement ;
      ps:P1343 wd:Q136677319 ;
      prov:wasDerivedFrom wdref:192fa81d79cdd66a3848d91f8083327e9e612f13
    ] .
```

to:

```turtle
wd:Q102071 wdt:P1343 wd:Q136677319 {| a wikibase:Statement ;
    prov:wasDerivedFrom wdref:192fa81d79cdd66a3848d91f8083327e9e612f13
  |} .
```

----

## Part 2

Extending the model with explicit revision information.

Using PROV-O

----

### Is the wikibase Statement model granular enough?

* Doesn't granularly model each qualification or source.
* Avoids infinite regress, modality of opinion, etc.

----

### Statement versioning

There is a `revision_id` (always incremented) per triple(s)
- Example uses:
  - query for edits (all claims by user ?x; who said what when)
  - imports (all claims from results of a particular process)

----

### Wikibase Revision

```turtle
<rev1> a hist:Revision ;
  prov:wasAttributedTo <User:123> ;
  dct:date "2024-01-07T11:42:52+0200"^^xsd:dateTime ;
  wikibase:addition <<( wd:Q102071 a foaf:Person )>> ;
  wikibase:addition <<( wd:Q102071 foaf:name "Tove Jansson" )>> .

<rev2> a wikibase:Revision ;
  prov:wasAttributedTo <User:456> ;
  dct:date "2026-06-09T16:33:11+0200"^^xsd:dateTime ;
  wikibase:addition <<( wd:Q102071 foaf:givenName "Tove" )>> ;
  wikibase:addition <<( wd:Q102071 foaf:familyName "Jansson" )>> ;
  wikibase:removal <<( wd:Q102071 foaf:name "Tove Jansson" )>> .
```

----

### Asking for Revision Data

```
$ curl -s -L -HAccept:text/turtle https://www.wikidata.org/wiki/Special:EntityData/Q102071.ttl?revision=112
```

----


### Revise The SPARQL Store Update Mechanism

Currently, wikibase generates a SPARQL update doing INSERT DELETE (a "poorperson" version of graph-store-update)?

Proposal 0: for a non-versioned graph store, keep one named graph per wikibase entity (the "entity dataset")

Proposal 1.1: For a versioned graph approach: keep one named graph *per revision*

Proposal 1.2: For a versioned changeset approach: compute the delta of old and new graph, store each revision with 

----

### Detailed Revision Query

```sparql
?revision_id a :Revision ;
  prov:wasAttributedTo ?x ;
  wikibase:appears <<( ?add_s ?add_p ?add_o )>> ;
  wikibase:retracts <<( ?rm_s ?rm_p ?rm_o )>> .
```

