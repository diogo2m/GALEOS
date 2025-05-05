var map = L.map('map').setView([0, 0], 2);
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://carto.com/">CartoDB</a>'
}).addTo(map);

var markers = {};
var icons = {};

// Load icons from the JSON file
$.getJSON('/icons.json', function(data) {
    for (let category in data) {
        icons[category] = L.icon(data[category]);
    }
});

function updateMarkers() {
    $.getJSON('/update_markers', function(data) {
        for (let category in data) {
            data[category].forEach(item => {
                let key = item.name ? item.name : category + '_' + item.id;
                if (markers[key]) {
                    markers[key].setLatLng([item.coordinates[0], item.coordinates[1]]); // Move existing marker
                } else {
                    let marker = L.marker([item.coordinates[0], item.coordinates[1]], { icon: icons[category] })
                        .bindPopup(`${category}: ${key}`);
                    marker.addTo(map);
                    markers[key] = marker;
                }
            });
        }
    });
}

setInterval(updateMarkers, 1000);  // Update every 1 second
