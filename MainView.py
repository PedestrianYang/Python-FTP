# -*- coding:utf-8 -*-
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import sys
import os.path
from ftplib import FTP
import ftplib
from SelectFile import  *
from SettingView import  *
import ftp_config
import time

_XFER_FILE = 'FILE'
_XFER_DIR  = 'DIR'

iyunshu = 'iyunshu'
wenhuayun = 'wenhuayun'
yunzhanggui = 'yunzhanggui'

class ConnectThread(QThread):
    loginCompelet = Signal()
    def __init__(self, ftp, host,username, password):
        QThread.__init__(self)
        self.ftp = ftp
        self.host = host
        self.username = username
        self.password = password
        print(username, password)

    def run(self, *args, **kwargs):
        self.ftp.connect(self.host, 21)
        self.ftp.encoding = 'gbk'
        self.ftp.login(self.username, self.password)
        self.loginCompelet.emit()

class UploadFileThread(QThread):
    uploadCompelet = Signal()
    def __init__(self, ftp, localPaths):
        QThread.__init__(self)
        self.ftp = ftp
        self.localPaths = localPaths


    def run(self, *args, **kwargs):
        for uploadPath in self.localPaths:
            self.upload('', uploadPath)
        self.uploadCompelet.emit()


    def upload(self, remoteRelDir, localPath):
        """
        :param ftp:
        :param remoteRelDir: 服务端文件夹相对路径，可以为None、""，此时文件上传到homeDir
        :param localPath: 客户端文件或文件夹路径，当路径以localDir开始，文件保存到homeDir的相对路径下
        :return:
        """

        if os.path.exists(localPath) == False:
            QMessageBox.warning(self, '提示', '路径%s未找到' % localPath, QMessageBox.Ok)
            return

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

class FileObj:
    def __init__(self, name, date):
        self.name = name
        self.date = date

class NameForm(QDialog):
    changeNameSingal = Signal(str, str)
    def __init__(self, fileObj, filterWord):
        QDialog.__init__(self)
        self.fileObj = fileObj
        self.filterWord = filterWord

        oldNameLab = QLabel('原名：' + self.fileObj.name)
        oldNameLab.setTextInteractionFlags(Qt.TextSelectableByMouse)

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
        newAppname = self.edit.text()
        if newAppname.endswith('.apk') == False :
            question = QMessageBox.warning(self, '提醒', "命名不规范：请以'.apk'为后缀，重新命名", QMessageBox.Ok)
            if question == QMessageBox.Ok:
                newAppname = newAppname + '.apk'
                self.edit.setText(newAppname)
            return

        self.filePerName = self.filterWord + '_'

        if newAppname.startswith(self.filePerName) == False:
            question2 = QMessageBox.warning(self, '提醒', "命名不规范：请以'%s'为前缀，重新命名" % self.filePerName, QMessageBox.Ok)
            if question2 == QMessageBox.Ok:
                newAppname = self.filePerName + newAppname
                self.edit.setText(newAppname)
            return

        msg = QMessageBox.question(self, '提醒', '是否要把'+ self.fileObj.name + '文件名改为'+ self.edit.text() + '？', QMessageBox.Ok|QMessageBox.Cancel)
        if msg == QMessageBox.Ok:
            print('是')
            self.changeNameSingal.emit(self.fileObj.name, self.edit.text())
        else:
            print('取消')




class ItemFile(QWidget):
    fixSingal = Signal(QListWidgetItem)
    checkSingal = Signal(QListWidgetItem)
    deleteSingal = Signal(QListWidgetItem)
    def __init__(self, fileOBj, tempItem, currentFile):
        QWidget.__init__(self)
        self.fileOBj = fileOBj
        self.tempItem = tempItem
        self.currentFile = currentFile
        self.setContainer()

    def setContainer(self):
        h_box = QHBoxLayout()

        filePathLab = QLabel(self.fileOBj.name)
        filePathLab.setMinimumWidth(200)
        h_box.addWidget(filePathLab)

        timeLab = QLabel(self.fileOBj.date)
        timeLab.setMinimumWidth(200)
        h_box.addWidget(timeLab)

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
        if self.fileOBj.name == self.currentFile:
            QMessageBox.information(self, '提醒', self.fileOBj.name + '已经是发布版本了！', QMessageBox.Ok)
            return
        self.checkSingal.emit(self.tempItem)


    def deleteBtnClick(self):
        if self.fileOBj.name == self.currentFile:
            QMessageBox.warning(self, '警告', '该文件是当前版本，不能删除，请先备份！')
            return
        else:
            msg = QMessageBox.question(self, '提醒', '是否要删除'+ self.fileOBj.name + '文件？', QMessageBox.Ok|QMessageBox.Cancel)
            if msg == QMessageBox.Ok:
                print('删除')
                self.deleteSingal.emit(self.tempItem)
            else:
                print('取消')



class MainView(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.ftpconnect(ftp_config.host, ftp_config.username, ftp_config.password, ftp_config.filterWords)
        self.files = []

        self.settingView = SettingView()
        self.settingView.comfirmSingal.connect(self.settingAction)
        self.selectView = SelectFile()
        self.selectView.comfirmSingal.connect(self.uploadAction)
        self.setContainer()

    def setListviewItem(self):

        self.listView.clear()

        for i in range(len(self.files)):
            fileObj = self.files[i]

            tempItem = QListWidgetItem()
            tempItem.setSizeHint(QSize(100, 60))
            fileItem = ItemFile(fileObj, tempItem, self.currentApp)
            fileItem.fixSingal.connect(self.fixFile)
            fileItem.checkSingal.connect(self.checkFile)
            fileItem.deleteSingal.connect(self.deleteFile)

            self.listView.addItem(tempItem)
            self.listView.setItemWidget(tempItem, fileItem)

    def fixFile(self, tempitem):
        #修改名字
        row = self.listView.row(tempitem)
        fileObj = self.files[row]

        self.form = NameForm(fileObj, self.filterWord)
        self.form.changeNameSingal.connect(self.changeName)
        self.form.show()

    def changeName(self, oldName, newName):

        for file in self.files:
            if file.name == newName:
                QMessageBox.warning(self, '提示', newName + '文件已经存在，不能重复命名！', QMessageBox.Ok)
                return

        self.ftp.rename(oldName, newName)
        self.form.close()
        self.refreshUI()


    def checkFile(self, tempitem):
        row = self.listView.row(tempitem)
        fileObj = self.files[row]

        if fileObj.name != self.currentApp:
            currentTime = time.strftime("%Y%m%d", time.localtime())

            newappName = self.filterWord + '_' + currentTime + '.apk'
            isNewAppExist = False
            isOldAppExist = False
            for file in self.files:
                if newappName == file.name and file.name != fileObj.name:
                    isNewAppExist =True
                    break

            for file in self.files:
                if self.currentApp == file.name:
                    isOldAppExist =True
                    break
            if isNewAppExist:
                addName = time.strftime("%H%M%S", time.localtime())
                newappName = self.filterWord + '_' + currentTime + '_' + addName + '.apk'

            msg = QMessageBox.question(self, '提醒', '是否要选择%s文件作为发布版本，并把之前版本名称改为%s？' %(fileObj.name, newappName), QMessageBox.Ok|QMessageBox.Cancel)
            if msg == QMessageBox.Ok:
                print('是')
                if isOldAppExist == True:
                    self.ftp.rename(self.currentApp, newappName)
                self.ftp.rename(fileObj.name, self.currentApp)
                self.refreshUI()
            else:
                print('取消')





    def deleteFile(self, tempitem):
        row = self.listView.row(tempitem)
        file = self.files[row]

        tempurl =  file.name

        #删除ftp文件时，先判断是否是文件夹
        if self.checkFileDir(tempurl):
            self.ftp.delete(tempurl)
        else:
            #如果是文件夹则递归删除
            self.deletFTPDir(tempurl)

        self.files.remove(file)
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

    def settingAction(self, host, username, password, apptype):
        self.ftp.quit()
        self.ftpconnect(host, username, password, apptype)

    def uploadAction(self, files):
        #上传，然后刷新界面
        shouldUploadFile = []
        for url in files:
            tempUrl:QUrl = url
            filename = tempUrl.fileName()
            isExist = False
            for file in self.files:
                if file.name == filename:
                    isExist = True
                    break
            if isExist:
                QMessageBox.information(self, '提醒', filename + '文件已经存在FTP服务器中，请改名后再上传！', QMessageBox.Ok)
                continue
            else:
                shouldUploadFile.append(tempUrl.path())

        self.uploadFileThread = UploadFileThread(self.ftp, shouldUploadFile)
        self.uploadFileThread.start()
        self.uploadFileThread.uploadCompelet.connect(self.refreshUI)

    def aaaa(self, aa):
        lll = list(aa)
        time = '20' + lll[6] + lll[7] + '-' + lll[0] + lll[1] + '-' + lll[3] + lll[4] + ' ' + lll[10] + lll[11] + \
               lll[12] + lll[13] + lll[14] + lll[15] + lll[16]
        filename = lll[39]
        for i in range(len(lll)):
            if i > 39:
                filename = filename + lll[i]



        if filename.startswith(self.filterWord):
            fileObj = FileObj(filename, time)
            self.files.append(fileObj)

        print(filename + " " +  time)


    def refreshUI(self):
        self.files.clear()

        # L = list(self.ftp.sendcmd('help'))
        # dir_t=L[4]+L[5]+L[6]+L[7]+'-'+L[8]+L[9]+'-'+L[10]+L[11]+' '+L[12]+L[13]+':'+L[14]+L[15]+':'+L[16]+L[17]
        # timeArray = time.strptime(dir_t, "%Y-%m-%d %H:%M:%S")
        # timeStamp = int(time.mktime(timeArray)) + 28800
        # timeArrayaa = time.localtime(timeStamp)
        # timeStr = time.strftime("%Y-%m-%d %H:%M:%S", timeArrayaa)
        # print(timeStr)
        # print(self.ftp.sendcmd('date'))
        # aaaa = []
        # self.ftp.retrlines('LIST', self.aaaa)
        # self.setListviewItem()

        # print(aaaa)
        # print(self.ftp.retrlines("list -lc %s " % ('iyunshu.apk')))
        files = self.ftp.nlst()

        for file in files:
            if file.startswith(self.filterWord) and file.endswith('.apk'):

                print(file)

                L = list(self.ftp.sendcmd('MDTM ' + "%s" % (file)))
                dir_t=L[4]+L[5]+L[6]+L[7]+'-'+L[8]+L[9]+'-'+L[10]+L[11]+' '+L[12]+L[13]+':'+L[14]+L[15]+':'+L[16]+L[17]
                timeArray = time.strptime(dir_t, "%Y-%m-%d %H:%M:%S")
                timeStamp = int(time.mktime(timeArray)) + 28800
                timeArrayaa = time.localtime(timeStamp)
                timeStr = time.strftime("%Y-%m-%d %H:%M:%S", timeArrayaa)
                fileObj = FileObj(file, timeStr)

                self.files.append(fileObj)
        self.setListviewItem()




    def setContainer(self):
        v_box = QVBoxLayout()

        self.listView = QListWidget()
        v_box.addWidget(self.listView)

        h_box = QHBoxLayout()


        settingBtn = QPushButton('修改配置')
        settingBtn.clicked.connect(self.settingBtnClick)
        h_box.addWidget(settingBtn)

        uploadBtn = QPushButton('上传文件')
        uploadBtn.clicked.connect(self.uploadBtnClick)
        h_box.addWidget(uploadBtn)

        v_box.addLayout(h_box)

        self.setLayout(v_box)





    def settingBtnClick(self):
        self.settingView.show()

    def uploadBtnClick(self):
        self.selectView.show()

    def ftpconnect(self, host, username, password, apptype):
        ftp = FTP()
        filterWord = iyunshu
        if apptype == 1:
            filterWord = iyunshu
        elif apptype == 2:
            filterWord = wenhuayun
        elif apptype == 3:
            filterWord = yunzhanggui

        self.filterWord = filterWord
        self.currentApp = self.filterWord + '.apk'
        self.loginThread = ConnectThread(ftp, host, username, password)
        self.loginThread.start()
        self.loginThread.loginCompelet.connect(self.ftpLoginComplete)

    def ftpLoginComplete(self):
        self.ftp = self.loginThread.ftp

        self.refreshUI()

    # 判断remote path isDir or isFile
    def isDir(self, path):
        try:
            self.ftp.cwd(path)
            self.ftp.cwd("..")
            return True
        except:
            return False



    def closeEvent(self, *args, **kwargs):
        self.ftp.quit()

