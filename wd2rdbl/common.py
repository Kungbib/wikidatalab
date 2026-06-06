from trld.jsonld.keys import (CONTAINER, CONTEXT, GRAPH, ID, INDEX, LANGUAGE,
                              TYPE, REVERSE, VALUE, VOCAB)

ANNOTATION = '@annotation'

DCT = "http://purl.org/dc/terms/"
SDO = 'https://schema.org/'
PROV = 'http://www.w3.org/ns/prov#'

DEFAULT_CONTEXT = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "sdo": "https://schema.org/",
    "dct": "http://purl.org/dc/terms/"
}

WIKIBASE = "http://wikiba.se/ontology#"
WD = "http://www.wikidata.org/entity/"
WD_STMT = "http://www.wikidata.org/entity/statement/"
WD_REF = "http://www.wikidata.org/reference/"
WDCOMMONS = "http://commons.wikimedia.org/entity/"
WD_DATA = "https://www.wikidata.org/wiki/Special:EntityData/"

WD2RDBL = "https://kungbib.github.io/wd2rdbl/ns/"

USER_AGENT = 'WD2RDBL/0.1 (https://libris.github.io/wikidatalab/; niklas.lindstrom@kb.se)'


def aslist(v) -> list:
    return [] if v is None else v if isinstance(v, list) else [v]
