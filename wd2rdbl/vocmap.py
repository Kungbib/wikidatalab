import json
import unicodedata
import re
from pathlib import Path

from trld.api import parse_rdf
from trld.jsonld.base import (CONTAINER, CONTEXT, GRAPH, ID, INDEX, LANGUAGE,
                              TYPE, REVERSE, VALUE, VOCAB)

from .common import DEFAULT_CONTEXT, aslist

CACHE_DIR = Path(__file__).parent.parent / 'cache'

TERM_DFN = {
    "terms": {
        REVERSE: 'rdfs:isDefinedBy',
        CONTAINER: INDEX,
        INDEX: "matches",  # equivalentProperty / equivalentClass
        CONTEXT: {"matches": ID}
    },
    "matches": {ID: "skos:exactMatch", TYPE: VOCAB}
}


def main() -> None:
    vocmap: dict[str, object] = {CONTEXT: dict(DEFAULT_CONTEXT) | TERM_DFN}

    classfile = str(CACHE_DIR / 'wikidataclasses.ttl')
    classes = parse_rdf(classfile)
    process_terms(classes, vocmap, isclass=True)

    propfile = str(CACHE_DIR / 'wikidataproperties.ttl')
    properties = parse_rdf(propfile)
    process_terms(properties, vocmap)

    print(json.dumps(vocmap, ensure_ascii=False))


def process_terms(term_doc: dict, vocmap: dict, *, isclass=False, lang='en'):
    vocmap[CONTEXT].update(term_doc[CONTEXT])
    terms = vocmap.setdefault('terms', {})

    equiv_rel = 'owl:equivalentClass' if isclass else 'owl:equivalentProperty'

    for term_node in term_doc[GRAPH]:
        if ID not in term_node:
            continue
        term_id = term_node[ID]
        for literal in aslist(term_node['rdfs:label']):
            if literal[LANGUAGE] == lang:
                label = literal[VALUE]
                break
        else:
            continue

        equivs = [
            equiv[ID] for equiv in aslist(term_node.get(equiv_rel)) if ID in equiv
        ]

        rdbl_term: str | None = None

        for equiv in equivs:
            for pfx, ns in DEFAULT_CONTEXT.items():
                if equiv.startswith(f"{pfx}:"):
                    rdbl_term = equiv
                    break
                if equiv.startswith(ns):
                    rdbl_term = f"{pfx}:{equiv.removeprefix(ns)}"
                    break

        if not rdbl_term:
            rdbl_term = label_to_term(label)
            if isclass:
                rdbl_term = rdbl_term.title()
            rdbl_term += '_' + term_id.removeprefix('wd:')

        terms[term_id] = {"matches": rdbl_term}


def label_to_term(label: str) -> str:
    term = label

    for frm, to in [
        (' ', '_'),
        (':', '_'),
        ('/', '_'),
        ('-', '_'),
        ('&', 'and'),
        ('@', 'at'),
    ]:
        term = term.replace(frm, to)

    term = ''.join(
        c for c in unicodedata.normalize('NFD', term) if unicodedata.category(c) != 'Mn'
    )

    term = re.sub(r'[+"\'.()!?–‘’\xc2\xa0\n,]', '', term)

    wprop, *parts = term.split('_')
    term = ''.join(x[0].upper() + x[1:].lower() for x in parts if x.strip())
    term = f'{wprop.lower()}{term}'

    return term


if __name__ == '__main__':
    main()
