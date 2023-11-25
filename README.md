# Python ScratchPad (PyScratchPad)

The production version of Python Scratchpad is available at https://pyscratchpad.com/.

![PyScratchPad Screenshot from 2023-11-25 00-23-06](https://github.com/andreburgaud/python-scratchpad/assets/6396088/7f9b07e0-2ede-4b4d-b7de-8dbbe5dc26e3)


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
