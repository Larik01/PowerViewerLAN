import subprocess


def cmd(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    result = process.communicate()[0].decode("utf-8")
    return result


def ping(ip):
    command = f'ping {ip} -n 1'
    result = cmd(command)
    return result


def get_router_ip():
    return cmd('ipconfig').split('\n')[9].split()[-1]


print(ping(get_router_ip()))