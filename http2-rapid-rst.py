import ssl
import sys
import csv
import socket
import argparse
import datetime
import urllib.parse
import http.client
import h2.connection
import h2.config
import httpx
import requests

def checkHTTP2(url):
    try:
        client_op = {
            'http2': True,
            'verify': False
        }

        with httpx.Client(**client_op) as client:
            response = client.get(url)
        
        if response.http_version == 'HTTP/2':
            return (1, '')
        else:
            return (0, f'{response.http_version}')
    except Exception as err:
        return (-1, f'check_http2_support - {err}')

def checkHTTP2RST(url,):
    try:
        context = ssl.create_default_context()
        context.set_alpn_protocols(['h2'])
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        ## context.load_default_certs()

        # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # sock.settimeout(5)
        # sock.connect((url, 443))
        # sock = context.wrap_socket(sock, server_hostname=url)
        # conn = h2.connection.H2Connection(h2.config.H2Configuration(client_side=False))
        # conn.initiate_connection()
        # sock.sendall(conn.data_to_send())

        conf = h2.config.H2Configuration(client_side=True)
        conn = h2.connection.H2Connection(config=conf)
        conn.initiate_connection()
        sock = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=url)
        sock.connect((url, 443))
        sock.settimeout(5)
        sock.sendall(conn.data_to_send())

        headers = [
            (':method', 'GET'),
            (':scheme', 'https'),
            (':authority', url),
            (':path', '/')
            # ('user-agent', 'python-hyper/0.7.0')
        ]
        conn.send_headers(1, headers, end_stream=True)
        sock.sendall(conn.data_to_send())

        while True:
            data = sock.recv(65535)
            if not data:
                break
            events = conn.receive_data(data)
            sent = False
            for event in events:
                if isinstance(event, h2.events.StreamReset):
                    # return (1, '')
                    sent = True
                    break
            if sent:
                return (1, '')
            else:
                return (0, '')
        conn.close_connection()
        sock.close()
        return (0, '')
    except Exception as err:
        return (-1, f'check_http2_rst - {err}')
                
    #     while True:
    #         data = sock.recv(65535)
    #         if not data:
    #             break
    #         events = conn.receive_data(data)
    #         for event in events:
    #             if isinstance(event, h2.events.StreamReset):
    #                 return (1, '')
    #     return (0, '')
    # except Exception as err:
    #     return (-1, f'check_http2_rst - {err}')

if __name__ == "__main__":
        # parser = argparse.ArgumentParser(description='Check HTTP2 Rapid RST')
        # parser.add_argument('-i', '--input', help='Input file', required=True)
        # parser.add_argument('-o', '--output', help='Output file', required=True)
        # args = parser.parse_args()
    
        with open(args.input, 'r') as f:
            reader = csv.reader(f)
            data = list(reader)

        url = input('Enter URL: ')

        print(f'[*] Start: {datetime.datetime.now()}')
        with open(args.output, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['URL', 'HTTP2', 'HTTP2-RST'])
            for url in data:
                url = url[0]
                print(f'[*] Checking {url}')
                http2 = checkHTTP2(url)
                http2_rst = checkHTTP2RST(url)
                writer.writerow([url, http2[0], http2_rst[0]])

                if http2[0] == 1 and http2_rst[0] == 1:
                    print(f'[+] {url} is HTTP2 Rapid RST')
                elif http2[0] == 1 and http2_rst[0] == 0:
                    print(f'[+] {url} is HTTP2 but not Rapid RST')
                elif http2[0] == 0 and http2_rst[0] == 1:
                    print(f'[+] {url} is not HTTP2 but Rapid RST')
                else:
                    print(f'[-] {url} is not HTTP2 and not Rapid RST')