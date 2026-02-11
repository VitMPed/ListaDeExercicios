import simpy
import random
import statistics

RANDOM_SEED = 42
SIM_TIME = 8 * 60  # minutes

random.seed(RANDOM_SEED)


# -----------------------------
# Model parameters
# -----------------------------
NUM_PREP_ATTENDANTS = 2
CONGESTION_FACTOR = 0.15  # sensitivity to queue congestion


CUSTOMER_TYPES = {
    "fast": {
        "interarrival_mean": 1.0,
        "order_service_mean": 0.5,
        "prep_base": 1.5,
        "complexity": 0.8,
        "pickup_service_mean": 0.3,
        "patience_order": 2.0,
        "patience_pickup": 1.5,
    },
    "medium": {
        "interarrival_mean": 2.0,
        "order_service_mean": 1.0,
        "prep_base": 2.5,
        "complexity": 1.0,
        "pickup_service_mean": 0.5,
        "patience_order": 4.0,
        "patience_pickup": 3.0,
    },
    "slow": {
        "interarrival_mean": 4.0,
        "order_service_mean": 1.8,
        "prep_base": 3.5,
        "complexity": 1.3,
        "pickup_service_mean": 0.8,
        "patience_order": 6.0,
        "patience_pickup": 5.0,
    },
}


# -----------------------------
# Statistics collector
# -----------------------------
class Stats:
    def __init__(self):
        self.order_waits = []
        self.prep_waits = []
        self.pickup_waits = []
        self.system_times = []

        self.completed = 0
        self.abandoned_order = 0
        self.abandoned_pickup = 0

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
# Café system
# -----------------------------
class Cafe:
    def __init__(self, env):
        self.order_counter = simpy.Resource(env, capacity=1)
        self.prep_station = simpy.Resource(env, capacity=NUM_PREP_ATTENDANTS)
        self.pickup_counter = simpy.Resource(env, capacity=1)


# -----------------------------
# Dynamic preparation time
# -----------------------------
def compute_prep_time(params, queue_length):
    base = params["prep_base"]
    complexity = params["complexity"]

    congestion_multiplier = 1 + CONGESTION_FACTOR * queue_length

    mean_time = base * complexity * congestion_multiplier

    return random.expovariate(1 / mean_time)


# -----------------------------
# Customer process
# -----------------------------
def customer(env, name, cust_type, cafe, stats):
    params = CUSTOMER_TYPES[cust_type]
    arrival = env.now

    # ---- Order queue ----
    with cafe.order_counter.request() as req:
        start = env.now
        result = yield req | env.timeout(params["patience_order"])

        if req not in result:
            stats.abandoned_order += 1
            return

        stats.order_waits.append(env.now - start)

        service = random.expovariate(1 / params["order_service_mean"])
        yield env.timeout(service)

    # ---- Preparation queue ----
    with cafe.prep_station.request() as req:
        start = env.now
        queue_len = len(cafe.prep_station.queue)

        yield req

        stats.prep_waits.append(env.now - start)

        prep_time = compute_prep_time(params, queue_len)
        yield env.timeout(prep_time)

    # ---- Pickup queue ----
    with cafe.pickup_counter.request() as req:
        start = env.now
        result = yield req | env.timeout(params["patience_pickup"])

        if req not in result:
            stats.abandoned_pickup += 1
            return

        stats.pickup_waits.append(env.now - start)

        service = random.expovariate(
            1 / params["pickup_service_mean"]
        )
        yield env.timeout(service)

    stats.system_times.append(env.now - arrival)
    stats.completed += 1


# -----------------------------
# Arrival generator
# -----------------------------
def arrival_generator(env, cust_type, cafe, stats):
    i = 0
    mean_interarrival = CUSTOMER_TYPES[cust_type]["interarrival_mean"]

    while True:
        interarrival = random.expovariate(1 / mean_interarrival)
        yield env.timeout(interarrival)

        i += 1
        env.process(customer(env, f"{cust_type}_{i}", cust_type, cafe, stats))


# -----------------------------
# Run simulation
# -----------------------------
def main():
    env = simpy.Environment()
    cafe = Cafe(env)
    stats = Stats()

    for cust_type in CUSTOMER_TYPES:
        env.process(arrival_generator(env, cust_type, cafe, stats))

    env.run(until=SIM_TIME)
    stats.report()


if __name__ == "__main__":
    main()
