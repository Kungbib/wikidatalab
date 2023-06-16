from typing import Iterator, cast
from urllib.parse import quote, urljoin

from .common import *


class Mapper:

    ctx: dict[str, object]
    prefixes: dict[str, str]

    def __init__(self, vocmap: dict):
        ctx = vocmap[CONTEXT]
        self.base = WD
        self.prefixes = DEFAULT_CONTEXT | {VOCAB: WD2RDBL}
        self.term_map = {
            (term.split(':', 1)[-1]): dfn['matches']
            for term, dfn in vocmap['terms'].items()
        }

    def to_readable(self, data: dict) -> dict:
        items: list[dict] = data['entities'].values() if 'entities' in data else [data]
        entities = [self._to_entity(qdata) for qdata in items]

        return {
            CONTEXT: self.prefixes,
            GRAPH: entities
        }

    def _to_entity(self, qdata: dict) -> dict:
        claims = qdata.get('claims') or qdata.get('statements') or {}

        qid: str = qdata['id']

        types = {
            typ for qtype in aslist(claims.get('P31'))  # instanceOf
            if (typ := self._map_type(qtype))
            if qtype.get('rank') == 'normal'
        } or {qdata['type'].title()}

        entity = cast(dict[str, object], self._to_link(qid))

        entity[TYPE] = list(types)

        for literal_key, prop in [('labels', 'rdfs:label'), ('descriptions', 'sdo:description')]:
            entity[prop] = [
                {f"@{k}": v for k, v in literal.items()}
                for literal in qdata.get(literal_key, {}).values()
            ]

        revs = cast(dict, entity.setdefault(REVERSE, {}))

        title = qdata.get('title')
        if title and title != qid:
            if title.startswith('File:'):
                revs['sdo:encodesCreativeWork'] = self._to_commons_link(title)
            else:
                entity['dct:title'] = title

        for prop, objects in self._map_claims(claims):
            entity[prop] = objects

        revs["sdo:mainEntity"] = {
            ID: urljoin(WD_DATA, qid),
            TYPE: 'sdo:Dataset',
            'dct:modified': qdata.get('modified')
        }

        return entity

    def _map_type(self, qtype) -> str | dict | None:
        if 'mainsnak' not in qtype:
            return None

        snak = qtype['mainsnak']
        if 'datavalue' not in snak:
            return None

        type_id = snak['datavalue']['value']['id']
        # TODO: add type references as quoted type annotations!

        return self._to_symbol(type_id)

    def _map_claims(self, claims) -> Iterator[tuple[str, list[object]]]:
        for qkey, qvalues in claims.items():
            prop = self.term_map.get(qkey, qkey)
            objects = [
                self._to_object(
                    qvalue['mainsnak'], qvalue.get('references'), qvalue.get('qualifiers')
                )
                for qvalue in aslist(qvalues)
                if qvalue.get('rank', 'normal') == 'normal'
                and qvalue['mainsnak']['snaktype'] != 'novalue'
                # TODO: '@quoted' if not normal?
            ]

            yield prop, objects

    def _to_object(
        self, snak: dict, references: list | None = None, qualifiers: dict | None = None
    ) -> object:
        if snak['snaktype'] == 'somevalue':
            return None

        o = self._to_simple_object(snak)

        if references or qualifiers:
            if not isinstance(o, dict):
                o = {VALUE: o}

            annots: dict = {}
            if references:
                annots['reference'] = [
                    self._map_reference(it['snaks'])
                    for it in references
                ]

            if qualifiers:
                annots['qualification'] = self._map_reference(qualifiers)

            if annots:
                o[ANNOTATION] = annots

        return o

    def _to_simple_object(self, snak: dict, islink=False) -> object:
        datatype: str | None = snak.get('datatype')
        datavalue: dict | None = snak.get('datavalue')
        if datavalue is None:
            return None

        value = datavalue['value']

        match datavalue['type']:
            case 'wikibase-entityid':
                return self._to_link(value['id'])

            case 'string':
                if islink or datatype == 'commonsMedia':
                    return self._to_commons_link(value)
                elif islink or datatype == 'url':
                    return self._to_link(value)
                else:
                    return value

            case 'monolingualtext':
                return {VALUE: value['text'], LANGUAGE: value['language']}

            case 'quantity':
                s: str = value['amount']
                v: int | float | str
                try:
                    v = float(s) if '.' in s else int(s)
                except ValueError:
                    v = s
                match value['unit']:
                    case '1':
                        return v
                    case unit:
                        return {TYPE: self._to_symbol(unit), 'rdf:value': v}

            case 'time':
                dt_type = 'xsd:dateTime'  # TODO: map 'calendarmodel'!
                return {VALUE: value['time'], TYPE: self._to_symbol(dt_type)}

            case 'globecoordinate':
                return {
                    TYPE: 'GlobeCoordinate',
                } | {
                    key: self._to_link(value) if key == 'globe' else value
                    for key, value in value.items()
                }

            case _:
                return snak

    def _map_reference(self, snaks: dict) -> dict:
        entity = {}

        for skey, svalues in snaks.items():
            prop = self.term_map.get(skey, skey)
            islink = prop == 'p4656-wikimediaImportUrl'
            objects = [self._to_simple_object(snak, islink) for snak in aslist(svalues)]

            entity[prop] = objects

        return entity

    def _to_commons_link(self, ref: str) -> dict[str, str]:
        if '://' not in ref:
            fname = quote(ref.removeprefix('File:'))
            ref = f"https://commons.wikimedia.org/wiki/Special:FilePath/{fname}"
        return self._to_link(ref)

    def _to_link(self, o: str) -> dict[str, str]:
        base = WDCOMMONS if o.startswith('M') else self.base
        return {ID: urljoin(base, o)}

    def _to_symbol(self, o: str) -> str:
        return self.term_map.get(o, o.removeprefix(self.prefixes[VOCAB]))


if __name__ == '__main__':
    import json
    import sys
    from pathlib import Path

    with open(Path(__file__).parent.parent / 'cache' / 'vocmap.jsonld') as f:
        vocmap = json.load(f)

    mapper = Mapper(vocmap)

    data = json.load(sys.stdin)
    result = mapper.to_readable(data)
    print(json.dumps(result, indent=2, ensure_ascii=False))
