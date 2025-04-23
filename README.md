README.md
### Script: Red_Dot_Counter.py

## 1. Introduction
The Red Dot Counter is a Python tool designed to automatically identify and count red fluorescent spots in microscopy images (e.g., RFP‑stained structures in muscle cell cross‑sections). It enhances image contrast, detects candidate spots, filters by local contrast, and produces annotated outputs along with detailed parameter summaries.

## 2. Prerequisites
- Python 3.7 or above
- A virtual environment (recommended)
- Install required packages:
  ```bash
  pip install opencv-python numpy pandas openpyxl
  ```

## 3. Directory Layout
```
project-root/
├─ mito_img/           # Place all raw images here (no “_counted” suffix)
├─ output/            # Script will create timestamped subfolders here
│   └─ MMDDYY_HHMMSS/   # Contains results for each run
└─ Red_Dot_Counter.py # Main script file
```  

## 4. Configuration
Open `Red_Dot_Counter.py` and locate the configuration section near the top. Adjust these values as needed:

| Parameter          | Default | Description                                          |
|--------------------|---------|------------------------------------------------------|
| `MIN_DIST`         | 8.0     | Minimum pixel distance between two detected spots    |
| `AMBIENT_SCALE`    | 2.0     | Factor to scale small‑circle radius for background   |
| `CONTRAST_THR`     | 25.0    | Minimum absolute intensity difference (dot vs ring)  |
| `REL_THR`          | 0.25    | Minimum relative contrast (25% increase)            |
| `CLAHE_CLIP`       | 3       | CLAHE clip limit (contrast enhancement strength)    |
| `CLAHE_GRID`       | (8,8)   | CLAHE grid size (tiles in x,y for equalization)     |
| `minArea/maxArea`  | 25/81   | Blob area range in pixels                            |
| `minThreshold`     | 100     | Minimum gray‑value threshold for blob detection     |
| `maxThreshold`     | 255     | Maximum threshold for blob detection                |

> **Tip:** Run the script once with default settings, inspect the printed intensity‑difference percentiles to choose thresholds that separate true spots from noise.

## 5. Running the Script
1. Ensure raw images are in `mito_img/`.  
2. In a terminal (inside your virtual environment), run:
   ```bash
   python Red_Dot_Counter.py
   ```
3. The script will process each image and create a new folder under `output/` named by the current date/time.

## 6. Output Files
Within the timestamped subfolder, you will find:
- **`<image_name>_counted.jpg`**: original image annotated with blue circles and overlaid count.  
- **`parameters_and_values.txt`**: a table of all parameter names, values, descriptions, plus per‑image count summary.  
- **`image_counts.xlsx`**: spreadsheet listing two columns—`Image` (filename) and `Count` (number of detected spots).

## 7. Interpreting Results
- Verify that the blue circles accurately overlay the red spots.  
- If circles are missing or spurious, revisit **Section 4** to fine‑tune thresholds, blob size, or CLAHE settings.
- Use the printed percentile information to guide adjustments:
  - Low percentiles represent noise; high percentiles represent true spots.
  - Set `CONTRAST_THR` just above the noise‑cluster maximum.

## 8. Troubleshooting
- **No output folder created**: check write permissions and correct working directory.  
- **`ModuleNotFoundError: openpyxl`**: ensure openpyxl is installed in your active environment.  
- **Over‑counting or under‑counting**: adjust `minArea`, `minThreshold`, or contrast thresholds based on percentile prints.

## 9. Tips for Extension
- Integrate parallel processing (e.g., `concurrent.futures`) for large datasets.  
- Swap to CSV export (`.to_csv`) if Excel writer issues persist.  
- Add command‑line arguments (using `argparse`) for on‑the‑fly parameter overrides.

## 10. License

This project is released under the **MIT License**, a permissive open‑source license that grants the following freedoms:

- **Use**: You may use, copy, and modify the software for any purpose, including commercial applications.
- **Distribution**: You can distribute original or modified versions without restriction.
- **Sublicensing**: You may combine and distribute this software with other software under different licenses.
- **Liability/Warranty**: The software is provided “as is,” without warranty of any kind. The authors are not liable for any damages that arise from its use.


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### Script: Gap_Area_Detector.py  

## 1. Introduction  
Gap_Area_Detector is a lightweight Python/OpenCV tool designed to detect and quantify dark “gap” regions in FITC-stained muscle tissue images. It suppresses intra-fiber striations by blurring the green channel, thresholds to locate coarse inter-fiber gaps, builds a true-black mask (max R,G,B ≤ a user-defined threshold), intersects the two masks so only black pixels inside gaps are counted, overlays those pixels in red, computes and stamps the percentage of gap pixels in the top-left corner, and saves the result into a timestamped folder with a `_gap_detected` suffix.

## 2. Prerequisites  
- Python 3.7 or above  
- A virtual environment (recommended)  
- Install required packages:  
  ```bash
  pip install opencv-python numpy
  ```

## 3. Directory Layout  
```
project-root/
├─ screened_gaps/       # Place raw FITC images here (e.g. ST3_0007_fitc.jpg)
├─ Gap_Area_Detector_Tuner.py             # Optional interactive parameter tuner
├─ Gap_Area_Detector.py    # Main single-image processing script
└─ output_area/         # Script creates timestamped subfolders here
```

## 4. Configuration  
Open `Gap_Area_Detector.py` and adjust the parameters at the top:  

| Parameter        | Default | Description                                                  |
|------------------|---------|--------------------------------------------------------------|
| `BLUR_K`         | 7       | Gaussian blur kernel size (odd) applied to the green channel |
| `THRESH`         | 7       | Threshold on blurred green (pixels < THRESH → gap)           |
| `DARK_THRESHOLD` | 5       | max(R,G,B) ≤ this → “true black” pixel                        |
| `FILENAME`       | —       | Name of the image file in `screened_gaps/` to process        |

> **Tip:** Use `Gap_Area_Detector_Tuner.py` to interactively slide BLUR_K, THRESH, and DARK_THRESHOLD on a representative image before batch runs.

## 5. Running the Script  
1. Place your FITC image in `screened_gaps/`.  
2. Edit `FILENAME` at the top of `Gap_Area_Detector.py` to match your file name.  
3. (Optional) Tweak `BLUR_K`, `THRESH`, and `DARK_THRESHOLD` or run `Gap_Area_Detector_Tuner.py`.  
4. Execute:  
    ```bash
    python Gap_Area_Detector.py
    ```

## 6. Output Files  
After running, you’ll find:  
```
output_area/
└─ MM_DD_YYYY_HH_MM_SS/
   └─ <base>_gap_detected<ext>
```

- A single image file named with your original base name plus `_gap_detected` and the same extension (e.g. `ST3_0007_fitc_gap_detected.jpg`), containing the red overlay and percentage annotation.

## 7. Interpreting Results  
- **Red pixels** mark the detected dark gaps.  
- **Annotation** shows the percentage of gap pixels over the total image area.  
- If gaps are over- or under-detected, revisit **Section 4** to refine parameters.

## 8. Troubleshooting  
- **FileNotFoundError**: verify `FILENAME` and that the image is in `screened_gaps/`.  
- **No output created**: ensure write permissions on `output_area/`.  
- **Over-sensitivity**: increase `THRESH` or `DARK_THRESHOLD` to reduce false positives.  
- **Under-sensitivity**: decrease `THRESH` or `DARK_THRESHOLD` to capture lighter gap pixels.

## 9. Tips for Extension  
- Loop over all images in `screened_gaps/` for batch processing.  
- Export `pct_dark` to CSV for downstream analysis.  
- Replace fixed threshold with adaptive thresholding or histogram normalization for variable lighting.

## 10. License

This project is released under the **MIT License**, a permissive open‑source license that grants the following freedoms:

- **Use**: You may use, copy, and modify the software for any purpose, including commercial applications.
- **Distribution**: You can distribute original or modified versions without restriction.
- **Sublicensing**: You may combine and distribute this software with other software under different licenses.
- **Liability/Warranty**: The software is provided “as is,” without warranty of any kind. The authors are not liable for any damages that arise from its use.

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### Script: Gap_Area_Detector_Tuner.py

## 1. Introduction  
`Gap_Area_Detector_Tuner.py` is an interactive Python/OpenCV utility for visually tuning image-processing parameters before running batch analysis. It displays three real-time views—gap mask, dark mask, and overlay—and provides sliders to adjust `BlurK`, `Thresh`, and `DarkTh` so you can instantly see how each affects detection of inter-fiber gaps in FITC-stained images.

## 2. Prerequisites  
- Python 3.7 or above  
- A desktop environment (required for OpenCV GUI)  
- Install required packages:  
  ```bash
  pip install opencv-python numpy
  ```

## 3. Directory Layout  
```
project-root/
├─ screened_gaps/         # Place one or more FITC images here (e.g. ST3_0007_fitc.jpg)
├─ Gap_Area_Detector_Tuner.py               # Interactive parameter tuning script
└─ Gap_Area_Detector.py      # Main processing script (uses tuned values)
```

## 4. Configuration  
At the top of `Gap_Area_Detector_Tuner.py`, modify these defaults as needed:  

| Variable    | Default         | Description                                  |
|-------------|-----------------|----------------------------------------------|
| `IMG_PATH`  | `screened_gaps/ST3_0007_fitc.jpg` | Path to the image to tune                      |
| `MAX_SHOW_W`| `800`           | Maximum display width (pixels)               |
| `MAX_SHOW_H`| `600`           | Maximum display height (pixels)              |

## 5. Running the Script  
1. Ensure your target image is in `screened_gaps/`.  
2. Launch the tuner:  
   ```bash
   python Gap_Area_Detector_Tuner.py [path/to/image.jpg]
   ```  
   If no argument is provided, it defaults to the `IMG_PATH` value.  
3. Three resizable windows will open:  
   - **Gap mask**: shows binary mask after Gaussian blur + threshold on green channel  
   - **Dark mask**: shows all pixels where max(R,G,B) ≤ `DarkTh`  
   - **Overlay** : original image with overlapping red pixels marking the intersection (gaps & dark) plus a percentage annotation  
   - **Settings**: control panel with sliders for `BlurK`, `Thresh`, and `DarkTh`  
4. Adjust sliders and watch how each mask updates in real time.  
5. Press **ESC** to exit when you have identified optimal values.

## 6. Using Tuned Values in `Gap_Area_Detector.py`  
After tuning:
1. Copy the best slider values for `BlurK` (odd integer), `Thresh`, and `DarkTh`.  
2. Open `Gap_Area_Detector.py` and set:
   ```python
   BLUR_K         = <your BlurK>
   THRESH         = <your Thresh>
   DARK_THRESHOLD = <your DarkTh>
   ```
3. Run `Gap_Area_Detector.py` to process individual images with those parameters.

## 7. Troubleshooting  
- **No GUI windows appear**: confirm you’re not running headless (must run on a machine with a display).  
- **Sliders have no effect**: click on the “Settings” window to focus it before dragging.  
- **Image too large**: adjust `MAX_SHOW_W`/`MAX_SHOW_H` or resize your source image.

## 8. Tips for Extension  
- Save tuned values automatically to a JSON file for reproducibility.  
- Extend `Gap_Area_Detector_Tuner.py` to loop through multiple images and record optimal parameters per-file.  
- Add command-line arguments (via `argparse`) for on-the-fly overrides of defaults.

## 9. License  
This project is released under the **MIT License**, a permissive open‑source license that grants the following freedoms:

- **Use**: You may use, copy, and modify the software for any purpose, including commercial applications.
- **Distribution**: You can distribute original or modified versions without restriction.
- **Sublicensing**: You may combine and distribute this software with other software under different licenses.
- **Liability/Warranty**: The software is provided “as is,” without warranty of any kind. The authors are not liable for any damages that arise from its use.


