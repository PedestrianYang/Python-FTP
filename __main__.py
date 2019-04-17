from MainView import *
if __name__ == '__main__':
    app = QApplication(sys.argv)

    downloadThreads = []
    requestPath = 1
    ui = MainView()
    # ui.setupUi(mainWindow)
    ui.show()
    sys.exit(app.exec_())