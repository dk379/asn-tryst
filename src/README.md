# asn-tryst README for Source

This is currently broken down into two scripts. One for pulling
a list of all traceroutes into the database, measurement_scraper.py, which
should be run first. One for pulling down the actual results of these
measurements, parsing the traceroutes, picking out the intersections,
annotating the data and writing it to the database (asn_tryst.py).

Expect this to change a lot in the coming days. These will be merged into
one daemon that will continually run and update with fresh data, instead
of the bulk process it is now. An API will also be added, allowing
querying of the results from, for example, visualisation tools. Tests will
also be added and optomisations made.
