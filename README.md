# dicom_outliner
Create a HU 3000 outline in a dicom scan using a specified structure


# Dev Setup (written for Windows)
1. Clone the code from the repository and then cd into the directory.

```
git clone https://github.com/Abe404/dicom_outliner.git
cd dicom_outliner
```

2. To avoid alterating global packages. I suggest using a virtual environment. Create a virtual environment 

```
python -m venv env
```


3. And then activate it
On windows:
```
env\Scripts\activate.bat
```


# Building the installer

1. remove any existing build files.
```
python build/clean.py
```

2. Build the application
```
python build/freeze.py
```

3. Add missing dependencies (skimage/pydicom are not currently handled by the build process (pyinstaller).
```
python install_fixes.py
```

4. Create the windows application installer.
```
python build/installer.py
```
