import random
import simpy
import statistics
import matplotlib.pyplot as plt

# --- Parameters ---
RANDOM_SEED = 42
SIM_TIME = 200         # simulation time (minutes)
ARRIVAL_RATE = 1.5     # average transaction arrivals per minute
SERVICE_TIME = 1.0     # average service duration (minutes)

# --- Metrics ---
wait_times = []
queue_lengths = []

def transaction(env, name, bank, service_time):
    """A single banking transaction process"""
    arrival = env.now
    with bank.request() as request:
        yield request
        wait = env.now - arrival
        wait_times.append(wait)
        yield env.timeout(random.expovariate(1.0 / service_time))

def transaction_generator(env, bank, arrival_rate, service_time):
    """Generate transactions over time"""
    i = 0
    while True:
        yield env.timeout(random.expovariate(arrival_rate))
        env.process(transaction(env, f"Transaction-{i}", bank, service_time))
        i += 1
        queue_lengths.append(len(bank.queue))

def simulate(num_servers, arrival_rate, service_time):
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    bank = simpy.Resource(env, capacity=num_servers)
    env.process(transaction_generator(env, bank, arrival_rate, service_time))
    env.run(until=SIM_TIME)

    avg_wait = statistics.mean(wait_times)
    throughput = len(wait_times) / SIM_TIME
    avg_queue = statistics.mean(queue_lengths)
    return avg_wait, throughput, avg_queue

# --- Experiments ---
configs = [
    # Simulate different user loads (arrival rates)
    ("Low User Load (Few Users)", 3, 0.5, 1.0),   # Light traffic
    ("Medium User Load", 3, 1.0, 1.0),            # Normal
    ("High User Load", 3, 1.5, 1.0),              # Busy
    ("Peak User Load", 3, 2.0, 1.0),              # Overloaded
    ("Optimized System (5 Servers)", 5, 2.0, 1.0) # Improved performance
]


results = []
for name, servers, rate, service in configs:
    wait_times.clear()
    queue_lengths.clear()
    avg_wait, throughput, avg_queue = simulate(servers, rate, service)
    results.append((name, avg_wait, throughput, avg_queue))

# --- Visualization ---
names = [r[0] for r in results]
waits = [r[1] for r in results]
throughputs = [r[2] for r in results]

plt.figure(figsize=(10, 5))
plt.bar(names, waits, color='orange')
plt.title("Average Waiting Time per Scenario")
plt.ylabel("Time (minutes)")
plt.xticks(rotation=15)
plt.show()

plt.figure(figsize=(10, 5))
plt.bar(names, throughputs, color='green')
plt.title("System Throughput per Scenario")
plt.ylabel("Transactions per Minute")
plt.xticks(rotation=15)
plt.show()

# Plot average queue length
queues = [r[3] for r in results]
plt.figure(figsize=(10, 5))
plt.bar(names, queues, color='skyblue')
plt.title("Average Queue Length per Scenario")
plt.ylabel("Queue Length (users)")
plt.xticks(rotation=15)
plt.show()

for r in results:
    print(f"{r[0]} → Avg Wait: {r[1]:.3f} min | Throughput: {r[2]:.2f}/min | Avg Queue: {r[3]:.2f}")
