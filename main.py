import subprocess
import sys

from PyQt6.QtWidgets import (QApplication, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QWidget, QPushButton, QHBoxLayout)
from PyQt6.QtCore import Qt


def get_host_list():
    return [host.split()[0] for host in cmd('arp -a').split('\n')[3:-1] if host.split()[-1] == 'dynamic']


def del_host(host_num: int):
    pass


def cmd(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    result = process.communicate()[0].decode("cp866")
    return result


def ping(ip):
    command = f'ping {ip} -n 1'
    result = cmd(command).lower()
    return 'reply' in result or 'ответ' in result


def get_router_ip():
    return cmd('ipconfig').split('\n')[9].split()[-1]


def get_lan_host_list():
    return [host.split()[0] for host in cmd('arp -a').split('\n')[3:-1] if host.split()[-1] == 'dynamic']


class HostList:
    def __init__(self, file_name: str) -> None:
        with open(file_name, encoding='cp866') as hosts_file:
            self.hosts = [host.split() for host in hosts_file.read().split('\n')]

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

    def del_host(self, ip: str):
        for host in self.hosts:
            if host[1] == ip:
                self.hosts.remove(host)
                break
        self.save_hosts()

    def ping_all(self):
        res = []

        for host in self.hosts:
            ping_res = ping(host[1])
            res.append(host + [ping_res])
        return res


class TableFromList(QWidget):
    def __init__(self, data, headers):
        super().__init__()
        self.data = data
        self.headers = headers
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Table')
        self.setGeometry(100, 100, 450, 400)

        layout = QVBoxLayout()
        self.tableWidget = QTableWidget()
        layout.addWidget(self.tableWidget)
        self.setLayout(layout)

        self.populate_table()

    def populate_table(self):
        num_rows = len(self.data)
        num_cols = len(self.headers)

        self.tableWidget.setRowCount(num_rows)
        self.tableWidget.setColumnCount(num_cols)
        self.tableWidget.setHorizontalHeaderLabels(self.headers)

        for row_idx, row_data in enumerate(self.data):
            for col_idx, item_data in enumerate(row_data[:-1]):  # Все кроме последнего элемента (кнопки)
                item = QTableWidgetItem(str(item_data))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Делаем ячейки нередактируемыми
                self.tableWidget.setItem(row_idx, col_idx, item)

            # Добавляем кнопку в последний столбец
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
        # Удаляем строку из таблицы
        self.tableWidget.removeRow(row)
        # Здесь можно добавить логику удаления из вашего host_list


if __name__ == '__main__':
    host_list = HostList('hosts.txt')

    app = QApplication(sys.argv)

    data: [[str]] = list()

    for i in host_list.ping_all():
        data.append(i)

    headers: [str] = ["name", "ip", "status", 'button']

    ex = TableFromList(data, headers)
    ex.show()
    sys.exit(app.exec())
