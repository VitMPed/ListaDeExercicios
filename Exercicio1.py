import math
import random
import matplotlib.pyplot as plt
import time


# -----------------------------
# Parameters
# -----------------------------

# Setup times (from the job in line i to the job in column j)
setup = [
 [0, 7, 2, 9, 5, 1, 8, 6, 3, 10],
 [4, 0, 6, 2, 8, 9, 1, 5, 7, 3],
 [9, 3, 0, 7, 1, 4, 6, 10, 2, 8],
 [5, 8, 1, 0, 6, 2, 9, 3, 10, 4],
 [7, 2, 10, 4, 0, 8, 3, 1, 6, 9],
 [1, 6, 5, 8, 3, 0, 2, 9, 4, 7],
 [8, 9, 3, 1, 7, 5, 0, 4, 2, 6],
 [2, 1, 8, 6, 9, 3, 4, 0, 5, 7],
 [6, 5, 4, 3, 2, 10, 7, 8, 0, 1],
 [3, 4, 7, 10, 8, 6, 5, 2, 9, 0]
]

# Processing times
processing = [12, 15, 10, 18, 14, 11, 19, 20, 14, 10]

# Time windows
release = [15, 50, 60, 40, 10, 20, 80, 0, 30, 20 ]
deadline = [200, 150, 170, 180, 195, 300, 110, 250, 100, 220]

n = len(processing) # Calculate the number of jobs inserted

# -----------------------------
# Schedule evaluation
# -----------------------------
def evaluate(sequence):
    time = 0
    prev = None
    schedule = []

    for job in sequence:
        if prev is not None:
            time += setup[prev][job]

        start = max(time, release[job])

        if start + processing[job] > deadline[job]:
            return math.inf, None

        finish = start + processing[job]
        schedule.append((job, start, finish))

        time = finish
        prev = job

    return time, schedule


# -----------------------------
# Neighborhood operators
# -----------------------------
def swap(seq, i, j):
    new_seq = seq[:]
    new_seq[i], new_seq[j] = new_seq[j], new_seq[i]
    return new_seq


def insert(seq, i, j):
    new_seq = seq[:]
    job = new_seq.pop(i)
    new_seq.insert(j, job)
    return new_seq


# -----------------------------
# Variable Neighborhood Search
# -----------------------------
def vns(initial_seq):
    best = initial_seq[:]
    best_cost, _ = evaluate(best)

    improved = True
    while improved:
        improved = False

        # Swap neighborhood
        for i in range(n):
            for j in range(i + 1, n):
                cand = swap(best, i, j)
                cost, _ = evaluate(cand)

                if cost < best_cost:
                    best, best_cost = cand, cost
                    improved = True

        # Insert neighborhood
        for i in range(n):
            for j in range(n):
                if i != j:
                    cand = insert(best, i, j)
                    cost, _ = evaluate(cand)

                    if cost < best_cost:
                        best, best_cost = cand, cost
                        improved = True

    return best, best_cost


# -----------------------------
# Iterated Local Search
# -----------------------------

def perturb(seq, strength=1):
    new_seq = seq[:]

    # stronger perturbation as iter grows
    for _ in range(strength):
        i, j = random.sample(range(len(seq)), 2)
        new_seq[i], new_seq[j] = new_seq[j], new_seq[i]

    return new_seq


def ils(maxIter=50):

    # Step 1: initial solution
    s = list(range(n))
    random.shuffle(s)

    s_best, f_best = vns(s)

    iter = 0

    while iter < maxIter:

        # Step 2: perturbation strength grows with iter
        s_prime = perturb(s_best, strength=iter + 1)

        # Step 3: local search
        s_double, f_double = vns(s_prime)

        # Step 4: acceptance criterion
        if f_double < f_best:
            s_best = s_double
            f_best = f_double
            iter = 0   # reset counter
        else:
            iter += 1

    return s_best, f_best



# -----------------------------
# Gantt chart
# -----------------------------

def plot_gantt(schedule, makespan):
    colors = [
        "red", "blue", "green", "orange", "purple",
        "cyan", "magenta", "yellow", "brown", "pink"
    ]

    fig, ax = plt.subplots(figsize=(10, 2))

    plt.subplots_adjust(bottom=0.35)

    for i, (job, start, finish) in enumerate(schedule):
        duration = finish - start

        ax.barh(
            y=0,
            width=duration,
            left=start,
            color=colors[i % len(colors)],
            edgecolor="black"
        )

        ax.text(
            start + duration / 2,
            0,
            f"Job {job}",
            ha="center",
            va="center",
            color="white",
            fontsize=9
        )
        
    ax.set_xlim(left=0)
    ax.set_yticks([])
    ax.set_xlabel("Time")
    ax.set_title("Single-Machine Gantt Chart")

    #Show Cmax in the chart area
    fig.text(
        0.5, 0.05,
        f"Cmax = {makespan}",
        ha="center",
        fontsize=12,
        fontweight="bold"
    )

    plt.show()


# -----------------------------
# Run algorithm
# -----------------------------
start_time = time.perf_counter()

best_seq, best_cost = ils()
cost, schedule = evaluate(best_seq)

end_time = time.perf_counter()
runtime = end_time - start_time

# -----------------------------
# Print computing time
# -----------------------------
print(f"\nComputing time: {runtime:.6f} seconds")

# -----------------------------
# Feasibility check
# -----------------------------
if not math.isfinite(cost) or schedule is None:
    print("Unfeasible Solution")

else:
    print("Best sequence:", best_seq)
    print("Cmax =", cost)

    print("\nDetailed schedule:")
    for job, start, finish in schedule:
        print(f"Job {job}: start={start}, finish={finish}")

    plot_gantt(schedule, cost)






