# Accessible_Real_Time_Forza_Companion
A blind and visually impaired  accessible real time companion app for use with Forza Motorsports
Welcome to the Accessible Real Time Forza Companion (ART FC) guide.
To jump to a section, search for the following headings:
###Set up
###Features
###Usage
###Set up
    To set up ART FC launch Forza Motorsports and navigate to the 'game play and HUD' tab. Then turn on the 'data out' option. Arrow down to the 'Data Out IP Address" and input your computer's internal network IP address if you are on the Xbox console. If you are on PC you can use the local host address of '127.0.0.1'. Next, navigate down to the 'Data Out IP Port' option and set it to port '5300'. Finally, navigate to the 'Data Out Packet Format' option, and set it to 'Car Dash'. Now you are all set up and ready to use ART FC.
##Features
    Currently ART FC supports the current features:
1. A compass - This can be read out by the screen reader when you reach certain directions, or you can have an audio queue that plays to indicate direction. There are three modes for the audio queues, one plays sounds for the 8 cardinal directions, and the other plays clicks based on your compass sensitivity. You can toggle all of these to suit your preference.
2. Speed monitoring - Your speed is monitored and reported with the screen reader and or audio queues based on your own preference. Speed intervals work in conjunction with speed sensitivity to read out speeds. For example, if speed sensitivity is set to 5 with an interval of 5, only when there have been 5 changes in speed greater than 5 Mph or Kph will the speed be read. Set intervals to 0 if you want to have the speed read whenever the change in speed is greater than the speed sensitivity level.
3. Elevation Sensor - This monitors the vehicles elevation on the track and will alert the driver with a sound, a screen reader announcement, or both if the vehicle ascends or descends past the elevation sensitivity. The elevation sensitivity can be adjusted by the user.
4. Tire temp monitoring - Toggleable screen reader announcements and audio queues for tire temps exceeding a threshold for front and rear tires that can be set by the user.
5. Suspension Monitoring - Toggleable screen reader announcements and audio queues for when the suspension bottoms out, includes which part of the suspension bottoms out in both announcements and audio.
6. Gear announcements - Screen reader announces gear, can be toggled. Useful for automatic transmission settings.
7. Speed benchmarking - You can start an acceleration benchmark to get your personal times for reaching certain speeds from a complete stop.
8. Saved Configuration - The user has the ability to save their configuration to be loaded on the next start up. Only one configuration file is supported at this time.
## Usage
    To use ART FC, extract the zip folder and run the executable provided. You will likely be asked for access to your network. Set it to allow. Once you are on a track with a car and racing, data will begin to be received by the application. At this point you will be able to customize how the data is interpreted. Whether that's with audio queues, read out by the screen reader, or both. You can also adjust the sensitivities for various things like the compass, front and rear tire temp thresholds, elevation sensitivity, and the speed monitor. The first panel is the audio and toggles panel. Here you will adjust the audio toggles, these are all of the buttons that end with 'Toggle'. Press spacebar to toggle the settings. You will also be able to adjust what information is read out by the screen reader, these are all of the options beginning with 'SR'. To navigate to the sensitivity panel, tab to the tab control section and move right. You'll be able to tab through the various edit boxes to adjust the values. When you are done entering the sensitivities, select the submit button and press spacebar. Once you have your desired settings, you can select save configuration from the audio and toggles tab. It's the last button in the list.
