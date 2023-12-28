# MyDualsenseChargeApp
This is a small piece of software written in Python, allowing Windows user feel like human again by having the possibility to check their DualSense controllers charge level from system Tray.

This software is based on [this great Python library](https://github.com/yesbotics/dualsense-controller-python/tree/main). You can also make wonderful things with it.

## 🔨 Prerequisites
- ⚙ hidapi.dll shared library (bundled) or you can get (build yourself) from [this repository](https://github.com/libusb/hidapi).
- 🐍 Python 3.10+ for dualsense-controller library
- *not this one* -> 🎮 DualSense controller (negotiable)
- 🛠 Some other libraries you'll find in requirements.txt

## ⁉ How2Use
Just open the file and enjoy. Also you can bundle it with PyInstaller with --noconsole and optionally --onefile keys so it will work like a commercial piece of software but be aware that you'll 90% get a Trojan message which you'll need to suppress in your ant*virus "software".

## 🐱‍👤 Someting more
This is just a prototype program written for fun. Any additional improvements are always welcome! Please create a MR for that.