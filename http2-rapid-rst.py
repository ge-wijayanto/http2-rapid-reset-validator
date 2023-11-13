import ssl, socket, datetime
import urllib.parse
import http.client
import h2.connection, h2.config
import httpx
import requests
from colorama import Fore, Back, Style

## Check HTTP/2 Support for the Target URL
def checkHTTP2(url):
    try:
        client_op = {
            'http2': True, # Enable HTTP/2 support
            'verify': False # Disable SSL verification
        }

        # Send HTTP/2 request
        with httpx.Client(**client_op) as client:
            response = client.get(url)
        
        if response.http_version == 'HTTP/2':
            return (1, '') # HTTP/2 supported
        else:
            return (0, f'{response.http_version}') # HTTP/2 not supported
    except Exception as err:
        return (-1, f'check_http2_support - {err}') # Error

## Send HTTP/2 RST_STREAM Frame
def sendHTTP2RST(host,port,path='/',timeout=5):
    try:
        # Create an SSL Context
        context = ssl.create_default_context()
        context.check_hostname = False # Disable hostname verification
        context.verify_mode = ssl.CERT_NONE # Disable SSL verification

        # Create an HTTP/2 connection
        conn.connect()

        # Send HTTP/2 RST_STREAM Frame
        conf = h2.config.H2Configuration(client_side=True) # Create an H2 Configuration
        conn = h2.connection.H2Connection(config=conf) # Create an H2 Connection
        conn.initiate_connection() # Initiate an H2 Connection
        sock = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=url) # Create an SSL Socket
        sock.connect((url, 443))
        sock.settimeout(5)
        sock.sendall(conn.data_to_send()) # Send an H2 Connection

        headers = [
            (':method', 'GET'),
            (':authority', host),
            (':scheme', 'https'),
            (':authority', url),
            (':path', path)
        ]
        conn.send_headers(1, headers, end_stream=True) # Send an H2 Request
        sock.sendall(conn.data_to_send()) # Send an H2 Connection

        while True:
            data = sock.recv(65535)
            if not data:
                break
            events = conn.receive_data(data) # Receive H2 Events
            sent = False
            for event in events:
                if isinstance(event, h2.events.StreamReset): # Check if the event is an H2 RST_STREAM Frame
                    # return (1, '')
                    sent = True
                    break
            if sent:
                return (1, '') # H2 RST_STREAM Frame sent
            else:
                return (0, '') # H2 RST_STREAM Frame not sent
        conn.close_connection()
        sock.close()
        return (0, '')
    except Exception as err:
        return (-1, f'check_http2_rst - {err}')

def sliceURL(url):
    try:
        parsed = urllib.parse.urlparse(url)
        scheme = parsed.scheme
        path = parsed.path
        host = parsed.hostname
        port = parsed.port
        query = parsed.query
        fragment = parsed.fragment

        if path == '':
            path = '/'
        if query == '':
            query = None
        if fragment == '':
            fragment = None
        if not host:
            return (-1, 'Invalid URL')
        if port:
            return host, port, path
        if scheme == 'http':
            return host, 80, path
        elif scheme == 'https':
            return host, 443, path

        return host, (80,443), path
    except Exception as err:
        return (-1, f'slice_url - {err}')

if __name__ == "__main__":
        url = input('Enter URL: ')
        
        h2support, err = checkHTTP2(url)
        host, port, path = sliceURL(url)

        print(f'[{Fore.CYAN}*{Style.RESET_ALL}] Start: {Fore.CYAN}{datetime.datetime.now()}{Style.RESET_ALL}')
        print(f'[{Fore.CYAN}!{Style.RESET_ALL}] Checking {Fore.CYAN}{url}{Style.RESET_ALL}')

        h2rst = sendHTTP2RST(host,port,path)

        if h2support == 1:
            print(f'[{Fore.YELLOW}!{Style.RESET_ALL}] {Fore.CYAN}{url}{Style.RESET_ALL} is {Fore.YELLOW}supporting HTTP/2{Style.RESET_ALL}')
            h2rst, err2 = sendHTTP2RST(host,port,path)
            if h2rst == 1:
                print(f'[{Fore.RED}!{Style.RESET_ALL}] {Fore.CYAN}{url}{Style.RESET_ALL} is {Fore.RED}VULNERABLE to HTTP/2 Rapid Reset{Style.RESET_ALL}')
            else:
                print(f'[{Fore.GREEN}!{Style.RESET_ALL}] {Fore.CYAN}{url}{Style.RESET_ALL} is {Fore.GREEN}NOT VULNERABLE to HTTP/2 Rapid Reset{Style.RESET_ALL}')
        else:
            print(f'[+] {Fore.CYAN}{url}{Style.RESET_ALL} is {Fore.GREEN}not supporting HTTP/2{Style.RESET_ALL}')