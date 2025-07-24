import streamlit as st
import numpy as np
import pandas as pd
import folium
import time
import math
import random
from datetime import datetime, timedelta
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import altair as alt
from PIL import Image
from geopy.distance import geodesic

# Set page configuration
st.set_page_config(
    page_title="FisherLink - Fishermen Monitoring System",
    page_icon="🚤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark mode with white text
st.markdown("""
<style>
    /* Dark mode base styling */
    body {
        color: white;
        background-color: #121212;
    }
    
    /* Override Streamlit's default styling for dark mode */
    .main-header {
        font-size: 36px;
        font-weight: bold;
        color: #90CAF9;
        text-align: center;
        margin-bottom: 20px;
        text-shadow: 1px 1px 2px #000;
    }
    .sub-header {
        font-size: 24px;
        font-weight: bold;
        color: #64B5F6;
        margin-top: 20px;
        margin-bottom: 10px;
        border-bottom: 2px solid #64B5F6;
        padding-bottom: 5px;
    }
    .alert {
        background-color: #5D1212;
        color: #FF5252;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        font-weight: bold;
        text-align: center;
    }
    .safe {
        background-color: #1B5E20;
        color: #81C784;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        font-weight: bold;
        text-align: center;
    }
    .warning {
        background-color: #4D4000;
        color: #FFEE58;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        font-weight: bold;
        text-align: center;
    }
    .data-container {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    .stButton button {
        background-color: #B71C1C;
        color: white;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #D32F2F;
        color: white;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        color: #FFFFFF;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 16px;
        color: #BBBBBB;
    }
    
    /* Make all text white */
    p, h1, h2, h3, h4, h5, h6, .stMarkdown, .stText, span, div {
        color: #FFFFFF !important;
    }
    
    .stTab p, .stTab span {
        color: #FFFFFF !important;
    }
    
    /* Dark background */
    div.stApp {
        background-color: #121212 !important;
    }
    
    .reportview-container {
        background: #121212 !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-12oz5g7 {
        background-color: #1E1E1E !important;
    }
    
    /* Input fields */
    .stTextInput input, .stNumberInput input, .stSelectbox, .stMultiselect {
        background-color: #333333 !important;
        color: white !important;
        border-color: #555555 !important;
    }
    
    /* Checkboxes */
    .stCheckbox label {
        color: white !important;
    }
    
    /* Tables and DataFrames */
    div.stDataFrame {
        background-color: #1E1E1E !important;
    }
    .dataframe {
        background-color: #1E1E1E !important;
        color: white !important;
    }
    .dataframe th {
        background-color: #2C2C2C !important;
        color: white !important;
    }
    .dataframe td {
        background-color: #1E1E1E !important;
        color: white !important;
    }
    
    /* Code blocks */
    code {
        background-color: #2C2C2C !important;
        color: #BBBBBB !important;
        padding: 2px 4px;
        border-radius: 3px;
    }
    
    /* Card styling for boat status */
    .boat-card-low {
        background-color: #1B5E20 !important;
        color: white !important;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .boat-card-medium {
        background-color: #4D4000 !important;
        color: white !important;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .boat-card-high {
        background-color: #5D1212 !important;
        color: white !important;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    
    /* Progress bars */
    .stProgress .st-bo {
        background-color: #4CAF50 !important;
    }
    
    /* Plotly charts background */
    .js-plotly-plot .plotly {
        background-color: #1E1E1E !important;
    }
    
    /* Tabs styling */
    div[data-baseweb="tab-list"] {
        background-color: #1E1E1E !important;
    }
    button[data-baseweb="tab"] {
        color: #BBBBBB !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #90CAF9 !important;
        border-bottom-color: #90CAF9 !important;
    }
</style>
""", unsafe_allow_html=True)

# Logo and Title
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown('<div class="main-header">FisherLink - Fishermen Monitoring System</div>', unsafe_allow_html=True)
    
    # Display the logo 
    logo_url = "https://cdn-icons-png.flaticon.com/128/1397/1397519.png"
    st.image(logo_url, width=100)

# Coastal coordinates (refined to better match OpenStreetMap purple boundary)
COASTAL_COORDS = [
    (13.1600, 80.3000), # Northern point near Chennai
    (13.0827, 80.2707), # Chennai
    (13.0500, 80.2800),
    (13.0000, 80.2900),
    (12.9500, 80.3000),
    (12.9000, 80.3100),
    (12.8500, 80.3200),
    (12.8000, 80.3300),
    (12.7500, 80.3400),
    (12.7000, 80.3500),
    (12.6500, 80.3600),
    (12.6000, 80.3700),
    (12.5500, 80.3800),
    (12.5000, 80.3900),
    (12.4500, 80.3900),
    (12.4000, 80.3800),
    (12.3500, 80.3600),
    (12.3000, 80.3400),
    (12.2500, 80.3200),
    (12.2000, 80.3000),
    (12.1500, 80.2800),
    (12.1000, 80.2600),
    (12.0500, 80.2400),
    (12.0000, 80.2200),
    (11.9500, 80.1000),
    (11.9300, 79.8300), # Pondicherry
]

# Calculate geofence points (30km from shore)
def calculate_geofence_point(lat, lon, distance_km, bearing_deg):
    earth_radius = 6371.0  # Earth radius in kilometers
    
    # Convert to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    bearing_rad = math.radians(bearing_deg)
    
    # Calculate new latitude
    new_lat_rad = math.asin(
        math.sin(lat_rad) * math.cos(distance_km / earth_radius) +
        math.cos(lat_rad) * math.sin(distance_km / earth_radius) * math.cos(bearing_rad)
    )
    
    # Calculate new longitude
    new_lon_rad = lon_rad + math.atan2(
        math.sin(bearing_rad) * math.sin(distance_km / earth_radius) * math.cos(lat_rad),
        math.cos(distance_km / earth_radius) - math.sin(lat_rad) * math.sin(new_lat_rad)
    )
    
    # Convert back to degrees
    new_lat = math.degrees(new_lat_rad)
    new_lon = math.degrees(new_lon_rad)
    
    return (new_lat, new_lon)

# Calculate geofence boundaries
def calculate_geofence_boundaries():
    geofence_points = []
    
    for coord in COASTAL_COORDS:
        # For the eastern coast of India, the sea is generally to the east (90°)
        sea_bearing = 90  # East
        
        # Calculate point 30km out to sea
        geofence_point = calculate_geofence_point(coord[0], coord[1], 30, sea_bearing)
        geofence_points.append(geofence_point)
    
    return geofence_points

# Get geofence points
GEOFENCE_POINTS = calculate_geofence_boundaries()

# Generate sample boats with realistic names
def generate_boats(num_boats=10):
    boat_names = [
        "Sea Explorer", "Coastal Fisher", "Ocean Voyager", "Bay Catcher", 
        "Wave Rider", "Deep Blue", "Sea Harvester", "Marine Master",
        "Aqua Venture", "Tide Chaser", "Chennai Fisher", "Tamil Mariner",
        "Gulf Voyager", "Bay Watcher", "Seaside Worker", "Coastal Guard",
        "Blue Waters", "Marina Fisher", "Bay Navigator", "Sea Pearl"
    ]
    
    boats = []
    for i in range(num_boats):
        # Generate initial positions close to shore
        shore_idx = random.randint(0, len(COASTAL_COORDS) - 1)
        shore_point = COASTAL_COORDS[shore_idx]
        
        # Random distance from shore (0-25 km)
        distance = random.uniform(0, 25)
        # Random bearing (45-135 degrees, roughly east with variation)
        bearing = random.uniform(45, 135)
        
        initial_pos = calculate_geofence_point(shore_point[0], shore_point[1], distance, bearing)
        
        speed = random.uniform(5, 15)
        heading = random.uniform(0, 360)
        crew_size = random.randint(3, 10)
        operation_time = random.randint(1, 12)
        fish_caught = random.uniform(0, 1000)
        risk_level = random.uniform(0, 0.5)  # Start with low to medium risk
        fuel_level = random.uniform(50, 100)
        
        boat = {
            "id": i + 1,
            "name": boat_names[i % len(boat_names)] + f"-{i+1}",
            "lat": initial_pos[0],
            "lon": initial_pos[1],
            "speed": speed,
            "heading": heading,
            "crew_size": crew_size,
            "operation_time": operation_time,
            "fish_caught": fish_caught,
            "risk_level": risk_level,
            "fuel_level": fuel_level,
            "engine_status": "Normal",
            "communication_status": "Active",
            "safety_status": "Safe",
            "last_update": datetime.now().strftime("%H:%M:%S"),
            "history": {
                "positions": [(initial_pos[0], initial_pos[1])],
                "risk_levels": [risk_level],
                "timestamps": [datetime.now().strftime("%H:%M:%S")],
            }
        }
        boats.append(boat)
    
    return boats

# Calculate distance to nearest shore point
def distance_to_shore(lat, lon):
    min_distance = float('inf')
    for coord in COASTAL_COORDS:
        distance = geodesic((lat, lon), coord).kilometers
        if distance < min_distance:
            min_distance = distance
    return min_distance

# Calculate distance to geofence
def distance_to_geofence(lat, lon):
    # Find closest shore point
    closest_shore_idx = 0
    min_distance = float('inf')
    
    for i, coord in enumerate(COASTAL_COORDS):
        distance = geodesic((lat, lon), coord).kilometers
        if distance < min_distance:
            min_distance = distance
            closest_shore_idx = i
            
    # Get corresponding geofence point
    if closest_shore_idx < len(GEOFENCE_POINTS):
        geofence_point = GEOFENCE_POINTS[closest_shore_idx]
        shore_point = COASTAL_COORDS[closest_shore_idx]
        
        # If boat is between shore and geofence point
        boat_to_shore = geodesic((lat, lon), shore_point).kilometers
        geofence_to_shore = geodesic(geofence_point, shore_point).kilometers
        
        if boat_to_shore <= geofence_to_shore:
            # Return distance to geofence boundary (negative is inside, positive is outside)
            return geofence_to_shore - boat_to_shore
    
    # If we can't determine it precisely, use the closest shore point + 30km as approximation
    return 30 - min_distance

# Update boat positions with natural movement patterns
def update_boat_positions(boats):
    for boat in boats:
        # Update heading with small random changes to simulate natural drift and steering
        heading_change = random.uniform(-15, 15)
        boat["heading"] = (boat["heading"] + heading_change) % 360
        
        # Update speed with small random changes
        speed_change = random.uniform(-0.5, 0.5)
        boat["speed"] = max(0.5, min(20, boat["speed"] + speed_change))
        
        # Calculate new position based on heading and speed
        speed_kmh = boat["speed"] * 1.852
        
        # Distance traveled in 1 minute (assuming update interval is 1 minute)
        distance_km = speed_kmh / 60
        
        # Update position
        new_pos = calculate_geofence_point(boat["lat"], boat["lon"], distance_km, boat["heading"])
        boat["lat"], boat["lon"] = new_pos
        
        # Update operation time
        boat["operation_time"] += 1/60  # Add 1 minute
        
        # Update fish caught with some randomness
        if random.random() < 0.3:  # 30% chance of catching fish in this update
            boat["fish_caught"] += random.uniform(0, 5)  # 0-5 kg per catch
            
        # Update fuel level (decreasing over time)
        fuel_decrease = random.uniform(0.05, 0.15)  # 0.05-0.15% decrease per minute
        boat["fuel_level"] = max(0, boat["fuel_level"] - fuel_decrease)
        
        # Calculate distance to boundary
        geofence_distance = distance_to_geofence(boat["lat"], boat["lon"])
        
        # Update risk level based on various factors
        # 1. Distance to geofence (higher risk when closer to or beyond geofence)
        distance_risk = max(0, min(1, 1 - ((geofence_distance + 5) / 35)))
        
        # 2. Fuel level (higher risk with lower fuel)
        fuel_risk = max(0, min(1, (100 - boat["fuel_level"]) / 100))
        
        # 3. Operation time (higher risk with longer operation time)
        time_risk = max(0, min(1, boat["operation_time"] / 24))  # Assuming max 24 hours
        
        # 4. Random environmental factors (weather, sea condition)
        env_risk = random.uniform(0, 0.3)
        
        # Calculate combined risk with different weights
        boat["risk_level"] = (
            0.4 * distance_risk +
            0.25 * fuel_risk +
            0.25 * time_risk +
            0.1 * env_risk
        )
        
        # Update engine status based on risk and random factors
        if boat["risk_level"] > 0.7 or (boat["risk_level"] > 0.5 and random.random() < 0.1):
            boat["engine_status"] = "Warning"
        elif boat["risk_level"] > 0.9 or (boat["risk_level"] > 0.7 and random.random() < 0.05):
            boat["engine_status"] = "Critical"
        else:
            boat["engine_status"] = "Normal"
            
        # Update communication status
        if boat["risk_level"] > 0.8 and random.random() < 0.1:
            boat["communication_status"] = "Intermittent"
        elif boat["risk_level"] > 0.9 and random.random() < 0.05:
            boat["communication_status"] = "Lost"
        else:
            boat["communication_status"] = "Active"
            
        # Update safety status
        if geofence_distance < -5:  # More than 5km beyond geofence
            boat["safety_status"] = "Danger"
        elif geofence_distance < 0:  # Beyond geofence but within 5km
            boat["safety_status"] = "Warning"
        elif boat["risk_level"] > 0.7:  # High risk but within geofence
            boat["safety_status"] = "Caution"
        else:
            boat["safety_status"] = "Safe"
            
        # Update last update time
        boat["last_update"] = datetime.now().strftime("%H:%M:%S")
        
        # Update history
        boat["history"]["positions"].append((boat["lat"], boat["lon"]))
        boat["history"]["risk_levels"].append(boat["risk_level"])
        boat["history"]["timestamps"].append(boat["last_update"])
        
        # Limit history length to prevent memory issues
        if len(boat["history"]["positions"]) > 100:
            boat["history"]["positions"] = boat["history"]["positions"][-100:]
            boat["history"]["risk_levels"] = boat["history"]["risk_levels"][-100:]
            boat["history"]["timestamps"] = boat["history"]["timestamps"][-100:]
    
    return boats

# Create the interactive map
def create_map(boats):
    # Create map centered between Chennai and Pondicherry
    center_lat = (13.0827 + 11.9300) / 2
    center_lon = (80.2707 + 79.8300) / 2
    
    # Use a dark map tile for the base map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=9,
        tiles="CartoDB dark_matter",  # Use dark theme map
        scrollWheelZoom=True
    )
    
    # Add additional map layers
    folium.TileLayer(
        'CartoDB dark_matter',
        name='Dark Map (Default)',
        attr='&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'
    ).add_to(m)
    
    folium.TileLayer(
        'CartoDB positron',
        name='Light Map',
        attr='&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'
    ).add_to(m)
    
    folium.TileLayer(
        'OpenStreetMap',
        name='Standard Map',
        attr='&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    ).add_to(m)
    
    folium.TileLayer(
        'Stamen Terrain',
        name='Terrain Map',
        attr='Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>'
    ).add_to(m)
    
    folium.TileLayer(
        'Stamen Watercolor',
        name='Watercolor Map',
        attr='Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>'
    ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add coastal line (following the OpenStreetMap purple boundary)
    coastal_line = folium.PolyLine(
        locations=COASTAL_COORDS,
        color='#BB86FC',  # Light purple for better visibility on dark background
        weight=3,
        opacity=0.8,
        tooltip='Coastline (OSM boundary)'
    )
    coastal_line.add_to(m)
    
    # Create geofence boundary line 30km from shore
    folium.PolyLine(
        locations=GEOFENCE_POINTS,
        color='#FF4444',  # Bright red for visibility on dark background
        weight=3,
        opacity=0.8,
        tooltip='30km Geofence Boundary (Signal Limit)'
    ).add_to(m)
    
    # Connect coastal points to geofence points to show the 30km distance
    for i in range(len(COASTAL_COORDS)):
        folium.PolyLine(
            locations=[COASTAL_COORDS[i], GEOFENCE_POINTS[i]],
            color='#FFAB40',  # Orange
            weight=1,
            opacity=0.5,
            dash_array='5',
            tooltip='30km Distance'
        ).add_to(m)
    
    # Add boats to the map
    for boat in boats:
        # Determine marker color based on risk level
        if boat["risk_level"] < 0.3:
            color = 'green'
            icon = 'ship'
        elif boat["risk_level"] < 0.7:
            color = 'orange'
            icon = 'ship'
        else:
            color = 'red'
            icon = 'warning'
        
        # Create popup content with dark mode styling
        popup_html = f"""
        <div style="width: 250px; background-color: #1E1E1E; color: white; border-radius: 5px; padding: 5px;">
            <h3 style="text-align: center; color: #90CAF9;">{boat['name']}</h3>
            <table style="width: 100%; color: white;">
                <tr><td><b>Speed:</b></td><td>{boat['speed']:.1f} knots</td></tr>
                <tr><td><b>Heading:</b></td><td>{boat['heading']:.1f}°</td></tr>
                <tr><td><b>Crew:</b></td><td>{boat['crew_size']} persons</td></tr>
                <tr><td><b>Operation Time:</b></td><td>{boat['operation_time']:.1f} hours</td></tr>
                <tr><td><b>Fish Caught:</b></td><td>{boat['fish_caught']:.1f} kg</td></tr>
                <tr><td><b>Fuel Level:</b></td><td>{boat['fuel_level']:.1f}%</td></tr>
                <tr><td><b>Engine Status:</b></td><td>{boat['engine_status']}</td></tr>
                <tr><td><b>Communication:</b></td><td>{boat['communication_status']}</td></tr>
                <tr><td><b>Safety Status:</b></td><td>{boat['safety_status']}</td></tr>
                <tr><td><b>Risk Level:</b></td><td>{boat['risk_level']:.2f}</td></tr>
                <tr><td><b>Last Update:</b></td><td>{boat['last_update']}</td></tr>
            </table>
        </div>
        """
        
        # Add marker
        folium.Marker(
            location=[boat["lat"], boat["lon"]],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{boat['name']} - Risk: {boat['risk_level']:.2f}",
            icon=folium.Icon(color=color, icon=icon, prefix='fa')
        ).add_to(m)
        
        # Add trail (recent movement history)
        if len(boat["history"]["positions"]) > 1:
            folium.PolyLine(
                locations=boat["history"]["positions"][-10:],  # Last 10 positions
                color=color,
                weight=2,
                opacity=0.6
            ).add_to(m)
    
    return m

# Configure matplotlib for dark mode
plt.style.use('dark_background')

# Initialize session state
if 'boats' not in st.session_state:
    st.session_state.boats = generate_boats(15)  # Generate 15 boats
    
if 'alerts' not in st.session_state:
    st.session_state.alerts = []
    
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
    
if 'update_count' not in st.session_state:
    st.session_state.update_count = 0
    
if 'sos_alert' not in st.session_state:
    st.session_state.sos_alert = None
    
if 'sos_time' not in st.session_state:
    st.session_state.sos_time = None

# Create SOS alert function
def send_sos_alert():
    alert_type = st.session_state.sos_type
    st.session_state.sos_alert = alert_type
    st.session_state.sos_time = datetime.now()
    
    # Add to alerts list
    st.session_state.alerts.append({
        "type": alert_type,
        "time": datetime.now().strftime("%H:%M:%S"),
        "message": f"EMERGENCY ALERT: {alert_type} warning issued to all vessels"
    })

# Main layout
# Sidebar for controls
with st.sidebar:
    st.markdown('<div class="sub-header">Control Panel</div>', unsafe_allow_html=True)
    
    auto_update = st.checkbox("Auto-update (5s)", value=True)
    
    if st.button("Update Now"):
        st.session_state.boats = update_boat_positions(st.session_state.boats)
        st.session_state.last_update = datetime.now()
        st.session_state.update_count += 1
    
    st.markdown('<div class="sub-header">SOS Alerts</div>', unsafe_allow_html=True)
    
    st.selectbox(
        "Alert Type", 
        ["Tsunami Warning", "High Wave Alert", "Cyclone Warning", "Storm Alert", "Coastal Flooding"], 
        key="sos_type"
    )
    
    if st.button("Send SOS Alert"):
        send_sos_alert()
    
    if st.session_state.sos_alert:
        elapsed = (datetime.now() - st.session_state.sos_time).total_seconds()
        if elapsed < 60:  # Show for 60 seconds
            st.markdown(f'<div class="alert">ACTIVE ALERT: {st.session_state.sos_alert}</div>', unsafe_allow_html=True)
        else:
            st.session_state.sos_alert = None
    
    st.markdown('<div class="sub-header">System Status</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Active Boats", len(st.session_state.boats))
    with col2:
        st.metric("Alerts", len(st.session_state.alerts))
    
    # Risk level summary
    high_risk = sum(1 for boat in st.session_state.boats if boat["risk_level"] > 0.7)
    medium_risk = sum(1 for boat in st.session_state.boats if 0.3 <= boat["risk_level"] <= 0.7)
    low_risk = sum(1 for boat in st.session_state.boats if boat["risk_level"] < 0.3)
    
    st.markdown("#### Risk Summary")
    st.progress(high_risk/len(st.session_state.boats), "High Risk: " + str(high_risk))
    st.progress(medium_risk/len(st.session_state.boats), "Medium Risk: " + str(medium_risk))
    st.progress(low_risk/len(st.session_state.boats), "Low Risk: " + str(low_risk))

# Auto-update logic
if auto_update and (datetime.now() - st.session_state.last_update).total_seconds() > 5:
    st.session_state.boats = update_boat_positions(st.session_state.boats)
    st.session_state.last_update = datetime.now()
    st.session_state.update_count += 1

# Main content
# Create tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["Map View", "Boat Details", "Alerts & Notifications", "Analytics"])

with tab1:
    st.markdown('<div class="sub-header">Real-time Monitoring Map</div>', unsafe_allow_html=True)
    
    # Create map
    m = create_map(st.session_state.boats)
    
    # Display the map
    folium_static(m, width=1200, height=600)
    
    # Display last update time
    st.markdown(f"<p style='text-align:right; color:#BBBBBB;'>Last updated: {st.session_state.last_update.strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
    
    # Display active SOS alert if any
    if st.session_state.sos_alert:
        elapsed = (datetime.now() - st.session_state.sos_time).total_seconds()
        if elapsed < 60:  # Show for 60 seconds
            st.markdown(f'<div class="alert">⚠️ EMERGENCY ALERT: {st.session_state.sos_alert} ⚠️</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="sub-header">Vessel Status and Details</div>', unsafe_allow_html=True)
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        risk_filter = st.selectbox(
            "Filter by Risk Level",
            ["All", "High Risk", "Medium Risk", "Low Risk"]
        )
    with col2:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Safe", "Caution", "Warning", "Danger"]
        )
    with col3:
        search_term = st.text_input("Search by Boat Name or ID")
    
    # Apply filters
    filtered_boats = st.session_state.boats
    
    if risk_filter == "High Risk":
        filtered_boats = [b for b in filtered_boats if b["risk_level"] > 0.7]
    elif risk_filter == "Medium Risk":
        filtered_boats = [b for b in filtered_boats if 0.3 <= b["risk_level"] <= 0.7]
    elif risk_filter == "Low Risk":
        filtered_boats = [b for b in filtered_boats if b["risk_level"] < 0.3]
        
    if status_filter != "All":
        filtered_boats = [b for b in filtered_boats if b["safety_status"] == status_filter]
        
    if search_term:
        filtered_boats = [b for b in filtered_boats if search_term.lower() in b["name"].lower() or 
                         search_term == str(b["id"])]
    
    # Create boat cards
    if not filtered_boats:
        st.write("No boats match the selected filters.")
    else:
        for i in range(0, len(filtered_boats), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(filtered_boats):
                    boat = filtered_boats[i + j]
                    with cols[j]:
                        if boat["risk_level"] < 0.3:
                            st.markdown(f"""
                            <div class="boat-card-low">
                                <h3>{boat['name']}</h3>
                                <p>Risk Level: {boat['risk_level']:.2f}</p>
                                <p>Status: {boat['safety_status']}</p>
                                <p>Position: ({boat['lat']:.4f}, {boat['lon']:.4f})</p>
                                <p>Last Update: {boat['last_update']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        elif boat["risk_level"] < 0.7:
                            st.markdown(f"""
                            <div class="boat-card-medium">
                                <h3>{boat['name']}</h3>
                                <p>Risk Level: {boat['risk_level']:.2f}</p>
                                <p>Status: {boat['safety_status']}</p>
                                <p>Position: ({boat['lat']:.4f}, {boat['lon']:.4f})</p>
                                <p>Last Update: {boat['last_update']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="boat-card-high">
                                <h3>{boat['name']}</h3>
                                <p>Risk Level: {boat['risk_level']:.2f}</p>
                                <p>Status: {boat['safety_status']}</p>
                                <p>Position: ({boat['lat']:.4f}, {boat['lon']:.4f})</p>
                                <p>Last Update: {boat['last_update']}</p>
                            </div>
                            """, unsafe_allow_html=True)
    
    # Detailed boat info
    st.markdown('<div class="sub-header">Detailed Vessel Information</div>', unsafe_allow_html=True)
    
    selected_boat = st.selectbox(
        "Select Boat for Details",
        options=[f"{boat['name']} (ID: {boat['id']})" for boat in st.session_state.boats],
        key="selected_boat_details"
    )
    
    # Extract boat ID from selection
    boat_id = int(selected_boat.split("(ID: ")[1].split(")")[0])
    boat = next((b for b in st.session_state.boats if b["id"] == boat_id), None)
    
    if boat:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="data-container">', unsafe_allow_html=True)
            st.markdown("#### Basic Information")
            st.write(f"**Boat Name:** {boat['name']}")
            st.write(f"**Boat ID:** {boat['id']}")
            st.write(f"**Crew Size:** {boat['crew_size']} persons")
            st.write(f"**Current Position:** ({boat['lat']:.4f}, {boat['lon']:.4f})")
            st.write(f"**Speed:** {boat['speed']:.1f} knots")
            st.write(f"**Heading:** {boat['heading']:.1f}°")
            st.write(f"**Operation Time:** {boat['operation_time']:.1f} hours")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="data-container">', unsafe_allow_html=True)
            st.markdown("#### Status Information")
            st.write(f"**Risk Level:** {boat['risk_level']:.2f}")
            
            # Risk level indicator
            if boat['risk_level'] < 0.3:
                st.markdown('<div class="safe">Low Risk</div>', unsafe_allow_html=True)
            elif boat['risk_level'] < 0.7:
                st.markdown('<div class="warning">Medium Risk</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert">High Risk</div>', unsafe_allow_html=True)
                
            st.write(f"**Safety Status:** {boat['safety_status']}")
            st.write(f"**Engine Status:** {boat['engine_status']}")
            st.write(f"**Communication Status:** {boat['communication_status']}")
            st.write(f"**Fuel Level:** {boat['fuel_level']:.1f}%")
            st.write(f"**Fish Caught:** {boat['fish_caught']:.1f} kg")
            st.write(f"**Last Update:** {boat['last_update']}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # Display risk history chart
            st.markdown('<div class="data-container">', unsafe_allow_html=True)
            st.markdown("#### Risk Level History")
            
            # Create DataFrame for chart
            risk_df = pd.DataFrame({
                'Time': boat['history']['timestamps'],
                'Risk Level': boat['history']['risk_levels']
            })
            
            # Create chart
            chart = alt.Chart(risk_df).mark_line(
                color='#FF5252',
                point=True
            ).encode(
                x=alt.X('Time:O', title='Time'),
                y=alt.Y('Risk Level:Q', scale=alt.Scale(domain=[0, 1]), title='Risk Level')
            ).properties(
                width=500,
                height=300
            ).configure_axis(
                labelColor='white',
                titleColor='white'
            ).configure_view(
                strokeWidth=0
            )
            
            st.altair_chart(chart, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display boat trajectory on mini map
            st.markdown('<div class="data-container">', unsafe_allow_html=True)
            st.markdown("#### Movement Trajectory")
            
            # Create mini map
            mini_map = folium.Map(
                location=[boat["lat"], boat["lon"]],
                zoom_start=10,
                tiles="CartoDB dark_matter"
            )
            
            # Add trajectory
            folium.PolyLine(
                locations=boat["history"]["positions"],
                color='cyan',
                weight=3,
                opacity=0.8
            ).add_to(mini_map)
            
            # Add marker for current position
            folium.Marker(
                location=[boat["lat"], boat["lon"]],
                tooltip=f"{boat['name']} - Current Position",
                icon=folium.Icon(color='red', icon='ship', prefix='fa')
            ).add_to(mini_map)
            
            # Display the mini map
            folium_static(mini_map, width=500, height=300)
            st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="sub-header">Alert Management System</div>', unsafe_allow_html=True)
    
    # Display current alerts
    if st.session_state.sos_alert:
        elapsed = (datetime.now() - st.session_state.sos_time).total_seconds()
        if elapsed < 60:  # Show for 60 seconds
            st.markdown(f'<div class="alert">⚠️ ACTIVE EMERGENCY ALERT: {st.session_state.sos_alert} ⚠️</div>', unsafe_allow_html=True)
    
    # Alert summary
    st.markdown('<div class="data-container">', unsafe_allow_html=True)
    st.markdown("#### Alert Summary")
    
    # Count alerts by type
    alert_types = {}
    for alert in st.session_state.alerts:
        if alert["type"] not in alert_types:
            alert_types[alert["type"]] = 0
        alert_types[alert["type"]] += 1
    
    # Display alert summary
    if not alert_types:
        st.write("No alerts have been issued yet.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            # Create DataFrame for alerts
            alert_df = pd.DataFrame({
                'Alert Type': list(alert_types.keys()),
                'Count': list(alert_types.values())
            })
            
            # Create chart
            chart = alt.Chart(alert_df).mark_bar(color='#FF5252').encode(
                x='Count:Q',
                y=alt.Y('Alert Type:N', sort='-x')
            ).properties(
                width=400,
                height=200
            ).configure_axis(
                labelColor='white',
                titleColor='white'
            )
            
            st.altair_chart(chart, use_container_width=True)
        
        with col2:
            for alert_type, count in alert_types.items():
                st.markdown(f"**{alert_type}:** {count} alerts")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent alerts
    st.markdown('<div class="data-container">', unsafe_allow_html=True)
    st.markdown("#### Recent Alerts")
    
    if not st.session_state.alerts:
        st.write("No recent alerts to display.")
    else:
        # Display recent alerts (most recent first)
        for alert in reversed(st.session_state.alerts[-10:]):  # Last 10 alerts
            if "EMERGENCY" in alert["message"]:
                st.markdown(f'<div class="alert">{alert["time"]}: {alert["message"]}</div>', unsafe_allow_html=True)
            elif "Warning" in alert["message"]:
                st.markdown(f'<div class="warning">{alert["time"]}: {alert["message"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="safe">{alert["time"]}: {alert["message"]}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # High risk vessels
    st.markdown('<div class="data-container">', unsafe_allow_html=True)
    st.markdown("#### High Risk Vessels")
    
    high_risk_boats = [b for b in st.session_state.boats if b["risk_level"] > 0.7]
    if not high_risk_boats:
        st.markdown('<div class="safe">No high risk vessels detected.</div>', unsafe_allow_html=True)
    else:
        for boat in high_risk_boats:
            st.markdown(f"""
            <div class="alert">
                <h4>{boat['name']} (Risk: {boat['risk_level']:.2f})</h4>
                <p>Safety Status: {boat['safety_status']}</p>
                <p>Engine Status: {boat['engine_status']}</p>
                <p>Communication: {boat['communication_status']}</p>
                <p>Fuel Level: {boat['fuel_level']:.1f}%</p>
                <p>Operation Time: {boat['operation_time']:.1f} hours</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Custom alert form
    st.markdown('<div class="sub-header">Send Custom Alert</div>', unsafe_allow_html=True)
    
    with st.form("custom_alert_form"):
        alert_msg = st.text_area("Alert Message")
        alert_recipients = st.multiselect(
            "Recipients",
            options=["All Vessels"] + [boat["name"] for boat in st.session_state.boats]
        )
        
        alert_type = st.selectbox(
            "Alert Type",
            ["Information", "Warning", "Emergency"]
        )
        
        submitted = st.form_submit_button("Send Alert")
        
        if submitted and alert_msg and alert_recipients:
            recipients_str = ", ".join(alert_recipients) if alert_recipients else "No recipients selected"
            
            # Add to alerts list
            st.session_state.alerts.append({
                "type": alert_type,
                "time": datetime.now().strftime("%H:%M:%S"),
                "message": f"{alert_type.upper()}: {alert_msg} (To: {recipients_str})"
            })
            
            st.success(f"Alert sent to {recipients_str}")

with tab4:
    st.markdown('<div class="sub-header">Analytics Dashboard</div>', unsafe_allow_html=True)
    
    # Create analytics dashboard
    col1, col2 = st.columns(2)
    
    with col1:
        # Risk distribution
        st.markdown('<div class="data-container">', unsafe_allow_html=True)
        st.markdown("#### Risk Level Distribution")
        
        # Create risk level categories
        risk_categories = {
            "Low Risk (0.0-0.3)": len([b for b in st.session_state.boats if b["risk_level"] < 0.3]),
            "Medium Risk (0.3-0.7)": len([b for b in st.session_state.boats if 0.3 <= b["risk_level"] <= 0.7]),
            "High Risk (0.7-1.0)": len([b for b in st.session_state.boats if b["risk_level"] > 0.7])
        }
        
        # Create DataFrame
        risk_df = pd.DataFrame({
            'Risk Category': list(risk_categories.keys()),
            'Count': list(risk_categories.values())
        })
        
        # Create chart
        colors = ['#4CAF50', '#FF9800', '#F44336']
        chart = alt.Chart(risk_df).mark_bar().encode(
            x=alt.X('Risk Category:N', sort=['Low Risk (0.0-0.3)', 'Medium Risk (0.3-0.7)', 'High Risk (0.7-1.0)']),
            y='Count:Q',
            color=alt.Color('Risk Category:N', scale=alt.Scale(domain=list(risk_categories.keys()), range=colors))
        ).properties(
            width=400,
            height=300
        ).configure_axis(
            labelColor='white',
            titleColor='white'
        )
        
        st.altair_chart(chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Fuel level analysis
        st.markdown('<div class="data-container">', unsafe_allow_html=True)
        st.markdown("#### Fuel Level Analysis")
        
        # Create fuel level categories
        fuel_cats = {
            "Critical (<10%)": len([b for b in st.session_state.boats if b["fuel_level"] < 10]),
            "Low (10-30%)": len([b for b in st.session_state.boats if 10 <= b["fuel_level"] < 30]),
            "Medium (30-60%)": len([b for b in st.session_state.boats if 30 <= b["fuel_level"] < 60]),
            "High (60-100%)": len([b for b in st.session_state.boats if b["fuel_level"] >= 60])
        }
        
        # Create DataFrame
        fuel_df = pd.DataFrame({
            'Fuel Level': list(fuel_cats.keys()),
            'Count': list(fuel_cats.values())
        })
        
        # Create chart
        fuel_colors = ['#F44336', '#FF9800', '#FFEB3B', '#4CAF50']
        fuel_chart = alt.Chart(fuel_df).mark_arc().encode(
            theta=alt.Theta(field="Count", type="quantitative"),
            color=alt.Color('Fuel Level:N', scale=alt.Scale(domain=list(fuel_cats.keys()), range=fuel_colors))
        ).properties(
            width=300,
            height=300
        )
        
        st.altair_chart(fuel_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Safety status summary
        st.markdown('<div class="data-container">', unsafe_allow_html=True)
        st.markdown("#### Safety Status Summary")
        
        # Create safety status categories
        safety_cats = {
            "Safe": len([b for b in st.session_state.boats if b["safety_status"] == "Safe"]),
            "Caution": len([b for b in st.session_state.boats if b["safety_status"] == "Caution"]),
            "Warning": len([b for b in st.session_state.boats if b["safety_status"] == "Warning"]),
            "Danger": len([b for b in st.session_state.boats if b["safety_status"] == "Danger"])
        }
        
        # Create DataFrame
        safety_df = pd.DataFrame({
            'Safety Status': list(safety_cats.keys()),
            'Count': list(safety_cats.values())
        })
        
        # Create chart
        safety_colors = ['#4CAF50', '#FFEB3B', '#FF9800', '#F44336']
        safety_chart = alt.Chart(safety_df).mark_bar().encode(
            x='Safety Status:N',
            y='Count:Q',
            color=alt.Color('Safety Status:N', scale=alt.Scale(domain=list(safety_cats.keys()), range=safety_colors))
        ).properties(
            width=400,
            height=300
        ).configure_axis(
            labelColor='white',
            titleColor='white'
        )
        
        st.altair_chart(safety_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Distance from shore analysis
        st.markdown('<div class="data-container">', unsafe_allow_html=True)
        st.markdown("#### Distance from Shore Analysis")
        
        # Calculate distances
        distances = []
        for boat in st.session_state.boats:
            dist = distance_to_shore(boat["lat"], boat["lon"])
            distances.append({
                "boat_name": boat["name"],
                "distance": dist,
                "risk_level": boat["risk_level"]
            })
        
        # Create DataFrame
        dist_df = pd.DataFrame(distances)
        
        # Create chart
        dist_chart = alt.Chart(dist_df).mark_circle(size=60).encode(
            x='distance:Q',
            y='risk_level:Q',
            color=alt.Color('risk_level:Q', scale=alt.Scale(scheme='redyellowgreen', domain=[1, 0])),
            tooltip=['boat_name', 'distance', 'risk_level']
        ).properties(
            width=400,
            height=300
        ).configure_axis(
            labelColor='white',
            titleColor='white'
        )
        
        st.altair_chart(dist_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Overall statistics
    st.markdown('<div class="data-container">', unsafe_allow_html=True)
    st.markdown("#### Overall Fleet Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_risk = sum(boat["risk_level"] for boat in st.session_state.boats) / len(st.session_state.boats)
        st.metric("Average Risk Level", f"{avg_risk:.2f}")
    
    with col2:
        avg_fuel = sum(boat["fuel_level"] for boat in st.session_state.boats) / len(st.session_state.boats)
        st.metric("Average Fuel Level", f"{avg_fuel:.1f}%")
    
    with col3:
        total_fish = sum(boat["fish_caught"] for boat in st.session_state.boats)
        st.metric("Total Fish Caught", f"{total_fish:.1f} kg")
    
    with col4:
        total_crew = sum(boat["crew_size"] for boat in st.session_state.boats)
        st.metric("Total Crew at Sea", total_crew)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Predictive analytics
    st.markdown('<div class="sub-header">Predictive Analysis</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="data-container">', unsafe_allow_html=True)
    st.markdown("#### Risk Forecast (Next 2 Hours)")
    
    # Generate simple forecast
    current_time = datetime.now()
    forecast_times = [(current_time + timedelta(minutes=30*i)).strftime("%H:%M") for i in range(5)]
    
    # Create forecast for each boat
    forecast_data = []
    for boat in st.session_state.boats:
        # Simple trend-based forecast with some randomness
        current_risk = boat["risk_level"]
        risk_trend = 0.05  # Base risk increase over time
        
        # Adjust trend based on current factors
        if boat["fuel_level"] < 30:
            risk_trend += 0.03  # Lower fuel increases risk faster
        if boat["operation_time"] > 10:
            risk_trend += 0.02  # Longer operation increases risk faster
        
        # Generate forecast points
        for i, time_point in enumerate(forecast_times):
            # Add some randomness to the forecast
            random_factor = random.uniform(-0.02, 0.02)
            forecasted_risk = min(1.0, current_risk + (risk_trend * (i+1)) + random_factor)
            
            forecast_data.append({
                "boat_name": boat["name"],
                "time": time_point,
                "forecasted_risk": forecasted_risk
            })
    
    # Create DataFrame
    forecast_df = pd.DataFrame(forecast_data)
    
    # Create chart
    forecast_chart = alt.Chart(forecast_df).mark_line().encode(
        x='time:N',
        y=alt.Y('forecasted_risk:Q', scale=alt.Scale(domain=[0, 1])),
        color='boat_name:N',
        tooltip=['boat_name', 'time', 'forecasted_risk']
    ).properties(
        width=800,
        height=400
    ).configure_axis(
        labelColor='white',
        titleColor='white'
    )
    
    st.altair_chart(forecast_chart, use_container_width=True)
    
    # Show high risk boat forecasts
    st.markdown("#### High Risk Forecast Alerts")
    
    high_risk_forecast = forecast_df[forecast_df["forecasted_risk"] > 0.7]
    high_risk_boats = high_risk_forecast["boat_name"].unique()
    
    if not len(high_risk_boats):
        st.markdown('<div class="safe">No high risk forecasts detected.</div>', unsafe_allow_html=True)
    else:
        for boat_name in high_risk_boats:
            boat_forecast = high_risk_forecast[high_risk_forecast["boat_name"] == boat_name]
            first_high_risk_time = boat_forecast.iloc[0]["time"]
            max_risk = boat_forecast["forecasted_risk"].max()
            
            st.markdown(f"""
            <div class="warning">
                <h4>{boat_name}</h4>
                <p>Predicted to reach high risk at {first_high_risk_time}</p>
                <p>Maximum forecasted risk: {max_risk:.2f}</p>
                <p>Recommended action: Consider recall or safety check</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center; margin-top:30px; padding:10px; background-color:#1E1E1E; border-radius:5px;">
    <p>FisherLink Monitoring System - Prototype Version 1.0</p>
    <p>© 2025 FisherLink Technologies. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)

# Generate automatic alerts based on boat conditions
for boat in st.session_state.boats:
    # Add alerts for high risk situations
    if boat["risk_level"] > 0.9 and random.random() < 0.05:  # 5% chance for very high risk boats
        st.session_state.alerts.append({
            "type": "Emergency",
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": f"EMERGENCY: Critical risk level detected for {boat['name']}! Immediate assistance required."
        })
    elif boat["risk_level"] > 0.8 and random.random() < 0.03:  # 3% chance for high risk boats
        st.session_state.alerts.append({
            "type": "Warning",
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": f"WARNING: High risk level detected for {boat['name']}. Monitor closely."
        })
    elif boat["fuel_level"] < 10 and random.random() < 0.05:  # 5% chance for low fuel boats
        st.session_state.alerts.append({
            "type": "Warning",
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": f"FUEL ALERT: Critically low fuel for {boat['name']}. Return to shore recommended."
        })
    elif distance_to_geofence(boat["lat"], boat["lon"]) < -1 and random.random() < 0.1:  # 10% chance for boats beyond geofence
        st.session_state.alerts.append({
            "type": "Boundary Alert",
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": f"BOUNDARY ALERT: {boat['name']} has crossed the geofence boundary and may lose communication."
        })
        
if len(st.session_state.alerts) > 100:
    st.session_state.alerts = st.session_state.alerts[-100:] 