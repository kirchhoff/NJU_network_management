#!/usr/bin/env python


#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################


from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QComboBox,
        QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QMessageBox, QMenu, QPushButton, QSpinBox, QStyle, QSystemTrayIcon,
        QTextEdit, QVBoxLayout)

from PyQt5.QtCore import Qt
import requests
import json
import os
import time


#
from img import *
import inspect
import ctypes

class Window(QDialog):
    path_file = "./nju_account.txt"

    # 新线程执行的代码:
    def loop(self):
        while True:
            #print('thread %s is running...' % threading.current_thread().name)
            r = requests.get('http://www.baidu.com')
            if r.status_code != 200:
                self.iconComboBox.setCurrentIndex(1)
            time.sleep(300)

    def login(self, name, password):
        """login work"""

        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                   'Accept-Encoding': 'gzip, deflate, sdch, br',
                   'Accept-Language': 'zh-CN,zh;q=0.8',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.101 Safari/537.36'}
        s = requests.Session()
        s.headers = headers
        post_data = {'username': name, 'password': password}
        print("in login ",name,password)
        try:
            r = s.post('http://p.nju.edu.cn/portal_io/login', data=post_data, verify=False)
        except Exception as e:
            print(e)
            return (0,0)

        reply_code = json.loads(r.content)['reply_code']
        print("log in, status = %s" % r.status_code)
        print(json.loads(r.content))
        return r.status_code,reply_code

    def logout(self):
        """login work"""
        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                   'Accept-Encoding': 'gzip, deflate, sdch, br',
                   'Accept-Language': 'zh-CN,zh;q=0.8',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.101 Safari/537.36'}
        s = requests.Session()
        s.headers = headers
        # post_data = {'username': name, 'password': password}
        try:

            r = s.post('http://p.nju.edu.cn/portal_io/logout', verify=False)
        except Exception as e:
            print(e)
            return 0
        print("logout, status = %s" % r.status_code)
        print(json.loads(r.content))
        return None

    def onTimerOut(self):
        try:
            r = requests.get("http://www.baidu.com")
        except Exception as e:
            print(e)
            self.iconComboBox.setCurrentIndex(1)

        else:
            if r.status_code != 200:
                self.iconComboBox.setCurrentIndex(1)
            else:
                self.iconComboBox.setCurrentIndex(0)


    def __init__(self):
        super(Window, self).__init__()
        self.timer = QtCore.QTimer()
        self.timer.setInterval(10*1000) #10秒检查网络连通性
        self.timer.start()
        self.timer.timeout.connect(self.onTimerOut)

        self.createIconGroupBox()
        self.createMessageGroupBox()

#        self.iconLabel.setMinimumWidth(self.durationLabel.sizeHint().width())

        self.createActions() #配置动作

        self.createTrayIcon() #配置托盘菜单项

        self.showMessageButton.clicked.connect(self.showMessage)
      #  self.showIconCheckBox.toggled.connect(self.trayIcon.setVisible)
        self.iconComboBox.currentIndexChanged.connect(self.setIcon)
       # self.trayIcon.messageClicked.connect(self.messageClicked)
        self.trayIcon.activated.connect(self.iconActivated)

        self.checkbox.stateChanged.connect(self.save_ap)

        mainLayout = QVBoxLayout()
        #mainLayout.addWidget(self.iconGroupBox)
        mainLayout.addWidget(self.messageGroupBox)
        self.setLayout(mainLayout)

        self.iconComboBox.setCurrentIndex(1) #默认ico
        self.trayIcon.show()

        self.setWindowTitle("NJU上网助手")
        self.resize(400, 300)

        if os.path.exists(self.path_file):
            with open(self.path_file, "r") as f:
                l = f.readline().split(';:;')
                self.titleEdit.setText(l[0])
                self.bodyEdit.setText(l[1])
                self.name = l[0]
                self.password=l[1]

            (responce_code, reply_code)= self.login(self.name,self.password)
            if responce_code == 0:
                QMessageBox.critical(None, "通知",
                                        "请检查校园网连接链路的有效性")
                sys.exit()


            elif responce_code == 200:
                if reply_code == 1 or reply_code ==6:
                    self.iconComboBox.setCurrentIndex(0)  # 默认ico
                else:
                    self.iconComboBox.setCurrentIndex(1)
                    QMessageBox.information(self, "通知",
                                            "您保存在nju_account.txt中的密码无效")
                    self.show()
            else:
                self.iconComboBox.setCurrentIndex(1)
                QMessageBox.critical(self, "通知",
                                        "网络连接有问题") #不知道会是啥问题
                #QApplication.instance().quit()
                sys.exit()
        else:
            self.show()



    def setVisible(self, visible):
        #self.minimizeAction.setEnabled(visible)
       # self.maximizeAction.setEnabled(not self.isMaximized())

        super(Window, self).setVisible(visible)

    def save_ap(self,state):
        if state == Qt.Checked:
            with open(self.path_file,"w") as f:
                f.write(self.titleEdit.text()+";:;"+self.bodyEdit.text())
        else:
            print("没有")

    def closeEvent(self, event):
    #     self.close()

        if self.trayIcon.isVisible():
            QMessageBox.information(self, "注意",
                    "该程序会在系统托盘中继续运行\n"
                    "可以在托盘中图标上右击选择 Quit 退出程序")
            self.hide()
            event.ignore()


    def setIcon(self, index):
        icon = self.iconComboBox.itemIcon(index)
        self.trayIcon.setIcon(icon)
        self.setWindowIcon(icon)

        self.trayIcon.setToolTip(self.iconComboBox.itemText(index))

    def iconActivated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            if self.iconComboBox.currentIndex() == 0:
                print("yes")
                self.logout()
                self.iconComboBox.setCurrentIndex(
                    (self.iconComboBox.currentIndex() + 1)
                    % self.iconComboBox.count())

            elif self.iconComboBox.currentIndex()==1:
                print("no")
                self.name = self.titleEdit.text()
                self.password= self.bodyEdit.text()
                print(self.name,self.password)
                (response_status, reply_code)= self.login(self.name,self.password)
                if response_status == 0:
                    QMessageBox.critical(None, "通知",
                                         "请检查校园网连接链路的有效性")
                    #sys.exit()
                else:

                    self.iconComboBox.setCurrentIndex(
                        (self.iconComboBox.currentIndex() + 1)
                        % self.iconComboBox.count())

        elif reason == QSystemTrayIcon.MiddleClick:
            self.showMessage()
        #print("ffff")

    def showMessage(self):
        account = self.titleEdit.text()
        password = self.bodyEdit.text()
        print("name",account,"password",password)

        self.logout()
        time.sleep(2)
        (responce_code, reply_code) = self.login(account,password)
        print("reply code", reply_code)
        if responce_code == 200:
            if reply_code == 6 or reply_code == 1:
                self.iconComboBox.setCurrentIndex(0)
                QMessageBox.information(self, "通知",
                                        "测试通过")

            elif reply_code == 3:
                self.iconComboBox.setCurrentIndex(1)
                QMessageBox.information(self, "通知",
                                        "您输入的密码无效")
            else:
                self.iconComboBox.setCurrentIndex(1)
                QMessageBox.information(self, "通知",
                                        "未知reply_code:"+str(reply_code))
        else:
            self.iconComboBox.setCurrentIndex(1)
            QMessageBox.information(self, "通知",
                                    "网络连接有问题")




    def createIconGroupBox(self):
        self.iconGroupBox = QGroupBox("Tray Icon")
        self.iconLabel = QLabel("Icon:")
        self.iconComboBox = QComboBox()
        self.iconComboBox.addItem(QIcon(':/picture/1.jpg'), "上线状态")
        self.iconComboBox.addItem(QIcon(':/picture/2.jpg'), "下线状态")


    def createMessageGroupBox(self):
        self.messageGroupBox = QGroupBox("配置上网账号")
        titleLabel = QLabel("用户名:")
        self.titleEdit = QLineEdit("")
        bodyLabel = QLabel("密码:")
        self.bodyEdit = QLineEdit("")
        self.bodyEdit.setEchoMode(QLineEdit.Password)

        self.showMessageButton = QPushButton("测试连接")
        self.showMessageButton.setDefault(True)

        self.checkbox = QCheckBox("记住密码")

        messageLayout = QGridLayout()

        messageLayout.addWidget(titleLabel, 2, 0)
        messageLayout.addWidget(self.titleEdit, 2, 1, 1, 1)

        messageLayout.addWidget(bodyLabel, 3, 0)
        messageLayout.addWidget(self.bodyEdit, 3, 1, 1, 1)

        messageLayout.addWidget(self.showMessageButton, 5, 1)
        messageLayout.addWidget(self.checkbox, 5,0 )
        #messageLayout.setColumnStretch(4, 1)
       # messageLayout.setRowStretch(1, 1)
        self.messageGroupBox.setLayout(messageLayout)


    def createActions(self):
        self.minimizeAction = QAction("配置", self, triggered=self.showNormal)
        #self.maximizeAction = QAction("Ma&ximize", self,
         #       triggered=self.showMaximized)
        self.quitAction = QAction("&Quit", self,
                triggered=QApplication.instance().quit)

    def createTrayIcon(self):

         self.trayIconMenu = QMenu(self)

         self.trayIconMenu.addAction(self.minimizeAction)
         #self.trayIconMenu.addAction(self.maximizeAction)

         self.trayIconMenu.addSeparator()
         self.trayIconMenu.addAction(self.quitAction)

         self.trayIcon = QSystemTrayIcon(self)
         self.trayIcon.setContextMenu(self.trayIconMenu)



if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "Systray",
                "I couldn't detect any system tray on this system.")
        sys.exit(1)

    QApplication.setQuitOnLastWindowClosed(False)

    window = Window()
   # window.show()
    sys.exit(app.exec_())
   #main()
