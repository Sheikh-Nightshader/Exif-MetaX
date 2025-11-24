Exif-MeTaX is the second edition of my MetaXtractor

This tool extracts full EXIF metadata from images, including GPS coordinates if available.  
It converts location data into multiple formats such as Decimal, DMS, DDM, UTM, Maidenhead Grid, and Plus Codes.  
It also performs reverse geolocation lookups and can optionally save the output to a text file.

The script works locally and never uploads images anywhere.


## Features
- Extract full EXIF metadata  
- GPS coordinate detection  
- Decimal → DMS, DDM, UTM, Maidenhead, Plus Code conversion  
- Reverse geolocation (OpenStreetMap / Nominatim)  
- Google Maps & OpenStreetMap direct links  
- Save output to a `.txt` file  
- Loop system to analyze multiple images  
- Colored terminal output  
- ASCII banner included  


## Requirements
Install dependencies:

```
pip install pillow requests openlocationcode
```

## Usage
Run the script:

```
python3 exif.py
```

Enter the path of an image file.  
Type **EXIT** at any time to quit.

---

## Example
```
Enter image path: myphoto.jpg
=== DEVICE INFO ===
Make: Samsung
Model: SM-A525F
Software: A525FXXU6EXX2
```



## Important Warning
This tool is made **only for educational, forensic, and ethical cybersecurity use**.

- Do **not** use it on images you do not own.  
- Do **not** use it to obtain someone’s location without consent.  
- Misusing location data can put people at risk.  
- The author and contributors are **not responsible** for any malicious or illegal use.

Use responsibly.

Sheikh Nightshader

## License
MIT License
