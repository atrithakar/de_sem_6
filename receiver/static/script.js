function waterLevel(moisture) {
  if (moisture < 65) return "LOW";
  if (moisture > 80) return "HIGH";
  return "MEDIUM";
}

function buildSuggestions(temp, humidity, moisture) {
  const suggestions = [];
  const water = waterLevel(moisture);

  if (water === "LOW") suggestions.push("⚠️ Water level low — consider irrigating.");
  else suggestions.push("✅ Soil moisture is sufficient.");

  if (temp < 15 || temp > 24) suggestions.push("⚠️ Temperature out of optimal range.");
  else suggestions.push("✅ Temperature optimal for most crops.");

  if (humidity < 60 || humidity > 80) suggestions.push("⚠️ Humidity is not ideal.");
  else suggestions.push("✅ Humidity within optimal range.");

  return suggestions;
}

function setStatus(id, isOn) {
  const el = document.getElementById(id);
  el.textContent = isOn ? "ON" : "OFF";
  el.className = "status-dot " + (isOn ? "status-on" : "status-off");
}

async function updateDashboard() {
  try {
    const res = await fetch("/api/latest");
    const data = await res.json();

    document.getElementById("temp").textContent = data.temperature;
    document.getElementById("humidity").textContent = data.humidity;
    // document.getElementById("water-level").textContent = waterLevel(data.soil_moisture);
    document.getElementById("water-level").textContent = data.soil_moisture;

    const suggestionsList = document.getElementById("suggestions");
    suggestionsList.innerHTML = "";
    const tips = buildSuggestions(data.temperature, data.humidity, data.soil_moisture);
    tips.forEach(tip => {
      const li = document.createElement("li");
      li.textContent = tip;
      suggestionsList.appendChild(li);
    });

    // Device status logic
    const pump = data.soil_moisture < 65 /* || data.soil_moisture > 80 */;
    const ac = data.temperature < 15 || data.temperature > 24;
    const humidifier = data.humidity < 60 || data.humidity > 80;

    setStatus("pump-status", pump);
    setStatus("ac-status", ac);
    setStatus("humidifier-status", humidifier);

  } catch (err) {
    console.error("Error updating dashboard:", err);
  }
}

async function updateHistory() {
  const res = await fetch("/api/history");
  const history = await res.json();
  const tbody = document.getElementById("history-table");
  tbody.innerHTML = "";

  history.forEach(entry => {
    const row = document.createElement("tr");

    const ts = new Date(entry.timestamp).toLocaleTimeString();
    // const water = waterLevel(entry.soil_moisture);
    const water = entry.soil_moisture;

    row.innerHTML = `
      <td>${ts}</td>
      <td>${entry.temperature}</td>
      <td>${entry.humidity}</td>
      <td>${water}</td>
    `;
    tbody.appendChild(row);
  });
}

setInterval(() => {
  updateDashboard();
  updateHistory();
}, 5000);

updateDashboard();
updateHistory();
