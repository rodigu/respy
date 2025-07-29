# pyresq

python https rest api to sql database integrator

## table generation

composite columns may be defined when there is no source-defined id to track response entries.
they will be used for metadata tracking (add date, deletion date, update date, etc).

### meta-tables

all tables receiving integration data have

metadata columns, such as the deleted flag, deletion date, etc, are named with an underscore prefix: `_DELETED`,`_DELETION_DATE`.
