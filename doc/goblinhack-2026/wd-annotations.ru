prefix wikibase: <http://wikiba.se/ontology#>

delete {
  ?entity ?p ?statement .
  ?statement ?statement_p ?direct_o .
}
insert {
  << ?entity ?direct_p ?direct_o ~ ?statement >> .
}
where {
  ?entity ?direct_p ?direct_o .
  ?entity ?p ?statement .
  ?statement ?statement_p ?direct_o .
  ?wp
    wikibase:claim ?p ;
    wikibase:directClaim ?direct_p ;
    wikibase:statementProperty ?statement_p .
}
