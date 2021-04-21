Script to fix the missing building parts in [Spanish Cadastre/Buildings Import][1].


# The problem

In march 2021, a [request][2] was made in the import list regarding this import 
and the [Simple 3D Buildings tagging scheme][3]. Untill then some building parts 
were been considered not needed because they only contains tags for the maximum 
and minimum values of the building:levels and building:levels:underground tags 
already present in the building outline. Nevertheless, the standard says that 
the entire building outline should be filled with building parts.

This [issue][4] was discussed in the [talk-es][5] list and fixed in version 
[1.3][6] of CatAtom2Osm.

Newer import projects conforms to Simple 3D schema, but 
many on going projects are very difficult to rebuild and there are a big amount 
of buildings already imported with the outline not filled.


# Solution

This tool search for the imported buildings and generates the missing building 
part. It operates on a changeset basis (one new fixs changeset for every 
historically imported changeset).

The new changesets will be uploaded using the catatom3dfix account with this tags:

* comment: Fixs #Spanish_Cadastre_Buildings_Import Simple 3D Buildings for cs <id>
* source: Dirección General del Catastro
* mechanical: yes
* url: https://wiki.openstreetmap.org/wiki/Spanish_Cadastre/Buildings_Import/CatAtom3Dfix

The tool will be operated by the user User:Javiersanp, a first time to fixs 
the data already imported (12212 till 2021/04/05) and then occasionally until 
all the buildings of projects in progress made with previous versions of 
CatAtom2Osm are fixed.


# Install

This code is shared with the intention of being reviewed by the OpenStreetMap 
community.

If you use it, please do it with caution against the [development server][7].

Automated edits should only be carried out by those with experience and 
understanding of the way the OpenStreetMap community creates maps, and only 
with careful planning and consultation with the local community.

See the [Import/Guidelines][8] and [Automated Edits/Code of Conduct][9] for 
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

Data in this import are identified with tags in the changesets uploaded. 
This option searchs for them in a full history file and output their 
identifiers. 

You need to download the [latest Full History Planet XML file][10]. As this is
file is huge and the script takes too long to process it, a list of changesets 
is already provided in the file 'changesets.list'.


## Download

  python3 catatom3dfix.py download <changeset-id>

Get the current data for a changeset and put the result in <changeset-id>.osm.
It needs a call to the [API][11] to get the ids of the buildings and its parts 
and another to [Overpass API][12] for their current versions.


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


# References

[1]: https://wiki.openstreetmap.org/wiki/Spanish_Cadastre/Buildings_Import
[2]: https://lists.openstreetmap.org/pipermail/imports/2021-March/006559.html
[3]: https://wiki.openstreetmap.org/wiki/Simple_3D_Buildings
[4]: https://github.com/OSM-es/CatAtom2Osm/issues/56
[5]: https://lists.openstreetmap.org/pipermail/talk-es/2021-March/017650.html
[6]: https://github.com/OSM-es/CatAtom2Osm/tree/v1.3
[7]: https://api06.dev.openstreetmap.org
[8]: http://wiki.openstreetmap.org/wiki/Import/Guidelines
[9]: http://wiki.openstreetmap.org/wiki/Automated_Edits/Code_of_Conduct
[10]: https://planet.osm.org/planet/full-history/
[11]: https://wiki.openstreetmap.org/wiki/API
[12]: https://wiki.openstreetmap.org/wiki/Overpass_API
