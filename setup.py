import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tahoe",
    version="0.0.1",
    author="Farhan Sadique",
    author_email="qclass@protonmail.com",
    description="Cyber Threat Information Sharing Language",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/tahoe",
    packages=setuptools.find_packages(),
    data_files=[('tahoe/schema', ['tahoe/schema/attribute.json',
                'tahoe/schema/object.json', 'tahoe/schema/event.json',
                'tahoe/schema/session.json', 'tahoe/schema/raw.json']),],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
