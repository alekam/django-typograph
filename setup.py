from setuptools import setup, find_packages


version = __import__('typograph').get_version()

setup(
    name="typograph",
    version=version,
    description="Typography application for django based projects",
    keywords="django typography tinymce",
    author="Alex Kamedov",
    author_email="alex@kamedov.ru",
    url="http://github.com/alekam/django-typograph.git",
    platforms=["any"],
    classifiers=["Development Status :: %s" % version,
                   "Environment :: Web Environment",
                   "Framework :: Django",
                   "Intended Audience :: Developers",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Topic :: Utilities"],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
