#/***************************************************************************
# PosiView
#
# PosiView tracks multiple mobile object and vehicles and displays its position on the canvas
#							 -------------------
#		begin				: 2015-06-01
#		git sha				: $Format:%H$
#		copyright			: (C) 2015 by Jens Renken/Marum/University of Bremen
#		email				: renken@marum.de
# ***************************************************************************/
#
#/***************************************************************************
# *																		 *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or	 *
# *   (at your option) any later version.								   *
# *																		 *
# ***************************************************************************/

#################################################
# Edit the following to match your sources lists
#################################################


#Add iso code for any locales you want to support here (space separated)
# default is no locales
# LOCALES = af
LOCALES = de

# If locales are enabled, set the name of the lrelease binary on your system. If
# you have trouble compiling the translations, you may have to specify the full path to
# lrelease
LRELEASE = lrelease
#LRELEASE = lrelease-qt4

# translation
SOURCES = \
	__init__.py \
	posi_view.py 

PLUGINNAME = PosiView

PY_FILES = \
	posi_view.py \
	__init__.py \
	position_marker.py \
	posiview_project.py \
	mobile_item.py \
	measure_maptool.py \
	recorder.py \
	gui/__init__.py \
	gui/posiview_properties.py \
	gui/tracking_dock.py \
	gui/guidance_dock.py \
	gui/dataprovider_dump.py \
	gui/position_display.py \
	gui/compass.py \
	dataprovider/__init__.py \
	dataprovider/data_provider.py \
	dataprovider/datadevice/__init__.py \
	dataprovider/datadevice/datadevice.py \
	dataprovider/datadevice/udpdevice.py \
	dataprovider/datadevice/tcpdevice.py \
	dataprovider/dataparser/__init__.py \
	dataprovider/dataparser/nmea.py \
	dataprovider/dataparser/parser_ixusbl.py \
	dataprovider/dataparser/parser_pise.py \
	dataprovider/dataparser/parser_minipos.py \
	dataprovider/dataparser/parser_gps.py \
	dataprovider/dataparser/parser_psonlld.py \
	dataprovider/dataparser/parser_cp16.py \
	dataprovider/dataparser/parser_ais.py \
	dataprovider/dataparser/parser_pmtm.py \
	dataprovider/dataparser/parser_test.py \
	dataprovider/dataparser/parser.py


UI_FILES = ui/guidance_dock_base.ui \
		ui/tracking_dock_base.ui \
		ui/dataprovider_dump_base.ui

COMPILED_UI_FILES = gui/ui_posiview_properties_base.py

EXTRAS = resources/icon.png metadata.txt

COMPILED_RESOURCE_FILES = resources_rc.py

PEP8EXCLUDE=pydev,resources_rc.py,conf.py,third_party,ui,ui_*.py


#################################################
# Normally you would not need to edit below here
#################################################

HELP = help/build/html

PLUGIN_UPLOAD = $(c)/plugin_upload.py

RESOURCE_SRC=$(shell grep '^ *<file' resources.qrc | sed 's@</file>@@g;s/.*>//g' | tr '\n' ' ')

QGISDIR=.qgis2

default: compile

compile: $(COMPILED_RESOURCE_FILES) $(COMPILED_UI_FILES)

%_rc.py : %.qrc $(RESOURCES_SRC)
	pyrcc4 -o $*_rc.py  $<

%.qm : %.ts
	$(LRELEASE) $<

gui/ui_%.py : ui/%.ui
	python -m qgis.PyQt.uic.pyuic -o $@ $<

test: compile transcompile
	@echo
	@echo "----------------------"
	@echo "Regression Test Suite"
	@echo "----------------------"

	@# Preceding dash means that make will continue in case of errors
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); \
		export QGIS_DEBUG=0; \
		export QGIS_LOG_FILE=/dev/null; \
		nosetests -v --with-id --with-coverage --cover-package=. \
		3>&1 1>&2 2>&3 3>&- || true
	@echo "----------------------"
	@echo "If you get a 'no module named qgis.core error, try sourcing"
	@echo "the helper script we have provided first then run make test."
	@echo "e.g. source run-env-linux.sh <path to qgis install>; make test"
	@echo "----------------------"

deploy: compile doc transcompile
	@echo
	@echo "------------------------------------------"
	@echo "Deploying plugin to your .qgis2 directory."
	@echo "------------------------------------------"
	# The deploy  target only works on unix like operating system where
	# the Python plugin directory is located at:
	# $HOME/$(QGISDIR)/python/plugins
	mkdir -p $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf --parents $(PY_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf --parents $(UI_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(COMPILED_RESOURCE_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf --parents $(COMPILED_UI_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(EXTRAS) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vfr --parents i18n $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vfr $(HELP) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/help

# The dclean target removes compiled python files from plugin directory
# also deletes any .git entry
dclean:
	@echo
	@echo "-----------------------------------"
	@echo "Removing any compiled python files."
	@echo "-----------------------------------"
	find $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME) -iname "*.pyc" -delete
	find $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME) -iname ".git" -prune -exec rm -Rf {} \;


derase:
	@echo
	@echo "-------------------------"
	@echo "Removing deployed plugin."
	@echo "-------------------------"
	rm -Rf $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)

zip: deploy dclean
	@echo
	@echo "---------------------------"
	@echo "Creating plugin zip bundle."
	@echo "---------------------------"
	# The zip target deploys the plugin and creates a zip file with the deployed
	# content. You can then upload the zip file on http://plugins.qgis.org
	rm -f $(PLUGINNAME).zip
	cd $(HOME)/$(QGISDIR)/python/plugins; zip -9r $(CURDIR)/$(PLUGINNAME).zip $(PLUGINNAME)

COMMITHASH=$(shell git rev-parse HEAD)
package: compile
	# Create a zip package of the plugin named $(PLUGINNAME).zip.
	# This requires use of git (your plugin development directory must be a
	# git repository).
	# To use, pass a valid commit or tag as follows:
	#   make package VERSION=Version_0.3.2
	@echo
	@echo "------------------------------------"
	@echo "Exporting plugin to zip package.	"
	@echo "------------------------------------"
	rm -f $(PLUGINNAME).zip
	git archive --prefix=$(PLUGINNAME)/ -o $(PLUGINNAME).zip $(COMMITHASH)
	echo "Created package: $(PLUGINNAME).zip"

upload: zip
	@echo
	@echo "-------------------------------------"
	@echo "Uploading plugin to QGIS Plugin repo."
	@echo "-------------------------------------"
	$(PLUGIN_UPLOAD) $(PLUGINNAME).zip

transup:
	@echo
	@echo "------------------------------------------------"
	@echo "Updating translation files with any new strings."
	@echo "------------------------------------------------"
	@chmod +x scripts/update-strings.sh
	@scripts/update-strings.sh $(LOCALES)

transcompile:
	@echo
	@echo "----------------------------------------"
	@echo "Compiled translation files to .qm files."
	@echo "----------------------------------------"
	@chmod +x scripts/compile-strings.sh
	@scripts/compile-strings.sh $(LRELEASE) $(LOCALES)

transclean:
	@echo
	@echo "------------------------------------"
	@echo "Removing compiled translation files."
	@echo "------------------------------------"
	rm -f i18n/*.qm

clean:
	@echo
	@echo "------------------------------------"
	@echo "Removing uic and rcc generated files"
	@echo "------------------------------------"
	rm $(COMPILED_UI_FILES) $(COMPILED_RESOURCE_FILES)

doc:
	@echo
	@echo "------------------------------------"
	@echo "Building documentation using sphinx."
	@echo "------------------------------------"
	cd help; make html

pylint:
	@echo
	@echo "-----------------"
	@echo "Pylint violations"
	@echo "-----------------"
	@pylint --reports=n --rcfile=pylintrc . || true
	@echo
	@echo "----------------------"
	@echo "If you get a 'no module named qgis.core' error, try sourcing"
	@echo "the helper script we have provided first then run make pylint."
	@echo "e.g. source run-env-linux.sh <path to qgis install>; make pylint"
	@echo "----------------------"


# Run pep8 style checking
#http://pypi.python.org/pypi/pep8
pep8:
	@echo
	@echo "-----------"
	@echo "PEP8 issues"
	@echo "-----------"
	@pep8 --repeat --ignore=E203,E121,E122,E123,E124,E125,E126,E127,E128,E501 --exclude $(PEP8EXCLUDE) . || true
	@echo "-----------"
	@echo "Ignored in PEP8 check:"
	@echo $(PEP8EXCLUDE)
