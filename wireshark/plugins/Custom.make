#
# $Id$
#

_CUSTOM_SUBDIRS_ = \
	nordic_ble

_CUSTOM_EXTRA_DIST_ = \
	Custom.m4 \
	Custom.make

_CUSTOM_plugin_ldadd_ = \
	-dlopen plugins/nordic_ble/nordic_ble.la
