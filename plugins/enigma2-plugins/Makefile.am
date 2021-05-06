ACLOCAL_AMFLAGS = -I m4

SUBDIRS = \
	automaticvolumeadjustment \
	antiscrollbar \
	bitrate \
	epgsearch \
	epgrefresh \
	ftpbrowser \
	filebrowser \
	mphelp \
	permanentclock \
	recordinfobar \
	servicemp3 \
	systemtime \
	pluginhider \
	networkbrowser

metadir = $(datadir)/meta
meta_DATA = index-enigma2-plugins.xml
CLEANFILES = index-enigma2-plugins.xml

index-enigma2-plugins.xml: $(top_srcdir)/genmetaindex.py $(top_srcdir)/*/meta/plugin_*.xml
	$(AM_V_GEN)$(PYTHON) $^ > $@
