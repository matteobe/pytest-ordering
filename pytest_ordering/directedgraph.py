"""
DirectedGraph implements the capability to reason about order of execution of items collected by pytest.
Cardinal ordering information (first, second, ..., second-to-last, last) can be integrated in the graph
"""

# To deal with the starting conditions (first, second, third, etc..)
# They can be added as the root of the tree
# TODO: Decide where to attach the end of the first-priority execution list to the graph of before/after relationships
# - Case 1: top10 priorities is a separate graph, in which case it gets executed first
# - Case 2: top10 priorities is attached to rest of graph, in which case the normal algorithm is applied

# To deal with the ending conditions (last, second-to-last, etc...)
# They can be added as a leaf of the tree
# TODO: Decide where to attach the start of the last-priority execution list to the graph of before/after relationships
# - Case 1: bottom10 priorities is a separate graph, in which case it gets executed last
# - Case 2: bottom10 priorities is attached to rest of graph, in which case the normal algorithm is applied

# TODO: How do you construct the execution list
# Apply topological sort algorithm (https://personal.utdallas.edu/~ravip/cs3345/slidesweb/node7.html)
# Step in procedure
# - Identify vertex without incoming edges
# - Add vertex to reversed_execution list
# - Remove the vertex from the graph (including incoming edges)
# - Repeat procedure for rest of graph
#
# Procedure order
# - Begin with bottom10 vertices
# - Perform on rest of graph (excluding top10 vertices)
# - Conclude with top10 vertices

# TODO: Outstanding problem
# - Identify if there is a priority conflict for the top10 vertices
#   Approach: Create the "source" tree for the nr. 10 vertex and if there are vertices other than the top 10, then
#             there is a priority conflict
# - Identify if there is a priority conflict for the bottom10 vertices
#   Approach: Reverse graphs direction of edge and perform the same procedure as for the nr. 10 vertex, this time
#             starting with the nr. 10-to-last vertex

from typing import Union
from collections import defaultdict


class DirectedGraph:

    def __init__(self):
        """
        Initialize a new graph object, including dictionaries to keep track of the vertices and edges
        """
        self.new_id = 0
        self.vertices = 0
        self.vertices_map = {}
        self.vertices_map_inv = {}
        self.graph = defaultdict(list)
        self.graph_inv = defaultdict(list)

    def add_vertex(self, vertex: Union[str, int, float]) -> int:
        """
        Add new vertex to the graph, including assigning a new unique ID to the vertex.
        Internally, the graph is represented using integer ID for vertices (faster calculation than with strings)
        """
        vertex_id = self.new_id
        self.new_id += 1
        self.vertices += 1
        self.vertices_map[vertex] = vertex_id
        self.vertices_map_inv[vertex_id] = vertex

        return vertex_id

    def remove_vertex(self, vertex: Union[str, int, float]) -> None:
        """
        Remove a vertex from the graph
        """

        # Remove vertex only if it's listed in the vertex list
        if vertex in self.vertices_map:
            self.vertices -= 1
            vertex_id = self.vertices_map.pop(vertex)
            _ = self.vertices_map_inv.pop(vertex_id)

            # Remove vertex as starting point from graph & inverted graph only if it was used
            if vertex_id in self.graph:
                _ = self.graph.pop(vertex_id)
            if vertex_id in self.graph_inv:
                _ = self.graph_inv.pop(vertex_id)

            # Remove vertex as end point from graph & inverted graph only if it was used
            for start_vertex_id in self.graph:
                if vertex_id in self.graph[start_vertex_id]:
                    self.graph[start_vertex_id].remove(vertex_id)
            for start_vertex_id in self.graph_inv:
                if vertex_id in self.graph_inv[start_vertex_id]:
                    self.graph_inv[start_vertex_id].remove(vertex_id)

    def get_vertex_id(self, vertex: Union[str, int, float]) -> int:
        """
        Function returns the vertex ID for an input vertex definition, if the vertex does not exist, it creates it
        """
        if vertex in self.vertices_map:
            vertex_id = self.vertices_map[vertex]
        else:
            vertex_id = self.add_vertex(vertex)

        return vertex_id

    def add_edge(self, start_vertex: Union[str, int, float], end_vertex: Union[str, int, float]) -> None:
        """
        Add new edge to the graph
        """
        start_vertex = self.get_vertex_id(start_vertex)
        end_vertex = self.get_vertex_id(end_vertex)
        self.graph[start_vertex].append(end_vertex)
        self.graph_inv[end_vertex].append(start_vertex)

    def remove_edge(self, start_vertex: Union[str, int, float], end_vertex: Union[str, int, float]) -> None:
        """
        Remove an edge from the graph
        """
        start_vertex = self.get_vertex_id(start_vertex)
        end_vertex = self.get_vertex_id(end_vertex)

        if start_vertex in self.graph:
            if end_vertex in self.graph[start_vertex]:
                self.graph[start_vertex].remove(end_vertex)
                self.graph_inv[end_vertex].remove(start_vertex)

    def is_cyclic(self, vertex_id, vertex_visited, recursion_stack):
        """
        Function checks
        """

        # Mark current node as visited and add it to the recursion stack
        vertex_visited[vertex_id] = True
        recursion_stack[vertex_id] = True

        # Recur for all neighbours, if any neighbour is visited and in recursion stack then graph is cyclic
        for neighbour_id in self.graph[vertex_id]:
            if not vertex_visited[neighbour_id]:
                if self.is_cyclic(neighbour_id, vertex_visited, recursion_stack):
                    return True
            elif recursion_stack[neighbour_id]:
                return True

        # The node needs to be popped from recursion stack before function ends
        recursion_stack[vertex_id] = False

        return False

    def is_graph_cyclic(self) -> bool:
        """
        Test if the graph is cyclic

        Returns:
            cyclic (bool): True if graph contains a cyclic component, False if not
        """

        # Initialize the tracking list to be the size of the new id, to avoid problems with deleted vertices
        vertex_visited = [False] * self.new_id
        recursion_stack = [False] * self.new_id

        for vertex_id in self.vertices_map_inv.keys():
            if not vertex_visited[vertex_id]:
                if self.is_cyclic(vertex_id, vertex_visited, recursion_stack):
                    return True

        return False
