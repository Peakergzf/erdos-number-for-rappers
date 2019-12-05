from spotify import sp
import itertools
from typing import Dict
import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()


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
    # flatten the list (https://stackoverflow.com/a/716482)
    artist_lst: [Dict] = list(itertools.chain.from_iterable(artist_lst_lst))
    # filter the dictionary by key (https://stackoverflow.com/a/953097)
    return [{k: v for k, v in artist.items() if k in ["name", "id"]} for artist in artist_lst]


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
        if sp.artist(feat_id)["popularity"] < 85:
            continue

        if G.has_node(feat_name) and G.has_edge(artist, feat_name):
            G[artist][feat_name]["weight"] += 1
        elif not G.has_edge(artist, feat_name):
            G.add_edge(artist, feat_name, weight=1)
            # add_artist(feat_name)


def main():
    artists = ["21 Savage", "Young Thug", "Travis Scott", "Migos", "Gucci Mane"]
    for artist in artists:
        add_artist(artist)

    # (https://networkx.github.io/documentation/stable/reference/drawing.html#layout)
    # (https://networkx.github.io/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw_networkx.html)
    pos = nx.spring_layout(G)
    node_labels = {node: node for node in G.nodes()}
    nx.draw(G, pos, edge_color='black', width=1, linewidths=1,
            node_size=500, node_color='grey', alpha=0.9,
            labels=node_labels, font_size=6)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.axis('off')
    plt.show()


if __name__ == '__main__':
    main()
