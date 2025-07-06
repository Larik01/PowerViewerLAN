import subprocess
import sys

from PyQt6.QtWidgets import (QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton,
                             QHBoxLayout, QDialog, QLineEdit, QLabel, QFormLayout, QDialogButtonBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


def cmd(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    result = process.communicate()[0].decode("cp866")
    return result


def ping(ip):
    command = f'ping {ip} -n 1'
    result = cmd(command).lower()
    return 'time' in result or 'время' in result


def get_router_ip():
    return cmd('ipconfig').split('\n')[9].split()[-1]


def get_lan_host_list():
    return [host.split()[0] for host in cmd('arp -a').split('\n')[3:-1] if host.split()[-1] == 'dynamic']


class AddHostDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add host")

        self.name_input = QLineEdit()
        self.ip_input = QLineEdit()

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QFormLayout()
        layout.addRow(QLabel("Name:"), self.name_input)
        layout.addRow(QLabel("IP:"), self.ip_input)
        layout.addRow(button_box)

        self.setLayout(layout)

    def get_host_data(self):
        return (self.name_input.text(), self.ip_input.text())


class HostList:
    def __init__(self, file_name: str) -> None:
        with open(file_name, encoding='cp866') as hosts_file:
            self.hosts = [host.split() for host in hosts_file.read().split('\n') if host.strip()]

    def save_hosts(self) -> None:
        with open('hosts.txt', 'w', encoding='cp866') as hosts_file:
            hosts_file.write('\n'.join([' '.join(host) for host in self.hosts]))

    def add_host(self, host) -> bool:
        if not host.split() in self.hosts:
            self.hosts.append(host.split())
            self.save_hosts()
            return True
        else:
            return False

    def del_host(self, host_num):
        del self.hosts[host_num]
        self.save_hosts()

    def ping_all(self):
        res = []

        for host in self.hosts:
            ping_res = ping(host[1])
            res.append(host + [['Offline'], ['Online']][ping_res])
        return res


class TableFromList(QWidget):
    def __init__(self, data, headers):
        super().__init__()
        self.data = data
        self.headers = headers
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Power Viewer LAN')
        self.setGeometry(100, 100, 350, 400)

        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.show_add_dialog)

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.refresh_table)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.refresh_button)

        layout.addLayout(button_layout)

        self.tableWidget = QTableWidget()
        layout.addWidget(self.tableWidget)
        self.setLayout(layout)

        self.populate_table()

    def show_add_dialog(self):
        dialog = AddHostDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, ip = dialog.get_host_data()
            if name and ip:
                host_list.add_host(f"{name} {ip}")
                self.refresh_table()

    def refresh_table(self):
        self.data = host_list.ping_all()
        self.populate_table()

    def populate_table(self):
        num_rows = len(self.data)
        num_cols = len(self.headers)

        self.tableWidget.setRowCount(num_rows)
        self.tableWidget.setColumnCount(num_cols)
        self.tableWidget.setHorizontalHeaderLabels(self.headers)

        for row_idx, row_data in enumerate(self.data):
            for col_idx, item_data in enumerate(row_data):
                item = QTableWidgetItem(str(item_data))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if 'Offline' == row_data[-1]:
                    item.setBackground(QColor(100, 0, 0))
                else:
                    item.setBackground(QColor(0, 100, 0))
                self.tableWidget.setItem(row_idx, col_idx, item)

            button = QPushButton("Delete")
            button.clicked.connect(lambda _, r=row_idx: self.delete_row(r))

            button_widget = QWidget()
            button_layout = QHBoxLayout(button_widget)
            button_layout.addWidget(button)
            button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_widget.setLayout(button_layout)

            self.tableWidget.setCellWidget(row_idx, num_cols - 1, button_widget)

    def delete_row(self, row):
        self.tableWidget.removeRow(row)
        host_list.del_host(row)


if __name__ == '__main__':
    host_list = HostList('hosts.txt')

    app = QApplication(sys.argv)

    data = host_list.ping_all()

    headers = ["name", "ip", 'button']

    ex = TableFromList(data, headers)
    ex.show()
    sys.exit(app.exec())