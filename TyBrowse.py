import sys
import os
import json
import re
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *

print("Running Tybrowse version 2.1.0")

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.config = self.load_config()
        self.history = self.load_history()

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_current_tab)

        self.apply_theme()
        self.apply_font()

        self.sidebar = QListWidget()
        self.sidebar.setMaximumWidth(250)
        self.sidebar.setMinimumWidth(150)
        self.sidebar.itemClicked.connect(self.open_bookmarked_url)

        self.splitter = QSplitter()
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.tab_widget)
        self.setCentralWidget(self.splitter)

        nav = QToolBar()
        self.addToolBar(nav)

        nav.addAction(QAction('Back', self, triggered=lambda:self.current_browser().back()))
        nav.addAction(QAction('Forward', self, triggered=lambda:self.current_browser().forward()))
        nav.addAction(QAction('Reload', self, triggered=lambda:self.current_browser().reload()))

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.load_url)
        nav.addWidget(self.url_bar)

        nav.addAction(QAction('New Tab', self, triggered=lambda:self.create_new_tab(self.config.get("default_search", "https://www.google.com/search?q={query}").replace("{query}", ""))))
        nav.addAction(QAction('Bookmark', self, triggered=self.save_bookmark))
        nav.addAction(QAction('Settings', self, triggered=self.open_settings_tab))
        nav.addAction(QAction('Toggle History', self, triggered=self.toggle_sidebar))

        self.setWindowTitle("Tybrowse - version 2.1.0")
        self.setGeometry(100, 100, 1400, 900)

        self.load_bookmarks_and_history()
        self.create_new_tab(self.config.get("default_search", "https://www.google.com/search?q={query}").replace("{query}", ""))

    def load_config(self):
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                return json.load(f)
        return {"theme": "light", "font": "Arial", "adblock": True, "bookmarks": [], "default_search": "https://www.google.com/search?q={query}"}

    def save_config(self):
        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=4)

    def load_history(self):
        if os.path.exists("history.json"):
            with open("history.json", "r") as f:
                return json.load(f)
        return []

    def save_history(self):
        with open("history.json", "w") as f:
            json.dump(self.history, f, indent=4)

    def apply_theme(self):
        if self.config.get("theme") == "dark":
            self.setStyleSheet("background:#2e2e2e;color:white;")
            self.tab_widget.setStyleSheet("QTabBar::tab{background:#333;color:white;}")
        else:
            self.setStyleSheet("")
            self.tab_widget.setStyleSheet("")

    def apply_font(self):
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/arial.ttf")
        app.setFont(QFont(self.config.get("font", "Arial"), 10))

    def toggle_sidebar(self):
        self.sidebar.setVisible(not self.sidebar.isVisible())

    def open_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Theme settings
        theme_grp = QGroupBox("Appearance")
        theme_layout = QVBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        theme_cb = QComboBox()
        theme_cb.addItems(["light", "dark"])
        theme_cb.setCurrentText(self.config.get("theme", "light"))
        theme_cb.currentTextChanged.connect(self.update_theme)
        theme_layout.addWidget(theme_cb)

        theme_layout.addWidget(QLabel("Font:"))
        font_cb = QFontComboBox()
        font_cb.setCurrentFont(QFont(self.config.get("font", "Arial")))
        font_cb.currentFontChanged.connect(self.update_font)
        theme_layout.addWidget(font_cb)

        font_note = QLabel("A restart is needed to apply this setting.")
        font_note.setStyleSheet("color: gray; font-size: 11px;")
        theme_layout.addWidget(font_note)

        theme_grp.setLayout(theme_layout)
        layout.addWidget(theme_grp)

        # Default search engine dropdown
        search_grp = QGroupBox("Search Engine")
        search_layout = QVBoxLayout()
        search_layout.addWidget(QLabel("Default Search Engine:"))
        self.search_cb = QComboBox()
        engines = {
            "Google": "https://www.google.com/search?q={query}",
            "DuckDuckGo": "https://duckduckgo.com/?q={query}",
            "Bing": "https://www.bing.com/search?q={query}",
            "Yahoo": "https://search.yahoo.com/search?p={query}",
            "Brave": "https://search.brave.com/search?q={query}"
        }
        self.engine_map = engines
        self.search_cb.addItems(engines.keys())

        current_engine = self.config.get("default_search", "")
        for name, url in engines.items():
            if url == current_engine:
                self.search_cb.setCurrentText(name)
                break

        search_layout.addWidget(self.search_cb)
        save_btn = QPushButton("Save Search Engine")
        save_btn.clicked.connect(self.save_search_engine)
        search_layout.addWidget(save_btn)
        search_grp.setLayout(search_layout)
        layout.addWidget(search_grp)

        # Dev tools
        dev_grp = QGroupBox("Developer Tools")
        dev_layout = QVBoxLayout()
        dev_btn = QPushButton("Open Python Console")
        dev_btn.clicked.connect(lambda: os.system("start cmd"))
        dev_layout.addWidget(dev_btn)
        dev_grp.setLayout(dev_layout)
        layout.addWidget(dev_grp)

        layout.addStretch()
        i = self.tab_widget.addTab(tab, "Settings")
        self.tab_widget.setCurrentIndex(i)

    def save_search_engine(self):
        engine_name = self.search_cb.currentText()
        self.config["default_search"] = self.engine_map[engine_name]
        self.save_config()

    def update_theme(self, t):
        self.config["theme"] = t
        self.apply_theme()
        self.save_config()

    def update_font(self, font):
        self.config["font"] = font.family()
        self.save_config()

    def create_new_tab(self, url):
        view = QWebEngineView()
        view.setUrl(QUrl(url))
        idx = self.tab_widget.addTab(view, "Loading...")
        self.tab_widget.setCurrentIndex(idx)
        view.titleChanged.connect(lambda title: self.update_tab_title(idx, title))
        view.urlChanged.connect(self.on_url_changed)
        self.log_page_visit(url)

    def update_tab_title(self, i, t):
        self.tab_widget.setTabText(i, t)

    def on_url_changed(self, qurl):
        u = qurl.toString()
        self.url_bar.setText(u)
        self.log_page_visit(u)

    def log_page_visit(self, url):
        if url and (not self.history or self.history[-1] != url):
            self.history.append(url)
            self.save_history()
            self.load_bookmarks_and_history()

    def save_bookmark(self):
        url = self.url_bar.text()
        if url and url not in self.config["bookmarks"]:
            self.config["bookmarks"].append(url)
            self.save_config()
            self.load_bookmarks_and_history()

    def load_bookmarks_and_history(self):
        self.sidebar.clear()
        self.sidebar.addItem("Bookmarks")
        for b in self.config.get("bookmarks", []):
            self.sidebar.addItem("★ " + b)
        self.sidebar.addItem("History")
        for h in reversed(self.history[-50:]):
            self.sidebar.addItem(h)

    def open_bookmarked_url(self, item):
        txt = item.text().lstrip("★ ")
        if txt not in ("Bookmarks", "History"):
            self.create_new_tab(txt)

    def close_current_tab(self, idx):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(idx)
        else:
            self.close()

    def current_browser(self):
        w = self.tab_widget.currentWidget()
        return w if isinstance(w, QWebEngineView) else w

    def load_url(self):
        u = self.url_bar.text().strip()
        if re.match(r'^(http|https)://', u):
            self.create_new_tab(u)
        else:
            search_url = self.config.get("default_search", "https://www.google.com/search?q={query}")
            full_url = search_url.replace("{query}", QUrl.toPercentEncoding(u).data().decode())
            self.create_new_tab(full_url)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    browser = Browser()
    browser.show()
    sys.exit(app.exec_())
