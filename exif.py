#!/usr/bin/env python3
import os, math, requests
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"

BANNER = fr"""{CYAN}
 _____      _ _____   __  __     _____    __  __
| ____|_  _(_)  ___| |  \/  | __|_   _|_ _\ \/ /
|  _| \ \/ / | |_    | |\/| |/ _ \| |/ _` |\  /
| |___ >  <| |  _|   | |  | |  __/| | (_| |/  \
|_____/_/\_\_|_|     |_|  |_|\___||_|\__,_/_/\_\
{MAGENTA}  EXIF Metadata + GPS + Location - By Sheikh{RESET}
"""

def get_exif(img_path):
    img = Image.open(img_path)
    exif_data = img._getexif()
    if not exif_data:
        return {}
    exif = {}
    for tag_id, value in exif_data.items():
        tag = TAGS.get(tag_id, tag_id)
        exif[tag] = value
    return exif

def get_gps(exif):
    gps_data = exif.get("GPSInfo")
    if not gps_data:
        return None
    gps_parsed = {}
    for key in gps_data.keys():
        name = GPSTAGS.get(key, key)
        gps_parsed[name] = gps_data[key]
    return gps_parsed

def convert_to_degrees(value):
    d = float(value[0][0]) / float(value[0][1])
    m = float(value[1][0]) / float(value[1][1])
    s = float(value[2][0]) / float(value[2][1])
    return d + (m/60.0) + (s/3600.0)

def gps_to_decimal(gps):
    if not gps: return None
    try:
        lat = convert_to_degrees(gps["GPSLatitude"])
        if gps["GPSLatitudeRef"] != "N":
            lat = -lat
        lon = convert_to_degrees(gps["GPSLongitude"])
        if gps["GPSLongitudeRef"] != "E":
            lon = -lon
        return lat, lon
    except:
        return None

def decimal_to_dms(coord):
    deg = int(coord)
    temp = abs(coord - deg) * 60
    minutes = int(temp)
    seconds = (temp - minutes) * 60
    return deg, minutes, seconds

def decimal_to_ddm(coord):
    deg = int(coord)
    minutes = abs((coord - deg) * 60)
    return deg, minutes

def to_utm(lat, lon):
    zone = int((lon + 180) / 6) + 1
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    lon_origin = (zone - 1) * 6 - 180 + 3
    lon_origin_rad = math.radians(lon_origin)
    a = 6378137.0
    ecc = 0.0818192
    k0 = 0.9996
    N = a / math.sqrt(1 - ecc**2 * math.sin(lat_rad)**2)
    T = math.tan(lat_rad)**2
    C = (ecc**2 / (1 - ecc**2)) * math.cos(lat_rad)**2
    A = math.cos(lat_rad) * (lon_rad - lon_origin_rad)
    M = a*((1 - ecc**2/4 - 3*ecc**4/64 - 5*ecc**6/256)*lat_rad
        - (3*ecc**2/8 + 3*ecc**4/32 + 45*ecc**6/1024)*math.sin(2*lat_rad)
        + (15*ecc**4/256 + 45*ecc**6/1024)*math.sin(4*lat_rad)
        - (35*ecc**6/3072)*math.sin(6*lat_rad))
    easting = k0*N*(A + (1-T+C)*A**3/6 + (5-18*T+T**2+72*C-58*(ecc**2/(1-ecc**2)))*A**5/120) + 500000
    northing = k0*(M + N*math.tan(lat_rad)*(A**2/2 + (5-T+9*C+4*C**2)*A**4/24
              + (61-58*T+T**2+600*C-330*(ecc**2/(1-ecc**2)))*A**6/720))
    if lat < 0:
        northing += 10000000
    return zone, easting, northing

def to_maidenhead(lat, lon):
    lat += 90
    lon += 180
    A = "ABCDEFGHIJKLMNOPQR"
    a = "abcdefghijklmnopqrstuvwx"
    return A[int(lon//20)] + A[int(lat//10)] + str(int((lon%20)//2)) + str(int((lat%10)//1)) + a[int((lon%2)*12)] + a[int((lat%1)*24)]

def to_pluscode(lat, lon):
    import openlocationcode
    return openlocationcode.encode(lat, lon)

def reverse_geocode(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
        return r.json() if r.status_code == 200 else None
    except:
        return None

def save_to_file(text):
    print(f"{YELLOW}Save output to text file? (y/n):{RESET}", end=" ")
    if input().strip().lower() != "y":
        return
    print(f"{YELLOW}Enter filename:{RESET}", end=" ")
    name = input().strip()
    if name == "":
        name = "location_output.txt"
    try:
        with open(name, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"{GREEN}Saved to {name}{RESET}")
    except:
        print(f"{RED}Error saving file.{RESET}")

def analyze_image(img):
    exif = get_exif(img)
    gps_raw = get_gps(exif)
    gps_decimal = gps_to_decimal(gps_raw)

    print(f"{GREEN}=== DEVICE INFO ==={RESET}")
    print("Make:", exif.get("Make","N/A"))
    print("Model:", exif.get("Model","N/A"))
    print("Software:", exif.get("Software","N/A"), "\n")

    print(f"{GREEN}=== EXIF DATA ==={RESET}")
    for k,v in exif.items():
        print(f"{CYAN}{k}{RESET}: {v}")

    print(f"\n{GREEN}=== GPS RAW ==={RESET}")
    print(gps_raw)

    output = []
    for k,v in exif.items():
        output.append(f"{k}: {v}")

    if not gps_decimal:
        print(f"{RED}No GPS coordinates found.{RESET}")
        save_to_file("\n".join(output))
        return

    lat, lon = gps_decimal
    dms_lat, dms_lon = decimal_to_dms(lat), decimal_to_dms(lon)
    ddm_lat, ddm_lon = decimal_to_ddm(lat), decimal_to_ddm(lon)
    zone, easting, northing = to_utm(lat, lon)
    maiden = to_maidenhead(lat, lon)
    plus = to_pluscode(lat, lon)
    geo = reverse_geocode(lat, lon)

    print(f"\n{GREEN}=== GPS DECIMAL ==={RESET}")
    print(lat, lon)

    print(f"\n{GREEN}=== DMS ==={RESET}")
    print("Latitude:", dms_lat)
    print("Longitude:", dms_lon)

    print(f"\n{GREEN}=== DDM ==={RESET}")
    print("Latitude:", ddm_lat)
    print("Longitude:", ddm_lon)

    print(f"\n{GREEN}=== UTM ==={RESET}")
    print("Zone:", zone)
    print("Easting:", easting)
    print("Northing:", northing)

    print(f"\n{GREEN}=== MAIDENHEAD GRID ==={RESET}")
    print(maiden)

    print(f"\n{GREEN}=== PLUS CODE ==={RESET}")
    print(plus)

    print(f"\n{GREEN}=== MAP LINKS ==={RESET}")
    print("Google Maps:", f"https://maps.google.com/?q={lat},{lon}")
    print("OpenStreetMap:", f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}")

    print(f"\n{GREEN}=== FULL REVERSE GEOLOCATION ==={RESET}")
    print(geo)

    output.append(f"\nDecimal: {lat},{lon}")
    output.append(f"DMS: {dms_lat}, {dms_lon}")
    output.append(f"DDM: {ddm_lat}, {ddm_lon}")
    output.append(f"UTM Zone {zone}, E={easting}, N={northing}")
    output.append(f"Maidenhead: {maiden}")
    output.append(f"Plus Code: {plus}")
    output.append(f"Reverse Geo: {geo}")

    save_to_file("\n".join(output))

def main():
    print(BANNER)

    while True:
        print(f"{YELLOW}Enter image path or type EXIT:{RESET}", end=" ")
        img = input().strip()

        if img.lower() == "exit":
            print(f"{RED}Goodbye.{RESET}")
            break

        if not os.path.isfile(img):
            print(f"{RED}File not found.{RESET}")
            continue

        analyze_image(img)

        print(f"\n{YELLOW}Analyze another image? (y/n):{RESET}", end=" ")
        if input().strip().lower() != "y":
            print(f"{RED}Goodbye.{RESET}")
            break

if __name__ == "__main__":
    main()