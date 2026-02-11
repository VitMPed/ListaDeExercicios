import pulp
import time
import matplotlib.pyplot as plt


def main():


    # Parameters
    p = [4, 4.5, 5, 4.1, 2.4, 5.2, 3.7, 3.5, 3.2, 4.5, 2.3, 3.3, 3.8, 4.6, 3] # Instance with length of cars
    m = 2 # number of queues
    n = len(p)


    model = pulp.LpProblem("Car_Parking",pulp.LpMinimize)

    # Variables
    x = pulp.LpVariable.dicts("x",((j, k) for j in range(1, n + 1) for k in range(1, m + 1)),cat="Binary")
    Cmax = pulp.LpVariable("Cmax", lowBound=0)

    # Objective function
    model += Cmax

    # Constraints
    for j in range(1, n + 1):
        model += pulp.lpSum(x[(j, k)] for k in range(1, m + 1)) == 1 # Each job assigned to exactly one machine

    
    for k in range(1, m + 1):
        model += Cmax >= pulp.lpSum(p[j - 1] * x[(j, k)] for j in range(1, n + 1)) # Makespan definition

    # Defining the solver
    solver = pulp.GUROBI(msg=True) 

    # Measuring the computing time
    start_time = time.time()
    model.solve(solver)
    end_time = time.time()


    # Output
    print("\nAssignment model for car parking")
    print("Optimization status:", pulp.LpStatus[model.status])
    print("Maximum length occupied:", pulp.value(Cmax))

    print("\nCar assignments:")

    assignments = {k: [] for k in range(1, m + 1)}

    for j in range(1, n + 1):
        for k in range(1, m + 1):
            if pulp.value(x[(j, k)]) > 0.5:
                print(f"Car {j} → Side of the street {k} (length = {p[j - 1]})")
                assignments[k].append(j)

    print(f"\nSolution time: {end_time - start_time:.4f} s")


    # Gantt Chart
    generate_gantt_chart(assignments, p, m)


def generate_gantt_chart(assignments, p, m):

    fig, ax = plt.subplots()

    for machine in range(1, m + 1):
        current_time = 0
        for job in assignments[machine]:
            duration = p[job - 1]

            ax.barh(machine, duration, left=current_time)
            ax.text(
                current_time + duration / 2,
                machine,
                f"J{job}",
                ha="center",
                va="center"
            )

            current_time += duration

    ax.set_xlabel("Position (m)")
    ax.set_ylabel("Side of the street")
    ax.set_title("Parking scheme")
    ax.set_yticks(range(1, m + 1))
    ax.set_yticklabels([f"Side {k}" for k in range(1, m + 1)])

    plt.show()

main()