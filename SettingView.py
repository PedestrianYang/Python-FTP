from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from ftp_config import *
import ftp_config

class MyButton(QPushButton):
    Clicked = Signal(QPushButton)
    def __init__(self, title, tag):
        QPushButton.__init__(self, title)
        self.tag = tag

    def mousePressEvent(self, event:QMouseEvent):
        if event.type() == QMouseEvent.MouseButtonPress:
            self.Clicked.emit(self)

class SettingView(QWidget):
    comfirmSingal = Signal(str, str, str, int)
    def __init__(self):
        self.type = 1
        QWidget.__init__(self)
        self.setContainer()

    def setContainer(self):
        v_box = QVBoxLayout()

        ipLay = QHBoxLayout()
        ipLab = QLabel('IP地址')
        self.ipEdit = QLineEdit(ftp_config.host)
        ipLay.addWidget(ipLab)
        ipLay.addWidget(self.ipEdit)
        v_box.addLayout(ipLay)

        nameLay = QHBoxLayout()
        nameLab = QLabel('用户名')
        self.nameEdit = QLineEdit(ftp_config.username)
        nameLay.addWidget(nameLab)
        nameLay.addWidget(self.nameEdit)
        v_box.addLayout(nameLay)

        pwdLay = QHBoxLayout()
        pwdLab = QLabel('密码')
        self.pwdEdit = QLineEdit(ftp_config.password)
        pwdLay.addWidget(pwdLab)
        pwdLay.addWidget(self.pwdEdit)
        v_box.addLayout(pwdLay)

        filterLay = QHBoxLayout()
        filterLab = QLabel('选择要上传的apk类型')
        filterLay.addWidget(filterLab)

        iyunshuBtn = MyButton('云书网', 1)
        iyunshuBtn.Clicked.connect(self.btnClick)
        wenhuayunBtn = MyButton('文化云', 2)
        wenhuayunBtn.Clicked.connect(self.btnClick)
        yunzhangguiBtn = MyButton('云掌柜', 3)
        yunzhangguiBtn.Clicked.connect(self.btnClick)
        hepiaoBtn = MyButton('核票app', 4)
        hepiaoBtn.Clicked.connect(self.btnClick)
        filterLay.addWidget(iyunshuBtn)
        filterLay.addWidget(wenhuayunBtn)
        filterLay.addWidget(yunzhangguiBtn)
        filterLay.addWidget(hepiaoBtn)



        v_box.addLayout(filterLay)

        controlLay = QHBoxLayout()

        restBtn = QPushButton('重置')
        restBtn.setFixedSize(60, 30)
        restBtn.clicked.connect(self.restBtnClick)
        controlLay.addWidget(restBtn)

        confirmBtn = QPushButton('确定')
        confirmBtn.setFixedSize(60, 30)
        confirmBtn.clicked.connect(self.confirmBtnClick)
        controlLay.addWidget(confirmBtn)
        v_box.addLayout(controlLay)

        self.setLayout(v_box)

    def restBtnClick(self):
        self.ipEdit.setText(ftp_config.host)
        self.nameEdit.setText(ftp_config.username)
        self.pwdEdit.setText(ftp_config.password)
        self.type = 1

    def confirmBtnClick(self):
        self.comfirmSingal.emit(self.ipEdit.text(), self.nameEdit.text(), self.pwdEdit.text(), self.type)
    def btnClick(self, btn):
        self.type = btn.tag

