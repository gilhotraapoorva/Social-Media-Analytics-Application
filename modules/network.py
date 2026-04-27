"""Module 3 + 9: Network Analysis — communities, influencers, connectors."""
from typing import List, Dict, Any
import networkx as nx


def build_graph(posts: List) -> nx.DiGraph:
    """Build a directed graph from author -> mention edges."""
    g = nx.DiGraph()
    for p in posts:
        author = p.author
        if not author:
            continue
        g.add_node(author)
        for mention in p.mention_list:
            if mention and mention != author:
                g.add_node(mention)
                if g.has_edge(author, mention):
                    g[author][mention]["weight"] += 1
                else:
                    g.add_edge(author, mention, weight=1)
    return g


def detect_communities(g: nx.Graph) -> List[List[str]]:
    """Greedy modularity-based communities (works on undirected projection)."""
    if g.number_of_nodes() == 0:
        return []
    undirected = g.to_undirected() if g.is_directed() else g
    try:
        from networkx.algorithms.community import greedy_modularity_communities
        return [sorted(c) for c in greedy_modularity_communities(undirected)]
    except Exception:
        return [sorted(undirected.nodes())]


def analyze_network(posts: List) -> Dict[str, Any]:
    g = build_graph(posts)
    n_nodes = g.number_of_nodes()
    n_edges = g.number_of_edges()

    if n_nodes == 0:
        return {
            "nodes": [], "edges": [], "communities": [],
            "influencers": [], "connectors": [],
            "metrics": {"node_count": 0, "edge_count": 0, "density": 0},
        }

    # Centralities
    try:
        eigenvector = nx.eigenvector_centrality_numpy(g)
    except Exception:
        eigenvector = {n: 0.0 for n in g.nodes()}
    betweenness = nx.betweenness_centrality(g)
    degree = dict(g.degree())

    influencers = sorted(
        [{"node": n, "score": round(s, 4), "degree": degree.get(n, 0)} for n, s in eigenvector.items()],
        key=lambda x: x["score"], reverse=True,
    )[:10]
    connectors = sorted(
        [{"node": n, "score": round(s, 4)} for n, s in betweenness.items()],
        key=lambda x: x["score"], reverse=True,
    )[:10]

    communities = detect_communities(g)

    # For visualization
    node_to_community = {}
    for idx, community in enumerate(communities):
        for node in community:
            node_to_community[node] = idx

    nodes = [
        {
            "id": n,
            "label": n,
            "degree": degree.get(n, 0),
            "eigenvector": round(eigenvector.get(n, 0), 4),
            "community": node_to_community.get(n, 0),
        }
        for n in g.nodes()
    ]
    edges = [
        {"source": u, "target": v, "weight": d.get("weight", 1)}
        for u, v, d in g.edges(data=True)
    ]

    return {
        "nodes": nodes,
        "edges": edges,
        "communities": [{"id": idx, "members": members, "size": len(members)}
                        for idx, members in enumerate(communities)],
        "influencers": influencers,
        "connectors": connectors,
        "metrics": {
            "node_count": n_nodes,
            "edge_count": n_edges,
            "density": round(nx.density(g), 4),
            "community_count": len(communities),
        },
    }
