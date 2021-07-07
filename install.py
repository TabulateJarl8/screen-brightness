#!/usr/bin/env python3

import shutil
import os
from configparser import ConfigParser
import argparse
import subprocess

# Script to install/uninstall screen adjust-brightness program


def less(data):
	process = subprocess.Popen(["less"], stdin=subprocess.PIPE)
	try:
		process.stdin.write(data.encode('UTF-8'))
		process.communicate()
	except IOError:
		pass


def make_executable(path):
	mode = os.stat(path).st_mode
	mode |= (mode & 0o444) >> 2    # copy R bits to X
	os.chmod(path, mode)


def install():
	LOCAL_BIN = os.path.expanduser('~/.local/bin/')
	LOCAL_APPLICATIONS = os.path.expanduser('~/.local/share/applications')
	LOCAL_ICONS = os.path.expanduser('~/.local/share/icons/hicolor/scalable/apps')
	DESKTOP_FILE_FINAL_PATH = os.path.join(LOCAL_APPLICATIONS, 'adjust-brightness.desktop')
	ICON_FILE_FINAL_PATH = os.path.join(LOCAL_ICONS, 'adjust-brightness.svg')
	path_to_binary = os.path.join(LOCAL_BIN, 'adjust-brightness')
	THIS_SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

	# Install desktop file

	# Make local directories if they doesn't exist

	if not os.path.isdir(LOCAL_BIN):
		print(f'Making {LOCAL_BIN}...')
		os.makedirs(LOCAL_BIN)

	if not os.path.isdir(LOCAL_APPLICATIONS):
		print(f'Making {LOCAL_APPLICATIONS}...')
		os.makedirs(LOCAL_APPLICATIONS)

	if not os.path.isdir(LOCAL_ICONS):
		print(f'Making {LOCAL_ICONS}...')
		os.makedirs(LOCAL_ICONS)

	if os.path.isfile(path_to_binary):
		if input(f'Error, file "{path_to_binary}" exists. Continue anyway? [y/N] ').lower() != 'y':
			print('Exiting...')
			exit(1)

	if os.path.isfile(DESKTOP_FILE_FINAL_PATH):
		if input(f'Error, file "{DESKTOP_FILE_FINAL_PATH}" exists. Continue anyway? [y/N] ').lower() != 'y':
			print('Exiting...')
			exit(1)

	if os.path.isfile(ICON_FILE_FINAL_PATH):
		if input(f'Error, file "{ICON_FILE_FINAL_PATH}" exists. Continue anyway? [y/N] ').lower() != 'y':
			print('Exiting...')
			exit(1)

	print('Generating desktop file...')

	desktop_content = ConfigParser()
	desktop_content.optionxform = str
	desktop_content.add_section('Desktop Entry')

	desktop_content['Desktop Entry']['Name'] = 'Screen Brightness'
	desktop_content['Desktop Entry']['Comment'] = 'Qt GUI frontend for adjusting screen brightness using xrandr'
	desktop_content['Desktop Entry']['Exec'] = path_to_binary
	desktop_content['Desktop Entry']['Icon'] = os.path.splitext(os.path.basename(ICON_FILE_FINAL_PATH))[0]
	desktop_content['Desktop Entry']['Terminal'] = 'false'
	desktop_content['Desktop Entry']['Type'] = 'Application'
	desktop_content['Desktop Entry']['Categories'] = 'System;Utility;Application;'
	desktop_content['Desktop Entry']['Keywords'] = 'brightness;xrandr;adjust;display;screen;'

	print('Writing desktop file...')
	with open(DESKTOP_FILE_FINAL_PATH, 'w') as f:
		desktop_content.write(f, space_around_delimiters=False)

	print('Copying icon...')
	if os.path.isfile(ICON_FILE_FINAL_PATH):
		os.remove(ICON_FILE_FINAL_PATH)
	shutil.copyfile(os.path.join(THIS_SCRIPT_DIRECTORY, 'icon.svg'), ICON_FILE_FINAL_PATH)

	print('Setting binary permissions and copying...')
	main_script_path = os.path.join(THIS_SCRIPT_DIRECTORY, 'main.py')
	if os.path.isfile(path_to_binary):
		os.remove(path_to_binary)
	shutil.copyfile(main_script_path, path_to_binary)
	make_executable(path_to_binary)


def uninstall():
	BINARY_PATH = os.path.expanduser('~/.local/bin/adjust-brightness')
	DESKTOP_FILE_PATH = os.path.expanduser('~/.local/share/applications/adjust-brightness.desktop')
	ICON_PATH = os.path.expanduser('~/.local/share/icons/hicolor/scalable/apps/adjust-brightness.svg')

	if not (os.path.isfile(BINARY_PATH) and os.path.isfile(DESKTOP_FILE_PATH) and os.path.isfile(ICON_PATH)):
		print('Not all installed files are present. Exiting')
		exit(1)

	print('View files before uninstallation')
	if input('Would you like to view the executable file? [Y/n] ').lower() != 'n':
		with open(BINARY_PATH) as f:
			less(f.read())
	if input('Would you like to view the desktop file? [Y/n] ').lower() != 'n':
		with open(DESKTOP_FILE_PATH) as f:
			less(f.read())
	if input('Would you like to view the icon file? [Y/n] ').lower() != 'n':
		with open(ICON_PATH) as f:
			less(f.read())

	if input('Are you sure you would like to continue? [y/N] ').lower() != 'y':
		print('Exiting')
		exit(1)

	print('Removing binary...')
	os.remove(BINARY_PATH)
	print('Removing desktop file...')
	os.remove(DESKTOP_FILE_PATH)
	print('Removing icon...')
	os.remove(ICON_PATH)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Script to install/uninstall screen adjust-brightness program')
	parser.add_argument('-u', '--uninstall', action='store_true', help='Uninstall program')
	args = parser.parse_args()

	if not args.uninstall:
		install()
	else:
		uninstall()
