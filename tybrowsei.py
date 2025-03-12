import sys
import re
import os
import json
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *

print("running pybrowse version 1.7")

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        font = QFont("Montserrat")
        app.setFont(font)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tab_widget)

        self.logs_display = QTextEdit()
        self.logs_display.setReadOnly(True)
        
        self.create_new_tab("https://www.google.com")

        nav_bar = QToolBar()
        self.addToolBar(nav_bar)

        # Navigation buttons
        back_btn = QAction('Back', self)
        back_btn.triggered.connect(lambda: self.current_browser().back())
        nav_bar.addAction(back_btn)

        forward_btn = QAction('Forward', self)
        forward_btn.triggered.connect(lambda: self.current_browser().forward())
        nav_bar.addAction(forward_btn)

        reload_btn = QAction('Reload', self)
        reload_btn.triggered.connect(lambda: self.current_browser().reload())
        nav_bar.addAction(reload_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.load_url)
        nav_bar.addWidget(self.url_bar)

        new_tab_btn = QAction('New Tab', self)
        new_tab_btn.triggered.connect(lambda: self.create_new_tab("https://www.google.com"))
        nav_bar.addAction(new_tab_btn)

        fullscreen_btn = QAction('Fullscreen', self)
        fullscreen_btn.triggered.connect(self.toggle_fullscreen)
        nav_bar.addAction(fullscreen_btn)

        menu_btn = QAction('Developer Menu', self)
        menu_btn.triggered.connect(self.toggle_menu)
        nav_bar.addAction(menu_btn)

        # Add extension manager button
        extensions_btn = QAction('Extensions', self)
        extensions_btn.triggered.connect(self.open_extension_manager)
        nav_bar.addAction(extensions_btn)

        # Extension manager
        self.extension_manager = QWidget()
        self.extension_layout = QVBoxLayout(self.extension_manager)
        self.extension_manager.setLayout(self.extension_layout)

        self.extension_list = QListWidget()
        self.extension_layout.addWidget(self.extension_list)

        # Developer Mode Checkbox
        self.dev_mode_checkbox = QCheckBox("Enable Developer Mode", self)
        self.dev_mode_checkbox.stateChanged.connect(self.toggle_dev_mode)
        self.extension_layout.addWidget(self.dev_mode_checkbox)

        # Load Unpacked Extension Button (visible only in Developer Mode)
        self.load_unpacked_btn = QPushButton("Load Unpacked Extension", self)
        self.load_unpacked_btn.setVisible(False)
        self.load_unpacked_btn.clicked.connect(self.load_unpacked_extension)
        self.extension_layout.addWidget(self.load_unpacked_btn)

        # Extension manager dialog
        self.extension_manager_dialog = QDialog(self)
        self.extension_manager_dialog.setWindowTitle("Extension Manager")
        self.extension_manager_dialog.setLayout(self.extension_layout)

        self.load_extensions()

        self.menu_widget = QWidget()
        self.menu_layout = QVBoxLayout()
        self.menu_widget.setLayout(self.menu_layout)
        self.menu_widget.setFixedWidth(250)

        self.python_console_btn = QPushButton("Open Python Console")
        self.python_console_btn.clicked.connect(self.open_python_console)
        self.menu_layout.addWidget(self.python_console_btn)
        
        self.menu_layout.addWidget(self.logs_display)

        self.menu_dock = QDockWidget("Menu", self)
        self.menu_dock.setWidget(self.menu_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.menu_dock)
        self.menu_dock.setVisible(False)

        self.setWindowTitle("Tybrowse - beta 1.7")
        self.setGeometry(100, 100, 1200, 800)
        self.is_fullscreen = False
        self.log_action("running tybrowse 1.7(beta)")

    def create_new_tab(self, url):
        new_tab = QWidget()
        new_tab_layout = QVBoxLayout(new_tab)
        new_tab.setLayout(new_tab_layout)

        browser_view = QWebEngineView()
        self.enable_html5_features(browser_view)
        browser_view.setUrl(QUrl(url))
        
        # Set custom user agent
        custom_user_agent = "TYBrowse-beta/1.7 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        browser_view.page().profile().setHttpUserAgent(custom_user_agent)
        
        new_tab_layout.addWidget(browser_view)

        index = self.tab_widget.addTab(new_tab, "Loading...")
        self.tab_widget.setCurrentIndex(index)

        browser_view.titleChanged.connect(lambda title: self.update_tab_title(index, title))
        browser_view.urlChanged.connect(lambda qurl: self.update_url_bar(qurl))

        self.log_action(f"User visited {url}")

    def enable_html5_features(self, browser_view):
        settings = browser_view.settings()
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)

    def update_tab_title(self, index, title):
        self.tab_widget.setTabText(index, title)

    def update_url_bar(self, qurl):
        self.url_bar.setText(qurl.toString())
        self.log_action(f"Loading {qurl.toString()}")

    def load_url(self):
        url = self.url_bar.text().strip()

        if ' ' in url:
            url = "https://www.google.com/search?q=" + '+'.join(url.split())
        elif re.match(r'^[a-zA-Z0-9-]+\.[a-zA-Z]{2,}', url):
            if not (url.startswith("http://") or url.startswith("https://")):
                url = "https://" + url
        else:
            url = "https://www.google.com/search?q=" + url

        self.current_browser().setUrl(QUrl(url))

    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.showNormal()
            self.setCursor(Qt.ArrowCursor)
        else:
            self.showFullScreen()
            self.setCursor(Qt.BlankCursor)
        self.is_fullscreen = not self.is_fullscreen

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_E and self.is_fullscreen:
            self.toggle_fullscreen()

    def current_browser(self):
        current_index = self.tab_widget.currentIndex()
        if current_index != -1:
            return self.tab_widget.widget(current_index).layout().itemAt(0).widget()
        return None

    def close_current_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            self.close()

    def toggle_menu(self):
        self.menu_dock.setVisible(not self.menu_dock.isVisible())
        self.log_action("Menu toggled")

    def open_python_console(self):
        self.log_action("Opened Python console")
        console = QDialog(self)
        console.setWindowTitle("Python Console")
        console_layout = QVBoxLayout()
        console.setLayout(console_layout)

        text_area = QTextEdit()
        text_area.setReadOnly(True)
        text_area.setPlainText("Python Console Opened.")
        console_layout.addWidget(text_area)

        console.show()

    def log_action(self, message):
        self.logs_display.append(message)

    def open_extension_manager(self):
        self.extension_manager_dialog.show()

    def load_extensions(self):
        # Simulating loading extensions from a folder
        extension_dir = "extensions"
        if not os.path.exists(extension_dir):
            os.makedirs(extension_dir)

        extension_files = [f for f in os.listdir(extension_dir) if f.endswith(".json")]
        for ext_file in extension_files:
            with open(os.path.join(extension_dir, ext_file)) as f:
                ext_data = json.load(f)
                item = QListWidgetItem(ext_data["name"])
                self.extension_list.addItem(item)

    def toggle_dev_mode(self):
        # Show or hide the button to load unpacked extensions
        if self.dev_mode_checkbox.isChecked():
            self.load_unpacked_btn.setVisible(True)
        else:
            self.load_unpacked_btn.setVisible(False)

    def load_unpacked_extension(self):
        # Let the user select an unpacked extension folder
        folder = QFileDialog.getExistingDirectory(self, "Select Unpacked Extension Folder")
        if folder:
            # Here we would handle the unpacked extension, assuming the extension is a valid folder with necessary files.
            extension_name = os.path.basename(folder)
            item = QListWidgetItem(extension_name)
            self.extension_list.addItem(item)
            self.log_action(f"Loaded unpacked extension: {extension_name}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    browser = Browser()
    browser.show()
    sys.exit(app.exec_())
