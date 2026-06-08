import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QMessageBox, 
                             QAction, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QFrame, QToolBar, QToolButton, QDoubleSpinBox,
                             QPushButton, QColorDialog)
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QIcon, QPainter, QImage, QColor, QFont, QKeySequence

from scene import MindMapScene, MindMapView
from node import Node
from storage import save_mind_map, load_mind_map

class MainWindow(QMainWindow):
    """
    Main Application Window containing the menu bar, top toolbar,
    status bar, central canvas view, and right-side properties panel.
    """
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Mind Map Application")
        self.resize(1150, 750)
        
        # State tracking variables
        self.current_file_path = None
        self.is_dirty = False
        self.selected_node = None
        self.current_theme = "light"
        
        # Initialize Scene and View
        self.scene = MindMapScene()
        self.view = MindMapView(self.scene)
        
        # Create Actions, Menus, Toolbar, and Status Bar
        self.create_actions()
        self.create_menus()
        self.create_toolbar()
        self.create_status_bar()
        
        # Setup central widget and layout (View and Properties Panel side-by-side)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Add Graphics View to layout
        main_layout.addWidget(self.view, stretch=4)
        
        # Add Properties Panel to layout
        self.prop_panel = self.create_properties_panel()
        main_layout.addWidget(self.prop_panel, stretch=1)
        
        # Initialize default mind map with a central node
        self.reset_map()
        
        # Connect selection and content change notifications
        self.scene.selectionChanged.connect(self.on_selection_changed)
        self.scene.node_added.connect(self.on_scene_node_added)
        self.scene.node_deleted.connect(self.on_scene_node_deleted)
        
        # Apply initial theme style
        self.set_theme("light")

    def create_actions(self):
        """Instantiates all QActions mapped to keyboard shortcuts and tips"""
        # File Actions
        self.new_action = QAction("&New", self)
        self.new_action.setShortcut(QKeySequence("Ctrl+N"))
        self.new_action.setStatusTip("Create a new Mind Map")
        self.new_action.triggered.connect(self.on_new)
        
        self.open_action = QAction("&Open...", self)
        self.open_action.setShortcut(QKeySequence("Ctrl+O"))
        self.open_action.setStatusTip("Open an existing Mind Map JSON")
        self.open_action.triggered.connect(self.on_open)
        
        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut(QKeySequence("Ctrl+S"))
        self.save_action.setStatusTip("Save current Mind Map")
        self.save_action.triggered.connect(self.on_save)
        
        self.save_as_action = QAction("Save &As...", self)
        self.save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.save_as_action.setStatusTip("Save current Mind Map to a new location")
        self.save_as_action.triggered.connect(self.on_save_as)
        
        self.sample_action = QAction("Load &Sample Map", self)
        self.sample_action.setStatusTip("Load a pre-configured sample Mind Map")
        self.sample_action.triggered.connect(self.on_load_sample_map)
        
        self.export_action = QAction("&Export as PNG...", self)
        self.export_action.setShortcut(QKeySequence("Ctrl+E"))
        self.export_action.setStatusTip("Export the canvas as a PNG image")
        self.export_action.triggered.connect(self.on_export_png)
        self.export_action.setIconText("Export PNG")
        
        self.exit_action = QAction("E&xit", self)
        self.exit_action.setStatusTip("Exit the application")
        self.exit_action.triggered.connect(self.close)
        
        # Edit Actions
        self.add_child_action = QAction("&Add Child Node", self)
        self.add_child_action.setStatusTip("Add a child node to the selected node")
        self.add_child_action.triggered.connect(self.add_child_node)
        self.add_child_action.setIconText("Add Child")
        
        self.rename_action = QAction("&Rename Selected Node", self)
        self.rename_action.setShortcut(QKeySequence("F2"))
        self.rename_action.setStatusTip("Rename the selected node")
        self.rename_action.triggered.connect(self.rename_selected_node)
        self.rename_action.setIconText("Rename Node")
        
        self.delete_action = QAction("&Delete Selected Node", self)
        self.delete_action.setShortcut(QKeySequence("Delete"))
        self.delete_action.setStatusTip("Delete the selected node and its descendants")
        self.delete_action.triggered.connect(self.delete_selected_node)
        self.delete_action.setIconText("Delete Node")
        
        self.auto_arrange_action = QAction("&Auto Arrange", self)
        self.auto_arrange_action.setStatusTip("Automatically organize the entire mind map layout")
        self.auto_arrange_action.triggered.connect(self.on_auto_arrange)
        self.auto_arrange_action.setIconText("Auto Arrange")
        
        self.center_view_action = QAction("&Center View", self)
        self.center_view_action.setStatusTip("Center view on selected node or root")
        self.center_view_action.triggered.connect(self.center_view)
        
        # View Actions
        self.zoom_in_action = QAction("Zoom &In", self)
        self.zoom_in_action.setShortcuts([QKeySequence("Ctrl+Plus"), QKeySequence("Ctrl+=")])
        self.zoom_in_action.setStatusTip("Zoom in the mind map canvas")
        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.zoom_in_action.setIconText("Zoom In")
        
        self.zoom_out_action = QAction("Zoom &Out", self)
        self.zoom_out_action.setShortcuts([QKeySequence("Ctrl+Minus"), QKeySequence("Ctrl+-")])
        self.zoom_out_action.setStatusTip("Zoom out the mind map canvas")
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.zoom_out_action.setIconText("Zoom Out")
        
        self.reset_zoom_action = QAction("&Reset Zoom", self)
        self.reset_zoom_action.setShortcut(QKeySequence("Ctrl+0"))
        self.reset_zoom_action.setStatusTip("Reset zoom level to 100%")
        self.reset_zoom_action.triggered.connect(self.reset_zoom)
        self.reset_zoom_action.setIconText("Reset Zoom")
        
        self.stats_action = QAction("Mind Map &Statistics", self)
        self.stats_action.setStatusTip("Show structural statistics of the mind map")
        self.stats_action.triggered.connect(self.show_statistics)
        
        # Themes
        self.light_theme_action = QAction("&Light Theme", self)
        self.light_theme_action.setStatusTip("Switch to Light Theme")
        self.light_theme_action.triggered.connect(lambda: self.set_theme("light"))
        
        self.dark_theme_action = QAction("&Dark Theme", self)
        self.dark_theme_action.setStatusTip("Switch to Dark Theme")
        self.dark_theme_action.triggered.connect(lambda: self.set_theme("dark"))
        
        # Help Actions
        self.about_action = QAction("&About", self)
        self.about_action.setStatusTip("Show details about the application")
        self.about_action.triggered.connect(self.on_about)

    def create_menus(self):
        """Creates the Menu Bar and binds menu items to their handler methods"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.sample_action)
        file_menu.addAction(self.export_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(self.add_child_action)
        edit_menu.addAction(self.rename_action)
        edit_menu.addAction(self.delete_action)
        edit_menu.addAction(self.auto_arrange_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.center_view_action)
        
        # View Menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction(self.zoom_in_action)
        view_menu.addAction(self.zoom_out_action)
        view_menu.addAction(self.reset_zoom_action)
        view_menu.addSeparator()
        
        # Themes submenu
        theme_menu = view_menu.addMenu("&Theme")
        theme_menu.addAction(self.light_theme_action)
        theme_menu.addAction(self.dark_theme_action)
        
        view_menu.addAction(self.stats_action)
        
        # Help Menu
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction(self.about_action)

    def create_toolbar(self):
        """Creates top tool bar panel with text button actions"""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextOnly)
        
        toolbar.addAction(self.new_action)
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addAction(self.export_action)
        
        toolbar.addSeparator()
        
        toolbar.addAction(self.add_child_action)
        toolbar.addAction(self.rename_action)
        toolbar.addAction(self.delete_action)
        toolbar.addAction(self.auto_arrange_action)
        
        toolbar.addSeparator()
        
        toolbar.addAction(self.zoom_in_action)
        toolbar.addAction(self.zoom_out_action)
        toolbar.addAction(self.reset_zoom_action)

    def create_properties_panel(self):
        """Creates the right-side properties editor panel"""
        panel = QFrame()
        panel.setObjectName("propPanel")
        panel.setFixedWidth(270)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setAlignment(Qt.AlignTop)
        
        title = QLabel("Node Properties")
        title.setObjectName("propTitle")
        layout.addWidget(title)
        
        # Helper to create styled header labels
        def create_field_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #64748b; font-size: 9pt; font-weight: 600; margin-top: 8px;")
            return lbl

        # Node Name input
        layout.addWidget(create_field_label("Node Text:"))
        self.prop_text_edit = QLineEdit()
        self.prop_text_edit.setPlaceholderText("Select a node...")
        self.prop_text_edit.setEnabled(False)
        self.prop_text_edit.textEdited.connect(self.on_prop_text_edited)
        layout.addWidget(self.prop_text_edit)
        
        # Helper for read-only metadata rows
        def add_read_only_row(label_text):
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: #64748b; font-size: 9pt; font-weight: 500;")
            val = QLabel("-")
            val.setStyleSheet("color: #334155; font-size: 9pt; font-family: 'Consolas', monospace;")
            row.addWidget(lbl)
            row.addWidget(val, 0, Qt.AlignRight)
            layout.addLayout(row)
            layout.addSpacing(4)
            return val
            
        layout.addSpacing(10)
        self.prop_id_val = add_read_only_row("Node ID:")
        self.prop_parent_val = add_read_only_row("Parent Node:")
        self.prop_level_val = add_read_only_row("Level:")
        self.prop_children_val = add_read_only_row("Child Count:")
        
        layout.addSpacing(8)
        
        # Editable X and Y Position coordinates
        layout.addWidget(create_field_label("Position (X, Y):"))
        pos_layout = QHBoxLayout()
        
        self.prop_x_spin = QDoubleSpinBox()
        self.prop_x_spin.setRange(-10000.0, 10000.0)
        self.prop_x_spin.setDecimals(1)
        self.prop_x_spin.setEnabled(False)
        self.prop_x_spin.valueChanged.connect(self.on_prop_coordinates_edited)
        
        self.prop_y_spin = QDoubleSpinBox()
        self.prop_y_spin.setRange(-10000.0, 10000.0)
        self.prop_y_spin.setDecimals(1)
        self.prop_y_spin.setEnabled(False)
        self.prop_y_spin.valueChanged.connect(self.on_prop_coordinates_edited)
        
        pos_layout.addWidget(self.prop_x_spin)
        pos_layout.addWidget(self.prop_y_spin)
        layout.addLayout(pos_layout)
        
        layout.addSpacing(8)
        
        # Editable Node Color Customization
        layout.addWidget(create_field_label("Node Color:"))
        color_layout = QHBoxLayout()
        
        self.prop_color_swatch = QPushButton()
        self.prop_color_swatch.setFixedWidth(24)
        self.prop_color_swatch.setFixedHeight(24)
        self.prop_color_swatch.setEnabled(False)
        self.prop_color_swatch.setStyleSheet("background-color: #cbd5e1; border: 1px solid #94a3b8; border-radius: 4px;")
        self.prop_color_swatch.clicked.connect(self.on_prop_color_clicked)
        
        self.prop_color_btn = QPushButton("Change...")
        self.prop_color_btn.setEnabled(False)
        self.prop_color_btn.clicked.connect(self.on_prop_color_clicked)
        
        self.prop_color_reset = QPushButton("Reset")
        self.prop_color_reset.setEnabled(False)
        self.prop_color_reset.clicked.connect(self.on_prop_color_reset)
        
        color_layout.addWidget(self.prop_color_swatch)
        color_layout.addWidget(self.prop_color_btn)
        color_layout.addWidget(self.prop_color_reset)
        layout.addLayout(color_layout)
        
        return panel

    def create_status_bar(self):
        """Creates the status bar and configures help labels"""
        status = self.statusBar()
        
        # Guide message
        guide_label = QLabel(
            "Double-click to Edit | Right-click Node for Options | Left-Drag Canvas to Pan | Mouse Scroll to Zoom"
        )
        guide_label.setStyleSheet("padding-left: 8px;")
        status.addWidget(guide_label)
        
        # Sync window title dirty status
        self.update_title()

    def update_title(self):
        """Updates main window title to reflect file path and save status"""
        file_name = os.path.basename(self.current_file_path) if self.current_file_path else "Untitled"
        dirty_marker = " *" if self.is_dirty else ""
        self.setWindowTitle(f"Mind Map Application - {file_name}{dirty_marker}")

    def reset_map(self):
        """Resets the mind map canvas and sets up the central root node"""
        try:
            self.scene.changed.disconnect(self.mark_dirty)
        except TypeError:
            pass # wasn't connected
            
        self.scene.clear_scene()
        self.selected_node = None
        self.on_selection_changed() # Update properties panel fields
        
        # Create central root node
        root = Node(text="Central Idea", x=0.0, y=0.0, parent_node=None)
        self.scene.set_root_node(root)
        
        # Center view
        self.view.resetTransform()
        self.view.centerOn(0, 0)
        
        # Reset state
        self.current_file_path = None
        self.is_dirty = False
        self.update_title()
        
        # Connect change signals to mark document as modified (dirty)
        self.connect_change_monitoring()

    def connect_change_monitoring(self):
        """Binds scene changes to trigger modified state tracking"""
        self.scene.changed.connect(self.mark_dirty)

    def mark_dirty(self):
        """Sets the dirty state to true and updates the window title"""
        if not self.is_dirty:
            self.is_dirty = True
            self.update_title()

    def confirm_discard_changes(self):
        """Warns the user about unsaved changes. Returns True if safe to proceed."""
        if not self.is_dirty:
            return True
            
        reply = QMessageBox.question(
            self, "Unsaved Changes",
            "You have unsaved changes. Do you want to discard them?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        return reply == QMessageBox.Yes

    # Selection Sync & Property Panel Handlers
    def on_selection_changed(self):
        """Triggered when selected elements on the canvas scene change"""
        # Disconnect previous selected node signals if any
        if self.selected_node:
            try:
                self.selected_node.moved.disconnect(self.update_properties_coordinates)
                self.selected_node.rename_requested.disconnect(self.update_properties_text)
                self.selected_node.appearance_changed.disconnect(self.update_properties_fields)
            except (TypeError, RuntimeError):
                pass # wasn't connected or item was deleted
                
        selected_items = self.scene.selectedItems()
        if len(selected_items) == 1 and isinstance(selected_items[0], Node):
            self.selected_node = selected_items[0]
            # Connect signals
            self.selected_node.moved.connect(self.update_properties_coordinates)
            self.selected_node.rename_requested.connect(self.update_properties_text)
            self.selected_node.appearance_changed.connect(self.update_properties_fields)
            
            # Enable controls in properties panel
            self.prop_text_edit.setEnabled(True)
            self.prop_x_spin.setEnabled(True)
            self.prop_y_spin.setEnabled(True)
            self.prop_color_swatch.setEnabled(True)
            self.prop_color_btn.setEnabled(True)
            self.prop_color_reset.setEnabled(True)
            
            self.update_properties_fields()
        else:
            self.selected_node = None
            self.prop_text_edit.setEnabled(False)
            self.prop_x_spin.setEnabled(False)
            self.prop_y_spin.setEnabled(False)
            self.prop_color_swatch.setEnabled(False)
            self.prop_color_btn.setEnabled(False)
            self.prop_color_reset.setEnabled(False)
            
            self.clear_properties_fields()

    def update_properties_fields(self):
        """Updates all properties fields for the current selected node"""
        if not self.selected_node:
            return
            
        # Temporarily block signals from inputs to avoid circular updates
        self.prop_text_edit.blockSignals(True)
        self.prop_text_edit.setText(self.selected_node.text)
        self.prop_text_edit.blockSignals(False)
        
        self.prop_x_spin.blockSignals(True)
        self.prop_x_spin.setValue(self.selected_node.x())
        self.prop_x_spin.blockSignals(False)
        
        self.prop_y_spin.blockSignals(True)
        self.prop_y_spin.setValue(self.selected_node.y())
        self.prop_y_spin.blockSignals(False)
        
        self.prop_id_val.setText(str(self.selected_node.node_id))
        
        parent_text = self.selected_node.parent_node.text if self.selected_node.parent_node else "None"
        self.prop_parent_val.setText(parent_text)
        
        self.prop_level_val.setText(str(self.selected_node.get_level()))
        self.prop_children_val.setText(str(len(self.selected_node.child_nodes)))
        
        # Color preview
        color = self.selected_node.get_color()
        self.prop_color_swatch.setStyleSheet(
            f"background-color: {color.name()}; border: 1px solid {color.darker(120).name()}; border-radius: 4px;"
        )

    def clear_properties_fields(self):
        """Clears properties panel inputs when no node is selected"""
        self.prop_text_edit.blockSignals(True)
        self.prop_text_edit.clear()
        self.prop_text_edit.blockSignals(False)
        
        self.prop_x_spin.blockSignals(True)
        self.prop_x_spin.setValue(0.0)
        self.prop_x_spin.blockSignals(False)
        
        self.prop_y_spin.blockSignals(True)
        self.prop_y_spin.setValue(0.0)
        self.prop_y_spin.blockSignals(False)
        
        self.prop_id_val.setText("-")
        self.prop_parent_val.setText("-")
        self.prop_level_val.setText("-")
        self.prop_children_val.setText("-")
        
        self.prop_color_swatch.setStyleSheet("background-color: #cbd5e1; border: 1px solid #94a3b8; border-radius: 4px;")

    def update_properties_coordinates(self, node):
        """Updates coordinates display in properties panel on drag movement"""
        if node == self.selected_node:
            self.prop_x_spin.blockSignals(True)
            self.prop_x_spin.setValue(node.x())
            self.prop_x_spin.blockSignals(False)
            
            self.prop_y_spin.blockSignals(True)
            self.prop_y_spin.setValue(node.y())
            self.prop_y_spin.blockSignals(False)

    def update_properties_text(self, node):
        """Updates properties panel text field when node is renamed inline"""
        if node == self.selected_node:
            self.prop_text_edit.blockSignals(True)
            self.prop_text_edit.setText(node.text)
            self.prop_text_edit.blockSignals(False)

    def on_prop_text_edited(self, text):
        """Triggered in real-time as the user edits text inside the properties panel"""
        if self.selected_node:
            self.selected_node.text = text
            self.selected_node.text_item.setPlainText(text)
            self.selected_node.update_geometry()
            self.mark_dirty()

    def on_prop_coordinates_edited(self):
        """Triggered when coordinates are modified inside the properties panel"""
        if self.selected_node:
            # Block selected_node.moved signal to prevent circular update loop
            self.selected_node.moved.disconnect(self.update_properties_coordinates)
            
            x = self.prop_x_spin.value()
            y = self.prop_y_spin.value()
            self.scene.set_node_position_recursive(self.selected_node, QPointF(x, y))
            
            # Reconnect
            self.selected_node.moved.connect(self.update_properties_coordinates)
            self.mark_dirty()

    def on_prop_color_clicked(self):
        """Opens QColorDialog to select a custom color for the selected node"""
        if self.selected_node:
            initial_color = self.selected_node.get_color()
            color = QColorDialog.getColor(initial_color, self, "Select Node Color")
            if color.isValid():
                self.selected_node.custom_color = color.name()
                self.selected_node.update_geometry()
                self.selected_node.appearance_changed.emit(self.selected_node)
                self.mark_dirty()

    def on_prop_color_reset(self):
        """Resets the selected node color to its default level color"""
        if self.selected_node:
            self.selected_node.custom_color = None
            self.selected_node.update_geometry()
            self.selected_node.appearance_changed.emit(self.selected_node)
            self.mark_dirty()

    # Scene Callback Slots
    def on_scene_node_added(self):
        self.statusBar().showMessage("Node added successfully", 3000)
        self.mark_dirty()
        self.update_properties_fields()

    def on_scene_node_deleted(self):
        self.statusBar().showMessage("Node deleted successfully", 3000)
        self.mark_dirty()
        self.on_selection_changed() # Re-verify selection coordinates

    # Edit Handlers
    def add_child_node(self):
        """Action handler to add child node under selection"""
        selected = self.scene.selectedItems()
        if not selected or not isinstance(selected[0], Node):
            QMessageBox.warning(
                self, "No Selection",
                "Please select a node to add a child to."
            )
            return
            
        parent_node = selected[0]
        child = self.scene.create_child_node(parent_node)
        
        # Select the new child node
        self.scene.clearSelection()
        child.setSelected(True)

    def rename_selected_node(self):
        """Triggers text edit box on the currently selected node"""
        selected = self.scene.selectedItems()
        if selected and isinstance(selected[0], Node):
            selected[0].start_editing()

    def delete_selected_node(self):
        """Deletes currently selected node if it's not the central root node"""
        selected = self.scene.selectedItems()
        if not selected or not isinstance(selected[0], Node):
            return
            
        node = selected[0]
        if node == self.scene.root_node:
            self.statusBar().showMessage("Root node cannot be deleted.", 3000)
            return
            
        self.scene.delete_node(node)

    def on_auto_arrange(self):
        """Action handler to automatically organize the mind map layout"""
        self.scene.auto_arrange()
        if self.scene.root_node:
            self.view.centerOn(self.scene.root_node)
        self.mark_dirty()
        self.update_properties_fields()

    def center_view(self):
        """Centers viewport focus onto selected node or root node"""
        selected = self.scene.selectedItems()
        if selected and isinstance(selected[0], Node):
            self.view.centerOn(selected[0])
        elif self.scene.root_node:
            self.view.centerOn(self.scene.root_node)

    # Zoom Handlers
    def zoom_in(self):
        self.view.scale(1.15, 1.15)

    def zoom_out(self):
        self.view.scale(1.0 / 1.15, 1.0 / 1.15)

    def reset_zoom(self):
        self.view.resetTransform()

    # File Handlers
    def on_new(self):
        if self.confirm_discard_changes():
            self.current_file_path = None
            self.reset_map()

    def on_open(self):
        if not self.confirm_discard_changes():
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Mind Map", "", "Mind Map Files (*.json)"
        )
        
        if file_path:
            # Temporarily disconnect listener to avoid marking dirty on load
            try:
                self.scene.changed.disconnect(self.mark_dirty)
            except TypeError:
                pass
                
            self.selected_node = None
            success = load_mind_map(file_path, self.scene)
            
            # Reconnect listener
            self.connect_change_monitoring()
            
            if success:
                self.current_file_path = file_path
                self.is_dirty = False
                self.update_title()
                self.on_selection_changed() # Sync panels
                
                # Center view on root node
                if self.scene.root_node:
                    self.view.centerOn(self.scene.root_node)
            else:
                QMessageBox.critical(self, "Error", "Failed to load the Mind Map file.")

    def on_save(self):
        if self.current_file_path:
            success = save_mind_map(self.current_file_path, self.scene)
            if success:
                self.is_dirty = False
                self.update_title()
                self.statusBar().showMessage("Mind map saved successfully", 3000)
            else:
                QMessageBox.critical(self, "Error", "Failed to save the Mind Map.")
        else:
            self.on_save_as()

    def on_save_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Mind Map As", "", "Mind Map Files (*.json)"
        )
        
        if file_path:
            # Ensure it ends with json
            if not file_path.endswith('.json'):
                file_path += '.json'
                
            success = save_mind_map(file_path, self.scene)
            if success:
                self.current_file_path = file_path
                self.is_dirty = False
                self.update_title()
                self.statusBar().showMessage("Mind map saved successfully", 3000)
            else:
                QMessageBox.critical(self, "Error", "Failed to save the Mind Map.")

    def on_load_sample_map(self):
        """Loads a predefined structured mind map tree layout"""
        if not self.confirm_discard_changes():
            return
            
        self.current_file_path = None
        self.selected_node = None
        self.on_selection_changed()
        
        # Temporarily disconnect dirty state monitor
        try:
            self.scene.changed.disconnect(self.mark_dirty)
        except TypeError:
            pass
            
        self.scene.clear_scene()
        
        # 1. Level 0 (Central Idea)
        root = Node(text="Central Idea", x=0.0, y=0.0, parent_node=None)
        self.scene.set_root_node(root)
        
        # 2. Level 1 (Python, Mind Map, Final Project)
        python_node = self.scene.create_child_node(root, "Python", x=-240.0, y=-100.0, start_edit=False)
        mm_node = self.scene.create_child_node(root, "Mind Map", x=240.0, y=-100.0, start_edit=False)
        fp_node = self.scene.create_child_node(root, "Final Project", x=0.0, y=170.0, start_edit=False)
        
        # 3. Level 2 under Python (PyQt5, JSON)
        self.scene.create_child_node(python_node, "PyQt5", x=-460.0, y=-150.0, start_edit=False)
        self.scene.create_child_node(python_node, "JSON", x=-460.0, y=-50.0, start_edit=False)
        
        # 4. Level 2 under Mind Map (Nodes, Edges)
        self.scene.create_child_node(mm_node, "Nodes", x=460.0, y=-150.0, start_edit=False)
        self.scene.create_child_node(mm_node, "Edges", x=460.0, y=-50.0, start_edit=False)
        
        # 5. Level 2 under Final Project (Report, Source Code)
        self.scene.create_child_node(fp_node, "Report", x=-180.0, y=260.0, start_edit=False)
        self.scene.create_child_node(fp_node, "Source Code", x=180.0, y=260.0, start_edit=False)
        
        # Reconnect listener
        self.connect_change_monitoring()
        
        # Reset scale zoom and viewport center
        self.view.resetTransform()
        self.view.centerOn(root)
        
        self.is_dirty = True
        self.update_title()
        self.statusBar().showMessage("Sample map loaded successfully.", 3000)

    def on_export_png(self):
        """Renders the bounding area of the mind map nodes into a PNG image file"""
        if not self.scene.nodes:
            QMessageBox.warning(self, "Warning", "Cannot export an empty map.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Mind Map as PNG", "", "PNG Images (*.png)"
        )
        
        if file_path:
            if not file_path.endswith('.png'):
                file_path += '.png'
                
            # Temporarily deselect all nodes so selection borders don't appear in export
            selected_items = self.scene.selectedItems()
            self.scene.clearSelection()
            
            # Find bounds of all elements in the scene
            rect = self.scene.itemsBoundingRect()
            
            # Add padding
            padding = 30
            rect.adjust(-padding, -padding, padding, padding)
            
            # Setup output QImage
            image = QImage(rect.size().toSize(), QImage.Format_ARGB32)
            
            # Match background color based on theme
            bg_color = QColor("#0f172a") if self.current_theme == "dark" else QColor("#ffffff")
            image.fill(bg_color)
            
            # Paint scene elements onto the image
            painter = QPainter(image)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setRenderHint(QPainter.TextAntialiasing, True)
            
            self.scene.render(painter, QRectF(image.rect()), rect)
            painter.end()
            
            # Save to file
            success = image.save(file_path)
            
            # Restore selection
            for item in selected_items:
                item.setSelected(True)
                
            if success:
                self.statusBar().showMessage(f"Exported to {os.path.basename(file_path)}", 3000)
            else:
                QMessageBox.critical(self, "Error", "Failed to export image.")

    def show_statistics(self):
        """Displays a dialog containing detailed structural statistics of the mind map"""
        from PyQt5.QtWidgets import QDialog, QFormLayout, QDialogButtonBox
        
        # Calculate stats
        total_nodes = len(self.scene.nodes)
        total_connections = max(0, total_nodes - 1)
        
        max_depth = 0
        if self.scene.nodes:
            max_depth = max(node.get_level() for node in self.scene.nodes.values())
            
        avg_children = 0.0
        if total_nodes > 0:
            total_children = sum(len(node.child_nodes) for node in self.scene.nodes.values())
            avg_children = total_children / total_nodes
            
        dialog = QDialog(self)
        dialog.setWindowTitle("Mind Map Statistics")
        dialog.setFixedWidth(300)
        
        # Responsive color variables matching current theme
        is_dark = self.current_theme == "dark"
        bg_color = "#1e293b" if is_dark else "#ffffff"
        text_color = "#e2e8f0" if is_dark else "#334155"
        header_color = "#f8fafc" if is_dark else "#0f172a"
        border_color = "#334155" if is_dark else "#e2e8f0"
        
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_color};
                font-family: "Inter", "Segoe UI", sans-serif;
            }}
            QLabel {{
                font-size: 10pt;
                color: {text_color};
            }}
            QLabel[header="true"] {{
                font-weight: bold;
                font-size: 11pt;
                color: {header_color};
                border-bottom: 1px solid {border_color};
                padding-bottom: 6px;
            }}
            QPushButton {{
                background-color: #3B82F6;
                color: white;
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: 500;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #2563EB;
            }}
        """)
        
        layout = QFormLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        header = QLabel("Structural Metrics")
        header.setProperty("header", "true")
        layout.addRow(header)
        layout.addRow("", QLabel(""))  # spacing
        
        layout.addRow("Total Nodes:", QLabel(str(total_nodes)))
        layout.addRow("Total Connections:", QLabel(str(total_connections)))
        layout.addRow("Maximum Depth:", QLabel(str(max_depth)))
        layout.addRow("Average Children:", QLabel(f"{avg_children:.2f}"))
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addRow("", QLabel(""))  # spacing
        layout.addRow(buttons)
        
        dialog.exec_()

    def set_theme(self, theme):
        """Switches the application appearance theme between Light and Dark modes."""
        self.current_theme = theme
        
        if theme == "dark":
            # Dark Theme Stylesheet
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #0f172a;
                }
                QMenuBar {
                    background-color: #1e293b;
                    color: #f8fafc;
                    border-bottom: 1px solid #334155;
                    padding: 4px;
                    font-family: "Inter", "Segoe UI", sans-serif;
                    font-size: 10pt;
                }
                QMenuBar::item {
                    background-color: transparent;
                    padding: 4px 10px;
                    border-radius: 4px;
                }
                QMenuBar::item:selected {
                    background-color: #334155;
                }
                QMenu {
                    background-color: #1e293b;
                    color: #f8fafc;
                    border: 1px solid #334155;
                    border-radius: 6px;
                    padding: 4px;
                }
                QMenu::item {
                    padding: 6px 20px;
                }
                QMenu::item:selected {
                    background-color: #334155;
                    color: #ffffff;
                }
                QMenu::separator {
                    height: 1px;
                    background-color: #334155;
                    margin: 4px 8px;
                }
                QToolBar {
                    background-color: #1e293b;
                    border-bottom: 1px solid #334155;
                    spacing: 8px;
                    padding: 6px;
                }
                QToolButton {
                    background-color: #0f172a;
                    border: 1px solid #334155;
                    border-radius: 4px;
                    padding: 5px 10px;
                    color: #e2e8f0;
                    font-family: "Inter", "Segoe UI", sans-serif;
                    font-size: 9pt;
                    font-weight: 500;
                }
                QToolButton:hover {
                    background-color: #334155;
                    border-color: #475569;
                }
                QToolButton:pressed {
                    background-color: #475569;
                }
                QStatusBar {
                    background-color: #1e293b;
                    border-top: 1px solid #334155;
                    color: #94a3b8;
                    font-family: "Inter", "Segoe UI", sans-serif;
                    font-size: 9pt;
                }
            """)
            
            # Update Properties Panel stylesheet for Dark Theme
            self.prop_panel.setStyleSheet("""
                QFrame#propPanel {
                    background-color: #1e293b;
                    border-left: 1px solid #334155;
                }
                QLabel#propTitle {
                    font-weight: bold;
                    font-size: 11pt;
                    color: #f8fafc;
                    border-bottom: 2px solid #334155;
                    padding-bottom: 8px;
                    margin-bottom: 12px;
                }
                QLabel {
                    color: #94a3b8;
                    font-size: 9pt;
                    font-weight: 500;
                }
                QLineEdit, QDoubleSpinBox {
                    background-color: #0f172a;
                    border: 1px solid #334155;
                    border-radius: 4px;
                    padding: 6px;
                    color: #f8fafc;
                    font-size: 10pt;
                }
                QLineEdit:focus, QDoubleSpinBox:focus {
                    background-color: #0f172a;
                    border: 1px solid #3B82F6;
                }
                QLineEdit:disabled, QDoubleSpinBox:disabled {
                    background-color: #1e293b;
                    color: #64748b;
                }
                QPushButton {
                    background-color: #334155;
                    color: #f8fafc;
                    border: 1px solid #475569;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #475569;
                }
            """)
            
            # Update Scene Colors for Dark Theme
            self.scene.setBackgroundBrush(QColor("#0f172a"))
            
        else:
            # Light Theme Stylesheet
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f8fafc;
                }
                QMenuBar {
                    background-color: #ffffff;
                    color: #000000;
                    border-bottom: 1px solid #e2e8f0;
                    padding: 4px;
                    font-family: "Inter", "Segoe UI", sans-serif;
                    font-size: 10pt;
                }
                QMenuBar::item {
                    background-color: transparent;
                    padding: 4px 10px;
                    border-radius: 4px;
                }
                QMenuBar::item:selected {
                    background-color: #f1f5f9;
                }
                QMenu {
                    background-color: #ffffff;
                    color: #334155;
                    border: 1px solid #e2e8f0;
                    border-radius: 6px;
                    padding: 4px;
                }
                QMenu::item {
                    padding: 6px 20px;
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
                QToolBar {
                    background-color: #ffffff;
                    border-bottom: 1px solid #e2e8f0;
                    spacing: 8px;
                    padding: 6px;
                }
                QToolButton {
                    background-color: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 4px;
                    padding: 5px 10px;
                    color: #334155;
                    font-family: "Inter", "Segoe UI", sans-serif;
                    font-size: 9pt;
                    font-weight: 500;
                }
                QToolButton:hover {
                    background-color: #f1f5f9;
                    border-color: #cbd5e1;
                }
                QToolButton:pressed {
                    background-color: #e2e8f0;
                }
                QStatusBar {
                    background-color: #ffffff;
                    border-top: 1px solid #e2e8f0;
                    color: #64748b;
                    font-family: "Inter", "Segoe UI", sans-serif;
                    font-size: 9pt;
                }
            """)
            
            # Update Properties Panel stylesheet for Light Theme
            self.prop_panel.setStyleSheet("""
                QFrame#propPanel {
                    background-color: #ffffff;
                    border-left: 1px solid #e2e8f0;
                }
                QLabel#propTitle {
                    font-weight: bold;
                    font-size: 11pt;
                    color: #0f172a;
                    border-bottom: 2px solid #f1f5f9;
                    padding-bottom: 8px;
                    margin-bottom: 12px;
                }
                QLabel {
                    color: #64748b;
                    font-size: 9pt;
                    font-weight: 500;
                }
                QLineEdit, QDoubleSpinBox {
                    background-color: #f8fafc;
                    border: 1px solid #cbd5e1;
                    border-radius: 4px;
                    padding: 6px;
                    color: #334155;
                    font-size: 10pt;
                }
                QLineEdit:focus, QDoubleSpinBox:focus {
                    background-color: #ffffff;
                    border: 1px solid #3B82F6;
                }
                QLineEdit:disabled, QDoubleSpinBox:disabled {
                    background-color: #f1f5f9;
                    color: #94a3b8;
                }
                QPushButton {
                    background-color: #f1f5f9;
                    color: #334155;
                    border: 1px solid #cbd5e1;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #e2e8f0;
                }
            """)
            
            # Update Scene Colors for Light Theme
            self.scene.setBackgroundBrush(QColor("#ffffff"))
            
        # Update node geometries and redraw edges to adapt to new theme colors
        for node in self.scene.nodes.values():
            node.update_geometry()
            node.update_edges()

    def on_about(self):
        """Triggers helper informational modal window"""
        QMessageBox.about(
            self, "About Mind Map Application",
            "<h3>Mind Map Application</h3>"
            "<p>A beautiful, stable and highly interactive desktop mind-mapping application built with Python and PyQt5.</p>"
            "<p>Developed for the Python Course Final Project.</p>"
            "<p><b>Key Operations:</b></p>"
            "<ul>"
            "<li><b>F2</b>: Rename selected node</li>"
            "<li><b>Delete</b>: Delete selected sub-tree node</li>"
            "<li><b>Ctrl+Mouse Wheel</b> or <b>Ctrl++/Ctrl+-</b>: Canvas zoom</li>"
            "<li><b>Left Mouse Click-Drag</b>: Canvas scroll/pan</li>"
            "</ul>"
        )

    def closeEvent(self, event):
        """Prompt to save changes before exiting"""
        if self.confirm_discard_changes():
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    # Support high DPI displays
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # Set app-wide font style
    app.setFont(QFont("Inter", 10))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
