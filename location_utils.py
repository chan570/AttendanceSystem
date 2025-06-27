# utils/location_utils.py

import geocoder

def get_teacher_location():
    try:
        g = geocoder.ip('me')
        if g.ok and g.latlng:
            lat, lng = g.latlng
            print(f"[LOCATION] Latitude={lat}, Longitude={lng}")
            return (lat, lng)
        else:
            print("[WARNING] Could not detect location.")
            return None
    except Exception as e:
        print(f"[ERROR] Location detection failed: {e}")
        return None
