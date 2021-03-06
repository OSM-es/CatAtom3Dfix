# Change log

**2021.06.03 (1.3.3)**

* Normalize coordinates output.

**2021-06-02 (1.3.2)**

* Unmarks failed downloads to retry.

**2021-06-01 (1.3.1)**

* Fixes download timeout for slow Overpass responses.

**2021-06-01 (1.3.0)**

* Handles upload conflicts.

**2021-06-01 (1.2.5)**

* Fixes download failing to include conflated buildings.

**2021-05-31 (1.2.4)**

* Fixes download timeout for slow Overpass responses.

**2021-05-30 (1.2.3)**

* Fixes list of changesets with mixed source.  

**2021-05-27 (1.2.2)**

* Fixes error refering relation new members (again).

**2021-05-26 (1.2.1)**

* Fixes missing modified ways.

**2021-05-26 (1.2.0)**

* Adds check of narrow vertices.

**2021-05-24 (1.1.1)**

* Fixes error refering relation new members.

**2021-05-13 (1.1.0)**

* Adds support to process big pbf files.

**2021-05-13 (1.0.10)**

* Fixes more duplicated ways coming from buildings referred by building:part relations.

**2021-05-11 (1.0.9)**

* Adds cmake to requirements

**2021-05-07 (1.0.8)**

* Fixes duplicated ways.

**2021-05-07 (1.0.7)**

* Fixes undetected orphand relation members.

**2021-05-07 (1.0.6)**

* Fixes wrong type=multipoligon in some ways.
* Adds warning for parts without levels.

**2021-05-06 (1.0.5)**

* Fixes error uploading relations.

**2021-05-06 (1.0.4)**

* Detects ways without tags.

**2021-05-06 (1.0.3)**

* Detects void relations or ways.

**2021-05-05 (1.0.2)**

* Tweak Overpass timeouts.
* Skips downloads with invalid status codes.
* Detects invalid geometry if exists overlapping building or building:parts.
* Adds logging capability.
* Adds user-agent to download requests and API calls.
* Fixes download of void changesets.
* Fixes authentication.

**2021-04-24 (1.0.1)**

* Take into account building parts contributed by users.

**2021-04-22 (1.0)**

* Initial development.

