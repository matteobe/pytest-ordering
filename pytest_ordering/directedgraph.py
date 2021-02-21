"""
DirectedGraph implements the capability to reason about order of execution of items collected by pytest.
Cardinal ordering information (first, second, ..., second-to-last, last) can be integrated in the graph
"""

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

            # Remove vertex as starting point from graph only if it was used
            if vertex_id in self.graph:
                _ = self.graph.pop(vertex_id)

            # Remove vertex as end point from graph only if it was used
            for start_vertex_id in self.graph:
                if vertex_id in self.graph[start_vertex_id]:
                    self.graph[start_vertex_id].remove(vertex_id)

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

    def remove_edge(self, start_vertex: Union[str, int, float], end_vertex: Union[str, int, float]) -> None:
        """
        Remove an edge from the graph
        """
        start_vertex = self.get_vertex_id(start_vertex)
        end_vertex = self.get_vertex_id(end_vertex)

        if start_vertex in self.graph:
            if end_vertex in self.graph[start_vertex]:
                self.graph[start_vertex].remove(end_vertex)

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
