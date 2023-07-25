from py2neo import Graph, Node, Relationship


def to_neo4j(data: dict, graph: Graph):
    # Parse the dict and add the nodes and edges
    for node in data["nodes"]:
        if node["type"] == "SQLTable":
            continue
        # Add the parent node
        class_node = Node(
            "ClassNode",
            name=node["name"],
            centrality=node["centrality"],
            type=node["type"],
            uncertainity=node["uncertainity"],
        )
        graph.create(class_node)

        # Add the child nodes
        for child in node["children"]:
            child_node = Node(
                "MethodNode",
                name=child["name"],
                centrality=child["centrality"],
                type=child["type"],
                uncertainity=node["uncertainity"],
            )
            graph.create(child_node)

            # Add relationship from parent node to child node
            parent_to_child = Relationship(class_node, "MEMBER", child_node)
            graph.create(parent_to_child)

    # Parse the links and add the relationships
    for link in data["links"]:
        # Get nodes by name
        source_node = graph.nodes.match(name=link["source"]).first()
        target_node = graph.nodes.match(name=link["target"]).first()

        # Create the relationship
        if source_node and target_node:
            rel = Relationship(
                source_node, link["type"], target_node, weight=link["weight"]
            )
            graph.create(rel)

        # Add relationships between child nodes
        for child_link in link["children"]:
            child_source_node = graph.nodes.match(name=child_link["source"]).first()
            child_target_node = graph.nodes.match(name=child_link["target"]).first()
            if child_source_node and child_target_node:
                child_rel = Relationship(
                    child_source_node, link["type"], child_target_node
                )
                graph.create(child_rel)
