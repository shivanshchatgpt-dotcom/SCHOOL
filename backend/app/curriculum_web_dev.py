"""Verified DeepSeek-authored Day 1 content for the Web Development track."""

WEB_DEV_DAY_1 = {
    "day": 1,
    "title": "Python Programs, Variables, Strings, and the Request-Response Cycle",
    "domain": "Python Foundations",
    "objective": "Write and run a first Python program using variables, strings, print(), and comments to simulate how a backend request becomes a response.",
    "theory": """A Python program is a text file of instructions that the Python interpreter runs from top to bottom. In web development, this simple idea becomes powerful: a backend server is a long-running Python program that receives HTTP requests and returns HTTP responses. Each request carries data: a method such as GET or POST, a path such as /about, headers, and sometimes a body. Your code stores that data in variables, builds a response as a string, and sends it back to the browser.

A variable is a named reference to a value stored in memory. Think of it as a labeled box. You create a variable with the assignment operator =. For example, http_method = 'GET' stores the string 'GET' in a variable named http_method. In Python, you do not declare a type; the interpreter infers it from the value. Variable names should be descriptive and follow snake_case: request_path, status_code, response_body. A string is a sequence of characters enclosed in single or double quotes. Strings are everywhere in web development: URLs, HTML, JSON, headers, cookies, and user input all arrive as text.

The print() function displays values to the console. It is your first debugging tool: when you are unsure what a variable contains, print it. Comments begin with #. Python ignores them. Comments are not for the computer; they are for you and your teammates. In a web project, comments explain why a route exists or why a validation rule is strict.

A useful mental model is a restaurant. The browser is a customer placing an order. The HTTP request is the order ticket. The backend is the kitchen. Variables are labeled containers where the kitchen stores ingredients and order details. Strings are the text written on the ticket and final receipt. print() is the kitchen display. Comments are notes on the recipe. The response is the meal sent back to the customer. This model matters because every web framework, from Flask to Django, is ultimately managing variables, strings, and output.

Common mistakes include forgetting quotes around strings, using = when comparing values, choosing unclear or reserved variable names, and introducing incorrect indentation. Python is case-sensitive: 'GET' is not the same as 'get'. At the top level, code should begin at the left margin. Consistent indentation becomes essential when blocks are introduced.

Why this matters: a backend request eventually produces a response through a chain of simple operations. The server parses the request into variables, checks the method and path, builds a response body as HTML or JSON, sets a status code, and sends the response. You can simulate this entire chain with variables and print(). Later, print() will be replaced by real network output, but the mental model remains the same.

A professional habit begins on Day 1: read each line as a small claim about the program state. If the line is `status_code = 200`, ask what value exists and whether that value belongs to a request or a response. If the line is `response_body = '<h1>About PySchool</h1>'`, ask whether the text is an input, an output, or a temporary value. This habit makes later debugging faster because a web request is never one mysterious operation. It is a sequence of named values, decisions, transformations, and outputs. You will add functions and validation to give those steps structure, but the habit of naming and observing state remains useful throughout backend development.""",
    "code_example": """# Simulate a backend request-response cycle
http_method = 'GET'
request_path = '/about'
user_agent = 'Mozilla/5.0'
status_code = 200
content_type = 'text/html'
response_body = '<h1>About PySchool</h1>'

print('Incoming request:')
print(http_method + ' ' + request_path)
print('User-Agent: ' + user_agent)
print('---')
print('Outgoing response:')
print('Status:', status_code)
print('Content-Type:', content_type)
print('Body:', response_body)""",
    "questions": [
        "What is a variable, and why should its name be descriptive?",
        "What does print() do, and how does it help when learning backend development?",
        "Name two common mistakes beginners make with strings or assignment in Python.",
    ],
    "answers": [
        "A variable is a named reference to a value stored in memory; descriptive names make code readable and maintainable, especially in web projects with many request details.",
        "print() displays values to the console; it helps you observe request data and response content while simulating a backend.",
        "Forgetting quotes around strings causes a NameError, and using = instead of == assigns instead of comparing.",
    ],
    "homework": "Create request_simulator.py that simulates two HTTP request-response cycles. First, a successful GET request to /about with status 200 and an HTML body. Second, a missing GET request to /missing with status 404 and a plain-text body. For each cycle, define variables for http_method, request_path, user_agent, status_code, content_type, and response_body. Use comments to label incoming-request and outgoing-response sections. Print the request line, User-Agent, status code, content type, and body for each cycle. Use only variables, strings, print(), and comments. Observable output: two complete request-response simulations.",
    "required_patterns": ["print(", "=", "#"],
}
