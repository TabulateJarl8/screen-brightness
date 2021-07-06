#!/usr/bin/env python3
import sys
import shutil
import subprocess
import logging

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QStyle, QStyleOptionSlider
from PyQt5.QtCore import QRect, QPoint, Qt


logging.basicConfig(level=logging.INFO)


class LabeledSlider(QtWidgets.QWidget):
	def __init__(self, minimum, maximum, interval=1, orientation=Qt.Horizontal,
			labels=None, parent=None, value=None):
		super(LabeledSlider, self).__init__(parent=parent)

		levels=range(minimum, maximum+interval, interval)
		if labels is not None:
			if not isinstance(labels, (tuple, list)):
				raise Exception("<labels> is a list or tuple.")
			if len(labels) != len(levels):
				raise Exception("Size of <labels> doesn't match levels.")
			self.levels=list(zip(levels,labels))
		else:
			self.levels=list(zip(levels,map(str,levels)))

		if orientation==Qt.Horizontal:
			self.layout=QtWidgets.QVBoxLayout(self)
		elif orientation==Qt.Vertical:
			self.layout=QtWidgets.QHBoxLayout(self)
		else:
			raise Exception("<orientation> wrong.")

		# gives some space to print labels
		self.left_margin=10
		self.top_margin=10
		self.right_margin=10
		self.bottom_margin=10

		self.layout.setContentsMargins(self.left_margin,self.top_margin,
				self.right_margin,self.bottom_margin)

		self.sl=QtWidgets.QSlider(orientation, self)
		self.sl.setMinimum(minimum)
		self.sl.setMaximum(maximum)

		if value is None:
			self.sl.setValue(minimum)
		else:
			self.sl.setValue(value)

		if orientation==Qt.Horizontal:
			self.sl.setTickPosition(QtWidgets.QSlider.TicksBelow)
			self.sl.setMinimumWidth(300) # just to make it easier to read
		else:
			self.sl.setTickPosition(QtWidgets.QSlider.TicksLeft)
			self.sl.setMinimumHeight(300) # just to make it easier to read
		self.sl.setTickInterval(interval)
		self.sl.setSingleStep(1)

		self.layout.addWidget(self.sl)

	def paintEvent(self, e):

		super(LabeledSlider,self).paintEvent(e)

		style=self.sl.style()
		painter=QPainter(self)
		st_slider=QStyleOptionSlider()
		st_slider.initFrom(self.sl)
		st_slider.orientation=self.sl.orientation()

		length=style.pixelMetric(QStyle.PM_SliderLength, st_slider, self.sl)
		available=style.pixelMetric(QStyle.PM_SliderSpaceAvailable, st_slider, self.sl)

		for v, v_str in self.levels:

			# get the size of the label
			rect=painter.drawText(QRect(), Qt.TextDontPrint, v_str)

			if self.sl.orientation()==Qt.Horizontal:
				# I assume the offset is half the length of slider, therefore
				# + length//2
				x_loc=QStyle.sliderPositionFromValue(self.sl.minimum(),
						self.sl.maximum(), v, available)+length//2

				# left bound of the text = center - half of text width + L_margin
				left = x_loc-rect.width() // 2 + self.left_margin
				# sligtly strange behavior, sometimes first text breaks
				bottom = self.rect().height() // 2 + self.bottom_margin + 3

				# enlarge margins if clipping
				if v==self.sl.minimum():
					if left<=0:
						self.left_margin=rect.width()//2-x_loc
					if self.bottom_margin<=rect.height():
						self.bottom_margin=rect.height()

					self.layout.setContentsMargins(self.left_margin,
							self.top_margin, self.right_margin,
							self.bottom_margin)

				if v==self.sl.maximum() and rect.width()//2>=self.right_margin:
					self.right_margin=rect.width()//2
					self.layout.setContentsMargins(self.left_margin,
							self.top_margin, self.right_margin,
							self.bottom_margin)

			else:
				y_loc=QStyle.sliderPositionFromValue(self.sl.minimum(),
						self.sl.maximum(), v, available, upsideDown=True)

				bottom = y_loc + length // 2 + rect.height() // 2 + self.top_margin - 3
				# there is a 3 px offset that I can't attribute to any metric

				left=self.left_margin-rect.width()
				if left<=0:
					self.left_margin=rect.width()+2
					self.layout.setContentsMargins(self.left_margin,
							self.top_margin, self.right_margin,
							self.bottom_margin)

			pos=QPoint(left, bottom)
			painter.drawText(pos, v_str)

		return


class Ui_MainWindow(object):
	def setupUi(self, MainWindow):
		MainWindow.setObjectName("MainWindow")
		MainWindow.resize(400, 300)

		self.slider = LabeledSlider(1, 10, 1, orientation=Qt.Horizontal)
		layout = QtWidgets.QHBoxLayout(self)
		layout.addWidget(self.slider)

		self.comboBox = QtWidgets.QComboBox(MainWindow)
		self.comboBox.setGeometry(QtCore.QRect(300, 10, 82, 28))
		self.comboBox.setObjectName("comboBox")

		self.updateDisplayOptions()
		self.resetCurrentSliderValue()

		self.buttonBox = QtWidgets.QDialogButtonBox(MainWindow)
		self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
		self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
		self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
		self.buttonBox.setObjectName("buttonBox")


		self.retranslateUi(MainWindow)
		self.buttonBox.accepted.connect(MainWindow.accept)
		self.buttonBox.rejected.connect(MainWindow.resetCurrentSliderValue)

		self.comboBox.currentTextChanged.connect(self.resetCurrentSliderValue)
		QtCore.QMetaObject.connectSlotsByName(MainWindow)


	def retranslateUi(self, MainWindow):
		_translate = QtCore.QCoreApplication.translate
		MainWindow.setWindowTitle(_translate("MainWindow", "Adjust Screen Brightness"))


	def updateDisplayOptions(self):
		# xrandr | grep -w connected | cut -f '1' -d ' '
		logging.info('Updating display options')
		# get xrandr outputcan
		xrandr = subprocess.check_output(['xrandr']).decode()

		# find connected devices
		lines = [line for line in xrandr.split('\n') if 'connected' in line.split(' ')]
		logging.debug(f'{lines=}')

		# extract device names
		devices = [device.split(' ')[0] for device in lines]
		logging.debug(f'{devices=}')

		logging.info(f'Adding {",".join(devices)} to combo box\n')
		for device in devices:
			self.comboBox.addItem(device)


	def setBrightness(self, device, value):
		# xrandr --output DP-0 --brightness 1
		logging.info(f'Setting brightness to {value / 10}\n')
		subprocess.check_output(['xrandr', '--output', device, '--brightness', str(value / 10)])


	def getBrightness(self, device):
		# xrandr --verbose | grep "DP-0" -A5 | grep -m 1 -i brightness | cut -f2 -d ' '
		xrandr = subprocess.check_output(['xrandr', '--verbose']).decode().split('\n')

		index_of_device = [i for i, string in enumerate(xrandr) if device in string][0]
		device_info = xrandr[index_of_device:index_of_device + 6]
		logging.debug(f'{device_info=}')

		brightness_line = next(line.strip() for line in device_info if 'brightness' in line.lower())
		logging.debug(f'{brightness_line=}')

		brightness = brightness_line.split(' ')[1]
		logging.info(f'Brightness level of device {device} is {brightness}\n')

		return int(float(brightness) * 10)


	def accept(self):
		self.setBrightness(str(self.comboBox.currentText()), int(self.slider.sl.value()))


	def resetCurrentSliderValue(self):
		logging.info('Resetting slider value to current device brightness\n')
		self.slider.sl.setValue(self.getBrightness(str(self.comboBox.currentText())))


class MainUiWindow(QtWidgets.QWidget, Ui_MainWindow):
	def __init__(self, *args, obj=None, **kwargs):
		super(MainUiWindow, self).__init__(*args, **kwargs)

		self.setupUi(self)


if __name__ == '__main__':

	if shutil.which('xrandr') is None:
		print('xrandr is not installed. Please install it with your package manager.')
		print('Debian: x11-xserver-utils')
		print('Arch: xorg-xrandr')
		print('Fedora: xrandr')
		sys.exit(1)

	app = QtWidgets.QApplication(sys.argv)
	frame = MainUiWindow()
	frame.show()
	sys.exit(app.exec_())

