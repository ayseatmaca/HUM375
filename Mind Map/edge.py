from PyQt5.QtWidgets import QGraphicsPathItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QPainterPath, QColor

class Edge(QGraphicsPathItem):
    """
    Representing the connection path between a parent node and a child node.
    Uses a smooth cubic Bezier curve that adjusts dynamically as nodes are dragged.
    """
    def __init__(self, source_node, dest_node):
        super().__init__()
        self.source = source_node
        self.dest = dest_node
        
        # Add references to nodes
        self.source.edges.append(self)
        self.dest.edges.append(self)
        
        # Visual style - color matches the destination node's theme level
        self.update_style()
        
        # Position calculation
        self.update_position()

    def update_style(self):
        """Sets the line color to match the level color of the destination node"""
        if self.dest:
            color = self.dest.get_color()
            pen = QPen(color, 2.2)
            pen.setCapStyle(Qt.RoundCap)
            # Enable high quality anti-aliasing rendering
            pen.setStyle(Qt.SolidLine)
            self.setPen(pen)

    def update_position(self):
        """Recalculates the Bezier curve path connecting the two nodes"""
        if not self.source or not self.dest:
            return
            
        # Determine source and destination connection ports based on relative positions
        src_x = self.source.x()
        dst_x = self.dest.x()
        
        # Center coordinates
        src_y = self.source.y()
        dst_y = self.dest.y()
        
        # Source half-dimensions
        src_hw = self.source.rect.width() / 2
        # Dest half-dimensions
        dst_hw = self.dest.rect.width() / 2
        
        if dst_x >= src_x:
            # Child is to the right: connect from parent's right side to child's left side
            p1 = QPointF(src_x + src_hw, src_y)
            p2 = QPointF(dst_x - dst_hw, dst_y)
            # Offset control points horizontally
            ctrl_offset = max(30.0, (p2.x() - p1.x()) * 0.5)
            c1 = QPointF(p1.x() + ctrl_offset, p1.y())
            c2 = QPointF(p2.x() - ctrl_offset, p2.y())
        else:
            # Child is to the left: connect from parent's left side to child's right side
            p1 = QPointF(src_x - src_hw, src_y)
            p2 = QPointF(dst_x + dst_hw, dst_y)
            # Offset control points horizontally
            ctrl_offset = max(30.0, (p1.x() - p2.x()) * 0.5)
            c1 = QPointF(p1.x() - ctrl_offset, p1.y())
            c2 = QPointF(p2.x() + ctrl_offset, p2.y())
            
        # Build cubic bezier path
        path = QPainterPath()
        path.moveTo(p1)
        path.cubicTo(c1, c2, p2)
        
        self.setPath(path)
        
    def disconnect(self):
        """Removes itself from the connected nodes' edge lists"""
        if self.source and self in self.source.edges:
            self.source.edges.remove(self)
        if self.dest and self in self.dest.edges:
            self.dest.edges.remove(self)
