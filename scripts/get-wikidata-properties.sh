#!/bin/bash
curl -s https://query.wikidata.org/sparql -HAccept:text/turtle --data-urlencode 'query=

CONSTRUCT {
    ?prop a rdf:Property ;
        rdfs:label ?l ;
        owl:equivalentProperty ?equiv
} WHERE {
    ?prop a wikibase:Property; rdfs:label ?l .
    OPTIONAL { ?prop wdt:P1628 ?equiv }
}

'
