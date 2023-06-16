import json
import sys
from pathlib import Path

from .jsonmapper import CONTEXT, GRAPH, ID, REVERSE, Mapper

MAIN_ENTITY = 'sdo:mainEntity'
ENCODES_WORK = 'sdo:encodesCreativeWork'


with open(Path(__file__).parent.parent / 'cache' / 'vocmap.jsonld') as f:
    vocmap = json.load(f)

mapper = Mapper(vocmap)


def convert(l: str) -> str | None:
    if not l.startswith('{'):
        return None

    try:
        l = l.rstrip()
        if l.endswith('},'):
            l = l[:-1]

        data = json.loads(l)
        result = mapper.to_readable(data)

        del result[CONTEXT]
        graph = result[GRAPH]
        if graph:
            item = graph[0]
            revs = item.pop(REVERSE, None)
            if revs:
                for rel in [MAIN_ENTITY, ENCODES_WORK]:
                    if ref := revs.get(rel):
                        ref[rel] = {ID: item[ID]}
                        if rel == MAIN_ENTITY:
                            graph.insert(0, ref)
                        else:
                            graph.append(ref)

    except Exception as e:
        printerr(f"Error: {repr(e)} in: {l}")
        return None

    return json.dumps(result, ensure_ascii=False)


def printerr(s):
    print(s, file=sys.stderr)


if __name__ == '__main__':
    import time
    from datetime import timedelta
    from multiprocessing import Pool

    pool = Pool()

    start = time.time()
    checkpoint = start
    j = 0

    batch: list[str] = []
    batch_size = 4096

    def process_batch():
        global batch
        for result in pool.map(convert, batch):
            if result:
                print(result)
        batch = []

    try:
        for i, l in enumerate(sys.stdin):
            batch.append(l)
            if i and i % batch_size == 0:
                process_batch()

            now = time.time()
            elapsed = now - checkpoint
            if elapsed > 4:
                r = (i - j) / elapsed
                delta = timedelta(seconds=int(now - start))
                printerr(f"[{delta}] At {i:,} ({r:.3f} lines/second)")
                checkpoint = now
                j = i

        process_batch()

    except KeyboardInterrupt:
        pool.terminate()
        printerr("Aborted.")
