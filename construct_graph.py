from spotify import sp
import networkx as nx
import matplotlib.pyplot as plt
import timeit
import itertools
from typing import Dict
from pyvis.network import Network

G = nx.Graph()
GENRES = []
ARTISTS = []


def read_files():
    global GENRES, ARTISTS

    with open("genres.txt", "r") as f:
        for line in f:
            GENRES.append(line.rstrip())

    with open("artists.txt", "r") as f:
        for line in f:
            ARTISTS.append(line.rstrip())


def get_artist_id(name: str) -> str:
    return sp.search(q="artist:" + name, type="artist")["artists"]["items"][0]["id"]


def get_artist_album_ids(artist_id: str) -> [str]:
    albums: [Dict] = []
    results = sp.artist_albums(artist_id, album_type="album")
    albums.extend(results["items"])
    while results["next"]:
        results = sp.next(results)
        albums.extend(results["items"])
    unique = set()
    album_ids = []
    for album in albums:
        name = album["name"].lower()
        if name not in unique:
            unique.add(name)
            album_ids.append(album["id"])
    return album_ids


def get_album_featured_artists(album_id: str) -> [Dict[str, str]]:
    # the tracks in the album
    album_tracks: [Dict] = sp.album_tracks(album_id)["items"]

    # list of lists of featured artists
    artist_lst_lst: [[Dict]] = [track["artists"][1:] for track in album_tracks]

    # flatten the list https://stackoverflow.com/a/716482
    artist_lst: [Dict] = list(itertools.chain.from_iterable(artist_lst_lst))

    # filter the dictionary by key https://stackoverflow.com/a/953097
    return [{k: v for k, v in artist.items() if k in ["name", "id"]} for artist in artist_lst]


def _include(artist_id):
    # only include "mainstream" rappers in the graph
    # https://stackoverflow.com/a/17735466
    artist = sp.artist(artist_id)
    return artist["popularity"] >= 85 and not set(artist["genres"]).isdisjoint(GENRES)


def add_artist(artist: str) -> None:
    # if len(G) > 10:
    #     return

    if artist not in G:
        G.add_node(artist)

    artist_id = get_artist_id(artist)
    album_ids = get_artist_album_ids(artist_id)

    featured_artist_lst_lst = [get_album_featured_artists(album_id) for album_id in album_ids]
    featured_artist_lst = list(itertools.chain.from_iterable(featured_artist_lst_lst))

    for featured_artist in featured_artist_lst:
        feat_name = featured_artist["name"]
        feat_id = featured_artist["id"]
        if feat_name.lower() == artist.lower():
            continue
        if not _include(feat_id):
            continue

        if G.has_node(feat_name) and G.has_edge(artist, feat_name):
            G[artist][feat_name]["weight"] += 1
        else:
            G.add_edge(artist, feat_name, weight=1)
            # add_artist(feat_name)


def construct_graph():
    for artist in ARTISTS:
        add_artist(artist)


def draw_graph():
    # https://networkx.github.io/documentation/stable/reference/drawing.html#layout
    # https://networkx.github.io/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw_networkx.html
    pos = nx.spring_layout(G)
    node_labels = {node: node for node in G.nodes()}
    nx.draw(G, pos, edge_color='black', width=1, linewidths=1,
            node_size=500, node_color='grey', alpha=0.9,
            labels=node_labels, font_size=6)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.axis('off')
    plt.show()


def vis_graph():
    # https://pyvis.readthedocs.io/en/latest/tutorial.html#example-visualizing-a-game-of-thrones-character-network
    nt = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
    nt.barnes_hut()
    nt.from_nx(G)
    neighbor_map = nt.get_adj_list()
    for node in nt.nodes:
        node["value"] = len(neighbor_map[node["id"]])
    nt.show("rappers.html")


def time(func, *args):
    t0 = timeit.default_timer()
    func(*args)
    t1 = timeit.default_timer()
    print(func.__name__ + " in {0:.2f}s".format(t1 - t0))


def main():
    read_files()
    time(construct_graph)
    # print(nx.center(G))
    # print(nx.eccentricity(G))
    # draw_graph()
    vis_graph()


if __name__ == '__main__':
    main()
