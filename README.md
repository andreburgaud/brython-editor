# Python ScratchPad (PyScratchPad)

![image](https://github.com/andreburgaud/python-scratchpad/releases/download/0.3.0/Screenshot.from.2023-01-22.16-14-53.png)

## Start Server

In the working directory, start a web server as follows:

```
$ python3 -m http.server --directory site
```

Then, point a browser to http://localhost:8000

## Docker

If you are using [Docker](https://www.docker.com/), you can start the **Python ScratchPad** server as follows:

```
$ docker run --rm -p 8080:80 andreburgaud/python-scratchpad
```

Then, point a browser to http://localhost:8080
