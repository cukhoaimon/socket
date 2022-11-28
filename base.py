import socket
import re
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def get_header(client) -> str:
    header = ""
    try:
        data = b''
        while data[-4:] != b'\r\n\r\n':
            data += client.recv(1)

        header = data.decode()
    except UnicodeDecodeError as e:
        print(e)
        exit(324)
    finally:
        return header


def parse_html_page(html_page) -> list:
    _files = []
    try:
        soup = BeautifulSoup(html_page, 'html.parser')
        _files = soup.find_all('a')
    except _files is not None:
        print("Empty list")
        exit(330)

    pattern = ".*\..*"
    ls = []
    for file in _files:
        if re.match(pattern, str(file)) is not None:
            ls.append(file.text)

    return ls


def is_chunked_encoding(header) -> bool:
    match = re.search("Transfer-Encoding: chunked", header)
    if match is not None:
        return True
    else:
        return False


def is_folder(url, header):
    if is_chunked_encoding(header) is True:
        return False
    else:
        host, path = url_parse(url)
        if path == '/':
            return False
        elif path[-1] == '/':
            return True
        else:
            return False



def get_file_name(url):
    host, path = url_parse(url)
    name = re.split('/', url)
    if name[-1] == '' or name[-1] == host:
        name = "index.html"
    else:
        name = name[-1]

    name = host + '_' + name

    return name


def get_folders_directory(url):
    temp = re.split('/', url)

    if temp != ['']:
        return  temp[-2]
    else:
        exit(329)


def url_parse(url):
    u = urlparse(url)
    return u.netloc, u.path


def send(client, host, path, file_name=''):
    file_name = file_name.replace (' ', '%20')
    path = path.replace(' ', '%20')
    request = f"GET {path}{file_name} HTTP/1.1\r\nHost:{host}\r\nConnection: Keep-Alive\r\n\r\n"
    try:
        request = request.encode()
    except UnicodeDecodeError as err:
        print(err)
        exit(324)

    try:
        client.send(request)
    except InterruptedError as err:
        print(err)
        exit(323)


def get_content_length(header) -> int:
    size = 0
    try:
        x = re.search("Content-Length:.*\r\n", header)
        if x is None:
            print("Error when getting header")
            exit(327)

        size = int(header[x.start() + len("Content-Length:"): x.end() - len('\r\n')])
    except AttributeError as e:
        print(e)
        exit(326)

    return size


def content_length_case(client, header, file_name) -> bytes:
    print(f'[Client] Downloading {file_name}...')

    length = get_content_length(header)

    data = b''
    while len(data) < length:
        data += client.recv(length - len(data))

    return data


def parse_chunk(client) -> int:
    # Get the size of chunk
    temp = client.recv(2)

    # check whether the chunk is the final chunk or not
    if temp == b'\r\n':
        return 0
    else:
        while temp[-2:] != b'\r\n':
            temp += client.recv(1)

        # delete '\r\n' at the end
        try:
            temp = temp[0:-2].decode()
        except UnicodeDecodeError as err:
            print(err)
            exit(324)

        # cast from hex-bytes to int
        chunk = int(temp, base=16)
        return chunk


def chunked_case(client, file_name) -> bytes:
    data = b''
    chunk_size = parse_chunk(client)

    print(f'[Client] Downloading {file_name}...')
    while chunk_size != 0:
        temp = b''
        while len(temp) < chunk_size:
            temp += client.recv(chunk_size - len(temp))

        data += temp

        # Ignore '\r\n'
        client.recv(2)
        chunk_size = parse_chunk(client)

    return data


def receive(client, header, file_name):
    # lay du lieu cua file vao bien data
    data = b''
    try:
        # chunked transfer encoding
        if is_chunked_encoding(header) is True:
            data = chunked_case(client, file_name)
        else:
            # content length
            data = content_length_case(client, header, file_name)
    except data == b'':
        print(f"There are some error when downloading {file_name}")
        exit(325)

    # write data to file
    with open(file_name, 'w+b') as f:
        f.write(data)

    print (f'[Client] Successful download {file_name}')


def download_folder(client, url, header):
    host, path = url_parse(url)

    # get html page
    length = get_content_length(header)
    page = b''
    while len (page) < length:
        page += client.recv(length - len(page))

    # Parse to get all file name in sub folder
    file_names = []
    try:
        file_names = parse_html_page(page.decode())
    except UnicodeDecodeError as err:
        print(err)
        exit(324)

    try:
        # Send all request
        for file_name in file_names:
            send(client, host, path, file_name)

        folder_name = host + '_' + get_folders_directory(path)

        # receive all data
        for file_name in file_names:
            # adjust file_name if download folder or not
            if folder_name != '':
                # if download folder then create folder
                try:
                    # if folder is not exist
                    os.mkdir(folder_name)
                except OSError:
                    # if folder existed then pass
                    pass

                # adjust file_name
                file_name =  folder_name + '/' + host + '_' +file_name
            else:
                pass
            header = get_header(client)
            receive(client, header, file_name)
    except Exception as err:
        print(err)
        exit(331)



def download(url):
    host, path = url_parse(url)
    port = 80

    # connect to get html page
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((host, port))
        send(client, host, path)
    except InterruptedError as err:
        print(err)
        exit(323)

    header = get_header(client)

    if is_folder(url, header):
        download_folder(client, url, header)
    else:
        file_name = get_file_name(url)
        receive(client, header, file_name)

    client.close()



