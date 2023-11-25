# HTTP Implementation

This is project idea was taken from [&#34;Build Your Own HTTP server&#34; Challenge](https://app.codecrafters.io/courses/http-server/overview) in Python.

I built a multi-threaded server, implementing Http.

## Endpoints

- GET /echo/<echo-message> - echo <echo-message> back to client

- GET /user-agent - retrieves and sends back to client User-Agent they used in their HttP Request

- GET /files/<filename> - retrieves data from file in <directory>/<filename> and sends it back to client in bytes

- POST /files/<filename> - Creates new file in <directory>/<filename> with given data from client (sent in bytes)


## Launch

To launch needs to give a --directory CLI argument, where it will create and fetch files and their data.

```shell
$ python3 /home/filipe/Desktop/codecrafters/codecrafters-http-server-python/app/main.py --directory /home/filipe/Desktop/codecrafters/codecrafters-http-server-python/files
```


## Testing

To test various endpoint use postman or curl, use -v flag in curl to better see HTTP exchanges:

```shell
$ curl http://localhost:4221/echo/my_message_wow
```

```shell
$ curl http://localhost:4221/user-agent
```

```shell
$ curl http://localhost:4221/user-agent -A ""
```

```shell
$ curl http://localhost:4221/files/file.txt
```

```shell
$ curl --data-binary $'\x48\x65\x6c\x6c\x6f\x2c\x20\x77\x6f\x72\x6c\x64' http://localhost:4221/files/file.txt
```

Some links given by codecrafters.io:
- [HTTP](https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol) is the protocol that powers the web. In this challenge, you'll build a HTTP/1.1 server that is capable of serving multiple clients.
- Along the way you'll learn about TCP servers, [HTTP request syntax](https://www.w3.org/Protocols/rfc2616/rfc2616-sec5.html), and more.


## What I Learned

Python code:
   - OOP
   - Builder design pattern
   - Parsing bytes <-> to str
   - Error handling and creating custom Exceptions
   - Building multi-threaded server
   - CLI arguments
   - File handling (creation, reading, writing, bytes/str)
   - Documentation (Docstrings)
   - Importing libraries (custom as well)

HTTP:
   - Http request structure: Request line / *(Headers CRLF) CRLF / Body
   - How path and path routing works in servers/frameworks
   - Http response structure and how it's built
   
   Interesting:
      - it's common for http unrecognized headers to be ignored
      - in handle_post_files if I have with_content_length(0) then connection stays alive otherwise it closes, not sure why, some http specification?


## TODO in future?

- Add tests, both in e2e/integration/unit. maybe having a script with curl calls?
- Learn more of http "edge-cases"
- Use/Add Enums
- My http implementation seems static. In real servers i will use netcat and send data in segments and server will retain and parse http only when it gives last CRLF (notifying that http request is sent). But in my implementation server parses as what it gets as a whole which is not conformant with real life it seems. Python has libraries that do this "from http.server import BaseHTTPRequestHandler, HTTPServer" (ask chatgpt for example). I would like to implement it like so in the future.


## ChatGPT thinks of my current version (some don't make sense?)

Your implementation looks quite solid! You've organized your code well and included comments that make it clear what each part of your code is doing. Here are a few suggestions for improvement:

1. Use Enum for HTTP Status Codes:
Consider using Python Enums for HTTP status codes. Enums make the code more readable and prevent errors from mistyping status codes.

2. Logging Instead of print:
Instead of using print statements for debugging, consider using Python's logging module. It provides a more flexible and standardized way to log messages, and you can easily configure it to write logs to files or different output streams.

3. Handle Edge Cases in handle_get_files and handle_post_files:
In handle_get_files and handle_post_files, you assume that http_path has a certain structure. It might be a good idea to add checks or error handling to ensure the expected structure.

4. Improve Error Handling:
While you have some error handling in place, consider refining it further. For example, in handle_post_files, if the body is not of type bytes, you return a 400 response. It might be helpful to provide more specific error messages in such cases.

5. Consistent Encoding/Decoding:
Ensure consistent use of encoding/decoding throughout your code. For instance, in handle_get_echo, you directly split http_path, which is a string, but later in handle_post_files, you check if the body is of type bytes before processing.

6. Use HTTP/1.0 as Default:
Your HTTP request parsing assumes HTTP/1.1. If you want to handle HTTP/1.0 requests as well, you might need to adjust your parsing logic accordingly.

7. Improve the HttpResponseBuilder Class:
The HttpResponseBuilder class is flexible, but you could further enhance it. For example, you could enforce that certain fields must be set before calling build, or you could provide default values for certain fields.

8. Documentation for HTTP Methods:
Consider adding docstrings to the functions that handle different HTTP methods (handle_get_echo, handle_get_user_agent, etc.) to explain their purpose and expected parameters.

9. Use os.path.join for File Paths:
You're correctly using os.path.join in some places, but ensure consistent use, especially in file paths.

10. Test Cases:
Consider adding unit tests to validate the behavior of your functions, especially the request parsing logic.

11. Handle SIGINT in a More Robust Way:
Instead of using a KeyboardInterrupt exception, consider using a signal handler for SIGINT to gracefully shut down your server.

12. Consistent Naming:
Ensure consistent naming conventions for variables and functions (e.g., handle_get_echo, handle_client_connection). This helps improve code readability.

Remember that these are just suggestions, and the improvements depend on the specific requirements and preferences. Overall, your implementation demonstrates a good understanding of the HTTP protocol and socket programming.