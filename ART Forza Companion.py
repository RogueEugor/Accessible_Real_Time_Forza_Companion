from pydub import AudioSegment
from pydub.playback import play
import io
import socket
import struct
import math
import keyboard
import accessible_output2.outputs.auto
import threading
import time
#Variables
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
speakingTemp = True
speakingSusp = True
speakingGear = True
speakingCompass = False
speakingElevation = False
speakingSpeed = False
last_executed = {}
o = accessible_output2.outputs.auto.Auto()
audioCompass = False
speedMon = False
elevationSensor = False
preYaw= 0.0
preDir=""
speedMonitor = [60, 80, 100, 120]
exceed=0
preElevation=0
elevationSense=3
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

# Example usage
sound = load_sound("beep.wav")
ascend = load_sound("ascend.wav")
descend = load_sound("descend.wav")
#adjusted_sound = set_stereo_panning(sound, -1)  # Full left
#adjusted_sound = set_pitch(adjusted_sound, 0)   # One octave higher
#adjusted_sound = set_volume(adjusted_sound, 6)  # Increase volume by 6dB

# Play sound (no pause functionality)
#play(adjusted_sound)
def ash(sound_path, heading):
	# Load the sound
	sound = AudioSegment.from_file(sound_path)

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

	# Adjust pitch if heading is between 90 and 270 degrees
	if 90 < heading < 270:
		sound = set_pitch(sound, -2)

	return sound

def repeatSound(times, sound_file='beep.wav'):
	try:
		# Load the sound file
		sound = AudioSegment.from_file(sound_file)
		
		# Concatenate the sound with itself the specified number of times
		combined_sound = sound
		if times > 0:
			for _ in range(times - 1):
				combined_sound += sound
		# Play the combined sound
			play(combined_sound)
		else:
			combined_sound = set_pitch(combined_sound, -1)
			play(combined_sound)
	except FileNotFoundError:
		print(f"The sound file {sound_file} was not found.")
	except Exception as e:
		print(f"An error occurred: {e}")
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
def add_or_remove():
	global speedMonitor
	user_input = input("Enter an speed, whole numbers only: ")

	try:
		# Convert input to integer
		num = int(user_input)

		# Add or remove the number from the array
		if num in speedMonitor:
			speedMonitor.remove(num)
			print(f"Removed {num} from the speed monitor.")
		else:
			speedMonitor.append(num)
			speedMonitor = sorted(speedMonitor)
			print(f"Added {num} to the speed monitor.")

		print(f"Current speeds being monitored: {speedMonitor}")

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

def edit_Speed_Monitor():
	if keyboard.is_pressed('s'):
		add_or_remove()
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

def audio_Compass_Toggle():
	global audioCompass
	if keyboard.is_pressed('a'):
		if audioCompass == False:
			audioCompass = True
			print("Audio compass enabled")
		else:
			audioCompass = False
			print("Audio compass disabled.")
def susp_Toggle():
	global suspAudio
	if keyboard.is_pressed('r'):
		if suspAudio == False:
			suspAudio = True
			print("Suspension audio enabled")
		else:
			suspAudio = False
			print("Suspension audio disabled.")
def temp_Toggle():
	global tempAudio
	if keyboard.is_pressed('f'):
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
	if keyboard.is_pressed('m'):
		if metric == False:
			metric = True
			print("Speed is now in kMPH.")
		else:
			metric = False
			print("Speed is now in MPH.")

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

print(f"Listening for packets on port {port}")
speak(f"Listening for packets on port {port}")
total_size = 1*4 + 1*4 + 27*4 + 4*4 + 20*4 + 5*4 + 17*4 + 1*2 + 6*1 + 3*1 + 5*4

try:
	# Continuously listen for packets
	while True:
		# Receive packets
		data, addr = server_socket.recvfrom(332)  # Adjust buffer size if necessary
		# Define the format string for unpacking
		format_string = 'iI27f4i20f5i17fH6B4bfi'
		edit_Speed_Monitor()
		edit_Elevation_Monitor()
		edit_TF_Monitor()
		edit_TR_Monitor()
		# Check if the received data matches the expected size
		if len(data) >= 0:
			# Unpack the data according to the specified format
			unpacked_data = struct.unpack(format_string, data[:struct.calcsize(format_string)])
			execute_After(temp_Toggle,.15)
			execute_After(susp_Toggle, .15)
			execute_After(gear_Toggle,.15)
			execute_After(audio_Compass_Toggle,.15)
			execute_After(speed_Monitor_Toggle,.15)
			execute_After(elevation_Sensor_Toggle,.15)
			execute_After(speaking_Toggle,.15)
			execute_After(measurement_Toggle,.15)
			# Print the unpacked data (or process/store it as needed)
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
			if TTRL >= maxTR and rearMax == False or TTRR >= maxTR and rearMax == False:
				print_Speak(speakingTemp, "Rear tires have exceeded "+str(maxTR)+" degrees")
				rearMax = True
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
			if suspFL < 1 and bottomedFL == True:
				bottomedFL = False
			if suspFR >= 1 and bottomedFR == False:
				print_Speak(speakingSusp, "Front right suspension bottomed out")
				bottomedFR = True
			if suspFR < 1 and bottomedFR == True:
				bottomedFR = False
			if suspRL >= 1 and bottomedRL == False:
				print_Speak(speakingSusp, "Rear left suspension bottomed out")
				bottomedRL = True
			if suspRL < 1 and bottomedRL == True:
				bottomedRL = False
			if suspRR >= 1 and bottomedRR == False:
				print_Speak(speakingSusp, "Rear right suspension bottomed out")
				bottomedRR = True
			if suspRR < 1 and bottomedRR == True:
				bottomedRR = False
			if preElevation < unpacked_data[59] or preElevation > unpacked_data[59]:
				curElevation = unpacked_data[59]
				if abs(preElevation-curElevation) >= elevationSense:
					if curElevation > preElevation:
						if elevationSensor == True:
							play(ascend)
						print_Speak(speakingElevation, "Ascending")
					if curElevation < preElevation:
						if elevationSensor == True:
							play(descend)
						print_Speak(speakingElevation, "Descending")
					preElevation=curElevation
			if(preYaw!=(unpacked_data[14]* (180 / math.pi))+180):
				preYaw = (unpacked_data[14]* (180 / math.pi))+180
				curDir = convertDir((unpacked_data[14]* (180 / math.pi))+180)
				if(preDir!=curDir):
					preDir = convertDir((unpacked_data[14]* (180 / math.pi))+180)
					if audioCompass == True:
						play(ash("beep.wav", preYaw))
					print_Speak(speakingCompass, curDir)
			curSpeed = speedConvert(unpacked_data[61])
			accel=-1
			for element in speedMonitor:
				if(element <= curSpeed and exceed < element):
					accel=1
					exceed = element
				if(element > curSpeed and exceed >= element):
					accel=0
					exceed = element-1
			if accel == 1:
				print_Speak(speakingSpeed, str(exceed)+" MPH exceeded.")
				if speedMon == True:
					repeatSound(speedMonitor.index(exceed)+1, 'speed.wav')
			if accel == 0:
				print_Speak(speakingSpeed, "Dropped below"+str(exceed+1))
				if speedMon == True:
					repeatSound(speedMonitor.index(exceed+1), 'speed.wav')
		else:
			print("Received data is shorter than expected format at "+str(len(data))+".")

except KeyboardInterrupt:
	# Close the socket when interrupted (e.g., by Ctrl+C)
	print("Stopping the server...")
	server_socket.close()
