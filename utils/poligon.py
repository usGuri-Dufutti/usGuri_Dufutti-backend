import numpy as np
from scipy.spatial import ConvexHull, QhullError
import warnings
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # metros
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def points_in_circle(points, center, radius):
    lat_c, lon_c = center
    return [p for p in points if haversine(p[0], p[1], lat_c, lon_c) <= radius]

def generate_polygon(points, site_point=None):
    points = list(set(points))  # remove duplicatas
    if len(points) < 3:
        # retorna o ponto do site se fornecido, senão os próprios pontos
        return [site_point] if site_point else points
    pts = np.array(points)
    try:
        hull = ConvexHull(pts)
        return [tuple(pts[v]) for v in hull.vertices]
    except QhullError:
        warnings.warn("Não foi possível criar o polígono: pontos colineares ou problemas numéricos")
        return [site_point] if site_point else points
