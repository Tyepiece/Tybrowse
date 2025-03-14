import sys
import os
import json
import re
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import Qt

print("Running Tybrowse version 2.0.0")

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize the splash screen
        self.splash = QSplashScreen(QPixmap("earth.ico"))
        self.splash.show()
        QTimer.singleShot(1000, lambda: self.splash.finish(self))

        # Tab widget initialization
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tab_widget)

        # Sidebar for bookmarks and history
        self.sidebar = QListWidget()
        self.sidebar.setMaximumWidth(250)
        self.sidebar.setMinimumWidth(150)

        # Load config and apply settings
        self.config = self.load_config()
        self.apply_theme()
        self.apply_font()

        self.splitter = QSplitter()
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.tab_widget)
        self.setCentralWidget(self.splitter)

        # Navigation Bar
        nav_bar = QToolBar()
        self.addToolBar(nav_bar)

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

        settings_btn = QAction('Settings', self)
        settings_btn.triggered.connect(self.open_settings_tab)
        nav_bar.addAction(settings_btn)

        self.setWindowTitle("Tybrowse - version 2.0.0")
        self.setGeometry(100, 100, 1400, 900)

        # Load history and bookmarks
        self.load_bookmarks_and_history()

        # Create initial tab
        self.create_new_tab("https://www.google.com")

    def load_config(self):
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                return json.load(f)
        else:
            return {"theme": "light", "font": "Arial", "adblock": True, "bookmarks": [], "history": []}

    def save_config(self):
        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=4)

    def apply_theme(self):
        theme = self.config["theme"]
        if theme == "dark":
            self.setStyleSheet("background-color: #2e2e2e; color: white;")
            self.tab_widget.setStyleSheet("QTabBar::tab { background-color: #333; color: white; }")
        else:
            self.setStyleSheet("background-color: white; color: black;")
            self.tab_widget.setStyleSheet("QTabBar::tab { background-color: white; color: black; }")

    def apply_font(self):
        font = QFont(self.config["font"], 10)
        app.setFont(font)

    def open_settings_tab(self):
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)

        theme_label = QLabel("Select Theme:")
        settings_layout.addWidget(theme_label)
        theme_select = QComboBox()
        theme_select.addItems(["light", "dark"])
        theme_select.setCurrentText(self.config["theme"])
        theme_select.currentTextChanged.connect(self.update_theme)
        settings_layout.addWidget(theme_select)

        python_console_btn = QPushButton("Open Python Console", self)
        python_console_btn.clicked.connect(self.open_python_console)
        settings_layout.addWidget(python_console_btn)

        index = self.tab_widget.addTab(settings_tab, "Settings")
        self.tab_widget.setCurrentIndex(index)

    def open_python_console(self):
        os.system("start cmd")

    def update_theme(self, theme):
        self.config["theme"] = theme
        self.apply_theme()
        self.save_config()

    def create_new_tab(self, url):
        browser_view = QWebEngineView()
        browser_view.setUrl(QUrl(url))
        index = self.tab_widget.addTab(browser_view, "Loading...")
        self.tab_widget.setCurrentIndex(index)
        browser_view.titleChanged.connect(lambda title: self.update_tab_title(index, title))
        browser_view.urlChanged.connect(lambda qurl: self.update_url_bar(qurl))

    def save_bookmark(self):
        url = self.url_bar.text()
        if url and url not in self.config["bookmarks"]:
            self.config["bookmarks"].append(url)
            self.save_config()
            self.load_bookmarks_and_history()

    def load_bookmarks_and_history(self):
        self.sidebar.clear()
        self.sidebar.addItem("Bookmarks")
        self.sidebar.addItems(self.config["bookmarks"])
        self.sidebar.addItem("History")
        self.sidebar.addItems(self.config["history"])

    def open_bookmarked_url(self, item):
        url = item.text()
        if url and url != "Bookmarks" and url != "History":
            self.create_new_tab(url)

    def update_tab_title(self, index, title):
        self.tab_widget.setTabText(index, title)

    def update_url_bar(self, qurl):
        self.url_bar.setText(qurl.toString())
        if qurl.toString() not in self.config["history"]:
            self.config["history"].append(qurl.toString())
            self.save_config()

    def close_current_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            self.close()

    def current_browser(self):
        current_index = self.tab_widget.currentIndex()
        if current_index != -1:
            return self.tab_widget.widget(current_index)
        return None

    def load_url(self):
        url = self.url_bar.text().strip()
        if self.is_valid_url(url):
            self.create_new_tab(url)
        else:
            search_query = self.format_search_query(url)
            self.create_new_tab(search_query)

    def is_valid_url(self, url):
        return re.match(r'^(http|https)://', url) is not None

    def format_search_query(self, query):
        return f"https://www.google.com/search?q={query}"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    browser = Browser()
    browser.show()
    sys.exit(app.exec_())
