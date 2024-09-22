from PyQt6.QtWidgets import (
    QHBoxLayout, QDialog, QFormLayout, QLineEdit,
    QPushButton, QFileDialog, QLabel, 
)


class ConfigDialog(QDialog):
    def __init__(self, current_root, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration")
        self.setGeometry(400, 400, 400, 100)
        self.current_root = current_root
        self.new_root = current_root
        self.initUI()
    
    def initUI(self):
        layout = QFormLayout()

        # Game Root Folder
        self.root_label = QLabel("Game Root Folder:")
        self.root_display = QLineEdit(self.current_root)
        self.root_display.setReadOnly(True)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_folder)
        
        root_layout = QHBoxLayout()
        root_layout.addWidget(self.root_display)
        root_layout.addWidget(self.browse_button)
        layout.addRow(self.root_label, root_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addRow(button_layout)

        self.setLayout(layout)    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Game Root Folder", self.current_root)
        if folder:
            self.new_root = folder
            self.root_display.setText(folder)
    
    def get_new_root(self):
        return self.new_root
