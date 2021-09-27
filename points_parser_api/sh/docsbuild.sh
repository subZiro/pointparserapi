#!/bin/sh

project_name="PointParserApi"
date_version=$(date '+%d.%m.%Y')
project_dir=$(pwd)
rm -rf docs && mkdir docs && cd docs
#sphinx-quickstart -q -p "Documentation of ${project_name}" -a Unknown -v ${date_version} --ext-autodoc --ext-intersphinx --ext-viewcode
sphinx-quickstart -q -p "Documentation of ${project_name}" -a Unknown -v ${date_version} --ext-autodoc --ext-intersphinx --ext-doctest --ext-coverage
perl -pi -e 's/# import os/import os/g;' conf.py
perl -pi -e 's/# import sys/import sys/g;' conf.py
perl -pi -e "s/# sys.path.insert\(0, os.path.abspath\(\'.\'\)\)/sys.path.insert(0, os.path.abspath(\"..\"))/g;" conf.py
perl -pi -e 's/alabaster/sphinx_rtd_theme/g' conf.py
perl -pi -e "print '   rst' if $. == 14" index.rst
perl -pi -e 's/if __name__ != "__main__":/if __name__ == "__main__":/g;' ../app/__init__.py
sphinx-apidoc -o rst ..
rm rst/config.rst rst/modules.rst
make html
perl -pi -e 's/if __name__ == "__main__":/if __name__ != "__main__":/g;' ../app/__init__.py
