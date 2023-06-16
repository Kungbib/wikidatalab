vocmap: cache/vocmap.jsonld

cache/vocmap.jsonld: wd2rdbl/vocmap.py cache/wikidataproperties.ttl cache/wikidataclasses.ttl
	python3 -m wd2rdbl.vocmap > $@

cache/wikidataproperties.ttl: scripts/get-wikidata-properties.sh | cache
	scripts/get-wikidata-properties.sh | trld -i ttl -e -f -c -o ttl > $@

cache/wikidataclasses.ttl: scripts/get-wikidata-classes.sh | cache
	scripts/get-wikidata-classes.sh | trld -i ttl -e -f -c -o ttl > $@

cache:
	mkdir -p cache
