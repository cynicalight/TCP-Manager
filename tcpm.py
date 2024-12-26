import psutil
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QCheckBox, QPushButton, QHBoxLayout, QTabWidget, QHBoxLayout, QLineEdit, QMessageBox
from PyQt6.QtGui import QScreen
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class Protect:
    def __init__(self):
        self.create_gui()

    def create_gui(self):
        app = QApplication([])
        window = QMainWindow()
        window.setWindowTitle("TCP MANAGER")
        window.resize(900, 600)

        # make window in center
        screen = QScreen.availableGeometry(QApplication.primaryScreen())
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        window.move(x, y)
        
        # Vertical layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        window.setCentralWidget(central_widget)

        # create tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # TCP tab
        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        
        tree = QTreeWidget()

        # filter
        self.populate_filter(tree, tab1_layout)

        # TCP tree
        self.populate_tree(tree)
        tab1_layout.addWidget(tree)

        # btn
        self.populate_btn(tree, tab1_layout)
        
        tabs.addTab(tab1, "TCP Connections")

        # pop-up monitoring tab
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        tab2_layout.addWidget(QPushButton("Nothing is here."))
        tabs.addTab(tab2, "bu44er")

        window.show()
        app.exec()
        
    def populate_filter(self, tree, layout):
        filter_layout = QHBoxLayout()
        self.local_address_filter = QLineEdit()
        self.local_address_filter.setPlaceholderText("Local Address")
        self.local_port_filter = QLineEdit()
        self.local_port_filter.setPlaceholderText("Local Port")
        self.remote_address_filter = QLineEdit()
        self.remote_address_filter.setPlaceholderText("Remote Address")
        self.remote_port_filter = QLineEdit()
        self.remote_port_filter.setPlaceholderText("Remote Port")

        for edit in [self.local_address_filter, self.local_port_filter, self.remote_address_filter, self.remote_port_filter]:
            filter_layout.addWidget(edit)
        
        layout.addLayout(filter_layout)
        
        # filter event
        for filter_edit in [self.local_address_filter, self.local_port_filter, self.remote_address_filter, self.remote_port_filter]:
            filter_edit.textChanged.connect(lambda: self.filter_tree(tree))
            
        
    def populate_btn(self, tree, layout):
        # btn
        button_layout = QHBoxLayout()
        refresh_button = QPushButton("Refresh TCP")
        stop_button = QPushButton("Stop TCP")
        ignore_button = QPushButton("Ignore TCP")
        
        # traversal addwidget
        for button in [refresh_button, stop_button, ignore_button]:
            button_layout.addWidget(button)
        layout.addLayout(button_layout)

        # btn event
        refresh_button.clicked.connect(lambda: self.populate_tree(tree))
        stop_button.clicked.connect(lambda: self.stop_selected_tcp(tree))
        ignore_button.clicked.connect(lambda: self.ignore_selected_tcp(tree))


    def populate_tree(self, tree):
        tree.clear()
        tree.setColumnCount(7)  # 修改列数为7，包含选择列
        tree.setHeaderLabels(
            ["Select", "Index", "Local Address", "Local Port", "Remote Address", "Remote Port", "Status"])

        # tree.clear()
        for index, conn in enumerate(self.list_tcp_connections(), start=1):
            laddr = f"{conn.laddr.ip}" if conn.laddr else "N/A"
            lport = f"{conn.laddr.port}" if conn.laddr else "N/A"
            raddr = f"{conn.raddr.ip}" if conn.raddr else "N/A"
            rport = f"{conn.raddr.port}" if conn.raddr else "N/A"
            item = QTreeWidgetItem(
                ["", str(index), laddr, lport, raddr, rport, conn.status])
            tree.addTopLevelItem(item)
            checkbox = QCheckBox()
            tree.setItemWidget(item, 0, checkbox)
        
        

    def filter_tree(self, tree):
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i)
            local_address_match = self.local_address_filter.text() in item.text(2)
            local_port_match = self.local_port_filter.text() in item.text(3)
            remote_address_match = self.remote_address_filter.text() in item.text(4)
            remote_port_match = self.remote_port_filter.text() in item.text(5)
            item.setHidden(not (local_address_match and local_port_match and remote_address_match and remote_port_match))

    def list_tcp_connections(self):
        connections = psutil.net_connections(kind='tcp')
        return connections

    def stop_selected_tcp(self, tree):
        
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i)
            checkbox = tree.itemWidget(item, 0)
            if checkbox.isChecked():
                # 停止选中的 TCP 连接
                logging.debug(f"Stopping TCP connection: {item.text(1)}")
                local_address = item.text(2)
                remote_address = item.text(4)
                local_port = item.text(3)           
                remote_port =item.text(5)
                remote_na_flag = False
                logging.debug(f"local address: {local_address}")
                
                if remote_address == 'N/A':
                    remote_na_flag = True
            
                for conn in psutil.net_connections(kind='tcp'): # or 短路
                    if conn.laddr.ip == local_address and conn.laddr.port == int(local_port):
                        if remote_na_flag or (conn.raddr.ip == remote_address and conn.raddr.port == int(remote_port)):
                            logging.debug(f"Detected system: {os.name}")
                            commands = {
                                "nt": f"taskkill /PID {conn.pid} /F",  # Windows
                                "posix": f"kill -9 {conn.pid}"  # Unix
                            }
                            command = commands.get(os.name, None)
                            
                            if command:
                                # os.system(command)
                                logging.debug(
                                    f"Stopped TCP connection: {item.text(1)}")
                            
                            # pop-up
                            msg = QMessageBox()
                            msg.setIcon(QMessageBox.Icon.Information)
                            msg.setText(f"Successfully stop: No.{item.text(1)} TCP")
                            msg.setWindowTitle("success")
                            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                            msg.exec()
                    
                

    def ignore_selected_tcp(self, tree):
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i)
            checkbox = tree.itemWidget(item, 0)
            if checkbox.isChecked():
                # ignore
                logging.debug(f"Ignoring TCP connection: {item.text(1)}")
                item.setHidden(True)


if __name__ == "__main__":
    protect = Protect()
