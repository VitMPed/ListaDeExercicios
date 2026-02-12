The exercises are attached to this repository in accordance with the following instructions:

### Exercise 1:
This exercise consists of a production scheduling problem in which tasks have different release times and due dates. Additionally, the setup times between tasks are variable. 
That makes this problem analogous to the Traveling Salesman Problem with Time Windows.
A literature review on metaheuristic applications to this type of problem indicates that Iterated Local Search and Variable Neighborhood Search are the approaches with the highest number of occurrences, and they were therefore selected for this problem.

### Exercise 2:
In this second exercise, vehicles must be allocated on both sides of a street in such a way as to minimize the space used on that street. 
This makes the problem analogous to a production scheduling problem in parallel machine environments aimed at minimizing the makespan, which is a well-known problem.
The problem was modeled using the Assignment approach, in which a binary variable is defined and assigned the value 1 if task j is scheduled on machine k, and 0 otherwise.

### Exercise 3:
This code implements a discrete-event simulation using the SimPy library. The model represents a system with three service stages: order, preparation and pickup. Customers arrive according to stochastic interarrival times and are divided into three types, each of them with specific parameters that describe their behavior.
For each customer type, the parameters include mean interarrival time, average order service time, baseline preparation time, order complexity factor, pickup service time, and maximum patience limits for waiting in queues. In addition, global parameters specify the number of preparation attendants and a congestion factor, which increases preparation time when the preparation queue is long.
During the simulation, the program calculates key performance indicators such as waiting times in each queue, total time spent in the system, and the number of completed versus abandoned customers.
