import json
import sys
from pathlib import Path
from urllib.request import urlopen

from trld.api import serialize_rdf

from .common import CONTEXT, GRAPH, ID, aslist
from .hacks import commons2dataurl
from .jsonmapper import Mapper


def process(mapper, source, ds_map, include_media_data=False):
    url = (
        source
        if '://' in source
        else f"https://www.wikidata.org/wiki/Special:EntityData/{source}.json?flavor=dump"
    )

    result = load_and_convert(mapper, url)

    ds_map[url] = result

    if include_media_data:
        add_media_data(mapper, result, ds_map)


def load_and_convert(mapper, url):
    with urlopen(url) as f:
        data = json.load(f)
    return mapper.to_readable(data)


def add_media_data(mapper, result, ds_map):
    graphitems = result[GRAPH] if GRAPH in result else result
    for node in aslist(graphitems):
        for objects in node.values():
            for o in aslist(objects):
                if isinstance(o, dict) and ID in o:
                    m_url = commons2dataurl(o[ID], mediatype="application/json")
                    if m_url:
                        mediadata = load_and_convert(mapper, m_url)
                        ds_map[m_url] = {
                            ID: m_url,
                            GRAPH: mediadata[GRAPH],
                        }


def main():
    with open(Path(__file__).parent.parent / 'cache' / 'vocmap.jsonld') as f:
        vocmap = json.load(f)

    mapper = Mapper(vocmap)

    sources = sys.argv[1:]

    ds_map = {}
    for source in sources:
        process(mapper, source, ds_map, include_media_data=True)

    graphs = list(ds_map.values())
    ctx = graphs[0].get(CONTEXT, {})
    dataset = {CONTEXT: ctx, GRAPH: graphs}
    serialize_rdf(dataset, 'trig')


if __name__ == '__main__':
    main()
