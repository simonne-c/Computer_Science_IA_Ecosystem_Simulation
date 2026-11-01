# This class represents one environment.
class Environment:


    # Store the user's environment choices.
    def __init__(self, terrain, climate, terrain_data, climate_data, resources):
        self.terrain = terrain
        self.climate = climate
        self.terrain_data = terrain_data
        self.climate_data = climate_data
        self.resources = resources


    # Return environment information for the webpage.
    def get_environment_data(self):
        return {
            "terrain": self.terrain,
            "terrain_name": self.terrain_data["name"],
            "terrain_description": self.terrain_data["description"],
            "climate": self.climate,
            "climate_name": self.climate_data["name"],
            "climate_description": self.climate_data["description"],
            "resources": self.resources
        }


    # Give organisms a suitability score from 0.5 to 1.5.
    def habitat_suitability(self, organism):
        score = 1.0


        # Different traits are useful in different environments.
        if self.terrain == "forest":
            score = score + (organism.traits["camouflage"] - 50) / 200


        elif self.terrain == "desert":
            score = score + (organism.traits["heat_tolerance"] - 50) / 200


        else:
            score = score + (organism.traits["speed"] - 50) / 200


        # Heat tolerance matters more in hot climates.
        if self.climate == "arid":
            score = score + (organism.traits["heat_tolerance"] - 50) / 180


        elif self.climate == "tropical":
            score = score + (organism.traits["heat_tolerance"] - 40) / 220


        else:
            score = score + (organism.traits["heat_tolerance"] - 50) / 300


        if score < 0.5:
            score = 0.5


        if score > 1.5:
            score = 1.5


        return score
