import json
from node import Node
from edge import Edge

def save_mind_map(file_path, scene):
    """
    Serializes the mind map structure and node coordinates to a JSON file.
    """
    if not scene or not scene.root_node:
        return False

    data = {
        "root_id": scene.root_node.node_id,
        "nodes": []
    }

    # Save details of every node in the map
    for node_id, node in scene.nodes.items():
        node_data = {
            "id": node.node_id,
            "text": node.text,
            "x": node.x(),
            "y": node.y(),
            "parent": node.parent_node.node_id if node.parent_node else None,
            "children": [child.node_id for child in node.child_nodes],
            "shape_type": getattr(node, "shape_type", "rounded_rect"),
            "custom_color": getattr(node, "custom_color", None),
            "icon_type": getattr(node, "icon_type", None)
        }
        data["nodes"].append(node_data)

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving to JSON file: {e}")
        return False


def load_mind_map(file_path, scene):
    """
    Loads serialized JSON map data, clears the current scene,
    and reconstructs the node tree along with their connection edges.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return False

    nodes_data = data.get("nodes", [])
    root_id = data.get("root_id")

    if not nodes_data:
        return False

    # Clear current canvas
    scene.clear_scene()

    # Step 1: Create all node instances and store their positions
    temp_nodes = {}
    for n_data in nodes_data:
        node_id = n_data["id"]
        text = n_data["text"]
        x = n_data.get("x", 0.0)
        y = n_data.get("y", 0.0)
        
        shape_type = n_data.get("shape_type", "rounded_rect")
        custom_color = n_data.get("custom_color", None)
        icon_type = n_data.get("icon_type", None)
        
        node = Node(node_id=node_id, text=text, x=x, y=y)
        node.shape_type = shape_type
        node.custom_color = custom_color
        node.icon_type = icon_type
        node.update_geometry()  # Recalculate dimensions for loaded shape/icon
        
        temp_nodes[node_id] = node

    # Step 2: Establish parent-child references
    for n_data in nodes_data:
        node_id = n_data["id"]
        parent_id = n_data.get("parent")
        node = temp_nodes.get(node_id)

        if node and parent_id:
            parent_node = temp_nodes.get(parent_id)
            if parent_node:
                node.parent_node = parent_node
                parent_node.child_nodes.append(node)

    # Step 3: Identify the root node
    root_node = temp_nodes.get(root_id)
    if not root_node:
        # Fallback: find the first node that doesn't have a parent
        for node in temp_nodes.values():
            if node.parent_node is None:
                root_node = node
                break

    if not root_node:
        return False

    # Set root node in the scene
    scene.set_root_node(root_node)

    # Step 4: Register remaining nodes to the scene
    for node_id, node in temp_nodes.items():
        if node != root_node:
            scene.add_node(node)

    # Step 5: Construct visual Edge lines between parent-child nodes
    for node_id, node in temp_nodes.items():
        for child in node.child_nodes:
            edge = Edge(node, child)
            scene.addItem(edge)

    # Trigger a redraw and bounding update
    scene.update()
    return True
