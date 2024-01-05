import pygame
from pydub import AudioSegment
from pydub.playback import play
import io
import socket
import struct
import math
import keyboard
import accessible_output2.outputs.auto
import threading
import concurrent.futures
import time
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
def edit_SpeedMonitor():
	global speedInterval
	global speedSense
	user_input = input("Enter desired speed interval to monitor for, whole numbers only: ")
	try:
		# Convert input to integer
		num = int(user_input)
		# Change the speed interval to the desired number
		speedInterval = num
		print("Speed interval set to "+str(num))
	except ValueError:
		print("Please enter a valid integer.")
	user_input = input("Enter desired speed sensitivity to monitor for, whole numbers only: ")
	try:
		# Convert input to integer
		num = int(user_input)
		# Change the speed sense to the desired number
		speedSense = num
		print("Speed sense set to "+str(num))
	except ValueError:
		print("Please enter a valid integer.")


def edit_Elevation_Sense():
	global elevationSense
	user_input = input("Enter a desired elevation interval for the elevation change monitor, whole numbers only: ")
	try:
		# Convert input to integer
		num = int(user_input)
		# Change the elevation sense to the desired number
		elevationSense=num
		print("Elevation sense set to "+str(num))
	except ValueError:
		print("Please enter a valid integer.")
def edit_Compass_Sense():
	global compassSense
	user_input = input("Enter desired interval for the compass clicks sensitivity, whole numbers only: ")
	try:
		# Convert input to integer
		num = int(user_input)
		# Change the sense to the desired number
		compassSense=num
		print("Compass click sensitivity set to "+str(num))
	except ValueError:
		print("Please enter a valid integer.")

def edit_Front_Temps():
	global maxTF
	user_input = input("Enter a desired maximum front tire temp to monitor for, whole numbers only: ")
	try:
		# Convert input to integer
		num = int(user_input)
		# Change the max front temp to the desired number
		maxTF=num
		print("Max front ttemp set to "+str(num))
	except ValueError:
		print("Please enter a valid integer.")
def edit_Rear_Temps():
	global maxTR
	user_input = input("Enter a desired maximum rear tire temp to monitor for, whole numbers only: ")
	try:
		# Convert input to integer
		num = int(user_input)
		# Change the max rear temp to the desired number
		maxTR = num
		print("Max rear ttemp set to "+str(num))
	except ValueError:
		print("Please enter a valid integer.")
def edit_CompassSense():
	if keyboard.is_pressed('u'):
		edit_Compass_Sense()

def edit_Speed_Monitor():
	if keyboard.is_pressed('s'):
		edit_SpeedMonitor()
def edit_TF_Monitor():
	if keyboard.is_pressed('f'):
		edit_Front_Temps()
def edit_TR_Monitor():
	if keyboard.is_pressed('r'):
		edit_Rear_Temps()

def edit_Elevation_Monitor():
	if keyboard.is_pressed('e'):
		edit_Elevation_Sense()

def speaking_Toggle():
	global speakingCompass
	global speakingSpeed
	global speakingElevation
	global speakingSusp
	global speakingTemp
	global speakingGear
	if keyboard.is_pressed('z'):
		if speakingCompass == False:
			speakingCompass = True
			print("Screen reader  compass enabled")
		else:
			speakingCompass = False
			print("Screen reader compass disabled.")
	if keyboard.is_pressed('x'):
		if speakingSpeed == False:
			speakingSpeed = True
			print("Screen reader  speed enabled")
		else:
			speakingSpeed = False
			print("Screen reader speed disabled.")
	if keyboard.is_pressed('c'):
		if speakingElevation == False:
			speakingElevation = True
			print("Screen reader  elevation enabled")
		else:
			speakingElevation = False
			print("Screen reader elevation disabled.")
	if keyboard.is_pressed('v'):
		if speakingSusp == False:
			speakingSusp = True
			print("Screen reader  announcements of bottomed out suspension enabled")
		else:
			speakingSusp = False
			print("Screen reader announcements of bottomed out suspension disabled.")
	if keyboard.is_pressed('b'):
		if speakingTemp == False:
			speakingTemp = True
			print("Screen reader  announcements of over heated front and rear tires enabled")
		else:
			speakingTemp = False
			print("Screen reader announcements of over heated front and rear tires disabled.")
	if keyboard.is_pressed('n'):
		if speakingGear == False:
			speakingGear = True
			print("Screen reader  announcements of gears enabled")
		else:
			speakingGear = False
			print("Screen reader announcements of gears disabled.")

def audio_Compass_Toggle():
	global audioCompass
	global compassClicks
	if keyboard.is_pressed('a'):
		if audioCompass == False and compassClicks == False:
			audioCompass = True
			print("Audio compass enabled")
		elif audioCompass == True and compassClicks == False:
			audioCompass = True
			print("Audio compass and clicks enabled")
			compassClicks = True
		elif audioCompass == True and compassClicks == True:
			audioCompass = False
			compassClicks = True
			print("Only compass clicks enabled.")
		else:
			audioCompass = False
			compassClicks=False
			print("Audio compass and clicks disabled.")
def susp_Toggle():
	global suspAudio
	if keyboard.is_pressed('y'):
		if suspAudio == False:
			suspAudio = True
			print("Suspension audio enabled")
		else:
			suspAudio = False
			print("Suspension audio disabled.")
def benchmark_Toggle():
	global bmMonitor
	global bmSpeed
	if keyboard.is_pressed('j'):
		if bmMonitor==False:
			user_input = input("Enter desired bench mark speed, whole numbers only: ")
			try:
				# Convert input to integer
				num = int(user_input)
				# Change the benchmark speed to the desired number
				bmSpeed = num
				print("Benchmark set for "+str(bmSpeed))
			except ValueError:
				print("Please enter a valid integer.")
		if bmMonitor == False:
			bmMonitor = True
			print("Bench mark in progress. Please reduce speed to 0 and engine RPM to idle")
		else:
			bmMonitor = False
			armedBenchmark=False
			startBenchmark=False
			bmStartTime= 0
			bmEndTime = 0
			print("Benchmarking ended..")

def temp_Toggle():
	global tempAudio
	if keyboard.is_pressed('h'):
		if tempAudio == False:
			tempAudio = True
			print("Tire temp audio enabled")
		else:
			tempAudio= False
			print("Tire temp audio disabled.")
def gear_Toggle():
	global gearAudio
	if keyboard.is_pressed('g'):
		if gearAudio == False:
			gearAudio = True
			print("Gear audio enabled")
		else:
			gearAudio = False
			print("Gear audio disabled.")

def measurement_Toggle():
	global metric
	global metricString
	if keyboard.is_pressed('m'):
		if metric == False:
			metricString="Kph"
			metric = True
			print("Speed is now in Kph.")
		else:
			metricString="Mph"
			metric = False
			print("Speed is now in Mph.")

def elevation_Sensor_Toggle():
	global elevationSensor
	if keyboard.is_pressed('w'):
		if elevationSensor == False:
			elevationSensor = True
			print("Elevation sensor enabled")
		else:
			elevationSensor = False
			print("Elevation sensor disabled.")
def speed_Monitor_Toggle():
	global speedMon
	if keyboard.is_pressed('q'):
		if speedMon == False:
			speedMon = True
			print("Speed monitor enabled.")
		else:
			speedMon = False
			print("Speed monitor disabled.")
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





packetThread = threading.Thread(target=packetReceiver)
try:
	packetThread.start()
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
		edit_Speed_Monitor()
		edit_Elevation_Monitor()
		edit_TF_Monitor()
		edit_TR_Monitor()
		edit_Speed_Monitor()
		edit_CompassSense()
		execute_After(temp_Toggle,.3)
		execute_After(susp_Toggle, .3)
		execute_After(gear_Toggle,.3)
		execute_After(audio_Compass_Toggle,.3)
		execute_After(speed_Monitor_Toggle,.3)
		execute_After(elevation_Sensor_Toggle,.3)
		execute_After(speaking_Toggle,.3)
		execute_After(measurement_Toggle,.3)
		execute_After(benchmark_Toggle,.3)
		if packed_data != []:
			processPacket()
		time.sleep(.05)
except KeyboardInterrupt:
	# Close the socket when interrupted (e.g., by Ctrl+C)
	print("Stopping the server...")
	pygame.mixer.quit()
	packeting=False
	time.sleep(2)
	server_socket.close()
	packetThread.join()


