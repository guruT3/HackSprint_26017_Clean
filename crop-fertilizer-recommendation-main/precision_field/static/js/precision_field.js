/**
 * Precision Field Zoning & Water Stress Map Controller
 */

window.PrecisionMapController = {
    map: null,
    zoneLayersGroup: null,
    targetMarker: null,
    fieldData: null,
    currentLat: 28.6139,
    currentLng: 77.2090,
    isUpdatingLocation: false,

    init: function (containerId, defaultLat, defaultLng) {
        if (!document.getElementById(containerId)) return;

        this.currentLat = defaultLat || 28.6139;
        this.currentLng = defaultLng || 77.2090;

        this.map = L.map(containerId).setView([this.currentLat, this.currentLng], 16);

        // OpenStreetMap Tile Layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap contributors | Sentinel-2 ESA'
        }).addTo(this.map);

        this.zoneLayersGroup = L.layerGroup().addTo(this.map);

        // Target field center pin marker
        this.targetMarker = L.marker([this.currentLat, this.currentLng], {
            draggable: true
        }).addTo(this.map).bindPopup("<b>Target Field Center</b><br>Drag pin or pan map to pick new field location.");

        const self = this;

        // Marker drag handler
        this.targetMarker.on('dragend', function (e) {
            const pos = e.target.getLatLng();
            self.setLocation(pos.lat, pos.lng, "Custom Dragged Location", true);
        });

        // Map click handler to select target location
        this.map.on('click', function (e) {
            self.setLocation(e.latlng.lat, e.latlng.lng, "Selected Map Point", true);
        });

        // Live Realtime Drag-to-Update Listener (updates grid automatically when user pans map)
        let panTimeout = null;
        this.map.on('moveend', function () {
            if (self.isUpdatingLocation) return;
            clearTimeout(panTimeout);
            panTimeout = setTimeout(function () {
                const center = self.map.getCenter();
                self.setLocation(center.lat, center.lng, "Panned Map Location", false);
            }, 350);
        });

        // Bind DOM elements & controls
        this.bindEvents();
    },

    bindEvents: function () {
        const self = this;

        // Preset Field Dropdown
        const selectEl = document.getElementById('pf-field-select');
        if (selectEl) {
            selectEl.addEventListener('change', function (e) {
                const val = e.target.value;
                if (val === 'north_field') {
                    self.setLocation(28.6139, 77.2090, "North Field (Punjab)", true);
                } else if (val === 'south_field') {
                    self.setLocation(12.9716, 77.5946, "South Field (Karnataka)", true);
                } else if (val === 'west_field') {
                    self.setLocation(19.0760, 72.8777, "West Field (Maharashtra)", true);
                }
            });
        }

        // GPS Button
        const gpsBtn = document.getElementById('pf-btn-gps');
        if (gpsBtn) {
            gpsBtn.addEventListener('click', function () {
                self.takeCurrentLocation();
            });
        }

        // Analyze Button
        const analyzeBtn = document.getElementById('pf-btn-analyze');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', function () {
                const lat = parseFloat(document.getElementById('pf-lat-input')?.value || self.currentLat);
                const lng = parseFloat(document.getElementById('pf-lng-input')?.value || self.currentLng);
                self.setLocation(lat, lng, "Custom Target Field", true);
            });
        }
    },

    takeCurrentLocation: function () {
        const self = this;
        const gpsText = document.getElementById('pf-gps-text');

        if (!navigator.geolocation) {
            alert('Geolocation is not supported by your browser.');
            return;
        }

        if (gpsText) gpsText.innerText = "📡 Locating GPS...";

        navigator.geolocation.getCurrentPosition(
            function (position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                if (gpsText) gpsText.innerText = "📍 Take Current Location";
                self.setLocation(lat, lng, "My GPS Current Location", true);
            },
            function (error) {
                if (gpsText) gpsText.innerText = "📍 Take Current Location";
                let msg = 'Unable to retrieve your location.';
                if (error.code === error.PERMISSION_DENIED) {
                    msg = 'Location permission denied. Please allow GPS access in browser or manually enter coordinates / click on map.';
                }
                alert(msg);
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
    },

    setLocation: function (lat, lng, fieldTitle, panMap) {
        if (panMap === undefined) panMap = true;

        this.isUpdatingLocation = true;
        this.currentLat = parseFloat(lat.toFixed(6));
        this.currentLng = parseFloat(lng.toFixed(6));

        // Update inputs
        const latInput = document.getElementById('pf-lat-input');
        const lngInput = document.getElementById('pf-lng-input');
        if (latInput) latInput.value = this.currentLat;
        if (lngInput) lngInput.value = this.currentLng;

        // Update active title badge
        const titleEl = document.getElementById('pf-active-field-title');
        if (titleEl) {
            titleEl.innerText = `${fieldTitle || 'Custom Location'} (${this.currentLat}, ${this.currentLng})`;
        }

        // Center map view on new target coordinates if requested
        if (panMap && this.map) {
            this.map.setView([this.currentLat, this.currentLng], 16);
        }

        // Update target pin marker position
        if (this.targetMarker) {
            this.targetMarker.setLatLng([this.currentLat, this.currentLng]);
        }

        // Reload zoning map for new target location
        const self = this;
        this.loadFieldZones('custom_field', { lat: this.currentLat, lng: this.currentLng, panMap: panMap }, function () {
            setTimeout(function () {
                self.isUpdatingLocation = false;
            }, 200);
        });
    },

    loadFieldZones: function (fieldId, options, callback) {
        options = options || {};
        const self = this;
        const lat = options.lat || this.currentLat;
        const lng = options.lng || this.currentLng;
        const panMap = options.panMap !== undefined ? options.panMap : true;

        const url = `/api/precision/fields/${fieldId}/zones?lat=${lat}&lng=${lng}&rows=3&cols=3&_t=${Date.now()}`;

        fetch(url)
            .then(res => res.json())
            .then(res => {
                if (res.status === 'success') {
                    self.fieldData = res.data;
                    self.renderZonesMap(res.data, panMap);
                    // Select first flagged zone or zone 1 by default
                    const firstAttention = res.data.zones.find(z => z.status !== "Normal / Healthy") || res.data.zones[0];
                    if (firstAttention) {
                        self.selectZone(firstAttention);
                    }
                } else {
                    console.warn('[Precision Module] Error loading precision zones');
                }
                if (typeof callback === 'function') callback();
            })
            .catch(err => {
                console.error('[Precision Module Exception]', err);
                if (typeof callback === 'function') callback();
            });
    },

    renderZonesMap: function (data, panMap) {
        const self = this;
        if (!this.map || !data.zones) return;

        this.zoneLayersGroup.clearLayers();
        const allBounds = [];

        data.zones.forEach(zone => {
            const coords = zone.geometry.coordinates[0].map(pt => [pt[1], pt[0]]);
            allBounds.push(...coords);

            // Determine zone color based on status
            let strokeColor = '#15803d';
            let fillColor = '#2ecc71'; // Green
            if (zone.status === "Potential Water Stress") {
                strokeColor = '#b91c1c';
                fillColor = '#e74c3c'; // Red
            } else if (zone.status === "Attention Required") {
                strokeColor = '#a16207';
                fillColor = '#f1c40f'; // Yellow
            }

            const poly = L.polygon(coords, {
                color: strokeColor,
                weight: 2,
                fillColor: fillColor,
                fillOpacity: 0.55
            });

            // Tooltip on hover
            poly.bindTooltip(`<b>${zone.zone_name} (${zone.grid_code})</b><br>Status: ${zone.status}<br>NDMI: ${zone.ndmi} | NDVI: ${zone.ndvi}`, {
                sticky: true
            });

            // Click listener
            poly.on('click', function () {
                self.selectZone(zone);
            });

            poly.addTo(self.zoneLayersGroup);
        });

        if (panMap && allBounds.length > 0) {
            this.map.fitBounds(L.latLngBounds(allBounds), { padding: [30, 30] });
        }
    },

    selectZone: function (zone) {
        // Update Zone Details Sidebar
        if (document.getElementById('pf-zone-name')) {
            document.getElementById('pf-zone-name').innerText = `${zone.zone_name} (${zone.grid_code})`;
        }
        if (document.getElementById('pf-zone-status')) {
            const el = document.getElementById('pf-zone-status');
            el.innerText = zone.status;
            el.className = 'pf-badge ' + (zone.status === 'Potential Water Stress' ? 'pf-badge-stress' : (zone.status === 'Attention Required' ? 'pf-badge-attention' : 'pf-badge-normal'));
        }
        if (document.getElementById('pf-zone-ndvi')) {
            document.getElementById('pf-zone-ndvi').innerText = zone.ndvi;
        }
        if (document.getElementById('pf-zone-ndmi')) {
            document.getElementById('pf-zone-ndmi').innerText = zone.ndmi;
        }
        if (document.getElementById('pf-zone-area')) {
            document.getElementById('pf-zone-area').innerText = zone.area_acres + ' acres';
        }
        if (document.getElementById('pf-zone-score')) {
            document.getElementById('pf-zone-score').innerText = zone.stress_indicator_score + ' / 100';
        }
        if (document.getElementById('pf-zone-confidence')) {
            document.getElementById('pf-zone-confidence').innerText = zone.confidence;
        }
        if (document.getElementById('pf-zone-recommendation')) {
            document.getElementById('pf-zone-recommendation').innerText = zone.recommendation;
        }

        // Render Explainability Reasons List
        const reasonsContainer = document.getElementById('pf-reasons-list');
        if (reasonsContainer && zone.reasons) {
            reasonsContainer.innerHTML = zone.reasons.map(r => `<li>${r}</li>`).join('');
        }
    }
};
