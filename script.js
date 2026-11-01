// Get the main webpage elements.
const organismArea = document.getElementById("organismArea");
const canvas = document.getElementById("simulationCanvas");
const ctx = canvas.getContext("2d");


let simulationState = null;
let running = false;
let timer = null;




// These species names are data, so the same code can be reused.
const speciesList = [
    ["rabbit", "Rabbit"],
    ["fox", "Fox"],
    ["deer", "Deer"],
    ["hawk", "Hawk"]
];




// Create one organism card.
// The same function is used for all three cards.
function createOrganismCard(number) {


    const card = document.createElement("div");
    card.className = "organism-card";


    let options = "";


    for (const species of speciesList) {
        options = options +
            "<option value='" + species[0] + "'>" +
            species[1] +
            "</option>";
    }


    card.innerHTML =
        "<h3>Species " + number + "</h3>" +


        "<label>Species</label>" +
        "<select class='species-select'>" +
        options +
        "</select>" +


        "<label>Hunger</label>" +
        "<input class='hunger-input' type='range' min='0' max='100' value='50'>" +


        "<label>Thirst</label>" +
        "<input class='thirst-input' type='range' min='0' max='100' value='50'>" +


        "<label>Energy</label>" +
        "<input class='energy-input' type='range' min='0' max='100' value='80'>" +


        "<label>Speed</label>" +
        "<input class='trait-speed' type='range' min='0' max='100' value='50'>" +


        "<label>Camouflage</label>" +
        "<input class='trait-camouflage' type='range' min='0' max='100' value='50'>" +


        "<label>Heat tolerance</label>" +
        "<input class='trait-heat' type='range' min='0' max='100' value='50'>" +


        "<label>Disease resistance</label>" +
        "<input class='trait-disease' type='range' min='0' max='100' value='50'>";


    organismArea.appendChild(card);
}




// Repeat the same function three times.
for (let number = 1; number <= 3; number++) {
    createOrganismCard(number);
}




// Get the settings from the three cards.
function collectOrganisms() {


    const cards = document.querySelectorAll(".organism-card");
    const organisms = [];


    for (const card of cards) {


        const traits = {
            speed: Number(card.querySelector(".trait-speed").value),
            camouflage: Number(card.querySelector(".trait-camouflage").value),
            heat_tolerance: Number(
                card.querySelector(".trait-heat").value
            ),
            disease_resistance: Number(
                card.querySelector(".trait-disease").value
            )
        };


        const organism = {
            type: card.querySelector(".species-select").value,
            hunger: Number(card.querySelector(".hunger-input").value),
            thirst: Number(card.querySelector(".thirst-input").value),
            energy: Number(card.querySelector(".energy-input").value),
            traits: traits
        };


        organisms.push(organism);
    }


    return organisms;
}




// Create a simulation.
async function createSimulation() {


    pauseSimulation();


    const species = collectOrganisms();
    const names = [];


    for (const organism of species) {
        names.push(organism.type);
    }


    if (new Set(names).size !== 3) {
        document.getElementById("message").textContent =
            "Choose three different species.";
        return;
    }


    const configuration = {
        terrain: document.getElementById("terrain").value,
        climate: document.getElementById("climate").value,
        resources: {
            food: Number(document.getElementById("food").value),
            water: Number(document.getElementById("water").value),
            shelter: Number(document.getElementById("shelter").value)
        },
        organisms: species
    };


    const response = await fetch("/create-environment", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(configuration)
    });


    const data = await response.json();


    if (!response.ok) {
        document.getElementById("message").textContent = data.error;
        return;
    }


    simulationState = data.state;
    updateInterface();
    drawSimulation();


    document.getElementById("message").textContent =
        "Simulation created.";
}




// Start the simulation.
function startSimulation() {


    if (running === false && simulationState !== null) {
        running = true;
        timer = setInterval(runStep, 200);
    }
}




// Pause the simulation.
function pauseSimulation() {


    running = false;


    if (timer !== null) {
        clearInterval(timer);
        timer = null;
    }
}




// Ask Python to run one step.
async function runStep() {


    if (simulationState === null) {
        return;
    }


    const response = await fetch("/simulate-step", {
        method: "POST"
    });


    const data = await response.json();


    if (!response.ok) {
        pauseSimulation();
        document.getElementById("message").textContent = data.error;
        return;
    }


    simulationState = data.state;


    updateInterface();
    drawSimulation();
}




// Reset the simulation.
async function resetSimulation() {


    pauseSimulation();


    const response = await fetch("/reset-simulation", {
        method: "POST"
    });


    const data = await response.json();


    if (!response.ok) {
        document.getElementById("message").textContent = data.error;
        return;
    }


    simulationState = data.state;


    updateInterface();
    drawSimulation();


    document.getElementById("message").textContent =
        "Simulation reset.";
}




// Save the form settings.
async function saveConfiguration() {


    const configuration = {
        terrain: document.getElementById("terrain").value,
        climate: document.getElementById("climate").value,
        resources: {
            food: Number(document.getElementById("food").value),
            water: Number(document.getElementById("water").value),
            shelter: Number(document.getElementById("shelter").value)
        },
        organisms: collectOrganisms()
    };


    const response = await fetch("/save-configuration", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(configuration)
    });


    const data = await response.json();


    document.getElementById("message").textContent = data.message;
}




// Load the saved form settings.
async function loadConfiguration() {


    const response = await fetch("/load-configuration");
    const data = await response.json();


    if (!response.ok) {
        document.getElementById("message").textContent = data.error;
        return;
    }


    const configuration = data.configuration;


    document.getElementById("terrain").value = configuration.terrain;
    document.getElementById("climate").value = configuration.climate;


    document.getElementById("food").value =
        configuration.resources.food;
    document.getElementById("water").value =
        configuration.resources.water;
    document.getElementById("shelter").value =
        configuration.resources.shelter;


    const cards = document.querySelectorAll(".organism-card");


    for (let i = 0; i < cards.length; i++) {


        const organism = configuration.organisms[i];
        const card = cards[i];


        card.querySelector(".species-select").value =
            organism.type;


        card.querySelector(".hunger-input").value =
            organism.hunger;


        card.querySelector(".thirst-input").value =
            organism.thirst;


        card.querySelector(".energy-input").value =
            organism.energy;


        card.querySelector(".trait-speed").value =
            organism.traits.speed;


        card.querySelector(".trait-camouflage").value =
            organism.traits.camouflage;


        card.querySelector(".trait-heat").value =
            organism.traits.heat_tolerance;


        card.querySelector(".trait-disease").value =
            organism.traits.disease_resistance;
    }


    updateSliderValues();


    document.getElementById("message").textContent =
        "Configuration loaded.";
}




// Update the numbers beside the sliders.
function updateSliderValues() {
    document.getElementById("foodValue").textContent =
        document.getElementById("food").value;


    document.getElementById("waterValue").textContent =
        document.getElementById("water").value;


    document.getElementById("shelterValue").textContent =
        document.getElementById("shelter").value;
}




// Display the current simulation information.
function updateInterface() {


    const environment = simulationState.environment;


    document.getElementById("environmentTitle").textContent =
        environment.terrain_name + " - " +
        environment.climate_name;


    document.getElementById("environmentDescription").textContent =
        environment.terrain_description + " " +
        environment.climate_description;


    document.getElementById("generation").textContent =
        simulationState.generation;


    let populationText = "";


    for (const species in simulationState.population) {


        if (populationText !== "") {
            populationText = populationText + " | ";
        }


        populationText =
            populationText +
            species + ": " +
            simulationState.population[species];
    }


    document.getElementById("populationInfo").textContent =
        populationText;


    document.getElementById("resourceInfo").textContent =
        "Food: " + environment.resources.food +
        " | Water: " + environment.resources.water +
        " | Shelter: " + environment.resources.shelter;


    const decisions = {};


    for (const organism of simulationState.organisms) {


        const decision = organism.decision;


        if (decisions[decision] === undefined) {
            decisions[decision] = 0;
        }


        decisions[decision] = decisions[decision] + 1;
    }


    let decisionText = "";


    for (const decision in decisions) {


        if (decisionText !== "") {
            decisionText = decisionText + " | ";
        }


        decisionText =
            decisionText +
            decision + ": " +
            decisions[decision];
    }


    document.getElementById("decisionInfo").textContent =
        decisionText;
}




// Draw the whole simulation.
function drawSimulation() {


    ctx.clearRect(0, 0, canvas.width, canvas.height);


    drawTerrain(simulationState.environment.terrain);


    for (const organism of simulationState.organisms) {
        drawOrganism(organism);
    }
}




// Draw the selected terrain.
function drawTerrain(terrain) {


    if (terrain === "forest") {


        ctx.fillStyle = "#b7d7a8";
        ctx.fillRect(0, 0, canvas.width, canvas.height);


        ctx.fillStyle = "#477a4c";


        for (let x = 20; x < canvas.width; x += 85) {
            ctx.fillRect(x, 260, 20, 90);
        }


    } else if (terrain === "desert") {


        ctx.fillStyle = "#e8d7a5";
        ctx.fillRect(0, 0, canvas.width, canvas.height);


        ctx.fillStyle = "#66865a";


        for (let x = 60; x < canvas.width; x += 150) {
            ctx.fillRect(x, 270, 12, 70);
        }


    } else {


        ctx.fillStyle = "#b9d99a";
        ctx.fillRect(0, 0, canvas.width, canvas.height);


        ctx.fillStyle = "#5a8c3d";


        for (let x = 10; x < canvas.width; x += 35) {
            ctx.fillRect(x, 310, 3, 30);
        }
    }
}




// Draw one organism.
function drawOrganism(organism) {


    ctx.fillStyle = organism.color;


    ctx.beginPath();


    ctx.arc(
        organism.x,
        organism.y,
        7 + organism.traits.speed / 25,
        0,
        2 * Math.PI
    );


    ctx.fill();


    if (organism.role === "Predator") {
        ctx.strokeStyle = "#222222";
        ctx.stroke();
    }
}




// Allow the user to click an organism.
canvas.addEventListener("click", function(event) {


    if (simulationState === null) {
        return;
    }


    const rectangle = canvas.getBoundingClientRect();


    const scaleX = canvas.width / rectangle.width;
    const scaleY = canvas.height / rectangle.height;


    const mouseX =
        (event.clientX - rectangle.left) * scaleX;


    const mouseY =
        (event.clientY - rectangle.top) * scaleY;


    let selected = null;
    let closest = 100000;


    for (const organism of simulationState.organisms) {


        const dx = mouseX - organism.x;
        const dy = mouseY - organism.y;
        const distance = Math.sqrt(dx * dx + dy * dy);


        if (distance < closest && distance < 20) {
            closest = distance;
            selected = organism;
        }
    }


    if (selected !== null) {


        document.getElementById("selectedOrganism").innerHTML =
            "<strong>" + selected.species_name + "</strong><br>" +
            "Generation: " + selected.generation + "<br>" +
            "Decision: " + selected.decision + "<br>" +
            "Hunger: " + selected.hunger + "<br>" +
            "Thirst: " + selected.thirst + "<br>" +
            "Energy: " + selected.energy + "<br>" +
            "Speed: " + selected.traits.speed + "<br>" +
            "Camouflage: " + selected.traits.camouflage + "<br>" +
            "Heat tolerance: " +
            selected.traits.heat_tolerance + "<br>" +
            "Disease resistance: " +
            selected.traits.disease_resistance;
    }
});




// Connect buttons to their functions.
document.getElementById("createButton")
    .addEventListener("click", createSimulation);


document.getElementById("startButton")
    .addEventListener("click", startSimulation);


document.getElementById("pauseButton")
    .addEventListener("click", pauseSimulation);


document.getElementById("resetButton")
    .addEventListener("click", resetSimulation);


document.getElementById("saveButton")
    .addEventListener("click", saveConfiguration);


document.getElementById("loadButton")
    .addEventListener("click", loadConfiguration);




// Update slider numbers when the page opens.
updateSliderValues();
