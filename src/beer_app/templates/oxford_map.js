const oxford = [51.7520, -1.2577];
const map = L.map("map").setView(oxford, 14);

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'
}).addTo(map);

const pubLayer = L.layerGroup().addTo(map);

function createPopup(pub) {
  const popup = document.createElement("section");
  popup.className = "pub-popup";

  const heading = document.createElement("h2");
  heading.textContent = pub.name;
  popup.appendChild(heading);

  if (pub.road || pub.location) {
    const address = document.createElement("p");
    address.className = "address";
    address.textContent = [pub.road, pub.location]
      .filter(Boolean)
      .join(", ");
    popup.appendChild(address);
  }

  if (pub.sponsor) {
    const sponsor = document.createElement("p");
    sponsor.innerHTML = '<span class="field-label">Sponsor:</span> ';
    sponsor.appendChild(document.createTextNode(pub.sponsor));
    popup.appendChild(sponsor);
  }

  if (pub.notes) {
    const notes = document.createElement("p");
    notes.className = "notes";
    notes.innerHTML = '<span class="field-label">Notes:</span> ';
    notes.appendChild(document.createTextNode(pub.notes));
    popup.appendChild(notes);
  }
// add visited status here
  return popup;
}

let pubVersion = -1;

async function refreshPubs() {
  const response = await fetch("/api/pubs");
  if (!response.ok) {
    throw new Error(`Could not load pubs: ${response.status}`);
  }

  const payload = await response.json();
  if (payload.version === pubVersion) {
    return;
  }

  pubVersion = payload.version;
  pubLayer.clearLayers();
  const bounds = [];

  for (const pub of payload.pubs) {
    const coordinates = [pub.latitude, pub.longitude];
    L.marker(coordinates).addTo(pubLayer).bindPopup(createPopup(pub));
    bounds.push(coordinates);
  }

  if (bounds.length > 0) {
    map.fitBounds(bounds, { padding: [25, 25], maxZoom: 14 });
  } else {
    map.setView(oxford, 14);
  }

  titleElement.textContent = `Oxford Pub Map · ${payload.pubs.length} pubs`;
}

const title = L.control({ position: "topright" });
let titleElement;
title.onAdd = () => {
  titleElement = L.DomUtil.create("div", "map-title");
  titleElement.textContent = "Oxford Pub Map · 0 pubs";
  return titleElement;
};
title.addTo(map);

async function updateMap() {
  try {
    await refreshPubs();
  } catch (error) {
    console.error(error);
    titleElement.textContent = "Oxford Pub Map · could not load pubs";
  }
}

updateMap();
window.setInterval(updateMap, 1000);
