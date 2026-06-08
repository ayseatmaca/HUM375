from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView
from PyQt5.QtCore import Qt, QPointF, pyqtSignal
from PyQt5.QtGui import QPainter, QColor
from node import Node
from edge import Edge

class MindMapScene(QGraphicsScene):
    """
    Custom QGraphicsScene managing the life-cycle of mind map nodes and edges,
    including node additions, structural deletion, and connecting edges.
    """
    node_added = pyqtSignal()
    node_deleted = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Set clean canvas size and white background
        self.setSceneRect(-2000, -2000, 4000, 4000)
        self.setBackgroundBrush(QColor("#ffffff"))
        
        self.root_node = None
        self.nodes = {}  # Dictionary mapping node_id -> Node

    def set_root_node(self, node):
        """Sets the central node of the mind map"""
        self.root_node = node
        self.add_node(node)

    def add_node(self, node):
        """Registers a node to the scene and hooks up its event signals"""
        self.addItem(node)
        self.nodes[node.node_id] = node
        
        # Connect signals
        node.child_added.connect(self.on_child_added)
        node.delete_requested.connect(self.on_delete_requested)

    def create_child_node(self, parent_node, text="Subtopic", x=None, y=None, start_edit=True):
        """Creates a new child node, connects it with an edge, and registers it"""
        custom_pos = (x is not None and y is not None)
        if x is None or y is None:
            x, y = self.calculate_child_position(parent_node)
            
        child = Node(text=text, x=x, y=y, parent_node=parent_node)
        parent_node.child_nodes.append(child)
        
        # Add node to scene
        self.add_node(child)
        
        # Create visual connecting edge
        edge = Edge(parent_node, child)
        self.addItem(edge)
        
        # Automatically rearrange all children radially if position wasn't manually specified
        if not custom_pos:
            self.rearrange_children(parent_node)
            
        # Make the child node start in edit mode immediately for premium UX
        if start_edit:
            child.start_editing()
        
        self.node_added.emit()
        return child

    def calculate_child_position(self, parent_node):
        """Calculates a logical, non-overlapping location for a new child node radially"""
        import math
        k = len(parent_node.child_nodes) + 1  # count including the new child
        
        if parent_node == self.root_node:
            r = 240
            angle = (k - 1) * (2.0 * math.pi / max(1, k))
            x_pos = parent_node.x() + r * math.cos(angle)
            y_pos = parent_node.y() + r * math.sin(angle)
            return x_pos, y_pos
        else:
            dx = parent_node.x() - self.root_node.x()
            dy = parent_node.y() - self.root_node.y()
            parent_angle = math.atan2(dy, dx)
            r = 180
            if k == 1:
                x_pos = parent_node.x() + r * math.cos(parent_angle)
                y_pos = parent_node.y() + r * math.sin(parent_angle)
            else:
                arc_width = min(5.0 * math.pi / 6.0, k * (math.pi / 6.0))
                angle = parent_angle - arc_width / 2.0 + (k - 1) * (arc_width / max(1, k - 1))
                x_pos = parent_node.x() + r * math.cos(angle)
                y_pos = parent_node.y() + r * math.sin(angle)
            return x_pos, y_pos

    def rearrange_children(self, parent_node):
        """Reposition all children of a parent node radially so they are evenly distributed."""
        children = parent_node.child_nodes
        if not children:
            return
            
        import math
        k = len(children)
        
        if parent_node == self.root_node:
            r = 240
            for i, child in enumerate(children):
                angle = i * (2.0 * math.pi / k)
                px = parent_node.x() + r * math.cos(angle)
                py = parent_node.y() + r * math.sin(angle)
                self.set_node_position_recursive(child, QPointF(px, py))
        else:
            dx = parent_node.x() - self.root_node.x()
            dy = parent_node.y() - self.root_node.y()
            parent_angle = math.atan2(dy, dx)
            
            r = 180
            if k == 1:
                px = parent_node.x() + r * math.cos(parent_angle)
                py = parent_node.y() + r * math.sin(parent_angle)
                self.set_node_position_recursive(children[0], QPointF(px, py))
            else:
                arc_width = min(5.0 * math.pi / 6.0, (k - 1) * (math.pi / 6.0))
                start_angle = parent_angle - arc_width / 2.0
                for i, child in enumerate(children):
                    angle = start_angle + i * (arc_width / (k - 1))
                    px = parent_node.x() + r * math.cos(angle)
                    py = parent_node.y() + r * math.sin(angle)
                    self.set_node_position_recursive(child, QPointF(px, py))

    def set_node_position_recursive(self, node, new_pos):
        """Sets a node's position and shifts all its descendants recursively by the same delta."""
        dx = new_pos.x() - node.x()
        dy = new_pos.y() - node.y()
        if dx == 0 and dy == 0:
            return
            
        node.setPos(new_pos)
        node.update_edges()
        
        for desc in node.get_all_descendants():
            desc.setPos(desc.x() + dx, desc.y() + dy)
            desc.update_edges()

    def auto_arrange(self):
        """Automatically organizes the entire mind map in a radial tree layout."""
        if not self.root_node:
            return
            
        import math
        
        # 1. Count leaves for each subtree to allocate angular sectors
        leaves = {}
        def count_subtree_leaves(node):
            if not node.child_nodes:
                leaves[node.node_id] = 1
                return 1
            total = 0
            for child in node.child_nodes:
                total += count_subtree_leaves(child)
            leaves[node.node_id] = total
            return total
            
        count_subtree_leaves(self.root_node)
        
        # 2. Position root at the center
        self.root_node.setPos(0, 0)
        self.root_node.update_edges()
        
        # 3. Recursively layout descendants in their allocated sectors
        def layout_node(node, theta_start, theta_end, depth):
            children = node.child_nodes
            if not children:
                return
                
            r = 240 if depth == 0 else 180
            total_leaves = leaves[node.node_id]
            current_theta = theta_start
            
            for child in children:
                child_leaves = leaves[child.node_id]
                theta_width = (theta_end - theta_start) * (child_leaves / total_leaves)
                
                # Center angle for the child
                child_theta = current_theta + theta_width / 2.0
                
                px = node.x() + r * math.cos(child_theta)
                py = node.y() + r * math.sin(child_theta)
                child.setPos(px, py)
                child.update_edges()
                
                # Constrain branching angles to prevent nodes from growing inwards
                if depth == 0:
                    half_w = min(theta_width, 2.0 * math.pi / 3.0) / 2.0
                    layout_node(child, child_theta - half_w, child_theta + half_w, depth + 1)
                else:
                    half_w = min(theta_width, math.pi * 0.6) / 2.0
                    layout_node(child, child_theta - half_w, child_theta + half_w, depth + 1)
                    
                current_theta += theta_width
                
        layout_node(self.root_node, 0, 2.0 * math.pi, 0)
        self.update()

    def delete_node(self, node):
        """Recursively deletes a node, all its descendants, and their connected edges"""
        # Do not allow deleting the root node
        if node == self.root_node:
            return
            
        parent_node = node.parent_node
        
        # 1. Fetch all child descendants
        descendants = node.get_all_descendants()
        targets = [node] + descendants
        
        # 2. Detach target node from its parent
        if parent_node and node in parent_node.child_nodes:
            parent_node.child_nodes.remove(node)
            
        # 3. Clean up scene registry and graphics items
        for n in targets:
            # Disconnect and delete edges
            edges_to_delete = list(n.edges)
            for edge in edges_to_delete:
                edge.disconnect()
                self.removeItem(edge)
            
            # Remove from local dictionary
            if n.node_id in self.nodes:
                del self.nodes[n.node_id]
                
            # Remove node from scene
            self.removeItem(n)
            
        # 4. Rearrange siblings to fill the gap
        if parent_node:
            self.rearrange_children(parent_node)
            
        self.node_deleted.emit()

    def clear_scene(self):
        """Clears all nodes and edges from the scene"""
        self.clear()
        self.nodes.clear()
        self.root_node = None

    # Signal slots
    def on_child_added(self, parent_node):
        self.create_child_node(parent_node)

    def on_delete_requested(self, node):
        self.delete_node(node)


class MindMapView(QGraphicsView):
    """
    Custom QGraphicsView widget displaying the MindMapScene.
    Implements anti-aliased rendering, canvas drag-to-scroll, and mouse wheel zooming.
    """
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        
        # Modern rendering quality configurations
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setRenderHint(QPainter.TextAntialiasing, True)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        
        # Panning behavior: left-drag will drag/pan the canvas
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        
        # Hide scroll bars for a cleaner look
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Anchor zoom conversions under mouse cursor
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

    def wheelEvent(self, event):
        """Zoom in and zoom out when mouse wheel is rotated"""
        zoom_factor = 1.15
        
        # Check scroll wheel direction
        if event.angleDelta().y() > 0:
            # Zoom In
            self.scale(zoom_factor, zoom_factor)
        else:
            # Zoom Out
            self.scale(1.0 / zoom_factor, 1.0 / zoom_factor)
            
        event.accept()
