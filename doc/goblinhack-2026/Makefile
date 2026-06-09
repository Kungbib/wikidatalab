.PHONY: all
all: presentation.md examples/Q102071-refsets.ttl

presentation.html: presentation.md
	marp $@

examples/Q102071-refsets.ttl: examples/Q102071-rdf12.ttl wd-refsets.rq
	oxrq -f wd-refsets.rq examples/Q102071-rdf12.ttl | python -m gnarly.trig > $@

examples/Q102071-rdf12.ttl: examples/Q102071-dump.ttl examples/Q102071-full.ttl wd-annotations.ru
	(cat examples/Q102071-dump.ttl; echo 'graph _:full {'; cat examples/Q102071-full.ttl | grep -v '^@prefix '; echo '}') | oxrq -f wd-annotations.ru -itrig -ottl | python -m gnarly.trig > $@

examples/Q102071-full.ttl: examples
	curl -s -L -HAccept:text/turtle https://www.wikidata.org/entity/Q102071 > $@

examples/Q102071-dump.ttl: examples
	curl -s -L -HAccept:text/turtle "https://www.wikidata.org/wiki/Special:EntityData/Q102071.ttl?flavor=dump" | python -m gnarly.trig > $@

examples:
	mkdir -p examples
