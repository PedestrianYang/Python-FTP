from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

class ItemFile(QWidget):
    deleteSingal = Signal(QListWidgetItem)
    def __init__(self, filePath, tempItem):
        QWidget.__init__(self)
        self.filePath = filePath
        self.tempItem = tempItem
        self.setContainer()

    def setContainer(self):
        h_box = QHBoxLayout()

        filePathLab = QLabel(self.filePath)

        h_box.addWidget(filePathLab)

        deleteBtn = QPushButton('删除')
        deleteBtn.setFixedSize(50, 50)
        deleteBtn.clicked.connect(self.deleteBtnClick)
        h_box.addWidget(deleteBtn)

        self.setLayout(h_box)

    def deleteBtnClick(self):
        self.deleteSingal.emit(self.tempItem)

class FileListView(QListWidget):

    def __init__(self):
        QListWidget.__init__(self)


        self.setAcceptDrops(True)

        self.files = []

    def setListViewContent(self):
        for i in range(len(self.files)):
            url:QUrl = self.files[i]
            path = url.path()


            tempItem = QListWidgetItem()
            tempItem.setSizeHint(QSize(100, 60))
            fileItem = ItemFile(path, tempItem)
            fileItem.deleteSingal.connect(self.deleteFile)

            self.addItem(tempItem)
            self.setItemWidget(tempItem, fileItem)


    def deleteFile(self, tempitem):
        row = self.row(tempitem)

        url = self.files[row]
        self.files.remove(url)
        self.takeItem(row)


    def dragEnterEvent(self, event:QDragEnterEvent):


        if event.mimeData().hasFormat("text/uri-list"):
            event.acceptProposedAction()
            event.accept()

    def dragMoveEvent(self, event:QDragEnterEvent):
        if event.mimeData().hasFormat("text/uri-list"):
            event.acceptProposedAction()
            event.accept()

    def dropEvent(self, event:QDropEvent):

        urls = event.mimeData().urls()
        if urls == None or len(urls) == 0:
            return

        self.files = urls

        self.setListViewContent()



class SelectFile(QWidget):
    comfirmSingal = Signal(list)
    def __init__(self):
        QWidget.__init__(self)

        self.setContainer()

    def setContainer(self):
        v_boc = QVBoxLayout()

        self.listView = FileListView()
        v_boc.addWidget(self.listView)


        h_box = QHBoxLayout()

        cleanBtn = QPushButton('清除')
        cleanBtn.setFixedSize(60, 30)
        cleanBtn.clicked.connect(self.cleanBtnClick)
        h_box.addWidget(cleanBtn)


        confirmBtn = QPushButton('确定')
        confirmBtn.setFixedSize(60, 30)
        confirmBtn.clicked.connect(self.confirmBtnClick)
        h_box.addWidget(confirmBtn)

        v_boc.addLayout(h_box)

        self.setLayout(v_boc)

    def cleanBtnClick(self):
        self.listView.clear()
        self.listView.files.clear()

    def confirmBtnClick(self):
        self.comfirmSingal.emit(self.listView.files)


