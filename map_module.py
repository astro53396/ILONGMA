import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, pyqtSlot

html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>World Map</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
    <style>
        #map {
            height: 80vh;
        }
        #instruction {
            position: absolute;
            top: 10px;
            left: 10px;
            background-color: rgba(255, 255, 255, 0.8);
            padding: 10px;
            border-radius: 5px;
            font-family: 'Helvetica', sans-serif;
            font-size: 15px;
            z-index: 1000;
        }
        .message {
            position: relative; 
            top: 10px; 
            left: 0;
            width: 130px; 
            background-color: rgba(0, 255, 0, 0.8);
            padding: 7px;
            border-radius: 5px;
            font-family: 'Helvetica', sans-serif;
            font-size: 15px;
            z-index: 1000;
            margin-top: 5px;
            display: block;
        }
        #messages {
            position: absolute;
            top: 50px; 
            left: 10px;
            width: 250px; 
        }
    </style>
</head>
<body>
    <div id="map"></div>
    <div id="instruction">Please click on the map to add a marker. Press Enter to save the coordinates.</div>
    <div id="messages"></div>

    <script>
        var map = L.map('map').setView([0, 0], 2);
        var marker = null;

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
        }).addTo(map);

        new QWebChannel(qt.webChannelTransport, function(channel) {
            window.pyObj = channel.objects.pyObj;
        });

        function addMarker(latitude, longitude) {
            if (marker) {
                map.removeLayer(marker);
            }
            marker = L.marker([latitude, longitude]).addTo(map)
                .bindPopup('Coordinates: ' + latitude + ', ' + longitude)
                .openPopup();
        }

        map.on('click', function(event) {
            var latlng = getLatLngFromClick(event);
            addMarker(latlng.latitude, latlng.longitude);
        });

        function getLatLngFromClick(event) {
            var latlng = map.mouseEventToLatLng(event.originalEvent);
            return { latitude: latlng.lat, longitude: latlng.lng };
        }

        document.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' && marker) {
                event.preventDefault();
                var latlng = marker.getLatLng();
                var coordinates = {latitude: latlng.lat, longitude: latlng.lng};
                window.pyObj.saveCoordinates(JSON.stringify(coordinates));
            }
        });

        function showMessage() {
            var messagesDiv = document.getElementById('messages');
            var messageDiv = document.createElement('div');
            messageDiv.className = 'message';
            messageDiv.innerText = 'Coordinates saved!';
            messagesDiv.appendChild(messageDiv);

            setTimeout(function() {
                messagesDiv.removeChild(messageDiv);
            }, 1500);
        }

        function coordinatesSaved() {
            showMessage();
        }

        map.zoomControl.setPosition('topright');
    </script>
</body>
</html>
'''

class Bridge(QObject):
    @pyqtSlot(str)
    def saveCoordinates(self, coordinates):
        data = json.loads(coordinates)
        latitude = data['latitude']
        longitude = data['longitude']
        with open('coordinates.txt', 'w') as file:
            file.write(f'Latitude: {latitude}, Longitude: {longitude}\n')
        self.viewer.webview.page().runJavaScript('coordinatesSaved();')

class WebViewer(QMainWindow):
    def __init__(self, html_content):
        super().__init__()
        self.setWindowTitle('I.L.O.N.G.M.A coordinate')
        self.setWindowIcon(QIcon('ILONGMA.png'))
        self.setGeometry(100, 100, 800, 600)

        self.webview = QWebEngineView()
        self.setCentralWidget(self.webview)

        self.channel = QWebChannel()
        self.bridge = Bridge()
        self.bridge.viewer = self
        self.channel.registerObject('pyObj', self.bridge)
        self.webview.page().setWebChannel(self.channel)

        self.webview.setHtml(html_content)

    def closeEvent(self, event):
        self.webview.setHtml('')
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    viewer = WebViewer(html_content)
    viewer.show()

    sys.exit(app.exec_())
