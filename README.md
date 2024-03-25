# Browser (Leonardo)

## General
This exhibit is part of the Leonardo ehibition.
It shows scans of a book with original writings by Leonardo, with an ability to navigate pages forward and backward using buttons.
Also, it is possible to use a magnifying glass tool to magnify parts of the writings, move it around, and show/hide it.
The exhibit is designed to work with a (large) touch screen but can be run using a mouse as well with a cursor.

## Installation & Run
The exhibit runs using python 3 on linux, using the pygame engine.

After the latest python 3 installation, use:

```
pip3 install pygame
pip3 install evdev
```

To install all necessary packages.

Then, to run, go to the root project dir and run:

```
python3 Leonardo.py
```

## Config
The exhibit supports an array of configurations using a config json file located in assets/config/config.json
Following is a complete description of all options:

### touch, touchDeviceName, touchMaxX, touchMaxY

These 4 keys define the characteristics of the touch screen connected to the exhibit.
touch should be set to true for the exhibit to use touch (otherwise a mouse is supported).
touchDeviceName is a partial name that is used to match the touch screen device. Use a partial name that is also unique.
You can enumerate all linux devices using this command:

```
lsinput
```

Finally, the touchMaxX and touchMaxY represent the logical screen resolution that evdev works with.
The exhibit will convert these coordinates to the actual screen resolution coordinates.
These usually change with the screen size, and are usually 4096x4096 but can also be 2048x2048 and 1024x1024, or other numbers potentially.
The best way to find out the proper value, is to add print statements in the TouchScreen.py file, in the readTouch method, in case the event type is ecodes.EV_ABS.

Like this:
```
elif event.type == ecodes.EV_ABS:
	absEvent = categorize(event)

	if absEvent.event.code == 0:
		currX = absEvent.event.value
	elif absEvent.event.code == 1:
		currY = absEvent.event.value

	print(currx, curry)
```

Then, run the exhibit, and touch various corners of the screen. It will be very easy to conclude on the max value sknowing they are a power of 2.

### magnifierImageCenterX, magnifierImageCenterY, magnifierWidth, magnifierHeight

These 4 keys describe the properties of the magnifier image, to make the magnifying effect look accurate.
They describe the width and height of the actual rectangular part of the image that bounds the magnifier circle (these are magnifierWidth and magnifierHeight), and the x and y specifying the exact center of that rectangle (magnifierImageCenterX and magnifierImageCenterY respectively). As always, x increases from left to right, and y from top to bottom.
Using these 4 keys, the exhibit can successfully know where it should locate the larger images, making the effect work to perfection.

### magnifierInitialPositionX, magnifierInitialPositionY

These 2 keys specify where the magnifier is located (its top/left corner) when you first turn it on (after the exhibit loads for the first time). If this is not the first time, it will reappear where it was beforehand, unless a long time passes (defined as 300 seconds), and that will also reset the magnifier position to this position. As always, x increases from left to right, and y from top to bottom.

### showFPS

This key can be set to true to show an FPS (frames per second) value and measure performance issues. FPS should be ideally between 30 and 60.

## Log
The exhibit supports a rotating log named browser.log in the root directory, that logs the following events:
* START (the exhibit loads)
* INIT (exhibit initalization is done)
* IDLE (exhibit was idle for 300 seconds, magnifier position is resetted and book page goes back to cover)
* NEXT,N (page was flipped forward to show page number N)
* PREV,N (page was flipped backwards to show page number N)
* MAGNIFIER_ON (magnifier was turned on)
* MAGNIFIER_OFF (magnifier was turned off)
* MAGNIFIER_MOVE_START,X,Y (magnifier drag has started at point x,y)
* MAGNIFIER_MOVE_END,X,Y (magnifier drag has ended at point x,y)

Each event will be prefixed by a timestamp (year-month-day hour:minute:seconds.mili with year as 4 digit, all rest as 2 digit and milliseconds as 3 digits) then a comma, following the event as specified above.