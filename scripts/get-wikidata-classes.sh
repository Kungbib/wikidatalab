#!/bin/bash
curl -s https://query.wikidata.org/sparql -HAccept:text/turtle --data-urlencode 'query=

CONSTRUCT {
    ?class a rdfs:Class ;
        rdfs:label ?l ;
        owl:equivalentClass ?equiv ;
        rdfs:subClassOf ?base .
} WHERE {
    ?class wdt:P1709 ?equiv ;
      rdfs:label ?l .
    OPTIONAL { ?class wdt:P279 ?base . }
}

'
