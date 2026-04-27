"""Module 9: Influencer Detection — Eigenvector centrality on the user graph."""
from typing import List, Dict, Any
from collections import defaultdict

import networkx as nx

from modules.network import build_graph


def detect_influencers(posts: List, top_n: int = 10) -> Dict[str, Any]:
    g = build_graph(posts)
    if g.number_of_nodes() == 0:
        return {"top": [], "metrics": {}}

    try:
        eigenvector = nx.eigenvector_centrality_numpy(g)
    except Exception:
        eigenvector = nx.degree_centrality(g)

    pagerank = nx.pagerank(g) if g.number_of_edges() > 0 else {n: 1.0 / g.number_of_nodes() for n in g.nodes()}
    in_degree = dict(g.in_degree())

    # Cross-reference with engagement totals from posts
    engagement_by_user = defaultdict(int)
    posts_by_user = defaultdict(int)
    for p in posts:
        engagement_by_user[p.author] += p.engagement
        posts_by_user[p.author] += 1

    rows = []
    for node in g.nodes():
        rows.append({
            "user": node,
            "eigenvector": round(eigenvector.get(node, 0), 4),
            "pagerank": round(pagerank.get(node, 0), 4),
            "in_degree": in_degree.get(node, 0),
            "engagement": engagement_by_user.get(node, 0),
            "posts": posts_by_user.get(node, 0),
            # composite influence score
            "score": round(
                0.5 * eigenvector.get(node, 0)
                + 0.3 * pagerank.get(node, 0)
                + 0.2 * (engagement_by_user.get(node, 0) / max(sum(engagement_by_user.values()), 1)),
                4,
            ),
        })

    rows.sort(key=lambda r: r["score"], reverse=True)
    return {
        "top": rows[:top_n],
        "all": rows,
        "metrics": {
            "user_count": g.number_of_nodes(),
            "edge_count": g.number_of_edges(),
        },
    }
