from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from ftp_config import *
import ftp_config

class SettingView(QWidget):
    comfirmSingal = Signal(str, str, str, str)
    def __init__(self):
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
        filterLab = QLabel('显示文件')
        self.filterEdit = QLineEdit(ftp_config.filterWords)
        filterLay.addWidget(filterLab)
        filterLay.addWidget(self.filterEdit)
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
        self.filterEdit.setText(ftp_config.filterWords)

    def confirmBtnClick(self):
        self.comfirmSingal.emit(self.ipEdit.text(), self.nameEdit.text(), self.pwdEdit.text(), self.filterEdit.text())

