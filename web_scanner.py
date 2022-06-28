import socket
import time
import random
import threading

import struct
import json

from queue import Queue
socket.setdefaulttimeout(5)
print_lock = threading.Lock()

#target = input('Enter the host to be scanned: ')
#t_IP = socket.gethostbyname(target)

#print ('Starting scan on host: ', t_IP)

class StatusPing:
    """ Get the ping status for the Minecraft server """

    def __init__(self, host='94.250.205.31', port=25565, timeout=0.35):
        """ Init the hostname and the port """
        self._host = host
        self._port = port
        self._timeout = timeout

    def _unpack_varint(self, sock):
        """ Unpack the varint """
        data = 0
        for i in range(5):
            ordinal = sock.recv(1)

            if len(ordinal) == 0:
                break

            byte = ord(ordinal)
            data |= (byte & 0x7F) << 7*i

            if not byte & 0x80:
                break

        return data

    def _pack_varint(self, data):
        """ Pack the var int """
        ordinal = b''

        while True:
            byte = data & 0x7F
            data >>= 7
            ordinal += struct.pack('B', byte | (0x80 if data > 0 else 0))

            if data == 0:
                break

        return ordinal

    def _pack_data(self, data):
        """ Page the data """
        if type(data) is str:
            data = data.encode('utf8')
            return self._pack_varint(len(data)) + data
        elif type(data) is int:
            return struct.pack('H', data)
        elif type(data) is float:
            return struct.pack('L', int(data))
        else:
            return data

    def _send_data(self, connection, *args):
        """ Send the data on the connection """
        data = b''

        for arg in args:
            data += self._pack_data(arg)

        connection.send(self._pack_varint(len(data)) + data)

    def _read_fully(self, connection, extra_varint=False):
        """ Read the connection and return the bytes """
        packet_length = self._unpack_varint(connection)
        packet_id = self._unpack_varint(connection)
        byte = b''

        if extra_varint:
            # Packet contained netty header offset for this
            if packet_id > packet_length:
                self._unpack_varint(connection)

            extra_length = self._unpack_varint(connection)

            while len(byte) < extra_length:
                byte += connection.recv(extra_length)

        else:
            byte = connection.recv(packet_length)

        return byte

    def get_status(self):
        """ Get the status response """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
            connection.settimeout(self._timeout)
            connection.connect((self._host, self._port))

            # Send handshake + status request
            self._send_data(connection, b'\x00\x00', self._host, self._port, b'\x01')
            self._send_data(connection, b'\x00')

            # Read response, offset for string length
            data = self._read_fully(connection, extra_varint=True)

            # Send and read unix time
            self._send_data(connection, b'\x01', time.time() * 1000)
            unix = self._read_fully(connection)

        # Load json and return
        response = json.loads(data.decode('utf8'))
        response['ping'] = int(time.time() * 1000) - struct.unpack('L', unix)[0]
        

        return response
        
class online_server_handler:
	def __init__(self, ip, resp):
		self.ip = ip
		self.resp = resp
		
	def save(self):
		json_resp = self.resp
		
		self.serv_name = json_resp["description"]["text"]
		self.players_max = json_resp["players"]["max"]
		self.players_online = json_resp["players"]["online"]
		self.serv_version = json_resp["version"]["name"]
		self.serv_prot = json_resp["version"]["protocol"]
		
		try:
			if 3 <= int(self.serv_prot) <= 757:
				self.vurn = "Likely"
			else:
				self.vurn = "False"
		except:
			self.vurn = "/"
		
		
		all_data = [self.ip , self.serv_name, self.players_max, self.players_online, self.serv_version, self.serv_prot, self.vurn]
		
		str_data = ""
		
		for i in range(len(all_data)):
			str_data += str(all_data[i]) + ","
			
		str_data = str_data[0:len(str_data)-1]
		
		
		f = open("good_servers.csv", "a+")
		f.write(str_data + "\n")
		f.close()

def save(ip):
    f = open("servers.txt", "a+")
    f.write(ip + "\n")
    f.close()

port = 25565
found_ip = False

def portscan(t_IP):
   global port, found_ips, found_ip
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   try:
     con = s.connect((t_IP, port))
     with print_lock:
       found_ip = True
       print(port, 'is open')
       print(t_IP)
       save(t_IP)
       #con.close()
       
       server = StatusPing(t_IP)
       resp = server.get_status()
       print("SERVER IS UP!!!!!")
       serv_handl = online_server_handler(t_IP, resp)
       serv_handl.save()
       time.sleep(1)

   except:
      #print("an error occured")
      pass
      

def threader():
   while True:
      worker = q.get()
      portscan(worker)
      q.task_done()
      
q = Queue()
startTime = time.time()
   
for x in range(100):
   t = threading.Thread(target = threader)
   t.daemon = True
   t.start()
   
ip = [210, 59, 104, 0]
found_ips = []

def update_ip():
    global ip
    
    if ip[3] != 255:
        ip[3] += 1
    else:
        if ip[2] != 255:
            ip[2] += 1
            ip[3] = 0
        else:
            if ip[1] != 255:
                ip[1] += 1
                ip[2] = 0
                #print(ip)
            else:
                ip[0] += 1
                ip[1] = 0
               # print(ip)
    
   
   
for _ in range(1, 99999999):
   ip = [random.randint(0,255) for _ in range(4)]
   ##ip = [94, 250, 205, 31]
   #update_ip()
   

       
   
   #print(ip)
   good_ip = ""
   for octo in ip:
      good_ip += str(octo) + "."
   good_ip = good_ip[0:len(good_ip)-1]
   worker = good_ip
   q.put(worker)
   ##portscan(good_ip)
   
   #if i %100000 == 0:
   # print(good_ip)
   # print(i)
   
   
   
q.join()
print('Time taken:', time.time() - startTime)

