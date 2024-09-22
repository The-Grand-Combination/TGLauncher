
import json
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, 
    QPushButton, QTreeWidget, QTreeWidgetItem,
    QDialog, QInputDialog, QMessageBox
)


class PresetManagerDialog(QDialog):
    def __init__(self, checked_mods, settings_file, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Presets")
        self.setGeometry(400, 400, 300, 400)
        self.checked_mods = checked_mods
        self.settings_file = settings_file
        self.settings = {}
        self.load_settings()
        self.initUI()

        self.preset_list.itemClicked.connect(self.load_selected_preset)

    def initUI(self):
        layout = QVBoxLayout()

        # List of presets
        self.preset_list = QTreeWidget()
        self.preset_list.setHeaderLabel("Presets")
        self.populate_preset_list()
        layout.addWidget(self.preset_list)

        # Buttons layout
        buttons_layout = QHBoxLayout()

        # Delete preset button
        self.delete_button = QPushButton("Delete Preset")
        self.delete_button.clicked.connect(self.delete_selected_preset)
        buttons_layout.addWidget(self.delete_button)

        layout.addLayout(buttons_layout)

        # New preset button
        self.new_preset_button = QPushButton("Save current as New Preset")
        self.new_preset_button.clicked.connect(self.create_new_preset)
        layout.addWidget(self.new_preset_button)

        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)

        self.setLayout(layout)

    def load_settings(self):
        """Loads the settings file, including presets."""
        try:
            with open(self.settings_file, 'r') as f:
                self.settings = json.load(f)
                if 'presets' not in self.settings:
                    self.settings['presets'] = {}
        except FileNotFoundError:
            self.settings = {'presets': {}}
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = {'presets': {}}

    def populate_preset_list(self):
        """Populates the preset list widget with existing presets."""
        self.preset_list.clear()
        for preset_name in self.settings['presets']:
            item = QTreeWidgetItem()
            item.setText(0, preset_name)
            self.preset_list.addTopLevelItem(item)

    def load_selected_preset(self):
        selected_item = self.preset_list.currentItem()
        if selected_item:
            preset_name = selected_item.text(0)
            self.checked_mods[:] = self.settings['presets'][preset_name]
            print(f"Loaded preset: {preset_name}")
            # Optionally, update the mod tree in the main window here
            self.parent().set_checked_mods(self.checked_mods)  # Update the main window's checked mods


    def delete_selected_preset(self):
        """Deletes the selected preset."""
        selected_item = self.preset_list.currentItem()
        if selected_item:
            preset_name = selected_item.text(0)
            reply = QMessageBox.question(
                self, 'Delete Preset', f"Are you sure you want to delete the preset '{preset_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                del self.settings['presets'][preset_name]
                self.save_settings()
                self.populate_preset_list()
                print(f"Deleted preset: {preset_name}")

    def create_new_preset(self):
        """Creates a new preset with the currently checked mods."""
        preset_name, ok = QInputDialog.getText(self, 'New Preset', 'Enter preset name:')
        if ok and preset_name:
            self.settings['presets'][preset_name] = list(self.checked_mods)
            self.save_settings()
            self.populate_preset_list()
            print(f"Saved new preset: {preset_name}")

    def save_settings(self):
        """Saves the presets to the settings file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving presets: {e}")
