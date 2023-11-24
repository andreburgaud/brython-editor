# Python ScratchPad (PyScratchPad)

The production version of Python Scratchpad is available at https://pyscratchpad.com/.

![PyScratchPad Screenshot from 2023-11-23 19-50-58](https://github.com/andreburgaud/python-scratchpad/assets/6396088/027e4fbb-cbc8-4284-9c32-823797c60a58)

# Local Server

In the working directory, start a web server as follows:

```
$ python3 -m http.server --directory site
```

Then, point a browser to http://localhost:8000

# Docker

If you are using [Docker](https://www.docker.com/), you can start the **Python ScratchPad** server as follows:

```
$ docker run --rm -p 8080:80 andreburgaud/python-scratchpad
```

Then, point a browser to http://localhost:8080
