import sys

from PyQt4.QtGui import QApplication, QTableWidget, QTableWidgetItem
from PyQt4.QtCore import QUrl
from PyQt4.QtWebKit import QWebView, QWebPage, QWebSettings
from PyQt4.QtGui import QGridLayout, QLineEdit, QWidget, QHeaderView
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkProxy

# not sure if this works yet
class ProxySettings(QNetworkProxy):
    def __init__(self, host, port):
        super(ProxySettings, self).__init__()
        self.host = host
        self.port = port

    def _enable_proxy(self):
        QNetworkProxy.setType(3)
        QNetworkProxy.HttpProxy("") #proxy setting here


class UrlBar(QLineEdit):
    def __init__(self, browser):
        super(UrlBar, self).__init__()
        self.browser = browser
        self.returnPressed.connect(self._return_pressed)

    def _return_pressed(self):
        url = QUrl(self.text())
        browser.load(url)


class JavaScriptEvaluator(QLineEdit):
    def __init__(self, page):
        super(JavaScriptEvaluator, self).__init__()
        self.page = page
        self.returnPressed.connect(self._return_pressed)

    def _return_pressed(self):
        frame = self.page.currentFrame()
        result = frame.evaluateJavaScript(self.text())

class ActionInputBox(QLineEdit):
    def __init__(self, page):
        super(ActionInputBox, self).__init__()
        self.page = page
        self.returnPressed.connect(self._return_pressed)

    def _return_pressed(self):
        frame = self.page.currentFrame()
        action_string = str(self.text()).lower()
        if action_string == "b":
            self.page.triggerAction(QWebPage.Back)
        elif action_string == "f":
            self.page.triggerAction(QWebPage.Forward)
        elif action_string == "s":
            self.page.triggerAction(QWebPage.Stop)
        elif action_string == "r":
            self.page.triggerAction(QWebPage.Reload)


class RequestsTable(QTableWidget):
    header = ["url", "status", "content-type"]

    def __init__(self):
        super(RequestsTable, self).__init__()
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(self.header)
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setResizeMode(QHeaderView.ResizeToContents)

    def update(self, data):
        last_row = self.rowCount()
        next_row = last_row + 1
        self.setRowCount(next_row)
        for col, dat in enumerate(data, 0):
            if not dat:
                continue
            self.setItem(last_row, col, QTableWidgetItem(dat))

class NetworkManager(QNetworkAccessManager):
    def __init__(self, table):
        QNetworkAccessManager.__init__(self)
        self.finished.connect(self._finished)
        self.table = table

    def _finished(self, reply):
        headers = reply.rawHeaderPairs()
        headers = {str(k):str(v) for k,v in headers}
        content_type = headers.get("Content-Type")
        url = reply.url().toString()
        status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        status, ok = status.toInt()
        self.table.update([url, str(status), content_type])


if __name__ == "__main__":
    app = QApplication(["AutoZone Taleo"])

    grid = QGridLayout()
    browser = QWebView()
    urlBar = UrlBar(browser)
    requestsTable = RequestsTable()  # Debug Requests

    networkManager = NetworkManager(requestsTable)
    page = QWebPage()
    page.setNetworkAccessManager(networkManager)
    browser.setPage(page)
    browser.load(QUrl(""))  # Defaul URL
    #browser.load(QUrl(""))
    QWebSettings.globalSettings().setAttribute(QWebSettings.PluginsEnabled, True)  # Enable Flash
    jsEval = JavaScriptEvaluator(page)  # Allow JS Rendering
    actionBox = ActionInputBox(page)

    grid.addWidget(urlBar, 1, 0)
#    grid.addWidget(actionBox, 2, 0)
    grid.addWidget(browser, 3, 0)
#   grid.addWidget(requestsTable, 4, 0)  # good for debugging request data
#    grid.addWidget(jsEval, 5, 0)

    mainFrame = QWidget()
    mainFrame.setLayout(grid)
    mainFrame.show()

    sys.exit(app.exec_())
