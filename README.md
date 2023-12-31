# Accessible_Real_Time_Forza_Companion
A blind and visually impaired  accessible real time companion app for use with Forza Motorsports
Welcome to the Accessible Real Time Forza Companion (ART FC) guide.
To jump to a section, search for the following headings:
*** Setting up
***Features
*** Usage
***Important Note
*** Keyboard shortcuts

*** Setting up
    To set up ART FC launch Forza Motorsports and navigate to the 'game play and HUD' tab. Then turn on the 'data out' option. Arrow down to the 'Data Out IP Address" and input your computer's internal network IP address if you are on the XBox console, and if you are on PC you can use the local host address of '127.0.01'.  Next, navigate down to the 'Data Out IP Port' option and set it to port '5300'. Finally, navigate to the 'Data Out Packet Format' option, and set it to 'Car Dash'. Now you are all set up and ready to use ART FC.
***Features
    Currently ART FC supports the current features:
1. A compass - This can be read out by the screen reader, or you can have an audio queue that plays to indicate direction. You can also have both of these options enabled.
2. Speed monitoring - This will alert the driver once they have reached or fall below specific speeds. This can be read out by the screen reader, have audio queues played, or both. The audio queue system will play the speed indicator sound once when the first speed is reached, then twice quickly when the second speed is reached, and so on so forth. When the speed drops below the most recently monitored speed, it will play the speed indicator one less time than it did when it reached that threshold, or at a lower pitch if the speed drops below the first threshold. By default, the speed monitor thresholds are set to 60, 80, 100, and 120. These can be removed or added to by the user.
3. Elevation Sensor - This monitors the vehicles elevation on the track and will alert the driver with a sound, a screen reader announcement, or both if the vehicle ascends or descends past the elevation sensitivity. The elevation sensitivity can be adjusted by the user.
*** Usage
    To use ART FC, extract the zip folder and run the executable provided. It will open a command line terminal and likely ask you for access to your network. Set it to allow. Once you are on a track with a car and racing, data will begin to be received by the terminal. At this point you will be able to customize how the data is interpreted. Whether that's with audio queues, read out by the screen reader, or both. You can also adjust the speeds you wish to monitor, and how sensitive you want the elevation sensor to be.
***Important Note
    When setting the speeds in the speed monitor and the elevation sensitivity, be sure to clear the prompt text box before submitting the value.
*** Keyboard shortcuts
A: Disables or enables the audio compass
Q: Disables or enables the speed monitor audio queues.
W: Disables or Enables the elevation sensor audio queues.
Z: disables or enables the screen reader from reading out the compass while in another window.
X: enables or disables the screen reader from reading out the speed monitor while in another window.
C: disables or enables the screen reader from reading out the elevation sensor while in another window.
S: Allows you to input a speed to add or remove from the speed monitor
E: Allows you to set the elevation sensitivity
