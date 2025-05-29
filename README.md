
# 📱 Android Bootanimation Previewer

Welcome to the **Android Bootanimation Previewer**! 👋 This Python script allows you to quickly and easily preview `bootanimation.zip` files right on your desktop, saving you the hassle of flashing or rebooting your Android device every time you want to see a new boot animation.

Whether you're a ROM developer, a theming enthusiast, or just curious about what's inside a `bootanimation.zip`, this tool is for you! ✨

---

## 🚀 Features

* **Flexible File Input:** Preview any `bootanimation.zip` file by specifying its path using a command-line argument.
* **Default File Handling:** If no file is specified, it automatically looks for `bootanimation.zip` in the current working directory.
* **Dual `desc.txt` Format Support:** Accurately parses `desc.txt` files using both `p` (legacy/AOSP) and `c` (Chromium/newer variants) prefixes for animation parts.
* **Multiple Image Format Compatibility:** Supports both `.png` and `.jpg` (including `.jpeg`) image formats commonly found inside `bootanimation.zip` files.
* **Automatic Cleanup:** Extracts the `bootanimation.zip` contents to a temporary folder and automatically cleans it up after the preview session.
* **Informative Console Output:** Provides helpful messages and error indications during the process.

---

## 📦 How to Use

### 1. Prerequisites

Make sure you have **Python 3.6+** installed on your system.
You'll also need the following Python libraries. You can install them via `pip`:

```bash
pip install pygame Pillow
```

### 2. Get the Script

1.  Save the provided Python code (your `bootanimation_previewer.py` file) to your local machine.
2.  (Optional but recommended) Rename the file to something descriptive, like `bootanimation_previewer.py` or `preview_bootanimation.py`.

### 3. Run the Previewer

Open your terminal or command prompt and navigate to the directory where you saved the script. Then, execute it using one of the following methods:

* **To preview `bootanimation.zip` in the current directory (default):**
    ```bash
    python bootanimation_previewer.py
    ```

* **To preview a specific `bootanimation.zip` file (using the `-f` or `--file` argument):**
    ```bash
    python bootanimation_previewer.py -f "/path/to/your/bootanimation.zip"
    ```
    (Replace `"/path/to/your/bootanimation.zip"` with the actual full path to your file. Use quotes if the path contains spaces!)
* **To change preview scale for `bootanimation.zip`  (using the `-s` or `--scale` argument):**
    ```bash
    python bootanimation_previewer.py -s 0.5
    ```
---

## ⚠️ Important Notes

* **Root Access:** This script previews the animation; it does NOT install it on your device. Installing a boot animation on an Android device typically requires root access or a custom recovery.
* **`bootanimation.zip` Structure:** The `bootanimation.zip` file must be a non-compressed (store method) ZIP archive containing a `desc.txt` file and folders (e.g., `part0`, `part1`) with sequentially numbered image frames.
* **Error Handling:** While the script has basic error handling, highly malformed `bootanimation.zip` files might still cause unexpected behavior.

---

## 🤝 Contributing & Support

This tool was created to help simplify the process of previewing Android boot animations. If you find issues or have suggestions for improvement, feel free to contribute or open an issue on GitHub!

---
