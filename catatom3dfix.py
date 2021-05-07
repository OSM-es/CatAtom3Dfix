import gzip
import logging
import os
import pkg_resources
import shutil
import sys

import osmapi
import osmium
import shapely.wkt as wktlib
import urllib3

from argparse import ArgumentParser
from glob import glob
from os.path import exists as file_exists
from osmium.osm import Area
from osmium.osm.mutable import Node, Way, Relation
from shapely.geometry import Polygon, mapping
from time import sleep

description = (
    "Script to fix missing building parts in Spanish Cadastre/Buildings Import"
)
version = pkg_resources.require('catatom3dfix')[0].version
usage = "catastro3dfix.py [OPTIONS] <PATH>"
overpassurl = 'https://lz4.overpass-api.de/api/interpreter'
apidelay = 10
cscomment = "Fixes #Spanish_Cadastre_Buildings_Import Simple 3D Buildings for cs "
csurl = 'https://wiki.openstreetmap.org/Automated_edits/CatAtom3Dfix'
sourcetext = "Dirección General del Catastro"

appid = f"catatom3dfix/{version}"
log = logging.getLogger(appid)
log.addHandler(logging.StreamHandler(sys.stderr))
log.addHandler(logging.FileHandler('catatom3dfix.log'))
log.setLevel(logging.INFO)

http = urllib3.PoolManager(headers={'user-agent': appid}, timeout=apidelay)

wktfab = osmium.geom.WKTFactory()

DEBUG = not file_exists('.password')
if DEBUG:
    api = osmapi.OsmApi(appid=appid)
else:
    api = osmapi.OsmApi(passwordfile='.password', appid=appid)


class HistoryHandler(osmium.SimpleHandler):
    """Search for this import changesets in a full history file"""

    def __init__(self):
        super(HistoryHandler, self).__init__()

    def changeset(self, cs):
        """Process this import changesets"""
        if not cs.bounds.valid() or len(cs.tags) == 0:
            return
        if (
            cs.tags.get('type') == 'import' and 
            cs.tags.get('source') == sourcetext
        ):
            print(cs.id)


class BuildingsHandler(osmium.SimpleHandler):
    """Get data for buildings and it parts in a osm file"""
    
    def __init__(self, cs):
        """'cs' is the CatChangeset to populate"""
        super(BuildingsHandler, self).__init__()
        self.cs = cs
    
    @staticmethod
    def get_polygon(elem):
        """
        Get a shapely geometry from either an osmium Area, Way or a list
        of (longitude, latitude) pairs.
        """
        if type(elem) is Area:
            wkt = wktfab.create_multipolygon(elem)
        elif type(elem) is osmium.osm.Way and elem.is_closed():
            wkt = (
                'POLYGON((' +
                ','.join([f'{n.lon} {n.lat}' for n in elem.nodes]) +
                '))'
            )
        elif hasattr(elem, '__iter__'):
            wkt = (
                'POLYGON((' +
                ','.join([f'{n[0]} {n[1]}' for n in elem]) +
                '))'
            )
        else:
            return None
        return wktlib.loads(wkt)

    def node(self, node):
        """Get nodes for conflation"""
        self.cs.nodes[(node.location.lat, node.location.lon)] = Node(
            base=node, tags=dict(node.tags)
        )
    
    def way(self, way):
        """Get rings geometries for conflation"""
        if way.is_closed():
            self.cs.ways[way.id] = Way(
                base=way, tags=dict(way.tags), nodes=[n.ref for n in way.nodes]
            )
            self.cs.geoms[way.id] = self.get_polygon(way)

    def area(self, area):
        """Get building and parts geometries and building tags"""
        aid = int(area.id / 2)
        if area.tags.get('building') is not None:
            self.cs.buildings.append(aid)
            tags = {
                tag.k: tag.v for tag in area.tags 
                if tag.k.startswith('building:levels')
            }
            self.cs.geoms[aid] = self.get_polygon(area)
            self.cs.building_tags[aid] = tags
        if area.tags.get('building:part') is not None:
            self.cs.parts.append(aid)
            self.cs.geoms[aid] = self.get_polygon(area)


class UploadHandler(osmium.SimpleHandler):
    """Get changeset payload for osm change file."""

    def __init__(self):
        super(UploadHandler, self).__init__()
        self.data = []
    
    def node(self, n):
        action = 'create' if n.id < 0 else 'modify'
        data = {'id': n.id, 'lat': n.location.lat, 'lon': n.location.lon}
        data['tag'] = dict(n.tags)
        self.data.append({'type': 'node', 'action': action, 'data': data})
    
    def way(self, w):
        action = 'create' if w.id < 0 else 'modify'
        data = {'id': w.id, 'nd': [n.ref for n in w.nodes], 'tag': dict(w.tags)}
        self.data.append({'type': 'way', 'action': action, 'data': data})
    
    def relation(self, r):
        action = 'create' if r.id < 0 else 'modify'
        osmtypes = {'n': 'node', 'w': 'way', 'r': 'relation'}
        members = [
            dict(type=osmtypes[m.type], ref=m.ref, role=m.role)
            for m in r.members
        ]
        data = {'id': r.id, 'member': members, 'tag': dict(r.tags)}
        self.data.append({'type': 'relation', 'action': action, 'data': data})


class OsmChangeset:
    """Data holder to generate a osmchange file"""

    def __init__(self, id):
        self.newid = -1
        self.id = id
        self.filename = str(self.id) + '.osc'
        self.nodes = []
        self.ways = []
        self.relations = []

    def add(self, elem):
        """Adds a Node, Way or Relation"""
        if elem.id is None:
            elem.id = self.newid
            self.newid -= 1
        if type(elem) is Node:
            self.nodes.append(elem)
        elif type(elem) is Way:
            self.ways.append(elem)
        elif type(elem) is Relation:
            self.relations.append(elem)

    def write(self, include_modify=False):
        """Generates file with new and optionally existing data"""
        writer = osmium.SimpleWriter(self.filename)
        for node in self.nodes:
            if include_modify or node.id < 0:
                writer.add_node(node)
        for way in self.ways:
            if include_modify or way.id < 0:
                writer.add_way(way)
        for rel in self.relations:
            if include_modify or rel.id < 0:
                writer.add_relation(rel)
        writer.close()


class CatChangeset:
    """Defines Cadastre changesets"""

    def __init__(self, filename):
        self.id = int(filename.replace('.osm', ''))
        self.buildings = []
        self.parts = []
        self.geoms = {}
        self.nodes = {}
        self.ways = {}
        self.building_tags = {}
        self.osc = OsmChangeset(self.id)
        self.error = 0
        bh = BuildingsHandler(self)
        bh.apply_file(filename, locations=True)

    def get_nodes_refs(self, coords):
        """Get references of nodes from list of (longitude, latitude) pairs."""
        nodes = []
        for (lat, lon) in list(coords):
            node = self.nodes.get((lon, lat))
            if node is None:
                log.error(f"{self.id} Invalid geometry in {lon}, {lat}")
                self.error += 1
            else:
                nodes.append(node.id)
        return nodes

    def get_way_ref(self, coords):
        """Get reference of a way with the geometry from coords or None."""
        for ref, g in self.geoms.items():
            if g.equals(BuildingsHandler.get_polygon(coords)):
                return ref
        return None

    def get_way(self, coords, tags=None):
        """Get way if exists or creates a new one."""
        ref = self.get_way_ref(coords)
        if ref is None:
            nodes = self.get_nodes_refs(coords)
            way = Way(id=None, nodes=nodes)
        else:
            way = self.ways[ref]
            nodes = way.nodes
        if way.tags is None:
            way.tags = tags
        elif tags is not None:
            way.tags.update(tags)
        for node in self.nodes.values():
            if node.id in nodes and node not in self.osc.nodes:
                self.osc.add(node)
        return way

    def get_relation(self, geom, tags={}):
        """Creates a new multipolygon relation."""
        way = self.get_way(geom.exterior.coords)
        self.osc.add(way)
        members = [('way', way.id, 'outer')]
        for ring in geom.interiors:
            way = self.get_way(ring.coords)
            members.append(('way', way.id, 'inner'))
            self.osc.add(way)
        rel = Relation(id=None, members=members, tags=tags)
        rel.tags['type'] = 'multipolygon'
        return rel

    @staticmethod
    def download(cid):
        """Get the current versions of buildings and parts for a changeset"""
        filename = str(cid) + '.osm'
        query = 'wr["building:part"];'
        lats = []
        lons = []
        for change in api.ChangesetDownload(cid):
            if change['type'] == 'node' and change['data']['visible']:
                lats.append(change['data']['lat'])
                lons.append(change['data']['lon'])
            if change['action'] == 'create':
                if 'building' in change['data']['tag']:
                    query += f"{change['type']}({change['data']['id']});"
        if len(lats) > 0 and len(lons) > 0:
            bounds = f"{min(lats)},{min(lons)},{max(lats)},{max(lons)}"
            url = (
                overpassurl +
                "?data=[out:xml][timeout:180][bbox:" + bounds + "];(" +
                query +
                ");(._;>;);out+meta;"
            )
            try:
                status = wget(url, filename)
                if status > 399:
                    log.error(f"{cid} failed to download {status}")
            except urllib3.exceptions.HTTPError:
                log.error(f"{cid} failed to download")
        else:
            log.warning(f"{cid} is void")
        sleep(apidelay)

    def get_missing_parts(self):
        """Creates a OsmChange file with the missing imported parts."""
        for bid in self.buildings:
            tags = self.building_tags[bid]
            tags['building:part'] = 'yes'
            if 'building:levels' not in tags:
                log.warning(f"{self.id} part without levels")
            geom = self.geoms[bid]
            diff = geom
            for pid in self.parts:
                diff = diff - self.geoms[pid]
                if diff.is_empty:
                    break
            if not diff.is_empty and not diff.equals(geom):
                geoms = getattr(diff, 'geoms', [diff])
                for g in geoms:
                    if not hasattr(g, 'interiors'):
                        log.error(f"{self.id} Invalid multipolygon")
                        self.error += 1
                        return
                    elif len(g.interiors) > 0:
                        rel = self.get_relation(g, dict(tags))
                        if len(rel.members) == 0:
                            log.error(f"{self.id} Relation without members")
                            self.error += 1
                            return
                        self.osc.add(rel)
                    else:
                        way = self.get_way(g.exterior.coords, dict(tags))
                        if len(way.nodes) == 0:
                            log.error(f"{self.id} Way without nodes")
                            self.error += 1
                            return
                        if len(way.tags) == 0:
                            log.error(f"{self.id} Way without tags")
                            self.error += 1
                            return
                        self.osc.add(way)


def wget(url, filename):
    response = http.request('GET', url)
    if response.status < 400:
        with open(filename, 'wb') as out:
            out.write(response.data)
    response.release_conn()
    return response.status
    

def help():
    print(description)
    print(f"\nusage: {sys.argv[0]} command arg\n")
    print("Commands:")
    print("  list <path-to-history-file>")
    print("  download <changeset-id>")
    print("  process <path-to-osm-file>")
    print("  upload <path-to-osmchange-file>")

def main(command, arg):
    if command == 'list':
        history = HistoryHandler()
        history.apply_file(arg)
    elif command == 'download':
        if len(glob(arg + ".os*")) == 0:
            CatChangeset.download(int(arg))
            if file_exists(arg + '.osm'):
                log.info(f"{arg} downloaded")
    elif command == 'process':
        fn = arg.replace('.osm', '.osc')
        if len(glob(fn + '*')) == 0:
            try:
                cs = CatChangeset(arg)
                cs.get_missing_parts()
                if cs.error > 0:
                    log.error(f"{cs.id} has errors")
                elif len(cs.osc.ways) + len(cs.osc.relations) > 0:
                    cs.osc.write(DEBUG)
                else:
                    log.warning(f"{cs.id} has no missing building parts")
            except RuntimeError:
                if file_exists(fn):
                    os.remove(fn)
                log.error(f"{arg.replace('.osm', '')} runtime error")
        if file_exists(arg):
            os.remove(arg)
    elif command == 'upload':
        if DEBUG:
            print("This option is intentionally deactivated")
        elif not file_exists(arg + '.gz'):
            csid = arg.replace('.osc', '')
            upload = UploadHandler()
            upload.apply_file(arg)
            cs = api.ChangesetCreate(
                {
                    'comment': cscomment + csid,
                    'source': sourcetext,
                    'type': 'bot',
                    'url': csurl,
                }
            )
            api.ChangesetUpload(upload.data)
            api.ChangesetClose()
            log.info(f"{csid} fixed in changeset {cs}")
            with open(arg, 'rb') as f_in:
                with gzip.open(arg + '.gz', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(arg)
            sleep(apidelay)
    else:
        help()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        help()
    else:
        main(sys.argv[1], sys.argv[2])

