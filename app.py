import streamlit as st
import xml.etree.ElementTree as ET
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime
from collections import Counter
import pandas as pd

st.set_page_config(page_title="Nabdk GPX Analyzer", layout="wide")

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)*2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)*2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def parse_time(t):
    return datetime.fromisoformat(t.replace("Z", "+00:00"))

def read_gpx(file):
    tree = ET.parse(file)
    root = tree.getroot()
    points = []

    for elem in root.iter():
        if elem.tag.endswith("trkpt"):
            lat = float(elem.attrib["lat"])
            lon = float(elem.attrib["lon"])
            time = None

            for child in elem:
                if child.tag.endswith("time"):
                    time = parse_time(child.text)

            if time:
                points.append({"lat": lat, "lon": lon, "time": time})

    return points

def analyze(points):
    total_distance = 0
    max_speed = 0
    speeds = []
    intervals = []

    for i in range(1, len(points)):
        p1 = points[i-1]
        p2 = points[i]

        dt = (p2["time"] - p1["time"]).total_seconds()
        if dt <= 0:
            continue

        distance = haversine(p1["lat"], p1["lon"], p2["lat"], p2["lon"])
        speed_kmh = (distance / dt) * 3.6

        total_distance += distance
        speeds.append(speed_kmh)
        intervals.append(round(dt))

        if speed_kmh > max_speed:
            max_speed = speed_kmh

    duration = (points[-1]["time"] - points[0]["time"]).total_seconds()
    avg_speed = (total_distance / duration) * 3.6 if duration > 0 else 0
    gps_interval = Counter(intervals).most_common(1)[0][0] if intervals else 0
    suspicious_points = sum(1 for s in speeds if s > 40)

    return total_distance, max_speed, avg_speed, duration, gps_interval, suspicious_points, speeds

st.title("⚽ Nabdk GPX Analyzer")
st.subheader("Football Performance Analysis")

player = st.text_input("👤 Player Name")
uploaded_file = st.file_uploader("📤 Upload GPX File", type=["gpx"])

if uploaded_file:
    points = read_gpx(uploaded_file)

    if len(points) < 2:
        st.error("الملف لا يحتوي على نقاط GPS كافية.")
    else:
        total_distance, max_speed, avg_speed, duration, gps_interval, suspicious_points, speeds = analyze(points)

        st.success("✅ تم تحليل الملف بنجاح")

        col1, col2, col3 = st.columns(3)
        col1.metric("📏 Total Distance", f"{total_distance/1000:.2f} km")
        col2.metric("🚀 Max Speed", f"{max_speed:.2f} km/h")
        col3.metric("⚡ Average Speed", f"{avg_speed:.2f} km/h")

        col4, col5, col6 = st.columns(3)
        col4.metric("⏱ Duration", f"{duration/60:.1f} min")
        col5.metric("📍 GPS Points", len(points))
        col6.metric("🛰 GPS Interval", f"{gps_interval} sec")

        if suspicious_points > 0:
            st.warning(f"⚠️ يوجد {suspicious_points} نقاط سرعة عالية جدًا قد تكون GPS spike.")
        else:
            st.info("✅ لا توجد قفزات GPS واضحة.")

        df = pd.DataFrame(points)

        st.markdown("## 🗺️ المسار")
        st.map(df[["lat", "lon"]])

        st.markdown("## 📈 منحنى السرعة")
        st.line_chart(pd.DataFrame({"Speed km/h": speeds}))
