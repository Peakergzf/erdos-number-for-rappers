# Erdős Number for Rappers
**_a.k.a. Young Thug Number_**

## Erdős Number
Consider the collaboration graph of mathematicians, 
where each vertex represents a mathematician and 
two vertices are adjacent if the they coauthored a paper.
[Erdős number](https://en.wikipedia.org/wiki/Erd%C5%91s_number) 
of a mathematician is defined as their distance to 
[Paul Erdős](https://en.wikipedia.org/wiki/Paul_Erd%C5%91s) in the graph.

## Collaboration Graph of Rappers
Similarly, we can define the collaboration graph of rappers,
where each vertex represents a rapper and 
two vertices are adjacent if the they collaborated on a song.

[spotipy](https://github.com/plamere/spotipy) and 
[networkx](https://github.com/networkx/networkx) 
are used to construct the graph and 
[pyvis](https://github.com/WestHealth/pyvis) 
is used to visualize the graph.
Due to the huge number of rappers, 
only "mainstream" rappers are included in the graph and 
this is determined by the "popularity" attribute of each artist provided by Spotify.
(Below are screenshots of the graph visualized.)

<img src="/images/screenshot2.png">
<img src="/images/screenshot1.png" height="60%" width="60%">


## Young Thug Number
The [center](https://mathworld.wolfram.com/GraphCenter.html)
of a graph is the set of vertices of
[eccentricity](https://mathworld.wolfram.com/GraphEccentricity.html)
equal to the graph [radius](https://mathworld.wolfram.com/GraphRadius.html).
In the rappers collaboration graph, there are 
multiple vertices in the center with eccentricity 3. 
[Young Thug](https://en.wikipedia.org/wiki/Young_Thug) 
is chosen as our Erdős and the Young Thug Number of a rapper 
is defined as their distance to Young Thug in the graph.

| Young Thug Number  | # rappers     |
| :---: | :---: |
| 0 | 1     |
| 1 | 42    |
| 2 | 76    |
| 3 | 3     |

Rappers collaborate more often than artists in any other genres
and the featuring phenomenon is bigger than ever. 
From the distribution of Young Thug Number above we can see that 
he has collaborated with at least 42 rappers and other 76 rappers 
are just two collaborations away from him.

<br>
:raised_hands:
<br>
<br>

<img src="/images/young_thug.png" height="20%" width="20%">

