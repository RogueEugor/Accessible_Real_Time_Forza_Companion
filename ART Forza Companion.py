import pygame
from pydub import AudioSegment
from pydub.playback import play
import io
import socket
import struct
import math
import accessible_output2.outputs.auto
import threading
import concurrent.futures
import time
import json
import os
pygame.mixer.init()
#Variables
bmMonitor=False
armedBenchmark=False
startBenchmark = False
bmSpeed = 60
bmStartTime= 0
bmEndTime = 0
speedInterval = 5
curSpeedInt = 0
preSpeed = 0
speedSense= 10
packeting = True
sound_events = {}
packed_data = []
preGear = 0
bottomedFL = False
bottomedFR = False
bottomedRL = False
bottomedRR = False
maxTF = 200
maxTR = 200
frontMax = False
rearMax = False
preTTFL=0
preTTFR = 0
preTTRL = 0
preTTRR = 0
preSuspFL = 0
preSuspFR = 0
preSuspRL = 0
preSuspRR = 0
metric=False
metricString= "MPH"
speakingTemp = False
speakingSusp = False
speakingGear = False
speakingCompass = False
speakingElevation = False
speakingSpeed = False
last_executed = {}
o = accessible_output2.outputs.auto.Auto()
audioCompass = False
compassClicks = False
speedMon = False
elevationSensor = False
suspAudio = False
tempAudio = False
gearAudio = False
preYaw= 0.0
preDir=""
preClick=0.0
exceed=0
preElevation=0
elevationSense=3
compassSense=10
configuration_values = {
	"Speed Interval": speedInterval,
	"Speed Sensitivity": speedSense,
	"Compass Sensitivity": compassSense,
	"Elevation Sensitivity": elevationSense,
	"Front Tire Temp": maxTF,
	"Rear Tire Temp": maxTR,
	"Benchmark Speed": bmSpeed
}
# Function to save configuration to a file
def save_configuration(dict1, dict2, int_value):
	current_directory = os.getcwd()
	file_path = os.path.join(current_directory, "config.json")

	config_data = {
		"dict1": dict1,
		"dict2": dict2,
		"int_value": int_value
	}

	with open(file_path, 'w') as config_file:
		json.dump(config_data, config_file)
	speak("Configuration saved.")

# Function to read and update configuration from a file
def load_configuration():
	current_directory = os.getcwd()
	file_path = os.path.join(current_directory, "config.json")

	try:
		with open(file_path, 'r') as config_file:
			config_data = json.load(config_file)
			dict1 = config_data.get("dict1", {})
			dict2 = config_data.get("dict2", {})
			int_value = config_data.get("int_value", 0)
			return dict1, dict2, int_value
	except FileNotFoundError:
		return  {label: False for label in [
	"Speed Audio Toggle", "Elevation Audio Toggle", "Suspension Audio Toggle",
	"Tire Temp Audio Toggle", "SR Speed Toggle", "SR Elevation Toggle",
	"SR Compass Toggle", "SR Suspension Toggle", "SR Tire Temps Toggle",
	"SR Gears Toggle", "Measurement Toggle", "Benchmark Toggle","Save Configuration"
]}, {
	"Speed Interval": None,
	"Speed Sensitivity": None,
	"Elevation Sensitivity": None,
	"Compass Sensitivity": None,
	"Front Tire Temp": None,
	"Rear Tire Temp": None,
	"Benchmark Speed": None
}, 0  # Return default values if the file doesn't exist

from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton, QComboBox, QLineEdit, QLabel
from PyQt5.QtGui import QIntValidator

# Define global variables
audio_compass_options = ['off', 'Cardinal Directions', 'Clicks only', 'Cardinal and clicks']
audio_compass_selection = 0

button_states = {label: False for label in [
	"Speed Audio Toggle", "Elevation Audio Toggle", "Suspension Audio Toggle",
	"Tire Temp Audio Toggle", "SR Speed Toggle", "SR Elevation Toggle",
	"SR Compass Toggle", "SR Suspension Toggle", "SR Tire Temps Toggle",
	"SR Gears Toggle", "Measurement Toggle", "Benchmark Toggle","Save Configuration"
]}

value_variables = {
	"Speed Interval": None,
	"Speed Sensitivity": None,
	"Elevation Sensitivity": None,
	"Compass Sensitivity": None,
	"Front Tire Temp": None,
	"Rear Tire Temp": None,
	"Benchmark Speed": None
}

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("Control Panels")
		self.setGeometry(100, 100, 600, 500)

		self.tab_widget = QTabWidget()
		self.setCentralWidget(self.tab_widget)

		self.add_audio_panel()
		self.add_edit_panel()

	def add_audio_panel(self):
		panel = QWidget()
		layout = QVBoxLayout()

		for label in button_states.keys():
			button = QPushButton(label)
			button.clicked.connect(lambda checked, label=label: self.toggle_button(label))
			layout.addWidget(button)

		global_combo_audio_compass = QComboBox()
		global_combo_audio_compass.addItems(audio_compass_options)
		global_combo_audio_compass.currentIndexChanged.connect(self.audio_compass_changed)
		layout.addWidget(global_combo_audio_compass)

		panel.setLayout(layout)
		self.tab_widget.addTab(panel, "Audio & Toggles")

	def toggle_button(self, label):
		global button_states
		global configuration_values
		global audio_compass_selection
		if label == "Benchmark Toggle" and button_states[label] == False:
			button_states[label] = not button_states[label]
			speak("Bench mark in progress. Please reduce speed to 0 and engine RPM to idle")
		elif label == "Benchmark Toggle" and button_states[label] == True:
			button_states[label] = not button_states[label]
			speak("Benchmark canceled.")
		if label == "Save Configuration":
			save_configuration(button_states, configuration_values, audio_compass_selection)

		if label != "Benchmark Toggle" and label != "Save Configuration":
			button_states[label] = not button_states[label]
			speak(f"{label} toggled to {button_states[label]}")

	def audio_compass_changed(self, index):
		global audio_compass_selection
		audio_compass_selection = index
		speak(f"Audio compass option changed to {audio_compass_options[index]} ({index})")

	def add_edit_panel(self):
		panel = QWidget()
		layout = QVBoxLayout()

		global value_variables
		for label_text in value_variables.keys():
			hbox = QVBoxLayout()
			lbl = QLabel(label_text)
			edit = QLineEdit()
			edit.setAccessibleName(label_text)
			edit.setValidator(QIntValidator(0, 10000))
			hbox.addWidget(lbl)
			hbox.addWidget(edit)
			value_variables[label_text] = edit
			layout.addLayout(hbox)

		submit_button = QPushButton("Submit")
		submit_button.clicked.connect(self.submit_values)
		layout.addWidget(submit_button)

		panel.setLayout(layout)
		self.tab_widget.addTab(panel, "Settings")

	def submit_values(self):
		global value_variables
		all_values_valid = True

		for label, edit in value_variables.items():
			text = edit.text().strip()
			if text and text.isdigit():
				value_variables[label] = int(text)
			elif text:
				all_values_valid = False

		if not all_values_valid:
			speak("Please enter valid integer values in all fields.")
		else:
			speak("All values set.")
def mainStart():
	if __name__ == '__main__':
		app = QApplication([])
		main_window = MainWindow()
		main_window.show()
		app.exec_()
def updateVars():
	global configuration_values
	global speedInterval
	global speedSense
	global elevationSense
	global compassSense
	global maxTF
	global maxTR
	global bmSpeed
	global bmMonitor
	global metric
	global speakingTemp
	global speakingSusp
	global speakingGear
	global speakingCompass
	global speakingElevation
	global speakingSpeed
	global audioCompass
	global compassClicks
	global speedMon
	global elevationSensor
	global suspAudio
	global tempAudio
	global button_states
	global value_variables
	global audio_compass_selection
	if isinstance(value_variables["Speed Interval"], int):
		speedInterval=value_variables["Speed Interval"]
		configuration_values["Speed Interval"] = speedInterval
	if isinstance(value_variables["Speed Sensitivity"], int):
		speedSense=value_variables["Speed Sensitivity"]
		configuration_values["Speed Sensitivity"] = speedSense
	if isinstance(value_variables["Elevation Sensitivity"], int):
		elevationSense=value_variables["Elevation Sensitivity"]
		configuration_values["Elevation Sensitivity"] = elevationSense
	if isinstance(value_variables["Compass Sensitivity"], int):
		compassSense=value_variables["Compass Sensitivity"]
		configuration_values["Compass Sensitivity"] = compassSense
	if isinstance(value_variables["Front Tire Temp"], int):
		maxTF=value_variables["Front Tire Temp"]
		configuration_values["Front Tire Temp"] = maxTF
	if isinstance(value_variables["Rear Tire Temp"], int):
		maxTR=value_variables["Rear Tire Temp"]
		configuration_value["Rear Tire Temp"] = maxTR
	if isinstance(value_variables["Benchmark Speed"], int):
		bmSpeed=value_variables["Benchmark Speed"]
		configuration_values["Benchmark Speed"] = bmSpeed
	metric=button_states["Measurement Toggle"]
	speakingTemp=button_states["SR Tire Temps Toggle"]
	speakingSusp=button_states["SR Suspension Toggle"]
	speakingGear=button_states["SR Gears Toggle"]
	speakingCompass=button_states["SR Compass Toggle"]
	speakingElevation=button_states["SR Elevation Toggle"]
	speakingSpeed=button_states["SR Speed Toggle"]
	if audio_compass_selection == 0:
		audioCompass = False
		compassClicks=False
	elif audio_compass_selection == 1:
		audioCompass=True
		compassClicks=False
	elif audio_compass_selection == 2:
		audioCompass=False
		compassClicks=True
	elif audio_compass_selection == 3:
		audioCompass=True
		compassClicks=True
	speedMon = button_states["Speed Audio Toggle"]
	elevationSensor=button_states["Elevation Audio Toggle"]
	suspAudio= button_states["Suspension Audio Toggle"]
	tempAudio=button_states["Tire Temp Audio Toggle"]
	bmMonitor = button_states["Benchmark Toggle"]
	if bmMonitor == False:
		armedBenchmark=False
		startBenchmark=False
		bmStartTime= 0
		bmEndTime = 0




#Wrapping the speech output to be more user friendly by defaulting the interrupt to on.
def speak(text,interrupt=True):
	o.output(text, interrupt)
def print_Speak(speaking, message):
	if speaking == True:
		speak(message)
		print(message)
	else:
		print(message)

def execute_After(func, interval):
	"""
	Executes a function after a given interval if not executed in that interval.
	:param func: Function to be executed.
	:param interval: Time in seconds after which the function will be executed.
	"""
	current_time = time.time()
	if func not in last_executed or current_time - last_executed[func] >= interval:
		last_executed[func] = current_time
		timer = threading.Timer(interval, func)
		timer.start()

# Function to load sound file
def load_sound(file_path):
	return AudioSegment.from_file(file_path)

# Function 2: Adjust stereo panning
def set_stereo_panning(sound, panning):
	return sound.pan(panning)

# Function 3: Adjust pitch
def set_pitch(sound, pitch):
	new_sample_rate = int(sound.frame_rate * (2 ** pitch))
	return sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})

# Function 4: Adjust volume
def set_volume(sound, volume):
	return sound + volume
sound = load_sound("beep.wav")
speed = load_sound("speed.wav")
click = load_sound("click.wav")
ascend = load_sound("ascend.wav")
descend = load_sound("descend.wav")
temp = load_sound("temp.wav")
tempR = load_sound("temp.wav")
tempR = set_pitch(temp, -1)
susp = load_sound("susp.wav")
Suspfl = load_sound("susp.wav")
Suspfr = load_sound("susp.wav")
Susprl = load_sound("susp.wav")
Susprr = load_sound("susp.wav")
Suspfl = set_stereo_panning(Suspfl,-1)
Suspfr = set_stereo_panning(Suspfr,1)
Susprl = set_stereo_panning(Susprl,-1)
Susprl = set_pitch(Susprl, -1)
Susprr = set_stereo_panning(Susprr,1)
Susprr = set_pitch(Susprr, -1)
newClick=click
newCompass= sound
def export_and_load(sound):
	buffer = io.BytesIO()
	sound.export(buffer, format="wav")
	buffer.seek(0)
	loadedSound = pygame.mixer.Sound(buffer)
	buffer.close()
	return loadedSound
speed = export_and_load(speed)
ascend = export_and_load(ascend)
descend = export_and_load(descend)
temp = export_and_load(temp)
tempR = export_and_load(tempR)
susp = export_and_load(susp)
Suspfl = export_and_load(Suspfl)
Suspfr = export_and_load(Suspfr)
Susprl = export_and_load(Susprl)
Susprr = export_and_load(Susprr)
def ash(masterSound, heading):
	sound = masterSound
	# Convert the heading to a panning value (-1 to 1)
	# 270 degrees -> -1, 90 degrees -> 1
	panning = (heading - 180) / 90
	if panning > 1:
		panning = -2 + panning
	elif panning < -1:
		panning = 2 + panning

	# Correct the panning logic
	if 270 > heading > 90:
		panning = -panning

	# Adjust panning
	sound = sound.pan(panning)
	# Adjust pitch 
	pitch=0
	if heading > 270:
		pitch= (heading-270)/90
	if heading > 180 and heading < 270:
		pitch= -1+((heading-180)/90)
	if heading > 90 and heading < 180:
		pitch = 1-(heading/90)
	if heading > 0 and heading < 90:
		pitch = 1-(heading/90)
	if heading == 270 or heading == 90:
		pitch=0
	if heading == 0:
		pitch=1
	if heading == 180:
		pitch =-1
	sound = set_pitch(sound, pitch)
	return sound
def preload_compass_sounds(master_sound):
    compass_sounds = []
    for heading in range(360):
        adjusted_sound = ash(master_sound, heading)
        sound_handle = export_and_load(adjusted_sound)
        compass_sounds.append(sound_handle)
    return compass_sounds
clickSounds = preload_compass_sounds(click)
compassSounds = preload_compass_sounds(sound)
def sound_thread_function(sound_name, soundHandle, index=None):
	if index is not None:
		threadSound = soundHandle[index]
	else:
		threadSound = soundHandle

	while True:
	# Wait for the event to be set
		sound_events[sound_name].wait()
		# Play sound
		threadSound.play()
		# Logic to stop the sound when the event is cleared
		sound_events[sound_name].clear()

def create_sound_thread(sound_name, soundHandle):
	if isinstance(soundHandle, list):
		# Handle a list of sounds
		for index, single_sound in enumerate(soundHandle):
			sound_events[f"{sound_name}_{index}"] = threading.Event()
			thread = threading.Thread(target=sound_thread_function, args=(f"{sound_name}_{index}", soundHandle, index))
			thread.daemon = True
			thread.start()
	else:
		# Handle a single sound
		sound_events[sound_name] = threading.Event()
		thread = threading.Thread(target=sound_thread_function, args=(sound_name, soundHandle))
		thread.daemon = True
		thread.start()

def addSound(sound_name, index=None):
	if index is not None:
		sound_events[f"{sound_name}_{index}"].set()
	else:
		sound_events[sound_name].set()

# Example usage for compassSounds list
#create_sound_thread("compass", compassSounds)
# To play a specific sound from compassSounds
#addSound("compass", index=45)  # Plays the sound at index 45 in compassSounds
def convertDir(degrees):
	if 337.5 <= degrees < 360 or 0 <= degrees < 22.5:
		return "North"
	elif 22.5 <= degrees < 67.5:
		return "Northeast"
	elif 67.5 <= degrees < 112.5:
		return "East"
	elif 112.5 <= degrees < 157.5:
		return "Southeast"
	elif 157.5 <= degrees < 202.5:
		return "South"
	elif 202.5 <= degrees < 247.5:
		return "Southwest"
	elif 247.5 <= degrees < 292.5:
		return "West"
	elif 292.5 <= degrees < 337.5:
		return "Northwest"
	else:
		return "Invalid degree"
def speedConvert(speed_mps):
	if metric == False:
		return speed_mps * 2.23694
	if metric == True:
		return speed_mps * 3.6
def speedBenchMark(curRPM, idleRPM, curSpeed, curTime):
	global bmMonitor
	global armedBenchmark
	global bmStartTime
	global bmEndTime
	global bmTotalTime
	global startBenchmark
	global bmSpeed
	speed=curSpeed
	curRPM = round(curRPM)
	idleRPM = round(idleRPM)
	if bmMonitor == True:
		speed=speedConvert(speed)
		if armedBenchmark == False and round(curRPM) == round(idleRPM) and round(speed) == 0:
			armedBenchmark = True
			print("benchmark ready")
		if armedBenchmark == True and curRPM != idleRPM and startBenchmark == False:
			startBenchmark = True
			bmStartTime = curTime
			print("Timer started.")
		if armedBenchmark == True and startBenchmark == True and speed >= bmSpeed:
			bmMonitor = False
			armedBenchmark = False
			startBenchmark = False
			bmEndTime=curTime
			bmTotalTime = (bmEndTime-bmStartTime)/1000
			print_Speak(True,str(bmSpeed)+" "+metricString+" bench mark completed in "+str(bmTotalTime)+" seconds")
# Set the server's port
port = 5300

# Create a socket object for UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', port))
server_socket.settimeout(1)
print(f"Listening for packets on port {port}")

def packetReceiver():
	global packed_data
	global packeting
	# Continuously listen for packets
	while packeting:
		# Receive packets
		try:
			data, addr = server_socket.recvfrom(332)  # Adjust buffer size if necessary
			# Define the format string for unpacking
			format_string = 'iI27f4i20f5i17fH6B4bfi'
			# Check if the received data matches the expected size
			if len(data) >= 0:
				# Pack the data according to the specified format
				packed_data = struct.unpack(format_string, data[:struct.calcsize(format_string)])
			else:
				print("Received data is shorter than expected format at "+str(len(data))+".")
		except socket.timeout:
			continue  # This allows checking the packeting flag periodically
		except Exception as e:
			print(f"Error: {e}")
			break  # Handle other exceptions, e.g., socket being closed
		speedBenchMark(packed_data[4], packed_data[3], packed_data[61], packed_data[1])

def processPacket():
	unpacked_data = []
	unpacked_data = packed_data
	# Print the unpacked data (or process/store it as needed)
	global speedInterval
	global curSpeedInt
	global preSpeed
	global preGear
	global bottomedFL
	global bottomedFR
	global bottomedRL
	global bottomedRR
	global maxTF
	global maxTR
	global frontMax
	global rearMax
	global preTTFl
	global preTTFR 
	global preTTRL 
	global preTTRR
	global preSuspFL
	global preSuspFR 
	global preSuspRL
	global preSuspRR
	global preYaw
	global preDir
	global preClick
	global speedMonitor
	global exceed
	global preElevation
	global elevationSense
	global compassSense
	curGear = unpacked_data[81]
	if curGear != preGear and curGear != 11 and curGear != 0:
		print_Speak(speakingGear,"Gear "+str(curGear))
		preGear=curGear
	elif curGear != preGear and curGear == 0:
		print_Speak(speakingGear, "Reverse")
		preGear=curGear
	TTFL = unpacked_data[64]
	TTFR = unpacked_data[65]
	TTRL = unpacked_data[66]
	TTRR = unpacked_data[67]
	if TTFL >= maxTF and frontMax == False or TTFR >= maxTF and frontMax == False:
		print_Speak(speakingTemp, "Front tires have exceeded "+str(maxTF)+" degrees. Front left is "+str(TTFL)+" and front right is "+str(TTFR)+".")
		frontMax = True
		if tempAudio == True:
			addSound('front temp')
	if TTRL >= maxTR and rearMax == False or TTRR >= maxTR and rearMax == False:
		print_Speak(speakingTemp, "Rear tires have exceeded "+str(maxTR)+" degrees")
		rearMax = True
		if tempAudio == True:
			addSound('rear temp')
	if TTFL < maxTF and TTFR < maxTF and frontMax == True:
		print_Speak(speakingTemp, "Front tires have dropped below "+str(maxTF)+" degrees to "+str(TTFL)+" front left, and "+str(TTFR)+" front right.")
		frontMax=False
	if TTRL < maxTR and TTRR < maxTR and rearMax == True:
		print_Speak(speakingTemp, "Rear tires have fallen below "+str(maxTR)+" degrees")
		rearMax = False
	suspFL = unpacked_data[17]
	suspFR = unpacked_data[18]
	suspRL = unpacked_data[19]
	suspRR = unpacked_data[20]
	if suspFL >= 1 and bottomedFL == False:
		print_Speak(speakingSusp, "Front left suspension bottomed out")
		bottomedFL = True
		if suspAudio == True:
			addSound('Suspfl')
	if suspFL < 1 and bottomedFL == True:
		bottomedFL = False
	if suspFR >= 1 and bottomedFR == False:
		print_Speak(speakingSusp, "Front right suspension bottomed out")
		bottomedFR = True
		if suspAudio == True:
			addSound('Suspfr')
	if suspFR < 1 and bottomedFR == True:
		bottomedFR = False
	if suspRL >= 1 and bottomedRL == False:
		print_Speak(speakingSusp, "Rear left suspension bottomed out")
		bottomedRL = True
		if suspAudio == True:
			addSound('Susprl')
	if suspRL < 1 and bottomedRL == True:
		bottomedRL = False
	if suspRR >= 1 and bottomedRR == False:
		print_Speak(speakingSusp, "Rear right suspension bottomed out")
		bottomedRR = True
		if suspAudio == True:
			addSound('Susprr')
	if suspRR < 1 and bottomedRR == True:
		bottomedRR = False
	if preElevation < unpacked_data[59] or preElevation > unpacked_data[59]:
		curElevation = unpacked_data[59]
		if abs(preElevation-curElevation) >= elevationSense:
			if curElevation > preElevation:
				if elevationSensor == True:
					addSound('ascend')
				print_Speak(speakingElevation, "Ascending")
			if curElevation < preElevation:
				if elevationSensor == True:
					addSound('descend')
				print_Speak(speakingElevation, "Descending")
			preElevation=curElevation
	curYaw = int((unpacked_data[14] * (180 / math.pi)) + 180)
	if curYaw == 360:
		curYaw = 0
	yawDiff = int(abs(preYaw - curYaw) % 360)
	clickDiff = int(abs(preClick - curYaw) % 360)
	if clickDiff > 180:
		clickDiff = 360 - clickDiff
	if yawDiff > 180:
		yawDiff = 360 - yawDiff
	if preYaw != curYaw and yawDiff > 1:
		preYaw=curYaw
		if abs(clickDiff) >= compassSense and compassClicks == True:
			preClick=curYaw
			addSound('click', preYaw)
		curDir = convertDir(round(curYaw))
		if(preDir!=curDir):
			preDir = curDir
			if audioCompass == True:
				addSound('compass', preYaw)
			print_Speak(speakingCompass, curDir)
	curSpeed = speedConvert(unpacked_data[61])
	if curSpeed != preSpeed and abs(curSpeed-preSpeed) >= speedSense:
		preSpeed=curSpeed
		if curSpeed > preSpeed:
			curSpeedInt = curSpeedInt+1
			if speedMon == True:
				addSound('speed')
		else:
			curSpeedInt = curSpeedInt-1
			if speedMon == True:
				addSound('speed')
		if speedInterval == 0 or curSpeedInt % speedInterval == 0:
			print_Speak(speakingSpeed, str(int(curSpeed))+" "+metricString)

def shutDown():
	print("Stopping the server...")
	pygame.mixer.quit()
	packeting=False
	time.sleep(2)
	server_socket.close()
	packetThread.join()




mainThread = threading.Thread(target=mainStart)
packetThread = threading.Thread(target=packetReceiver)
button_states, value_variables, audio_compass_selection = load_configuration()
try:
	packetThread.start()
	mainThread.start()
	create_sound_thread('descend', descend)
	create_sound_thread('ascend', ascend)
	create_sound_thread('front temp', temp)
	create_sound_thread('rear temp', tempR)
	create_sound_thread('Suspfl', Suspfl)
	create_sound_thread('Suspfr', Suspfr)
	create_sound_thread('Susprl', Susprl)
	create_sound_thread('Susprr', Susprr)
	create_sound_thread('speed', speed)
	create_sound_thread('click', clickSounds)
	create_sound_thread('compass', compassSounds)

	while True:
		updateVars()
		if packed_data != []:
			processPacket()
		time.sleep(.05)
		if mainThread.is_alive() == False:
			shutDown()
			break
except KeyboardInterrupt:
	# Close the socket when interrupted (e.g., by Ctrl+C)
	shutDown()

