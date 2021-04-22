Script to fix the missing building parts in [Spanish Cadastre/Buildings Import][1].


# Description

See this proposal[2].


# Install

This code is shared with the intention of being reviewed by the OpenStreetMap 
community.

If you use it, please do it with caution against the [development server][3].

Automated edits should only be carried out by those with experience and 
understanding of the way the OpenStreetMap community creates maps, and only 
with careful planning and consultation with the local community.

See the [Import/Guidelines][4] and [Automated Edits/Code of Conduct][5] for 
more information.

Clone or copy the repository, make a virtual environment and install the 
requeriments.

  git clone https://github.com/OSM-es/CatAtom3Dfix.git
  cd CatAtom3Dfix
  python3 -m venv venv
  source venv/bin/activate
  pip3 install -r requirements.txt


# Usage

  python3 catatom3dfix.py catatom3dfix.py command arg


## List

  python3 catatom3dfix.py list <path-to-history-file>

Get the identifiers of the Spanish Cadastre Buildings Import changesets from 
[Full History Planet XML file][6]. As this is file is huge and the script 
takes too long to process it, a list of changesets is already provided in the 
file 'changesets.list'.


## Download

  python3 catatom3dfix.py download <changeset-id>

Get the current data for a changeset and put the result in <changeset-id>.osm.
It needs a call to the [API][7] to get the ids of the buildings and its parts 
and another to [Overpass API][8] for their current versions.


## Process

  python3 catatom3dfix.py process <path-to-osm-file>

Reads the previous file and generates a osc file with the missing building 
parts.

For each building, it substracts all the parts. If the resulting geometry is 
not empty and different from the original, the building outline is not fully 
filled and goes to the output file. This will exclude buildings with only one 
level (no building:parts in it) and those created with the fixed CatAtom2Osm 
tool. The new building parts will be defined referencing the existing nodes and 
ways (if used in multipolygon relations).


## Upload

  python3 catatom3dfix.py <path-to-osmchange-file>

Uploads the file to OSM in a single request. If result is OK, prints the new
changeset id. 


[1]: https://wiki.openstreetmap.org/wiki/Spanish_Cadastre/Buildings_Import
[2]: https://wiki.openstreetmap.org/wiki/Automated_edits/CatAtom3Dfix
[3]: https://api06.dev.openstreetmap.org
[4]: http://wiki.openstreetmap.org/wiki/Import/Guidelines
[5]: http://wiki.openstreetmap.org/wiki/Automated_Edits/Code_of_Conduct
[6]: https://planet.osm.org/planet/full-history/
[7]: https://wiki.openstreetmap.org/wiki/API
[8]: https://wiki.openstreetmap.org/wiki/Overpass_API
