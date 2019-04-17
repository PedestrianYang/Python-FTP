# -*- coding:utf-8 -*-
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import sys
import os.path
from ftplib import FTP
import ftplib
from SelectFile import  *
import ftp_config

_XFER_FILE = 'FILE'
_XFER_DIR  = 'DIR'

class NameForm(QDialog):
    changeNameSingal = Signal(str, str)
    def __init__(self, oldName):
        QDialog.__init__(self)
        self.oldName = oldName

        oldNameLab = QLabel('原名：' + self.oldName)

        self.edit = QLineEdit()
        button = QPushButton("确定")
        # 创建布局并添加控件
        layout = QVBoxLayout()

        layout.addWidget(oldNameLab)
        layout.addWidget(self.edit)
        layout.addWidget(button)
        # 设置对话框布局
        self.setLayout(layout)
        # 添加按钮并设置触发事件
        button.clicked.connect(self.buttonClick)

    def buttonClick(self):
        self.changeNameSingal.emit(self.oldName,self.edit.text())




class ItemFile(QWidget):
    fixSingal = Signal(QListWidgetItem)
    checkSingal = Signal(QListWidgetItem)
    deleteSingal = Signal(QListWidgetItem)
    def __init__(self, filePath, tempItem):
        QWidget.__init__(self)
        self.filePath = filePath
        self.tempItem = tempItem
        self.setContainer()

    def setContainer(self):
        h_box = QHBoxLayout()

        filePathLab = QLabel(self.filePath)
        filePathLab.setMinimumWidth(200)
        h_box.addWidget(filePathLab)

        fixBtn = QPushButton('修改名字')
        fixBtn.setFixedSize(90, 50)
        fixBtn.clicked.connect(self.fixBtnClick)
        h_box.addWidget(fixBtn)

        checkBtn = QPushButton('选择')
        checkBtn.setFixedSize(50, 50)
        checkBtn.clicked.connect(self.checkBtnClick)
        h_box.addWidget(checkBtn)

        deleteBtn = QPushButton('删除')
        deleteBtn.setFixedSize(50, 50)
        deleteBtn.clicked.connect(self.deleteBtnClick)
        h_box.addWidget(deleteBtn)

        self.setLayout(h_box)

    def fixBtnClick(self):
        self.fixSingal.emit(self.tempItem)

    def checkBtnClick(self):
        self.checkSingal.emit(self.tempItem)

    def deleteBtnClick(self):
        self.deleteSingal.emit(self.tempItem)

class MainView(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.ftp = self.ftpconnect(ftp_config.host, ftp_config.username, ftp_config.password)
        self.files = []
        self.selectView = SelectFile()
        self.selectView.comfirmSingal.connect(self.uploadAction)
        self.setContainer()

    def setListviewItem(self):

        self.listView.clear()

        for i in range(len(self.files)):
            url = self.files[i]

            tempItem = QListWidgetItem()
            tempItem.setSizeHint(QSize(100, 60))
            fileItem = ItemFile(url, tempItem)
            fileItem.fixSingal.connect(self.fixFile)
            fileItem.checkSingal.connect(self.checkFile)
            fileItem.deleteSingal.connect(self.deleteFile)

            self.listView.addItem(tempItem)
            self.listView.setItemWidget(tempItem, fileItem)

    def fixFile(self, tempitem):
        #修改名字
        row = self.listView.row(tempitem)
        url = self.files[row]

        self.form = NameForm(url)
        self.form.changeNameSingal.connect(self.changeName)
        self.form.show()

    def changeName(self, oldName, newName):
        self.ftp.rename(oldName, newName)
        self.form.close()
        self.refreshUI()


    def checkFile(self, tempitem):
        row = self.listView.row(tempitem)
        url = self.files[row]

        # self.ftp.rename('', 'iyunshu.apk')


    def deleteFile(self, tempitem):
        row = self.listView.row(tempitem)
        url = self.files[row]

        tempurl =  url

        #删除ftp文件时，先判断是否是文件夹
        if self.checkFileDir(tempurl):
            self.ftp.delete(tempurl)
        else:
            #如果是文件夹则递归删除
            self.deletFTPDir(tempurl)

        self.files.remove(url)
        self.listView.takeItem(row)

    def deletFTPDir(self, url):
        print('url:' + url)
        currntFiles = self.ftp.nlst(url)
        print(currntFiles)
        for file in currntFiles:
            path = url + '/' + file
            if self.checkFileDir(path):
                self.ftp.delete(path)
            else:
                self.deletFTPDir(file)
        self.ftp.rmd(url)
        #使用nlst函数展示当前目录时，默认进入该目录下，需要退出该目录
        self.ftp.cwd("..")



    def checkFileDir(self, file_name):
        """
        判断当前目录下的文件与文件夹
        :param ftp: 实例化的FTP对象
        :param file_name: 文件名/文件夹名
        :return:返回字符串“File”为文件，“Dir”问文件夹，“Unknow”为无法识别
        """
        rec = None
        try:
            rec = self.ftp.cwd(file_name)   # 需要判断的元素
            self.ftp.cwd("..")   # 如果能通过路劲打开必为文件夹，在此返回上一级
        except ftplib.error_perm as fe:
            rec = fe # 不能通过路劲打开必为文件，抓取其错误信息

        finally:
            resutStr = str(rec).split(' ')
            resultstr = resutStr[0]
            if resultstr == '250':
                print('文件夹' + file_name)
                return False
            elif resultstr == '550':
                print('文件' + file_name)
                return True
            else:
                print('不识别' + file_name)
                return True






    def uploadAction(self, files):
        #上传，然后刷新界面
        print(files)
        for url in files:
            tempUrl:QUrl = url
            self.upload('', tempUrl.path())
        self.refreshUI()


    def refreshUI(self):
        self.files = self.ftp.nlst()
        self.setListviewItem()


    def setContainer(self):
        v_box = QVBoxLayout()

        self.listView = QListWidget()
        v_box.addWidget(self.listView)

        uploadBtn = QPushButton('上传文件')
        uploadBtn.clicked.connect(self.uploadBtnClick)
        v_box.addWidget(uploadBtn)
        self.setLayout(v_box)

        self.refreshUI()



    def uploadBtnClick(self):
        self.selectView.show()

    def ftpconnect(self, host, username, password):
        print(host)
        ftp = FTP()
        ftp.connect(host, 21)
        ftp.encoding = 'gbk'
        ftp.login(username, password)
        return ftp

    def upload(self, remoteRelDir, localPath):
        """
        :param ftp:
        :param remoteRelDir: 服务端文件夹相对路径，可以为None、""，此时文件上传到homeDir
        :param localPath: 客户端文件或文件夹路径，当路径以localDir开始，文件保存到homeDir的相对路径下
        :return:
        """
        result = [1, ""]

        try:
            remoteRelDir = self.formatPath(remoteRelDir)

            localPath = self.formatPath(localPath)

            if localPath == "":
                return
            else:
                if localPath.startswith(ftp_config.localDir):  # 绝对路径
                    localRelDir = localPath.replace(ftp_config.localDir, "/")
                else:  # 相对(localDir)路径
                    localPath = self.formatPath(ftp_config.localDir, localPath)


            if os.path.isdir(localPath):  # isDir
                current_dir = os.path.abspath(localPath)
                dirName = os.path.basename(current_dir)
                remoteRelDir = self.formatPath('/' + dirName + '/')

                rs = self.uploadDir(remoteRelDir, localPath)
            else:  # isFile
                rs = self.uploadFile(remoteRelDir, localPath)

            if rs[0] == -1:
                result[0] = -1
            result[1] = result[1] + "\n" + rs[1]

        except Exception as e:
            result = [-1, "upload fail, reason:{0}".format(e)]

        return result

     # 上传指定文件夹下的所有
    def uploadDir(self, remoteRelDir, localAbsDir):
        """
        :param ftp:
        :param remoteRelDir: 服务端文件夹相对路径，可以为None、""，此时文件上传到homeDir
        :param localAbsDir: 客户端文件夹路径，当路径以localDir开始，文件保存到homeDir的相对路径下
        :return:
        """
        print("start upload dir by use FTP...")
        result = [1, ""]

        try:
            for root, dirs, files in os.walk(localAbsDir):
                if len(files) > 0:
                    for fileName in files:
                        localAbsPath = localAbsDir + fileName
                        rs = self.uploadFile(remoteRelDir, localAbsPath)
                        if rs[0] == -1:
                            result[0] = -1
                        result[1] = result[1] + "\n" + rs[1]

                if len(dirs) > 0:
                    for dirName in dirs:
                        rrd = self.formatPath(remoteRelDir, dirName)
                        lad = self.formatPath(localAbsDir, dirName)
                        self.ftp.mkd(rrd)
                        rs = self.uploadDir(rrd, lad)
                        if rs[0] == -1:
                            result[0] = -1
                        result[1] = result[1] + "\n" + rs[1]
                #创建目录默认进入该目录，需要退出该目录
                self.ftp.cwd('..')

                break


        except Exception as e:
            result = [-1, "upload fail, reason:{0}".format(e)]

        return result

    # 上传指定文件
    def uploadFile(self, remoteRelDir, localAbsPath):
        """
        :param ftp:
        :param remoteRelDir: 服务端文件夹相对路径，可以为None、""，此时文件上传到homeDir
        :param localAbsPath: 客户端文件路径，当路径以localDir开始，文件保存到homeDir的相对路径下
        :return:
        """
        print("start upload file by use FTP...")
        result = [1, ""]

        try:
            try:
                print('+++++++:' + remoteRelDir)
                self.ftp.cwd(remoteRelDir)

            except ftplib.error_perm:
                try:
                    self.ftp.mkd(remoteRelDir)
                    print(remoteRelDir)
                except ftplib.error_perm:
                    print("U have no authority to make dir")

            fileName = os.path.basename(localAbsPath)
            remoteRelPath = self.formatPath(remoteRelDir, fileName)

            print(remoteRelPath)
            handle = open(localAbsPath, "rb")
            self.ftp.storbinary("STOR %s" % remoteRelPath, handle, 1024)
            handle.close()

            result = [1, "upload " + fileName + " success"]
        except Exception as e:
            result = [-1, "upload fail, reason:{0}".format(e)]

        #创建目录默认进入该目录，需要退出该目录
        self.ftp.cwd("..")

        return result


    # 判断remote path isDir or isFile
    def isDir(self, path):
        try:
            self.ftp.cwd(path)
            self.ftp.cwd("..")
            return True
        except:
            return False


    # return last dir'name in the path, like os.path.basename
    def lastDir(self, path):
        path = self.formatPath(path)
        paths = path.split("/")
        if len(paths) >= 2:
            return paths[-2]
        else:
            return ""

        # 格式化路径或拼接路径并格式化
    def formatPath(self, path, *paths):
        """
        :param path: 路径1
        :param paths: 路径2-n
        :return:
        """
        if path is None or path == "." or path == "/" or path == "//":
            path = ""

        if len(paths) > 0:
            for pi in paths:
                if pi == "" or pi == ".":
                    continue
                path = path + "/" + pi

        if path == "":
            return path

        while path.find("\\") >= 0:
            path = path.replace("\\", "/")
        while path.find("//") >= 0:
            path = path.replace("//", "/")

        if path.find(":/") > 0:  # 含磁盘符 NOT EQ ZERO, OS.PATH.ISABS NOT WORK
            if path.startswith("/"):
                path = path[1:]
        else:
            if not path.startswith("/"):
                path = "/" + path

        if os.path.isdir(path):  # remote path is not work
            if not path.endswith("/"):
                path = path + "/"
        elif os.path.isfile(path):  # remote path is not work
            if path.endswith("/"):
                path = path[:-1]
        elif path.find(".") < 0:  # maybe it is a dir
            if not path.endswith("/"):
                path = path + "/"
        else:  # maybe it is a file
            if path.endswith("/"):
                path = path[:-1]
        return path



    def closeEvent(self, *args, **kwargs):
        self.ftp.quit()
