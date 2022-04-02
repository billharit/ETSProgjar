import sys
import socket
import logging
import json
import os
import ssl
import threading

DataPemain = {
    '1': {'nomor': 1, 'nama': 'Pemain 1'},
    '2': {'nomor': 2, 'nama': 'Pemain 2'},
    '3': {'nomor': 3, 'nama': 'Pemain 3'},
    '4': {'nomor': 4, 'nama': 'Pemain 4'},
    '5': {'nomor': 5, 'nama': 'Pemain 5'},
    '6': {'nomor': 6, 'nama': 'Pemain 6'},
    '7': {'nomor': 7, 'nama': 'Pemain 7'},
    '8': {'nomor': 8, 'nama': 'Pemain 8'},
    '9': {'nomor': 9, 'nama': 'Pemain 9'},
    '10': {'nomor': 10, 'nama': 'Pemain 10'},
    '11': {'nomor': 11, 'nama': 'Pemain 11'},
    '12': {'nomor': 12, 'nama': 'Pemain 12'},
    '13': {'nomor': 13, 'nama': 'Pemain 13'},
    '14': {'nomor': 14, 'nama': 'Pemain 14'},
    '15': {'nomor': 15, 'nama': 'Pemain 15'},
    '16': {'nomor': 16, 'nama': 'Pemain 16'},
    '17': {'nomor': 17, 'nama': 'Pemain 17'},
    '18': {'nomor': 18, 'nama': 'Pemain 18'},
    '19': {'nomor': 19, 'nama': 'Pemain 19'},
    '20': {'nomor': 20, 'nama': 'Pemain 20'},
}

def versi():
    return "versi 0.0.1"

def proses_request(request_string):
    #format request
    # NAMACOMMAND spasi PARAMETER
    cstring = request_string.split(" ")
    hasil = None
    try:
        command = cstring[0].strip()
        if (command == 'getdatapemain'):
            # getdata spasi parameter1
            # parameter1 harus berupa nomor pemain
            # logging.warning("getdata")
            nomorpemain = cstring[1].strip()
            try:
                # logging.warning(f"data {nomorpemain} ketemu")
                hasil = DataPemain[nomorpemain]
            except:
                hasil = None
        elif (command == 'versi'):
            hasil = versi()
    except:
        hasil = None
    return hasil

def serialisasi(a):
    #print(a)
    #serialized = str(dicttoxml.dicttoxml(a))
    serialized =  json.dumps(a)
    # logging.warning("serialized data")
    logging.warning(serialized)
    return serialized

def acceptConnection(client_address, connection):
    selesai=False
    data_received="" #string
    while True:
        data = connection.recv(32)
        # logging.warning(f"received {data}")
        if data:
            data_received += data.decode()
            if "\r\n\r\n" in data_received:
                selesai=True

            if (selesai==True):
                hasil = proses_request(data_received)
                logging.warning(f"Hasil Response: {hasil}")

                #hasil bisa berupa tipe dictionary
                #harus diserialisasi dulu sebelum dikirim via network
                # Send data
                # some data structure may have complex structure
                # how to send such data structure through the network ?
                # use serialization
                #  example : json, xml

                # complex structure, nested dict
                # all data that will be sent through network has to be encoded into bytes type"
                # in this case, the message (type: string) will be encoded to bytes by calling encode

                hasil = serialisasi(hasil)
                hasil += "\r\n\r\n"
                connection.sendall(hasil.encode())
                selesai = False
                data_received = ""  # string
                break

        else:
            logging.warning(f"no more data from {client_address}")
            break

def run_server(server_address,is_secure=False):
    # ------------------------------ SECURE SOCKET INITIALIZATION ----
    print("SERVERADDRES")
    print(server_address)
    if is_secure == True:
        print(os.getcwd())
        cert_location = os.getcwd() + '/certs/'
        socket_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        socket_context.load_cert_chain(
            certfile=cert_location + 'domain.crt',
            keyfile=cert_location + 'domain.key'
        )
    # ---------------------------------

    #--- INISIALISATION ---
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind the socket to the port
    logging.warning(f"starting up on {server_address}")
    sock.bind(server_address)
    # Listen for incoming connections
    sock.listen(1000)

    # Initialize Thread
    thread = dict()
    i = 0

    while True:
        # Wait for a connection
        # logging.warning("waiting for a connection")
        koneksi, client_address = sock.accept()
        logging.warning(f"Incoming connection from {client_address}")
        # Receive the data in small chunks and retransmit it

        try:
            if is_secure == True:
                connection = socket_context.wrap_socket(koneksi, server_side=True)
            else:
                connection = koneksi

            thread[i] = threading.Thread(
                target=acceptConnection, args=(client_address, connection))
            thread[i].start()
            i += 1

        # Clean up the connection
        except ssl.SSLError as error_ssl:
            logging.warning(f"SSL error: {str(error_ssl)}")


if __name__=='__main__':
    try:
        run_server(('0.0.0.0', 12000),is_secure=True)
    except KeyboardInterrupt:
        logging.warning("Control-C: Program berhenti")
        exit(0)
    finally:
        logging.warning("seelsai")