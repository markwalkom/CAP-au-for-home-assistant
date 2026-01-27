# cap_polygon_to_zone.py (HA python_script sandbox; no imports)
PI = 3.141592653589793

def deg2rad(d):
    return d * PI / 180.0

def cos_approx(x):
    x2 = x * x
    x4 = x2 * x2
    x6 = x4 * x2
    return 1.0 - x2/2.0 + x4/24.0 - x6/720.0

def distance_km(lat1, lon1, lat2, lon2):
    lat1r = deg2rad(lat1)
    lat2r = deg2rad(lat2)
    lon1r = deg2rad(lon1)
    lon2r = deg2rad(lon2)
    x = (lon2r - lon1r) * cos_approx((lat1r + lat2r) * 0.5)
    y = (lat2r - lat1r)
    R = 6371.0088
    return (x*x + y*y) ** 0.5 * R

poly = data.get('polygon', '').strip()
name = data.get('name', 'CAP Polygon')
icon = data.get('icon', 'mdi:alert')
pts = []
for pair in poly.split(' '):
    if ',' in pair:
        y, x = pair.split(',', 1)
        try:
            pts.append((float(y), float(x)))
        except Exception:
            pass
cent_lat = 0.0
cent_lon = 0.0
if len(pts) >= 1:
    cent_lat = sum(p[0] for p in pts) / len(pts)
    cent_lon = sum(p[1] for p in pts) / len(pts)
radius_m = 1000.0
if len(pts) >= 3:
    max_km = 0.0
    for p in pts:
        dk = distance_km(cent_lat, cent_lon, p[0], p[1])
        if dk > max_km:
            max_km = dk
    radius_m = max_km * 1000.0
hass.bus.fire('cap_polygon_zone_ready', {
    'name': name,
    'icon': icon,
    'latitude': cent_lat,
    'longitude': cent_lon,
    'radius': radius_m
})
