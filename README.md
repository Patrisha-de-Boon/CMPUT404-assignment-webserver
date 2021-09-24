CMPUT404-assignment-webserver
=============================

CMPUT404-assignment-webserver

See requirements.org (plain-text) for a description of the project.

Make a simple webserver.

Contributors / Licensing
========================

Generally everything is LICENSE'D under the Apache 2 license by Abram Hindle.

server.py contains contributions from:

* Patrisha de Boon
* Abram Hindle
* Eddie Antonio Santos
* Jackson Z Chang
* Mandy Meindersma 

But the server.py example is derived from the python documentation
examples thus some of the code is Copyright © 2001-2013 Python
Software Foundation; All Rights Reserved under the PSF license (GPL
compatible) http://docs.python.org/2/library/socketserver.html

Similarily, example code from 
https://docs.python.org/3/library/datetime.html was used to format 
date and time for the Date header in server.py. Examples from
https://docs.python.org/3/library/mimetypes.html were used to identify
mime types and encoding for system files, and examples from 
https://docs.python.org/3/library/urllib.parse.html were used
to decode file names before searching for them on disk. Examples from 
https://docs.python.org/3/library/os.path.html were used to navigate
the files on disk and to create and validate paths to files and directories.

server.py was also made with extensive use of documentation from
https://developer.mozilla.org/en-US/docs/Web/HTTP as a reference for 
formatting and parsing data.