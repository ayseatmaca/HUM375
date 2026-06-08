import uuid
from PyQt5.QtWidgets import QGraphicsObject, QGraphicsItem, QGraphicsTextItem, QMenu, QGraphicsDropShadowEffect, QColorDialog
from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QPointF
from PyQt5.QtGui import QColor, QPen, QBrush, QPainterPath, QFont

class EditableTextItem(QGraphicsTextItem):
    """
    A text item that enables inline editing, auto-saves on focus loss,
    and finishes editing when Enter/Return is pressed.
    """
    def __init__(self, parent_node):
        super().__init__(parent_node)
        self.parent_node = parent_node
        # Use a readable font
        font = QFont("Inter", 11)
        self.setFont(font)
        self.setTabChangesFocus(True)
        # Wrap text at a maximum width to prevent nodes from becoming too wide
        self.setTextWidth(200)
        
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.parent_node.finish_editing()
        
    def keyPressEvent(self, event):
        # Pressing Enter/Return finishes editing
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Shift+Enter can be used for new lines if needed, otherwise Enter submits
            if event.modifiers() & Qt.ShiftModifier:
                super().keyPressEvent(event)
            else:
                self.clearFocus()
                event.accept()
        elif event.key() == Qt.Key_Escape:
            # Cancel editing and restore old text
            self.setPlainText(self.parent_node.text)
            self.clearFocus()
            event.accept()
        else:
            super().keyPressEvent(event)

class Node(QGraphicsObject):
    """
    A custom QGraphicsItem representing a node in the Mind Map.
    Has customizable background shape (rounded rect, ellipse, capsule),
    level-based or custom color schemes, icons, a drop shadow,
    and supports dragging, editing, and context menus.
    """
    # Signals to communicate actions back to the scene/controller
    child_added = pyqtSignal(object)       # Emits (parent_node)
    rename_requested = pyqtSignal(object)  # Emits (node)
    delete_requested = pyqtSignal(object)  # Emits (node)
    moved = pyqtSignal(object)             # Emits (node)
    appearance_changed = pyqtSignal(object)  # Emits (node)

    def __init__(self, node_id=None, text="New Node", x=0.0, y=0.0, parent_node=None):
        super().__init__()
        self.node_id = node_id if node_id else str(uuid.uuid4())
        self.text = text
        self.parent_node = parent_node
        self.child_nodes = []
        self.edges = []  # List of connected Edge objects
        
        # New customizable visual traits
        self.shape_type = "rounded_rect"
        self.custom_color = None
        self.icon_type = None
        
        # Configure item flags for movement, selection, and geometry notifications
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # Create and style the child text item
        self.text_item = EditableTextItem(self)
        self.text_item.setPlainText(self.text)
        self.text_item.setDefaultTextColor(Qt.white)
        
        # Add modern drop shadow for premium look
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(12)
        self.shadow.setColor(QColor(0, 0, 0, 50))
        self.shadow.setOffset(0, 3)
        self.setGraphicsEffect(self.shadow)
        
        # Initial position
        self.setPos(x, y)
        
        # Initial bounding rectangle
        self.rect = QRectF(-60, -20, 120, 40)
        self.update_geometry()
        
    def get_level(self):
        """Calculates tree level depth (0 for root, 1 for children, etc.)"""
        level = 0
        curr = self.parent_node
        while curr:
            level += 1
            curr = curr.parent_node
        return level

    def get_color_for_level(self):
        """Returns background color depending on node hierarchy level"""
        level = self.get_level()
        if level == 0:
            return QColor("#4F46E5")  # Indigo (Root)
        elif level == 1:
            return QColor("#0284C7")  # Ocean Blue
        elif level == 2:
            return QColor("#059669")  # Emerald Green
        else:
            return QColor("#475569")  # Slate Grey (Leaves)

    def get_color(self):
        """Returns custom color if defined, otherwise level default color"""
        if self.custom_color:
            return QColor(self.custom_color)
        return self.get_color_for_level()

    def update_geometry(self):
        """Adjusts the node size to perfectly fit its text label and icon with padding"""
        self.prepareGeometryChange()
        
        # Set font scale based on level: Root node has larger bold font
        level = self.get_level()
        font = QFont("Inter")
        if level == 0:
            font.setPointSize(13)
            font.setBold(True)
        else:
            font.setPointSize(11)
            font.setBold(False)
        self.text_item.setFont(font)
        
        # Automatically update text color based on background brightness for premium readability
        bg_color = self.get_color()
        luminance = (0.299 * bg_color.red() + 0.587 * bg_color.green() + 0.114 * bg_color.blue()) / 255.0
        if luminance > 0.6:
            self.text_item.setDefaultTextColor(QColor("#1e293b"))  # Dark slate for light backgrounds
        else:
            self.text_item.setDefaultTextColor(Qt.white)           # White for dark backgrounds

        text_rect = self.text_item.boundingRect()
        
        # Standard paddings per shape
        if self.shape_type == "ellipse":
            padding_x = 30
            padding_y = 16
        elif self.shape_type == "capsule":
            padding_y = 10
            padding_x = 22
        else:  # rounded_rect
            padding_x = 18
            padding_y = 10
            
        # Larger padding for root node
        if level == 0:
            padding_x += 8
            padding_y += 6
            
        icon_w = 20
        icon_spacing = 6
        
        if self.icon_type:
            content_width = text_rect.width() + icon_w + icon_spacing
        else:
            content_width = text_rect.width()
            
        width = max(110 if level != 0 else 140, content_width + 2 * padding_x)
        height = max(42 if level != 0 else 54, text_rect.height() + 2 * padding_y)
        
        # Enforce capsule geometry constraint: width must fit the rounded end-caps
        if self.shape_type == "capsule":
            width = max(width, content_width + height)
            
        self.rect = QRectF(-width / 2, -height / 2, width, height)
        
        # Center the combined [icon + text] group horizontally
        if self.icon_type:
            total_content_w = text_rect.width() + icon_w + icon_spacing
            text_x = -total_content_w / 2 + icon_w + icon_spacing
            self.text_item.setPos(text_x, -text_rect.height() / 2)
        else:
            self.text_item.setPos(-text_rect.width() / 2, -text_rect.height() / 2)
            
        # Redraw
        self.update()
        
        # Update connection lines
        self.update_edges()

    def finish_editing(self):
        """Called when text editing is complete. Updates label and dimensions."""
        new_text = self.text_item.toPlainText().strip()
        if not new_text:
            new_text = self.text  # Revert if blank
        
        changed = (self.text != new_text)
        self.text = new_text
        self.text_item.setPlainText(new_text)
        self.update_geometry()
        
        if changed:
            self.rename_requested.emit(self)
        
    def start_editing(self):
        """Enables text editing and focuses the text item."""
        self.text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.text_item.setFocus()
        
        # Place cursor at the end of text
        cursor = self.text_item.textCursor()
        cursor.select(cursor.Document)
        self.text_item.setTextCursor(cursor)

    def update_edges(self):
        """Recalculates shapes of all connected edge lines"""
        for edge in self.edges:
            edge.update_position()

    def get_all_descendants(self):
        """Returns a list of all child nodes recursively"""
        descendants = []
        for child in self.child_nodes:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants

    # Qt graphics view overrides
    def boundingRect(self):
        # Expand slightly to prevent clipping of the border / shadow
        return self.rect.adjusted(-6, -6, 6, 6)

    def paint(self, painter, option, widget):
        # Build path based on shape type
        path = QPainterPath()
        if self.shape_type == "ellipse":
            path.addEllipse(self.rect)
        elif self.shape_type == "capsule":
            radius = self.rect.height() / 2
            path.addRoundedRect(self.rect, radius, radius)
        else:  # rounded_rect
            path.addRoundedRect(self.rect, 8, 8)
            
        color = self.get_color()
        
        # Selection styling
        if self.isSelected():
            painter.setPen(QPen(QColor("#3B82F6"), 2.5, Qt.DashLine))
        else:
            painter.setPen(QPen(color.darker(115), 1.5))
            
        painter.setBrush(QBrush(color))
        painter.setRenderHint(painter.Antialiasing)
        painter.drawPath(path)
        
        # Draw emoji icon inside the node bounds if present
        if self.icon_type:
            emoji_map = {
                "idea": "💡",
                "folder": "📁",
                "task": "☑️",
                "note": "📝",
                "star": "⭐"
            }
            emoji = emoji_map.get(self.icon_type, "")
            if emoji:
                text_rect = self.text_item.boundingRect()
                icon_w = 20
                icon_spacing = 6
                total_content_w = text_rect.width() + icon_w + icon_spacing
                
                # Align left relative to the text
                icon_x = -total_content_w / 2
                # Vertically center the emoji text bounding rect
                icon_rect = QRectF(icon_x, -11, icon_w, 22)
                
                # Check background brightness for icon readability
                luminance = (0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue()) / 255.0
                
                # Draw the emoji
                painter.save()
                font = QFont("Segoe UI Emoji", 11)
                painter.setFont(font)
                painter.drawText(icon_rect, Qt.AlignCenter, emoji)
                painter.restore()

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.update_edges()
            self.moved.emit(self)
        return super().itemChange(change, value)

    def mouseDoubleClickEvent(self, event):
        self.start_editing()
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu()
        # Set stylesheet for elegant modern look
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                color: #334155;
            }
            QMenu::item:selected {
                background-color: #f1f5f9;
                color: #1e293b;
                border-radius: 4px;
            }
            QMenu::separator {
                height: 1px;
                background-color: #e2e8f0;
                margin: 4px 8px;
            }
        """)
        
        add_child_action = menu.addAction("Add Child Node")
        rename_action = menu.addAction("Rename Node")
        
        menu.addSeparator()
        
        # Submenu for Custom Shapes
        shape_menu = menu.addMenu("Node Shape")
        rect_action = shape_menu.addAction("Rounded Rectangle")
        ellipse_action = shape_menu.addAction("Ellipse")
        capsule_action = shape_menu.addAction("Capsule")
        
        # Submenu for Icons
        icon_menu = menu.addMenu("Set Icon")
        no_icon_action = icon_menu.addAction("No Icon")
        idea_action = icon_menu.addAction("Idea 💡")
        folder_action = icon_menu.addAction("Folder 📁")
        task_action = icon_menu.addAction("Task ☑️")
        note_action = icon_menu.addAction("Note 📝")
        star_action = icon_menu.addAction("Star ⭐")
        
        # Submenu for Color Selection
        color_menu = menu.addMenu("Node Color")
        change_color_action = color_menu.addAction("Change Node Color...")
        reset_color_action = color_menu.addAction("Reset Default Color")
        
        delete_action = None
        # Root node cannot be deleted
        if self.parent_node is not None:
            menu.addSeparator()
            delete_action = menu.addAction("Delete Node")
            
        # Execute menu and map actions to signal emitters
        action = menu.exec_(event.screenPos())
        if action == add_child_action:
            self.child_added.emit(self)
        elif action == rename_action:
            self.start_editing()
        elif action == delete_action and delete_action:
            self.delete_requested.emit(self)
        elif action == rect_action:
            self.shape_type = "rounded_rect"
            self.update_geometry()
            self.appearance_changed.emit(self)
        elif action == ellipse_action:
            self.shape_type = "ellipse"
            self.update_geometry()
            self.appearance_changed.emit(self)
        elif action == capsule_action:
            self.shape_type = "capsule"
            self.update_geometry()
            self.appearance_changed.emit(self)
        elif action == no_icon_action:
            self.icon_type = None
            self.update_geometry()
            self.appearance_changed.emit(self)
        elif action == idea_action:
            self.icon_type = "idea"
            self.update_geometry()
            self.appearance_changed.emit(self)
        elif action == folder_action:
            self.icon_type = "folder"
            self.update_geometry()
            self.appearance_changed.emit(self)
        elif action == task_action:
            self.icon_type = "task"
            self.update_geometry()
            self.appearance_changed.emit(self)
        elif action == note_action:
            self.icon_type = "note"
            self.update_geometry()
            self.appearance_changed.emit(self)
        elif action == star_action:
            self.icon_type = "star"
            self.update_geometry()
            self.appearance_changed.emit(self)
        elif action == change_color_action:
            initial_color = self.get_color()
            color = QColorDialog.getColor(initial_color, None, "Select Node Color")
            if color.isValid():
                self.custom_color = color.name()
                self.update_geometry()
                self.appearance_changed.emit(self)
        elif action == reset_color_action:
            self.custom_color = None
            self.update_geometry()
            self.appearance_changed.emit(self)

