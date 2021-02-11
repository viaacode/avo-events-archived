# AvO Events Archived

## Synopsis

When an item is archived for AvO it needs to be updated with the metadata from the original fragment.
This service queries MediaHaven for the original metdata and updates the new item after a small transformation.

## Prerequisites

- Git
- Docker (optional)
- Python 3.6+
- Access to the [meemoo PyPi](http://do-prd-mvn-01.do.viaa.be:8081)
- Poetry