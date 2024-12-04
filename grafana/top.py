import psutil
import GPUtil
from time import sleep
from time import time
from config import *

from psycopg2 import connect
import psycopg2

class OpenGaussConnector:
    def __init__(self, ip, port, user, pwd, database) -> None:
        params = {
            'database': database,
            'user': user,
            'password': pwd,
            'host': ip,
            'port': port
        }
        self.conn = connect(**params)
    
    def exec(self, cmd:str):
        with self.conn:
            with self.conn.cursor() as cursor:
                cursor.execute(cmd)
                try:
                    result = cursor.fetchall()
                except psycopg2.ProgrammingError as e:
                    if str(e).strip() == 'no results to fetch':
                        return None
                    else:
                        raise e
        return result
    
    def get_one_res(self, cmd:str):
        res = self.exec(cmd)
        if len(res) == 0:
            return None
        elif len(res) > 1:
            raise Exception(f"more than 1 result, cmd={cmd}")
        else:
            return res[0]

def avg(lst):
    return sum(lst) / len(lst)
# print(f"{avg(psutil.cpu_percent(interval=0.5, percpu=True))}%")
def get_cpu_percent():
    return avg(psutil.cpu_percent(interval=0.5, percpu=True))
def get_mem_percent():
    return psutil.virtual_memory().percent

def get_mem_total():
    return psutil.virtual_memory().total/(1024*1024)

def get_mem_used():
    return psutil.virtual_memory().used/(1024*1024)

disk_io_start = psutil.disk_io_counters()
last_time = time()
def get_disk_io_rate():
    global disk_io_start, last_time
    disk_io_end = psutil.disk_io_counters()
    current_time = time()
    read_bytes = disk_io_end.read_bytes - disk_io_start.read_bytes
    write_bytes = disk_io_end.write_bytes - disk_io_start.write_bytes

    read_rate = read_bytes / (current_time - last_time)
    write_rate = write_bytes / (current_time - last_time)

    disk_io_start = disk_io_end
    last_time = current_time
    return read_rate, write_rate

net_io_start = psutil.net_io_counters()
last_time_net = time()
def get_network_traffic():
    global net_io_start, last_time_net
    net_io_end = psutil.net_io_counters()
    current_time = time()
    send_bytes = net_io_end.bytes_sent - net_io_start.bytes_sent
    recv_bytes = net_io_end.bytes_recv - net_io_start.bytes_recv
    
    send_rate = send_bytes / (current_time - last_time_net)
    recv_rate = recv_bytes / (current_time - last_time_net)
    
    net_io_start = net_io_end
    last_time_net = current_time
    if send_rate < 0:
        send_rate = 0
    if recv_rate < 0:
        recv_rate = 0
    return send_rate, recv_rate

def get_gpu():
    """
    Returns: gpu load, gpu memory percentage, gpu memory used, gpu memory total, gpu temperature
    """
    GPUs = GPUtil.getGPUs()
    if len(GPUs) == 0:
        return 0, 0
    else:
        return GPUs[0].load, GPUs[0].memoryUtil, GPUs[0].memoryUsed, GPUs[0].memoryTotal, GPUs[0].temperature
    
def main(db:OpenGaussConnector, flush=10):
    while True:
        cpu_percent = get_cpu_percent()
        mem_percent = get_mem_percent()
        gpu_load, gpu_mem_percent, gpu_mem_used, gpu_mem_total, gpu_temp = get_gpu()
        db.exec(
            f"""INSERT INTO gauge VALUES ('now', {cpu_percent}, {mem_percent}, {gpu_load}, {gpu_mem_percent});"""
        )
        db.exec(
            f"""INSERT INTO memory VALUES ('now', {get_mem_total()}, {get_mem_used()});"""
        )
        db.exec(
            f"""INSERT INTO gpumem VALUES ('now', {gpu_mem_total}, {gpu_mem_used});"""
        )
        sleep(flush)
        read_rate, write_rate = get_disk_io_rate()
        db.exec(
            f"""INSERT INTO diskio VALUES ('now', {read_rate / 1024/1024}, {write_rate / 1024/1024});"""
        )
        send_rate, recv_rate = get_network_traffic()
        db.exec(
            f"""INSERT INTO netio VALUES ('now', {send_rate / 1024/1024}, {recv_rate / 1024/1024});"""
        )

if __name__ == "__main__":
    db = OpenGaussConnector(
        ip=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        pwd=DB_PWD,
        database=DB_CONNECT_DB
    )
    main(db)