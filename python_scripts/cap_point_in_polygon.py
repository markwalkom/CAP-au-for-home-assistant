# cap_point_in_polygon.py (HA python_script sandbox; imports are not allowed)
# data: polygon -> "lat,lon lat,lon ..." ; point_lat ; point_lon
polygon_str = data.get('polygon', '')
plat = float(data.get('point_lat', 0.0))
plon = float(data.get('point_lon', 0.0))
pts = []
for pair in polygon_str.strip().split(' '):
    if ',' in pair:
        y, x = pair.split(',', 1)
        try:
            pts.append((float(y), float(x)))
        except Exception:
            pass
inside = False
n = len(pts)
if n >= 3:
    j = n - 1
    for i in range(n):
        yi, xi = pts[i]
        yj, xj = pts[j]
        cond = ((xi > plon) != (xj > plon)) and                (plat < (yj - yi) * (plon - xi) / ((xj - xi) if (xj - xi) != 0 else 1e-12) + yi)
        if cond:
            inside = not inside
        j = i
hass.bus.fire('python_script.cap_point_in_polygon_result', {'match': inside})
