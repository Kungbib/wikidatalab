import subprocess
from pathlib import Path
from typing import cast

from trld.api import parse_rdf, serialize_rdf
from trld.jsonld.keys import GRAPH, ID, LANGUAGE, TYPE, VALUE

from .common import WD, aslist
from .vocmap import clean_characters, label_to_term


class TypeLabels:
    indexfile: Path
    index: dict[str, str]

    def __init__(self, cachedir: Path):
        self.indexfile = cachedir / 'typelabels.tsv'
        self.index = self.load()

    def get(self, qid: str) -> str | None:
        typelabel = self.index.get(qid)
        if typelabel is None:
            typelabel = fetch_label(qid)
            if typelabel:
                self.index[qid] = typelabel

        if typelabel:
            typelabel = label_to_term(typelabel)
            typelabel = typelabel[0].upper() + typelabel[1:]

        return typelabel

    def load(self) -> dict[str, str]:
        if not self.indexfile.exists():
            return {}
        with self.indexfile.open() as f:
            return dict(l.rstrip().split('\t', 1) for l in f)

    def save(self) -> None:
        with self.indexfile.open('w') as f:
            for k, v in self.index.items():
                print(k, v, sep='\t', file=f)


def fetch_label(qid: str, lang='en') -> str | None:
    qid = qid.removeprefix('wd:')
    query = 'select ?l { wd:%s rdfs:label ?l . FILTER(lang(?l) = "%s") } limit 1' % (qid, lang)
    endpoint = "https://query.wikidata.org/sparql"
    try:
        args = [
            "curl", "-f", "-s", endpoint, "-HAccept:text/csv", "--data-urlencode", f"query= {query}"
        ]
        out = subprocess.run(args, check=True, capture_output=True).stdout
        rows = out.decode('utf-8').split('\n')
        if len(rows) > 1:
            return rows[1].rstrip()
    except:
        pass

    return None


def replace_ids(itemlabels: dict[str, str], item: dict[str, object]) -> None:
    if ID in item:
        itemid = cast(str, item[ID]).removeprefix(WD).removeprefix('wd:')
        idlabel: object = itemlabels.get(itemid)
        if idlabel is None:
            idlabel = item.get('rdfs:label')
            if isinstance(idlabel, dict):
                idlabel = idlabel[VALUE]
            if idlabel is None:
                idlabel = fetch_label(itemid)
            if isinstance(idlabel, str):
                itemlabels[idlabel] = idlabel
        if isinstance(idlabel, str):
            labelterm = (
                clean_characters(idlabel).replace(' ', '_').replace('__', '_').lower()
            )
            item[ID] = f'{labelterm}_{itemid}'

    for vs in item.values():
        for v in aslist(vs):
            if isinstance(v, dict):
                replace_ids(itemlabels, v)


def main():
    import sys

    itemlabels = {}
    typelabels = TypeLabels(Path(__file__).parent.parent / 'cache')

    args = sys.argv[1:]
    if args:
        for arg in args:
            print(typelabels.get(arg))
    else:
        data = parse_rdf('-', 'ttl')
        for item in data[GRAPH]:
            itypes = aslist(item.get(TYPE))
            ltypes = []
            for itype in itypes:
                ltype = typelabels.get(itype)
                ltypes.append(ltype if ltype and ltype != itype else itype)

            if ltypes:
                item[TYPE] = ltypes[0] if len(ltypes) == 1 else ltypes

            replace_ids(itemlabels, item)

        serialize_rdf(data, 'trig')

    typelabels.save()


if __name__ == '__main__':
    main()
