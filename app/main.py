'''
    Author: Filipe Serina
    
    Read README.md for more details
'''
import socket
import threading
import argparse
import os
from httpHelp import HttpResponse, HttpRequest, HttpRequestParsingError, build_400_http_response

global serving_directory

def handle_get_echo(http_path):
    '''
        Echo back to client message in Http Request headers: /echo/<message>
        
        Parameters:
        - http_path (str): @HttpRequest.path containing message to echo back

        Returns:
        @HttpResponse: Appropriate @HttpResponse
    '''
    echo_message = http_path.split("/")[2]
    return HttpResponse() \
        .toBuilder() \
        .with_status_code(200) \
        .with_content_type("text/plain") \
        .with_content_length(len(echo_message)) \
        .with_body(echo_message) \
        .build() \
        .encode()


def handle_get_user_agent(http_headers):
    '''
        Retrieves User-Agent from Http Request and sends it back.
        If no User-Agent in Http Request headers then returns appropriate @HttpResponse.
        
        Parameters:
        - http_headers (dict): @HttpRequest.headers dictionary of headers {str: None|str}

        Returns:
        @HttpResponse: Appropriate @HttpResponse
    '''
    user_agent = http_headers.get("User-Agent", None)
    if user_agent:
        return HttpResponse() \
            .toBuilder() \
            .with_status_code(200) \
            .with_content_type("text/plain") \
            .with_content_length(len(user_agent)) \
            .with_body(user_agent) \
            .build() \
            .encode()
    else:
        return build_400_http_response('Error: no User-Agent found in your HTTP headers')


def handle_get_files(http_path):
    '''
        Retrieves file data (in bytes) from a given filename.
        Uses directory chosen when launching application through CLI args.
        If file with given name does not exist, returns appropriate @HttpResponse
        
        Parameters:
        - http_path (str): @HttpRequest.path containing filename

        Returns:
        @HttpResponse: Appropriate @HttpResponse
    '''
    filename = http_path.split("/")[-1]
    file_path = os.path.join(serving_directory, filename)
    
    if os.path.isfile(file_path):
        with open(file_path, 'rb') as file_stream:
            file_content = file_stream.read()
            return HttpResponse() \
                .toBuilder() \
                .with_status_code(200) \
                .with_content_type('application/octet-stream') \
                .with_content_length(len(file_content)) \
                .with_body(file_content) \
                .build() \
                .encode()
    
    else:
        return build_400_http_response(f'Error: no file by the name of "{filename}"')


def handle_post_files(http_path, body):
    '''
        Create new file with given data (in bytes).
        Uses directory chosen when launching application through CLI args.
        If filename is already in use, returns appropriate @HttpResponse
        
        Parameters:
        - http_path (str): @HttpRequest.path containing name for new file
        - body (bytes): Given data to write in file

        Returns:
        @HttpResponse: Appropriate @HttpResponse
    '''
    filename = http_path.split("/")[-1]
    file_path = os.path.join(serving_directory, filename)
    
    if not isinstance(body, bytes):
        return build_400_http_response(f'Error: body of HTTP request is in wrong format')

    if not os.path.exists(file_path):
        with open(file_path, 'wb') as file_stream:
            file_stream.write(body)
        
        return HttpResponse() \
                .toBuilder() \
                .with_status_code(201) \
                .with_content_length(0) \
                .build() \
                .encode()
    
    else:
        return build_400_http_response(f'Error: file by the name of "{filename}" already exists')


def get_http_response(request_bytes):
    '''
    Does:
        - Parse http request
        - Redirect to each logic handler, giving only necessary parameters
        - Error handling of parsing and 500s
        
    Parameters:
        - request_bytes (bytes): raw Http request received from client connection

        Returns:
        bytes: @HttpResponse encoded in bytes in compliant with HTTP
    '''
    
    try:
        http_request = HttpRequest(request_bytes)
    
        if http_request.method == 'GET' and http_request.path.startswith('/echo') and len(http_request.path.split("/")) == 3:
            return handle_get_echo(http_request.path)
            
        elif http_request.method == 'GET' and http_request.path == '/user-agent':
            return handle_get_user_agent(http_request.headers)
            
        elif http_request.method == 'GET' and http_request.path.startswith('/files') and len(http_request.path.split("/")) == 3:
            return handle_get_files(http_request.path)
            
        elif http_request.method == 'POST' and http_request.path.startswith('/files') and len(http_request.path.split("/")) == 3:
            return handle_post_files(http_request.path, http_request.body)
                
        else:
            return HttpResponse() \
                .toBuilder() \
                .with_status_code(404) \
                .with_content_length(0) \
                .build() \
                .encode()
        
    except HttpRequestParsingError as e:
        return build_400_http_response(f"Error: {e}")
    
    except Exception as e:
        error_message = f'Error: {e}'
        return HttpResponse() \
            .toBuilder() \
            .with_status_code(500) \
            .with_content_type('text/plain') \
            .with_content_length(len(error_message)) \
            .with_body(error_message) \
            .build() \
            .encode()


def handle_client_connection(client_socket, address):
    print(f'client connected: address = {address}') # do this in a log file
    client_socket.sendall(get_http_response(client_socket.recv(1024)))
    client_socket.close()


def main():
    '''
    Validates --directory CLI param was given.
    Creates and starts Multi-treaded server.
    '''
    
    global serving_directory
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True, help="The directory to serve files from")
    args = parser.parse_args()
    serving_directory = args.directory

    server_address, server_port = "localhost", 4221
    server_socket = socket.create_server((server_address, server_port), reuse_port=True)
    ''' Line above odes this, not sure about reuse_port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 4221))
    s.listen()
    '''
    print(f'Server running: address={server_address} in port={server_port}')

    try:
        while True:
            client_socket, address = server_socket.accept() # wait for client
            client_thread = threading.Thread(target=handle_client_connection, args=(client_socket, address))
            client_thread.daemon = True
            client_thread.start()
    except KeyboardInterrupt:
        server_socket.close()


if __name__ == "__main__":
    main()
