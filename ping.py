import subprocess
import csv


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


class Host_list:
    def __init__(self, file_name) -> None:
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
            res.append(ping(host[1]))
        return zip(self.hosts, res)


host_list = Host_list('hosts.txt')
data: [{str: str}] = list()

for i in host_list.ping_all():
    dct: {str: str} = {'name': i[0][0], 'ip': i[0][1], 'status': i[1]}
    data.append(dct)

with open('table.csv', 'w', newline='', encoding="utf8") as f:
    writer = csv.DictWriter(
        f, fieldnames=list(data[0].keys()),
        delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()
    for d in data:
        writer.writerow(d)
