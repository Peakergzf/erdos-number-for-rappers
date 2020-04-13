import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from credentials import CLIENT_ID, CLIENT_SECRET
import networkx as nx
from pyvis.network import Network
import matplotlib.pyplot as plt
import timeit
import itertools
from typing import Dict

ccm = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=ccm)

# collaboration graph of rappers
G = nx.Graph()
# list of hip-hop genres
GENRES = []
# list of rappers
ARTISTS = []


def read_files():
    global GENRES, ARTISTS

    with open("genres.txt", "r") as f:
        for line in f:
            GENRES.append(line.rstrip())

    with open("artists.txt", "r") as f:
        for line in f:
            ARTISTS.append(line.rstrip())


def get_artist_id(artist_name: str) -> str:
    return sp.search(q="artist:" + artist_name, type="artist")["artists"]["items"][0]["id"]


def get_artist_album_ids(artist_id: str) -> [str]:
    # https://github.com/plamere/spotipy/blob/master/examples/artist_albums.py#L15
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
    """
    :param album_id
    :return: a list of dictionary of artist name-id featured in the album
    """
    # the tracks in the album
    album_tracks: [Dict] = sp.album_tracks(album_id)["items"]

    # list of lists of featured artists
    artist_lst_lst: [[Dict]] = [track["artists"][1:] for track in album_tracks]

    # flatten the list https://stackoverflow.com/a/716482
    artist_lst: [Dict] = list(itertools.chain.from_iterable(artist_lst_lst))

    # filter the dictionary by key https://stackoverflow.com/a/953097
    return [{k: v for k, v in artist.items() if k in ["name", "id"]} for artist in artist_lst]


def _include(artist_id):
    artist = sp.artist(artist_id)
    # only include "mainstream" rappers in the graph (popularity >= 80)
    # (check if two sets are disjoint https://stackoverflow.com/a/17735466)
    return artist["popularity"] >= 80 and not set(artist["genres"]).isdisjoint(GENRES)


def add_artist(artist_name: str, freq_cnt=False) -> None:
    """
    :param artist_name
    :param freq_cnt:
    True if the edge between two rappers represents the # of times they collaborated
    False if the edge only indicates they collaborated or not
    """
    if artist_name not in G:
        G.add_node(artist_name)

    artist_id = get_artist_id(artist_name)
    album_ids = get_artist_album_ids(artist_id)

    # list of featured artists for each album
    featured_artist_lst_lst = [get_album_featured_artists(album_id) for album_id in album_ids]
    # flatten the nested list
    featured_artist_lst = list(itertools.chain.from_iterable(featured_artist_lst_lst))

    for featured_artist in featured_artist_lst:
        feat_name = featured_artist["name"]
        feat_id = featured_artist["id"]
        if feat_name.lower() == artist_name.lower():
            continue
        if not _include(feat_id):
            continue

        if freq_cnt:
            if G.has_edge(artist_name, feat_name):
                G[artist_name][feat_name]["weight"] += 1
            else:
                G.add_edge(artist_name, feat_name, weight=1)
        else:
            if not G.has_edge(artist_name, feat_name):
                G.add_edge(artist_name, feat_name, weight=1)


def construct_graph():
    num_artists = len(ARTISTS)
    cnt = 0
    for artist in ARTISTS:
        add_artist(artist)
        cnt += 1
        print(cnt, "/", num_artists)


def draw_graph():
    """
    using networkx
    """
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
    """
    using pyvis
    """
    # https://pyvis.readthedocs.io/en/latest/tutorial.html#example-visualizing-a-game-of-thrones-character-network
    nt = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
    nt.barnes_hut()
    nt.from_nx(G)
    neighbor_map = nt.get_adj_list()
    for node in nt.nodes:
        node["title"] += " neighbors:<br>" + "<br>".join(neighbor_map[node["id"]])
        node["value"] = len(neighbor_map[node["id"]])
    nt.show("rappers.html")


def time(func, *args):
    t0 = timeit.default_timer()
    func(*args)
    t1 = timeit.default_timer()
    print(func.__name__ + " in {0:.2f}s".format(t1 - t0))


def main():
    read_files()

    print(sp.artist((get_artist_id(ARTISTS[0]))).keys())
    for artist_name in ARTISTS:
        artist_id = get_artist_id(artist_name)
        artist = sp.artist(artist_id)
        print(artist["name"], artist["popularity"], artist["genres"])

    dash_size = 50
    print("=" * dash_size)
    time(construct_graph)
    print("=" * dash_size)

    print(len(G), "rappers included.\n" + "=" * dash_size)

    yt = "Young Thug"
    for comp in nx.connected_components(G):
        if len(comp) == 1:
            continue

        s = G.subgraph(comp)
        print("eccentricity:\n", nx.eccentricity(s))

        c = nx.center(s)
        print("center:\n", c)

        dists = nx.single_source_shortest_path_length(G, yt if yt in c else c[0])

        print("distributions of distance:")
        freq = {}
        for _, d in dists.items():
            if d not in freq:
                freq[d] = 0
            freq[d] += 1
        print(freq)

        print("distance from center:\n", dists)
        print("-" * dash_size)

    vis_graph()


if __name__ == '__main__':
    main()
