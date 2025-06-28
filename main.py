import subprocess
import pygame as pg
from pygame.locals import *


def cmd(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    result = process.communicate()[0].decode("utf-8")
    return result


def ping(ip):
    command = f'ping {ip} -n 1'
    result = cmd(command)
    print(ip, len(result))


def get_host_list():
    return [host.split()[0] for host in cmd('arp -a').split('\n')[3:-1] if host.split()[-1] == 'dynamic']


def ping_hosts():
    host_list = get_host_list()
    for host in host_list:
        ping(host)


def read_hosts():
    with open('hosts.txt', encoding='utf-8') as hosts_file:
        return hosts_file.read().split('\n')


def add_host(host: str):
    with open('hosts.txt', 'a', encoding='utf-8') as hosts_file:
        hosts_file.write('\n' + host)


def del_host(host_num: int):
    pass


def blit_all():
    hosts = read_hosts()
    for i, host in enumerate(hosts, 0):
        font = pg.font.SysFont("Comic Sans MS", 100)
        color = (0, 60, 20)
        text_surface = font.render(host, False, color)
        screen.blit(text_surface, (0, i * 100))


hosts = read_hosts()

clock = pg.time.Clock()
pg.init()
screen = pg.display.set_mode((1000, len(hosts * 100)), RESIZABLE)
pg.display.set_caption('PowerViewerLAN')

run = True
while run:
    blit_all()
    for event in pg.event.get():
        if event.type == QUIT:
            run = False
        elif event.type == VIDEORESIZE:
            size_ch = event.dict['size']
            size = tuple(map(lambda x: x if x > 120 else 120, size_ch))
            pg.display.set_mode(size, RESIZABLE)
    pg.display.flip()
    clock.tick(10)
pg.quit()