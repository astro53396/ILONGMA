import sys
import subprocess
import folium
import tempfile
import csv
import math
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import contextily as ctx
from geopy.distance import great_circle
from pyproj import CRS
from matplotlib.widgets import Slider
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QDoubleSpinBox,
    QMessageBox
)
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView


class RocketSimulation(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.loadCoordinates()
        self.loadRocketDetails()
        self.setupMap()

    def initUI(self):
        self.setWindowTitle('I.L.O.N.G.M.A simulations')
        self.setWindowIcon(QIcon('ILONGMA.png'))
        self.setWindowTitle('Rocket Launch Simulation with Coriolis Effect')
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()

        # Initial Velocity Input
        self.initialVelocityLabel = QLabel('Initial Velocity (km/s):')
        self.layout.addWidget(self.initialVelocityLabel)
        self.initialVelocitySpinBox = QDoubleSpinBox()
        self.initialVelocitySpinBox.setRange(0.1, 11.2)
        self.initialVelocitySpinBox.setDecimals(2)
        self.initialVelocitySpinBox.setValue(1.0)
        self.layout.addWidget(self.initialVelocitySpinBox)

        # Target Altitude Input
        self.targetAltitudeLabel = QLabel('Target Altitude (km):')
        self.layout.addWidget(self.targetAltitudeLabel)
        self.targetAltitudeSpinBox = QDoubleSpinBox()
        self.targetAltitudeSpinBox.setRange(1.0, 35786.0)
        self.targetAltitudeSpinBox.setDecimals(2)
        self.targetAltitudeSpinBox.setValue(100.0)
        self.layout.addWidget(self.targetAltitudeSpinBox)

        # Launch Angle Input
        self.launchAngleLabel = QLabel('Launch Angle (degrees):')
        self.layout.addWidget(self.launchAngleLabel)
        self.launchAngleSpinBox = QDoubleSpinBox()
        self.launchAngleSpinBox.setRange(0, 90)
        self.launchAngleSpinBox.setDecimals(2)
        self.launchAngleSpinBox.setValue(45.0)
        self.layout.addWidget(self.launchAngleSpinBox)

        # Start Button
        self.startButton = QPushButton('Start Simulation')
        self.startButton.clicked.connect(self.startSimulation)
        self.layout.addWidget(self.startButton)

        # Status Label
        self.statusLabel = QLabel('Current Altitude: 0 km\nCurrent Latitude: 0°\nCurrent Longitude: 0°')
        self.layout.addWidget(self.statusLabel)

        # Map View
        self.mapView = QWebEngineView()
        self.layout.addWidget(self.mapView)

        self.setLayout(self.layout)

        # Timer for Simulation
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateSimulation)

        # Simulation Variables
        self.currentAltitude = 0.0
        self.velocity = 0.0
        self.targetAltitude = 0.0
        self.latitude = 0.0
        self.longitude = 0.0
        self.launchAngle = 0.0
        self.start_time = 0  # Simulation start time

        # Constants
        self.g0 = 9.81  # Standard gravity at Earth's surface (m/s²)
        self.R = 6371.0  # Radius of the Earth (km)
        self.earth_rotation_rate = 7.2921159e-5  # Earth's rotational speed at the equator (rad/s)

        # Latitude and Longitude Limits
        self.max_latitude = 90.0  # Latitude cannot exceed ±90 degrees
        self.max_longitude = 180.0  # Longitude cannot exceed ±180 degrees

        # Store positions for the map
        self.positions = []

    def loadCoordinates(self):
        # Load the initial latitude and longitude from coordinates.txt
        try:
            with open('coordinates.txt', 'r') as file:
                line = file.readline()
                parts = line.split(',')
                self.latitude = float(parts[0].split(": ")[1].strip())
                self.longitude = float(parts[1].split(": ")[1].strip())
        except FileNotFoundError:
            # Default values if file is not found
            self.latitude = 0.0
            self.longitude = 0.0

    def loadRocketDetails(self):
        # Load rocket details from rocket_selection_details.txt or fallback to rocket_selection_details_defaults.txt
        details = self.readRocketDetails('rocket_selection_details.txt')
        if details is None:
            details = self.readRocketDetails('rocket_selection_details_defaults.txt')
            if details is None:
                # Handle case where neither file is available
                details = {
                    "Max Speed": "7.8 km/s",
                    "Orbit": "10000 km",
                    "Launch Angle": "0.0°"
                }

        self.max_speed = float(details["Max Speed"].split()[0]) * 1000  # Convert to m/s
        self.targetAltitude = float(details["Orbit"].split()[0])  # in km
        self.launchAngle = float(details["Launch Angle"].replace("°", ""))  # in degrees

        # Set initial velocity and target altitude from the rocket details
        self.initialVelocitySpinBox.setValue(float(details["Max Speed"].split()[0]))  # km/s
        self.targetAltitudeSpinBox.setValue(self.targetAltitude)  # km

    def readRocketDetails(self, file_path):
        try:
            with open(file_path, 'r') as file:
                details = {}
                for line in file:
                    key, value = line.split(": ")
                    details[key.strip()] = value.strip()
                return details
        except FileNotFoundError:
            return None

    def setupMap(self):
        # Create a map centered at the initial latitude and longitude
        self.map = folium.Map(location=[self.latitude, self.longitude], zoom_start=10)
        folium.Marker([self.latitude, self.longitude], popup='Start').add_to(self.map)
        self.updateMap()

    def updateMap(self):
        # Save map to a temporary HTML file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as temp_file:
            self.map.save(temp_file.name)
            self.map_file_path = temp_file.name

        # Load map in QWebEngineView
        self.mapView.setUrl(QUrl.fromLocalFile(self.map_file_path))

    def startSimulation(self):
        self.velocity = self.initialVelocitySpinBox.value() * 1000  # Convert km/s to m/s
        self.targetAltitude = self.targetAltitudeSpinBox.value()
        self.launchAngle = self.launchAngleSpinBox.value()
        self.currentAltitude = 0.0
        self.positions = [(self.latitude, self.longitude, self.currentAltitude)]  # Initialize positions
        self.start_time = 0  # Initialize simulation start time
        self.timer.start(100)  # Update every 100 ms (0.1 seconds)

        # Open CSV file for writing the trajectory
        self.trajectory_file = open('rocket_trajectory.csv', 'w', newline='', encoding='utf-8')
        self.trajectory_writer = csv.writer(self.trajectory_file)
        self.trajectory_writer.writerow(['Time (s)', 'Altitude (km)', 'Latitude (°)', 'Longitude (°)'])

    def calculate_gravity(self, altitude):
        # Calculate gravity based on altitude
        g_h = self.g0 * (self.R / (self.R + altitude)) ** 2
        return g_h

    def updateSimulation(self):
        # Time step (in seconds)
        dt = 0.1
        self.start_time += dt

        if self.currentAltitude < self.targetAltitude:
            # Calculate the change in altitude
            self.currentAltitude += self.velocity * dt / 1000.0  # Convert meters to kilometers

            # Calculate current gravity based on altitude
            g = self.calculate_gravity(self.currentAltitude)

            # Update velocity based on gravity
            acceleration = g - 9.81  # Acceleration due to gravity
            self.velocity += acceleration * dt

            # Update latitude and longitude based on launch angle and Coriolis effect
            distance_travelled = self.velocity * dt / 1000.0  # Convert meters to kilometers
            new_latitude = self.latitude + (distance_travelled * math.sin(math.radians(self.launchAngle)) / 111)  # 1 degree ~ 111 km
            new_longitude = self.longitude + (2 * self.velocity * self.earth_rotation_rate * math.sin(math.radians(self.latitude)) * dt / (111 * math.cos(math.radians(self.latitude))))  # Convert to degrees

            # Enforce latitude and longitude limits
            if abs(new_latitude) <= self.max_latitude:
                self.latitude = new_latitude
            if abs(new_longitude) <= self.max_longitude:
                self.longitude = new_longitude

            # Add new position to the list
            self.positions.append((self.latitude, self.longitude, self.currentAltitude))

            # Create a new map for each update
            self.map = folium.Map(location=[self.latitude, self.longitude], zoom_start=10)
            for lat, lon, alt in self.positions:
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=5,
                    color='blue',
                    fill=True,
                    fill_color='blue',
                    fill_opacity=0.6,
                    popup=f'Altitude: {alt:.2f} km'
                ).add_to(self.map)
            self.updateMap()

            # Write to CSV
            self.trajectory_writer.writerow([self.start_time, self.currentAltitude, self.latitude, self.longitude])

        # Check if the target altitude is reached or exceeded
        if self.currentAltitude >= self.targetAltitude:
            self.currentAltitude = self.targetAltitude
            self.timer.stop()
            self.trajectory_file.close()  # Close CSV file
            QMessageBox.information(self, 'Simulation Complete', f'Rocket reached the target altitude of {self.targetAltitude} km.')

            # Call the external script
            subprocess.run(['python', 'diffusion_module.py'])

        # Update status label
        self.statusLabel.setText(f'Current Altitude: {self.currentAltitude:.2f} km\n'
                                 f'Current Latitude: {self.latitude:.2f}°\n'
                                 f'Current Longitude: {self.longitude:.6f}°')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RocketSimulation()
    ex.show()
    sys.exit(app.exec_())
