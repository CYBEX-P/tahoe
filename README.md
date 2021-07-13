![unittests](https://github.com/CYBEX-P/tahoe/workflows/unittests/badge.svg)

# TAHOE — A Cyberthreat Language

Any CIS platform like [CYBEX-P](https://github.com/cybex-p) potentially handles hundreds of different data formats. Thus, it needs a standard data format and structure to represent threat data. Examples of threat data are email, firewall logs, malware signatures, file hashes etc. A cyberthreat language (CTL) is a specification of how to format and serialize any kind of threat data. CYBEX-P uses TAHOE instead of other CTLs like [STIX](https://oasis-open.github.io/cti-documentation/) or [MISP](https://github.com/MISP/misp-rfc). TAHOE structures threat data as JSON documents.

This repository is a Python library that should be used to structure any threat data in TAHOE format.


## Installation

1. Download & install [Python 3.9.x](https://www.python.org/downloads/).

2. Create and activate Python virtual environment [(official documentation)](https://docs.python.org/3/library/venv.html). \
Create: ```python -m venv myenv``` \
Activate in *Ubuntu*: ```source myenv/bin/activate``` \
Activate in *Windows*: ```source myenv/Scripts/activate```

3. Download the files from the TAHOE repository.
```
git clone https://github.com/CYBEX-P/tahoe
```

4. Install
```
cd tahoe
python setup.py install
```

5. Unittest
```
python -m unittest
```


## TAHOE Data Instance

A piece of TAHOE data is called an instance and there are 5 types of TAHOE instances —

1.  **Raw** A data instance stores unprocessed user data.

2.  **Attribute** The most basic datatype that holds a single piece of
    information, like an IP address.

3.  **Object** Groups several attributes or other objects together, e.g., a file may have a filename attribute and a file-size attribute.

4.  **Event** An event consists of one or more attributes or objects along with a timestamp. Events structure attributes or objects into complete threat data. 

5.  **Session** A session groups arbitrarily related events. (e.g. events when a user visits a website).








```
python setup.py sdist
pip install dist/tahoe
```


# Documentation Generation


## gen docs
```bash
python3 -m venv sphinx-env
source sphinx-env/bin/activate
pip install -r docs/requirements.txt # doc gen requirements
python3 setup.py install # install requirements for tahoe
cd docs

# the following step might not be needed depending how it is imported
# if modules.rst and reStructuredText files are used somewhere in the source docs 
#then use the following line to regenerate modules
sphinx-apidoc -f -o source/ ../tahoe # regenerate automatic file generation

make clean html
```

output is in `docs/build/html`.   

## information
[basic rst language](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)   
[how to import docstring directly into current file.](https://medium.com/@eikonomega/getting-started-with-sphinx-autodoc-part-1-2cebbbca5365)   
[generate reStructuredText files (using modules.rst)](https://shunsvineyard.info/2019/09/19/use-sphinx-for-python-documentation/#10-step-3-use-sphinx-apidoc-to-generate-restructuredtext-files-from-source-code)   
https://medium.com/@richdayandnight/a-simple-tutorial-on-how-to-document-your-python-project-using-sphinx-and-rinohtype-177c22a15b5b   
[manipulating the toctree](https://www.sphinx-doc.org/en/1.2/markup/toctree.html)   
