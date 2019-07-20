#!/usr/bin/env python3
#Importing Flask Module
from flask import Flask, request, jsonify

#Starting Myapp 
myapp = Flask(__name__)

#Decorator app using Route / and /hello uri's
@myapp.route("/")
def index():
    return """
        Welcome to my website!<br /><br />
        <a href="/hello">Go to hello world</a>
    """

@myapp.route("/hello")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"



#Closing app with main and running with different port with debug mode
if __name__ == "__main__":
    myapp.run(host="0.0.0.0", debug=True)
