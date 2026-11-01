import random
from simulation.organism import Organism




# This class controls the whole ecosystem.
class Simulation:


    # Create the simulation.
    def __init__(self, environment, choices, organism_data):
        self.environment = environment
        self.choices = choices
        self.organism_data = organism_data


        self.generation = 0
        self.step_number = 0
        self.next_id = 1
        self.organisms = []


        # Save the starting values for Reset.
        self.original_resources = dict(environment.resources)
        self.original_choices = []


        for choice in choices:
            self.original_choices.append(dict(choice))


        self.create_population()


    # Create 10 organisms for each selected species.
    def create_population(self):
        for choice in self.choices:
            species = choice["type"]
            species_data = self.organism_data[species]


            for number in range(10):
                organism = Organism(
                    self.next_id,
                    species,
                    species_data,
                    choice["hunger"],
                    choice["thirst"],
                    choice["energy"],
                    choice["traits"]
                )


                self.organisms.append(organism)
                self.next_id = self.next_id + 1


    # Find organisms close to another organism.
    def nearby(self, organism, distance):
        nearby_organisms = []


        for other in self.organisms:
            if other.id != organism.id and other.alive:
                dx = organism.x - other.x
                dy = organism.y - other.y
                actual_distance = (dx * dx + dy * dy) ** 0.5


                if actual_distance <= distance:
                    nearby_organisms.append(other)


        return nearby_organisms


    # Run one step of the simulation.
    def step(self):
        self.step_number = self.step_number + 1


        for organism in list(self.organisms):
            if organism.alive:


                nearby_organisms = self.nearby(organism, 55)


                prey = []
                competitors = []


                for other in nearby_organisms:


                    if (
                        organism.species_data["predator"]
                        and other.species_data["prey"]
                        and other.species != organism.species
                    ):
                        prey.append(other)


                    if other.species == organism.species:
                        competitors.append(other)


                action = organism.choose_action(
                    self.environment,
                    prey,
                    competitors
                )


                organism.perform_action(action, self.environment)
                organism.age()


        self.process_predation()
        self.process_competition()


        babies = self.process_reproduction()


        for baby in babies:
            self.organisms.append(baby)


        # Remove dead organisms.
        living = []


        for organism in self.organisms:
            if organism.alive:
                living.append(organism)


        self.organisms = living


        # Every 20 steps is one generation.
        if self.step_number % 20 == 0:
            self.generation = self.generation + 1
            self.natural_selection()


    # Predators can catch nearby prey.
    def process_predation(self):
        for predator in self.organisms:


            if predator.alive and predator.species_data["predator"]:


                prey_list = []


                for prey in self.nearby(predator, 30):
                    if (
                        prey.alive
                        and prey.species_data["prey"]
                        and prey.species != predator.species
                    ):
                        prey_list.append(prey)


                if len(prey_list) > 0:


                    prey = random.choice(prey_list)


                    chance = (
                        0.25
                        + predator.traits["speed"] / 250
                        - prey.traits["speed"] / 400
                    )


                    if random.random() < chance:
                        prey.alive = False
                        predator.energy = min(100, predator.energy + 30)


    # Nearby organisms compete for resources.
    def process_competition(self):
        for organism in self.organisms:


            if organism.alive:


                same_species = []


                for other in self.nearby(organism, 35):
                    if other.species == organism.species:
                        same_species.append(other)


                if len(same_species) >= 3:
                    organism.energy = organism.energy - 1.5


                    # Disease resistance reduces the competition penalty.
                    organism.energy = (
                        organism.energy
                        + organism.traits["disease_resistance"] / 200
                    )


    # Find healthy pairs and create offspring.
    def process_reproduction(self):
        babies = []
        used_pairs = []


        for organism in self.organisms:


            if organism.alive:
                if (
                    organism.energy >= 75
                    and organism.hunger <= 30
                    and organism.thirst <= 30
                ):


                    partners = []


                    for other in self.nearby(organism, 25):
                        if (
                            other.species == organism.species
                            and other.energy >= 75
                            and other.hunger <= 30
                            and other.thirst <= 30
                        ):
                            partners.append(other)


                    if len(partners) > 0:


                        partner = random.choice(partners)


                        first_id = organism.id
                        second_id = partner.id


                        if first_id > second_id:
                            first_id, second_id = second_id, first_id


                        pair = (first_id, second_id)


                        if pair not in used_pairs:
                            used_pairs.append(pair)


        # Only create a few babies each step.
        for pair in used_pairs[:3]:


            first = self.find_organism(pair[0])
            second = self.find_organism(pair[1])


            if first is not None and second is not None:
                if first.alive and second.alive:


                    baby = first.reproduce(second, self.next_id)
                    babies.append(baby)
                    self.next_id = self.next_id + 1


        return babies


    # Find an organism using its ID.
    def find_organism(self, organism_id):
        for organism in self.organisms:
            if organism.id == organism_id:
                return organism


        return None


    # Environmental conditions affect survival every generation.
    def natural_selection(self):
        for organism in self.organisms:


            score = self.environment.habitat_suitability(organism)


            if score < 0.9:
                organism.energy = organism.energy - 5


            elif score > 1.1:
                organism.energy = min(100, organism.energy + 3)


            if organism.energy <= 0:
                organism.alive = False


        living = []


        for organism in self.organisms:
            if organism.alive:
                living.append(organism)


        self.organisms = living


    # Return to the original settings.
    def reset(self):
        self.generation = 0
        self.step_number = 0
        self.next_id = 1
        self.organisms = []
        self.environment.resources = dict(self.original_resources)


        self.create_population()


    # Send all information to the webpage.
    def get_state(self):
        populations = {}


        for organism in self.organisms:
            if organism.species not in populations:
                populations[organism.species] = 0


            populations[organism.species] = (
                populations[organism.species] + 1
            )


        organism_data = []


        for organism in self.organisms:
            organism_data.append(organism.to_dict())


        return {
            "environment": self.environment.get_environment_data(),
            "generation": self.generation,
            "step": self.step_number,
            "population": populations,
            "organisms": organism_data
        }
