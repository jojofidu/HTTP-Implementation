'''
    Author: Filipe Serina
    
    Read README.md for more details
'''
class HttpRequest:
    
    def __init__(self, request: bytes) -> None:
        request_parts = request.split(b"\r\n")
        
        self.method, self.path, self.version = request_parts[0].decode().split(" ")
        
        self.headers = {"User-Agent": None, "Host": None, "Content-Length": None, "Content-Type": None}
        
        for index, line in enumerate(request_parts):
            
            if index == 0:
                self.method, self.path, self.version = line.decode().split(" ")
            
            elif b': ' in line:
                header = line.decode().split(': ')
                if header[0] in self.headers:
                    self.headers[header[0]] = header[-1]
            
            # allows for more CRLFs but only fetch the line right after the double CRLF into the body
            elif line == b'' and len(request_parts) > index + 1:
                if self.headers['Content-Type'] is not None and 'application/x-www-form-urlencoded' in self.headers['Content-Type']:
                    self.body = request_parts[index+1]  # Keep body as bytes
                else:
                    self.body = request_parts[index+1].decode()
                break
            
            else:
                print(line)
                print(line == b'')
                print(f'{len(request_parts) > index + 1}  c   {request_parts}   c   {index}')
                print(self.body)
                raise HttpRequestParsingError(message='Wrong format of HTTP request')


class HttpResponse:
    
    def __init__(self, status_code=None, content_type=None, content_length=None, body=None):
        self.status_code = status_code
        self.content_type = content_type
        self.content_length = content_length
        self.body = body
        
    def toBuilder(self):
        return HttpResponseBuilder()
    
    def encode(self) -> bytes:       
        response = f'HTTP/1.1 {self.status_code}\r\n'
        
        if self.content_type:
            response = f'{response}Content-type: {self.content_type}\r\n'
            
        if self.content_length is not None:
            response = f'{response}Content-Length: {self.content_length}\r\n'
            
        response = f'{response}\r\n'.encode()

        if self.body:
            if isinstance(self.body, bytes):
                response = response + self.body
            else:
                response = response + self.body.encode()
        return response

    def __str__(self):
        return f'HttpResponse(status_code={self.status_code}, content_type={self.content_type}, content_length={self.content_length}, body={self.body})'


class HttpRequestParsingError(Exception):
    def __init__(self, message="Parsing of HTTP request"):
        self.message = message
        super().__init__(self.message)


class HttpResponseBuilder:
    def __init__(self, status_code=None, content_type=None, content_length=None, body=None):
        self.status_code = status_code
        self.content_type = content_type
        self.content_length = content_length
        self.body = body
    
    # TODO could be done with enums
    def with_status_code(self, status_code):
        if status_code == 200:
            self.status_code = '200 OK'
        if status_code == 201:
            self.status_code = '201 CREATED'
        elif status_code == 400:
            self.status_code = '400 BAD REQUEST'
        elif status_code == 404:
            self.status_code = '404 NOT FOUND'
        elif status_code == 500:
            self.status_code = '500 INTERNAL SERVER ERROR'
        else:
            self.status_code = status_code
        return self

    def with_content_type(self, content_type):
        self.content_type = content_type
        return self

    def with_content_length(self, content_length):
        self.content_length = content_length
        return self

    def with_body(self, body):
        self.body = body
        return self

    def build(self):
        return HttpResponse(
            status_code=self.status_code,
            content_type=self.content_type,
            content_length=self.content_length,
            body=self.body
        )
        
        
def build_400_http_response(error_message):
    return HttpResponse() \
        .toBuilder() \
        .with_status_code(400) \
        .with_content_type('text/plain') \
        .with_content_length(len(error_message)) \
        .with_body(error_message) \
        .build() \
        .encode()
