import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen

from trld.api import serialize_rdf

from .common import CONTEXT, GRAPH, ID, USER_AGENT, aslist
from .hacks import commons2dataurl
from .jsonmapper import Mapper


def process(mapper, source, ds_map, include_media_data=False, user_agent=USER_AGENT):
    url = (
        source
        if '://' in source
        else f"https://www.wikidata.org/wiki/Special:EntityData/{source}.json?flavor=dump"
    )

    result = load_and_convert(mapper, url, user_agent)

    ds_map[url] = result

    if include_media_data:
        add_media_data(mapper, result, ds_map, user_agent)


def load_and_convert(mapper, url, user_agent):
    req = Request(url, headers={'User-Agent': user_agent})
    with urlopen(req) as f:
        data = json.load(f)
    return mapper.to_readable(data)


def add_media_data(mapper, result, ds_map, user_agent):
    graphitems = result[GRAPH] if GRAPH in result else result
    for node in aslist(graphitems):
        for objects in node.values():
            for o in aslist(objects):
                if isinstance(o, dict) and ID in o:
                    m_url = commons2dataurl(
                        o[ID], mediatype="application/json", user_agent=user_agent
                    )
                    if m_url:
                        mediadata = load_and_convert(mapper, m_url, user_agent)
                        ds_map[m_url] = {
                            ID: m_url,
                            GRAPH: mediadata[GRAPH],
                        }


def main():
    from .args import get_args

    args = get_args()

    with open(Path(__file__).parent.parent / 'cache' / 'vocmap.jsonld') as f:
        vocmap = json.load(f)

    mapper = Mapper(vocmap, args.nest_annotations, args.nest_quoted)

    ds_map = {}
    for source in args.sources:
        process(mapper, source, ds_map, include_media_data=True)

    graphs = list(ds_map.values())
    ctx = graphs[0].get(CONTEXT, {})
    dataset = {CONTEXT: ctx, GRAPH: graphs}
    serialize_rdf(dataset, args.output)


if __name__ == '__main__':
    main()
