import simpy
import random
import statistics

SIM_TIME = 8 * 60  # Simulation time (minutes)


# -----------------------------
# Parameters
# -----------------------------
NUM_PREP_ATTENDANTS = 2 # Number of atendants
CONGESTION_FACTOR = 0.15  # parameter that controls how much the preparation time increases when the preparation queue gets crowded


CUSTOMER_TYPES = {
    "fast": {
        "interarrival_mean": 1.0, # average time between arrivals of customers
        "order_service_mean": 0.5, # average time to place an order
        "prep_base": 1.5, # average time to prepare a standard order
        "complexity": 0.8, # multiplier that represents how complicated the order is
        "pickup_service_mean": 0.3, # average time to hand the order to the customer at pickup
        "patience_order": 3.0, # Maximum time a customer is willing to wait in the order queue
        "patience_pickup": 10.0, # Maximum time a customer is willing to wait in the pickup queue
    },
    "medium": {
        "interarrival_mean": 2.0,
        "order_service_mean": 1.0,
        "prep_base": 2.5,
        "complexity": 1.0,
        "pickup_service_mean": 0.5,
        "patience_order": 4.0,
        "patience_pickup": 12.0,
    },
    "slow": {
        "interarrival_mean": 4.0,
        "order_service_mean": 1.8,
        "prep_base": 3.5,
        "complexity": 1.3,
        "pickup_service_mean": 0.8,
        "patience_order": 6.0,
        "patience_pickup": 15.0,
    },
}


# -----------------------------
# Statistics collector
# -----------------------------
class Stats:
    def __init__(self):
        self.order_waits = [] # list to store order queue waiting times
        self.prep_waits = [] # waiting time in the preparation queue
        self.pickup_waits = [] # waiting time in the pickup queue
        self.system_times = [] # total time each completed customer spends in the system

        self.completed = 0 # Counts customers who finish the full process
        self.abandoned_order = 0 # Counts customers who abandon the order queue
        self.abandoned_pickup = 0 # Counts customers who abandon the pickup queue

    def report(self):
        print("\n=== Simulation Results ===")
        print(f"Completed: {self.completed}")
        print(f"Abandoned (order): {self.abandoned_order}")
        print(f"Abandoned (pickup): {self.abandoned_pickup}")

        if self.order_waits:
            print(f"Avg order wait: {statistics.mean(self.order_waits):.2f}")
        if self.prep_waits:
            print(f"Avg prep wait: {statistics.mean(self.prep_waits):.2f}")
        if self.pickup_waits:
            print(f"Avg pickup wait: {statistics.mean(self.pickup_waits):.2f}")
        if self.system_times:
            print(f"Avg total time: {statistics.mean(self.system_times):.2f}")


# -----------------------------
# Café
# -----------------------------
class Cafe:
    def __init__(self, env):
        self.order_counter = simpy.Resource(env, capacity=1) # Creates a single order counter resource
        self.prep_station = simpy.Resource(env, capacity=NUM_PREP_ATTENDANTS) # Creates preparation attendants resource
        self.pickup_counter = simpy.Resource(env, capacity=1) # Creates a single pickup counter resource


# -----------------------------
# Dynamic preparation time
# -----------------------------
def compute_prep_time(params, queue_length):
    base = params["prep_base"]
    complexity = params["complexity"]

    congestion_multiplier = 1 + CONGESTION_FACTOR * queue_length # Calculates slowdown due to congestion
    mean_time = base * complexity * congestion_multiplier # adjusted average prep time

    return random.expovariate(1 / mean_time)


# -----------------------------
# Customer process
# -----------------------------
def customer(env, name, cust_type, cafe, stats):
    params = CUSTOMER_TYPES[cust_type]
    arrival = env.now # Records customer arrival time

    # ---- Order queue ----
    with cafe.order_counter.request() as req:
        start = env.now # Records time when waiting begins
        result = yield req | env.timeout(params["patience_order"])

        if req not in result:
            stats.abandoned_order += 1
            return

        stats.order_waits.append(env.now - start)

        service = random.expovariate(1 / params["order_service_mean"])
        yield env.timeout(service) # Simulates order processing

    # ---- Preparation queue ----
    with cafe.prep_station.request() as req:
        start = env.now # Records prep waiting start
        queue_len = len(cafe.prep_station.queue) # Measures current prep queue length

        yield req # Waits for prep service

        stats.prep_waits.append(env.now - start) # Records prep waiting time

        prep_time = compute_prep_time(params, queue_len) # Calculates dynamic prep time
        yield env.timeout(prep_time) # Simulates preparation

    # ---- Pickup queue ----
    with cafe.pickup_counter.request() as req:
        start = env.now # Records pickup waiting start
        result = yield req | env.timeout(params["patience_pickup"])

        if req not in result:
            stats.abandoned_pickup += 1
            return

        stats.pickup_waits.append(env.now - start) # Records pickup waiting time

        service = random.expovariate(
            1 / params["pickup_service_mean"]
        )
        yield env.timeout(service) # Simulates pickup processing

    stats.system_times.append(env.now - arrival) # Records total time in system
    stats.completed += 1 # Increments completed customer count


# -----------------------------
# Arrival generator
# -----------------------------
def arrival_generator(env, cust_type, cafe, stats): # Generates customers of one type
    i = 0 # Initializes customer counter
    mean_interarrival = CUSTOMER_TYPES[cust_type]["interarrival_mean"] # Average interarrival time

    while True:
        interarrival = random.expovariate(1 / mean_interarrival) # Samples time to next arrival
        yield env.timeout(interarrival) # Waits until next arrival

        i += 1 # Increments customer
        env.process(customer(env, f"{cust_type}_{i}", cust_type, cafe, stats)) # Starts a new customer process


# -----------------------------
# Run simulation
# -----------------------------
def main():
    env = simpy.Environment() # Creates simulation environment
    cafe = Cafe(env) # Initializes Café system
    stats = Stats() # Initializes statistics collector

    for cust_type in CUSTOMER_TYPES:
        env.process(arrival_generator(env, cust_type, cafe, stats)) # starts arrival processes

    env.run(until=SIM_TIME) # Runs simulation for set time
    stats.report() # Prints results


main()

