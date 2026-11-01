import random
import math




# One Organism class is reused for every species.
class Organism:


    # Create one organism.
    def __init__(
        self, organism_id, species, species_data,
        hunger, thirst, energy, traits=None,
        x=None, y=None, generation=0
    ):
        self.id = organism_id
        self.species = species
        self.species_data = species_data


        self.hunger = float(hunger)
        self.thirst = float(thirst)
        self.energy = float(energy)


        self.generation = generation


        # Create four traits if the user did not provide them.
        if traits is None:
            self.traits = {}
            self.traits["speed"] = random.randint(30, 70)
            self.traits["camouflage"] = random.randint(30, 70)
            self.traits["heat_tolerance"] = random.randint(30, 70)
            self.traits["disease_resistance"] = random.randint(30, 70)
        else:
            self.traits = {}
            self.traits["speed"] = int(traits["speed"])
            self.traits["camouflage"] = int(traits["camouflage"])
            self.traits["heat_tolerance"] = int(traits["heat_tolerance"])
            self.traits["disease_resistance"] = int(traits["disease_resistance"])


        # Give the organism a random starting position.
        if x is None:
            self.x = random.randint(20, 680)
        else:
            self.x = x


        if y is None:
            self.y = random.randint(20, 380)
        else:
            self.y = y


        self.alive = True
        self.last_decision = "moving"


    # Calculate movement speed from the speed trait.
    def movement_speed(self):
        return self.species_data["base_speed"] * (
            0.6 + self.traits["speed"] / 100
        )


    # Choose one of six possible actions.
    def choose_action(self, environment, prey, competitors):


        # Decision 1: drink.
        if self.thirst >= 70 and environment.resources["water"] > 0:
            self.last_decision = "drinking"
            return "drink"


        # Decision 2: hunt.
        if (
            self.species_data["predator"]
            and len(prey) > 0
            and self.hunger >= 45
        ):
            self.last_decision = "hunting"
            return "hunt"


        # Decision 3: eat.
        if self.hunger >= 60 and environment.resources["food"] > 0:
            self.last_decision = "eating"
            return "eat"


        # Decision 4: avoid nearby competitors.
        if self.energy <= 25 and len(competitors) > 0:
            self.last_decision = "avoiding"
            return "avoid"


        # Decision 5: reproduce when healthy.
        if (
            self.energy >= 75
            and self.hunger <= 30
            and self.thirst <= 30
        ):
            self.last_decision = "reproducing"
            return "reproduce"


        # Decision 6: move when no other action is needed.
        self.last_decision = "moving"
        return "move"


    # Move in a random direction.
    def move(self):
        angle = random.uniform(0, 2 * math.pi)


        self.x = self.x + self.movement_speed() * 0.45 * math.cos(angle)
        self.y = self.y + self.movement_speed() * 0.45 * math.sin(angle)


        # Keep the organism inside the canvas.
        if self.x < 10:
            self.x = 10
        if self.x > 690:
            self.x = 690


        if self.y < 10:
            self.y = 10
        if self.y > 390:
            self.y = 390


        self.energy = self.energy - 0.5


    # Perform the chosen action.
    def perform_action(self, action, environment):


        if action == "drink":
            self.thirst = max(0, self.thirst - 25)
            environment.resources["water"] = environment.resources["water"] - 1
            self.energy = self.energy - 0.2


        elif action == "eat":
            self.hunger = max(0, self.hunger - 30)
            environment.resources["food"] = environment.resources["food"] - 1
            self.energy = min(100, self.energy + 12)


        elif action == "hunt":
            self.energy = self.energy - 2


        elif action == "avoid":
            self.move()


        elif action == "move":
            self.move()


    # Update internal conditions over time.
    def age(self):
        self.hunger = min(100, self.hunger + 3)
        self.thirst = min(100, self.thirst + 3)
        self.energy = max(0, self.energy - 0.8)


        if self.energy <= 0:
            self.alive = False


        if self.hunger >= 100:
            self.alive = False


        if self.thirst >= 100:
            self.alive = False


    # Create an offspring using traits from both parents.
    def reproduce(self, partner, new_id):


        child_traits = {}


        # There are four inherited traits.
        trait_names = [
            "speed",
            "camouflage",
            "heat_tolerance",
            "disease_resistance"
        ]


        for trait in trait_names:


            # The child receives the value from one parent.
            if random.randint(0, 1) == 0:
                value = self.traits[trait]
            else:
                value = partner.traits[trait]


            # Ten percent chance of mutation.
            if random.random() < 0.10:
                value = value + random.choice([-10, -5, 5, 10])


            if value < 0:
                value = 0


            if value > 100:
                value = 100


            child_traits[trait] = value


        # Create the child.
        child = Organism(
            new_id,
            self.species,
            self.species_data,
            35,
            35,
            70,
            child_traits,
            self.x + random.randint(-15, 15),
            self.y + random.randint(-15, 15),
            max(self.generation, partner.generation) + 1
        )


        self.energy = self.energy - 20
        partner.energy = partner.energy - 20


        return child


    # Convert the organism into simple data for JavaScript.
    def to_dict(self):
        return {
            "id": self.id,
            "species": self.species,
            "species_name": self.species_data["name"],
            "role": self.species_data["role"],
            "color": self.species_data["color"],
            "x": round(self.x, 1),
            "y": round(self.y, 1),
            "hunger": round(self.hunger, 1),
            "thirst": round(self.thirst, 1),
            "energy": round(self.energy, 1),
            "traits": self.traits,
            "generation": self.generation,
            "decision": self.last_decision
        }
