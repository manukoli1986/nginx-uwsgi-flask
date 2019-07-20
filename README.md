# Serve Flask Applications with uWSGI and Nginx 
=====

> In this guide, you will build a Python application using the Flask microframework on alpine. The bulk of this article will be about how to set up the uWSGI application server and how to launch the application and configure Nginx to act as a front-end reverse proxy which is provisioned on K8(minikube).

How this thing works
-----

* Flask is managed by `uWSGI`.
* `uWSGI` talks to `nginx`.
* `nginx` handles contact with the outside world.

```
[SERVER] Flask <---> uWSGI <---> nginx <---> client [Internet]
```

When a client connects to your server trying to reach your Flask app:  
* `nginx` opens the connection and proxies it to `uWSGI`
* `uWSGI` handles the Flask instances you have and connects one to the client
* Flask talks to the client happily

Flask
-----

Write your app. Three things that matter:

1. Flask script filename (e.g. `server_dev.py`)
2. App name (e.g. if your Flask app says this: `myapp = Flask(__name__)`, your app name is `myapp`)
3. If you have `myapp.run()` in your application somewhere, MAKE SURE IT'S INSIDE THE FOLLOWING CHECK:  

``` python
if __name__ == '__main__':
    myapp.run()
```

OTHERWISE YOU WILL START ANOTHER WSGI SERVER ALONGSIDE YOUR uWSGI SERVER.  
You do NOT want this.

uWSGI
-----

There's at least two ways to get uWSGI talking to nginx:

* Connect the two via a TCP port
* Connect the two via a filesocket

Filesockets have issues with read/write and user permissions sometimes. These aren't hard problems but I'm too lazy to figure out these problems when there's an easier way to do it with simple TCP ports.

Here's a working uWSGI setup:  
* that communiates with a web server via port `8080`
* for file `server.py`
* with app name `myapp`

```
uwsgi --socket 127.0.0.1:8080 --module server --callab myapp
```

Note that this runs without a daemon and you probably want this daemonized in case it crashes. Try using [uWSGI in emperor mode](http://uwsgi-docs.readthedocs.org/en/latest/Emperor.html) or [supervisor](http://supervisord.org/).

nginx
-----

This is easy. Super easy.
Here's an `nginx` config that works with `uwsgi` on port `8080`:

```
server {
    listen      80;
    server_name localhost;

    location / {
    uwsgi_pass uwsgi://localhost:8080;
    }
    error_page  500 502 503 504  /50x.html;
    location = /50x.html {
        root    /usr/share/nginx/html;
    }
}
```

Well I have given you knowledge how I have prepared platfrom to run Flask app with UWSGI/Nginx. 

# Now let's understand how I integrated in multicontainer image and provisioned on K8 (minikube).

### This project consist of two steps:
### TASK1 
1. Creating a Sample App

* Below are output of Dockerfile and python file(server.py) (Application1)
```
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
```

2. supervisod file - for autostarting services in container

3. uwsgi.ini file - Creating the WSGI Entry Point

4. Reverse-proxy.conf - file placed under nginx conf directory which is just passing our request to uwsgi server

5. alpine_nginx - Default nginx file and customize reverse-proxy file copied to base nginx:alpine image

6. samle_app dir - Sample flask app, supervisored and uwsgi.ini file copied to base alpine image


### TASK2

> Created deployment object file with service mentioned and used configmap to mount reverse-proxy.conf file under nginx configration directory and mount it using volume specified. I have used multicontainer deployment to make availability of application within a pod and that can be auto-scaled according to requirement.

```
 cat deployment/configmap/reverse-proxy.conf
server {
    listen      80;
    server_name localhost;

    location / {
    uwsgi_pass uwsgi://localhost:8080;
    }
    error_page  500 502 503 504  /50x.html;
    location = /50x.html {
        root    /usr/share/nginx/html;
    }
}

```
```
$ kubectl.exe create configmap helloworld --from-file=configmap/reverse-proxy.conf
configmap/helloworld created

$ kubectl.exe get configmap
NAME         DATA   AGE
helloworld   1      166m

$ kubectl.exe apply -f deploy.yaml
deployment.apps/nginx-uwsgi-nginx unchanged
service/nginx unchanged

$ cat deployment/deploy.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-uwsgi-nginx
  labels:
    app: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx         -> Nginx Container
        image: manukoli1986/alpine_nginx:v1  -> Used customized image
        ports:
        - containerPort: 80  -> connecting to conatiner port
        resources:           -> providing resource limit and request
          limits:
            cpu: 100m
            memory: 128Mi
          requests:
            cpu: 50m
            memory: 64Mi
        volumeMounts:        -> Mentioned volume mount location
          - name: nginx-conf
            mountPath: /etc/nginx/conf.d
      - name: helloworld     -> Flask app container
        image: manukoli1986/alpine_uwsgi_flask:v2  -> Used customized image
        resources:
          limits:
            cpu: 100m
            memory: 128Mi
          requests:
            cpu: 50m
            memory: 64Mi
      volumes:
      - name: nginx-conf      -> Created config map and map it to volume mounted under nginx config
        configMap:
          name: helloworld
---
apiVersion: v1
kind: Service
metadata:
  name: nginx
spec:
  type: NodePort
  selector:
    app: nginx
  ports:
    - port: 80
      nodePort: 30180

```

# Output
$ minikube.exe service list
|-------------|------------|-----------------------------|
|  NAMESPACE  |    NAME    |             URL             |
|-------------|------------|-----------------------------|
| default     | kubernetes | No node port                |
| default     | nginx      | http://192.168.99.104:30180 |
| kube-system | kube-dns   | No node port                |
|-------------|------------|-----------------------------|


![alt text](https://github.com/manukoli1986/nginx-uwsgi-flask/images/1.jpg)
![alt text](https://github.com/manukoli1986/nginx-uwsgi-flask/images/2.jpg)

## Conclusion

In this guide, we created and secured a simple Flask application within a Python environment. We created a WSGI entry point so that any WSGI-capable application server can interface with it, and then configured the uWSGI app server to provide this function. Afterwards, we created a systemd service file to automatically launch the application server on boot. You also created an Nginx server block that passes web client traffic to the application server, relaying external requests, and secured traffic to your server with Let's Encrypt.
It's all provisioned on K8 which is very common nowadays and cna be used on AKS or GKE.

Flask is a very simple, but extremely flexible framework meant to provide your applications with functionality without being too restrictive about structure and design. You can use the general stack described in this guide to serve the flask applications that you design.


Prepared By: 
MayanK