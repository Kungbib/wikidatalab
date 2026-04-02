# Wikidata Lab

Experimental tooling for working with Wikidata dumps.

## WD2RDBL - Readable Wikidata

This tool maps the numbered P-properties into *either* a "well-known"
`owl:equivalentProperty`, or a generated "camelCased" term based on its English
label. When Q-items are used with P31 ("instance of"), it replaces those with
any found `owl:equivalentClass`.

It uses the direct form of statements, but keeps the qualified data together
with these by using
[RDF 1.2 annotations](https://www.w3.org/TR/rdf12-concepts/#dfn-triple-annotation).

### Example Output (Excerpt)
```turtle
<http://www.wikidata.org/entity/Q102071> a sdo:Person ;
  sdo:name "Jansson, Tove"@sv
      {| a :Qualification ; sdo:alternateName "Ânson, Tuve", "Ânsson, Tuve", "Jānsone, Tūve", "يانسون، توفا" |}
      ~ wdref:8566348fa77729d56b55c24bd29f18f5e6631f99 ;
  rdfs:label "Tove Jansson"@es, "توفي يانسون"@ar, "Туве Янсон"@bg, "Tove Janssonová"@cs ;
  sdo:birthDate "+1914-08-09"^^xsd:date
      ~ wdref:f6f7cdf3b7dec9923484fbbd5daee432400b9c0e
      ~ wdref:d682ef906ae51801222e28f655ef92298ceecf26
      ~ wdref:d487201e3d7abd6d49f0f60c8403480a96a90bec ;
  sdo:deathDate "+2001-06-27"^^xsd:date
      ~ wdref:f6f7cdf3b7dec9923484fbbd5daee432400b9c0e
      ~ wdref:d682ef906ae51801222e28f655ef92298ceecf26 ;
  sdo:image <https://commons.wikimedia.org/wiki/Special:FilePath/Tove-Jansson-1956b.jpg> ;
  :imageOfGrave_P1442 <https://commons.wikimedia.org/wiki/Special:FilePath/Gr%C3%B3b%20Tove%20Jansson.jpg> ;
  :isni_P213 "0000000121478925"
      {| a :Qualification ; :subjectNamedAs_P1810 "Jansson, Tove" |}
      ~ wdref:fbc824608bf047fcbfb803c1b0f98e66f4372207 ,
    "0000 0004 8444 8792" {| a :Qualification ; :pseudonym_P742 "Haij, Vera" |} .
    "0000000484448792" {| a :Qualification ; :pseudonym_P742 "Haij, Vera" |} ;

wdref:8566348fa77729d56b55c24bd29f18f5e6631f99 a wikibase:Reference ;
  :statedIn_P248 <http://www.wikidata.org/entity/Q104089764> .

wdref:fbc824608bf047fcbfb803c1b0f98e66f4372207 a wikibase:Reference ;
  :statedIn_P248 <http://www.wikidata.org/entity/Q423048> .

wdref:f6f7cdf3b7dec9923484fbbd5daee432400b9c0e a wikibase:Reference ;
  :statedIn_P248 <http://www.wikidata.org/entity/Q36578> ;
  :retrieved_P813 "+2014-04-24"^^xsd:date .

wdref:fa278ebfc458360e5aed63d5058cca83c46134f1 a wikibase:Reference ;
  :importedFromWikimediaProject_P143 <http://www.wikidata.org/entity/Q328> .

wdref:d682ef906ae51801222e28f655ef92298ceecf26 a wikibase:Reference ;
  :statedIn_P248 <http://www.wikidata.org/entity/Q19938912> ;
  :bibliothequeNationaleDeFranceId_P268 "119085992" ;
  :retrieved_P813 "+2015-10-10"^^xsd:date .

wdref:d487201e3d7abd6d49f0f60c8403480a96a90bec a wikibase:Reference ;
  :biografisktLexikonForFinlandIdUrnfi_P10713 "4317-1416928956923" ;
  dct:title "Tove Jansson"@sv ;
  :statedIn_P248 <http://www.wikidata.org/entity/Q10429758> .

<https://commons.wikimedia.org/wiki/Special:FilePath/Tove-Jansson-1956b.jpg>
  sdo:encodesCreativeWork <http://commons.wikimedia.org/entity/M49252756> .

<http://commons.wikimedia.org/entity/M49252756> a :Mediainfo ;
  :depicts_P180 <http://www.wikidata.org/entity/Q102071> ;
  sdo:foundingDate "+1956-01-01T00:00:00Z"^^xsd:dateTime .

<https://commons.wikimedia.org/wiki/Special:FilePath/Gr%C3%B3b%20Tove%20Jansson.jpg>
  sdo:encodesCreativeWork <http://commons.wikimedia.org/entity/M122065492> .

<http://commons.wikimedia.org/entity/M122065492> a sdo:Photograph ;
  sdo:license <http://www.wikidata.org/entity/Q18199165> ;
  sdo:foundingDate "+2022-08-09T00:00:00Z"^^xsd:dateTime ;
  :exposureTime_P6757 [ a <http://www.wikidata.org/entity/Q11574> ; rdf:value 0.003787878787878788 ] ;
  :focalLength_P2151 [ a <http://www.wikidata.org/entity/Q174789> ; rdf:value 5.89 ] ;
  :isoSpeed_P6789 50 ;
  sdo:encodingFormat "image/jpeg" .
```

### Usage

Install dependencies:
```sh
$ pip3 install -r requirements.txt
```
Initially generate or update the `cache/vocmap.jsonld` file used by the tool:
```sh
$ make vocmap
```
Then transform individual items to "readable" [Turtle 1.2](https://www.w3.org/TR/rdf12-turtle/):
```sh
$ python3 -m wd2rdbl Q102071  # Person (Tove Janson)
$ python3 -m wd2rdbl Q34851  # Person (Elizabeth Taylor)
$ python3 -m wd2rdbl Q780785  # Geographic (Långholmen)
```
(This also looks up descriptions about related Wikimedia resources. That data
is currently a bit tricky to discover, since Wikimedia Commons pages do not
content-negotiate to provide structured data; but it *is* there, linked to
within the HTML page with an "alternate" relation.)

You can also use just the conversion, which is "WDJSON in, JSON-LD out".
```sh
$ curl -s -L -HAccept:application/json http://www.wikidata.org/entity/Q102071 | python3 -m wd2rdbl.jsonmapper
```

### Get & Convert Dumps

To convert all of Wikidata, get and convert the dumps (requires ~200G of free
storage and some cores to spare):
```sh
$ curl -O https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz
$ pbzcat latest-all.json.bz | python3 -m wd2rdbl.dumpconvert | pbzip2 > wd2rdbl-latest-all.ndjson.bz

$ curl -O https://dumps.wikimedia.org/commonswiki/entities/latest-mediainfo.json.bz2
$ pbzcat latest-mediainfo.json.bz2 | python3 -m wd2rdbl.dumpconvert | pbzip2 > wd2rdbl-latest-mediainfo.ndjson.bz2
```
