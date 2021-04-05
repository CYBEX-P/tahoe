import setuptools

import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(dir_path, "README.md"), "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tahoe",
    version="0.8.0",
    author="Farhan Sadique",
    author_email="qclass@protonmail.com",
    description="TAHOE -- A CyberThreat Language (CTL)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cybex-p/tahoe",
    packages=setuptools.find_packages(),
    data_files=[
##        ('tahoe/schema', [
##            'tahoe/schema/attribute.json',
##            'tahoe/schema/object.json', 'tahoe/schema/event.json',
##            'tahoe/schema/session.json', 'tahoe/schema/raw.json'
##        ]),
##
##        ('tahoe/objects/feature/geolite2', [
##            'tahoe/objects/feature/geolite2/GeoLite2-ASN.mmdb',
##            'tahoe/objects/feature/geolite2/GeoLite2-City.mmdb',
##            'tahoe/objects/feature/geolite2/GeoLite2-Country.mmdb'
##        ]),
##
##        ('tahoe/objects/feature', [
##            'tahoe/objects/feature/proxies.txt',
##            'tahoe/objects/feature/socks.txt',
##            'tahoe/objects/feature/tld.txt'
##        ])
    ],
    classifiers=[
        "Programming Language :: Python :: 3.8.x",
    ],
    install_requires = [
        "pymongo",
        "mongomock",
        "PyJWT"
    ]
)
