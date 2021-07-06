![unittests](https://github.com/CYBEX-P/tahoe/workflows/unittests/badge.svg)

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
