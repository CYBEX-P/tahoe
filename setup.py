import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tahoe",
    version="0.5",
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
        "Programming Language :: Python :: 3.7.x",
    ],
    install_requires = [
        "pymongo",
        "mongomock"        
    ]
)
