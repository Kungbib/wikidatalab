from trld.jsonld.base import (CONTAINER, CONTEXT, GRAPH, ID, INDEX, LANGUAGE,
                              TYPE, REVERSE, VALUE, VOCAB)

ANNOTATION = '@annotation'

DCT = "http://purl.org/dc/terms/"
SDO = 'https://schema.org/'

DEFAULT_CONTEXT = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "sdo": "https://schema.org/",
    "dct": "http://purl.org/dc/terms/"
}

WD = "http://www.wikidata.org/entity/"
WDCOMMONS = "http://commons.wikimedia.org/entity/"
WD_DATA = "https://www.wikidata.org/wiki/Special:EntityData/"

WD2RDBL = "https://kungbib.github.io/wd2rdbl/ns/"


def aslist(v) -> list:
    return [] if v is None else v if isinstance(v, list) else [v]
