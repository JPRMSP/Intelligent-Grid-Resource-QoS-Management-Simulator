import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Intelligent Grid Resource & QoS Simulator", layout="wide")

st.title("⚙️ Intelligent Grid Resource & QoS Management Simulator")
st.markdown("""
This simulator demonstrates **advanced Grid Resource Management** concepts:
- 🧠 Predictive & Economic Scheduling  
- ⚡ Dynamic QoS (Latency, Throughput, Reliability)  
- 🤝 SLA Negotiation & Resource Brokering  
- 💰 Economic Resource Allocation  
""")

# Sidebar Controls
st.sidebar.header("Simulation Settings")
num_nodes = st.sidebar.slider("Number of Grid Nodes", 3, 10, 5)
num_tasks = st.sidebar.slider("Number of Tasks", 3, 15, 8)
algorithm = st.sidebar.selectbox("Scheduling Algorithm", 
                                 ["Round Robin", "Shortest Job First", "Economic", "Predictive QoS-Aware"])
simulate = st.sidebar.button("🚀 Run Simulation")

# Grid Setup
def create_nodes(n):
    return [{
        "id": f"Node-{i+1}",
        "CPU": random.randint(2, 10),
        "Memory": random.randint(8, 32),
        "Bandwidth": random.randint(50, 150),
        "Reliability": round(random.uniform(0.85, 0.99), 2),
        "Cost": round(random.uniform(0.5, 3.0), 2),
        "Load": 0
    } for i in range(n)]

def create_tasks(n):
    return [{
        "id": f"Task-{i+1}",
        "Workload": random.randint(3, 10),
        "Priority": random.choice(["Low", "Medium", "High"]),
        "SLA_Time": random.randint(3, 9)
    } for i in range(n)]

# Scheduling Algorithms
def round_robin(nodes, tasks):
    assignments = []
    for i, task in enumerate(tasks):
        node = nodes[i % len(nodes)]
        node["Load"] += task["Workload"]
        assignments.append((task["id"], node["id"]))
    return assignments

def shortest_job_first(nodes, tasks):
    tasks_sorted = sorted(tasks, key=lambda x: x["Workload"])
    nodes_sorted = sorted(nodes, key=lambda x: x["Load"])
    assignments = []
    for i, task in enumerate(tasks_sorted):
        node = nodes_sorted[i % len(nodes)]
        node["Load"] += task["Workload"]
        assignments.append((task["id"], node["id"]))
    return assignments

def economic(nodes, tasks):
    nodes_sorted = sorted(nodes, key=lambda x: x["Cost"])
    assignments = []
    for i, task in enumerate(tasks):
        node = nodes_sorted[i % len(nodes)]
        node["Load"] += task["Workload"]
        assignments.append((task["id"], node["id"]))
    return assignments

def predictive_qos(nodes, tasks):
    # Predictive heuristic: Select node with best QoS score (bandwidth + reliability - load)
    assignments = []
    for task in tasks:
        for node in nodes:
            # Simulate dynamic fluctuation of resources
            node["CPU"] = max(1, node["CPU"] + random.choice([-1, 0, 1]))
            node["Bandwidth"] = max(10, node["Bandwidth"] + random.choice([-10, 0, 10]))
            node["Reliability"] = max(0.7, min(0.99, node["Reliability"] + random.choice([-0.01, 0, 0.01])))

        scored = sorted(nodes, key=lambda x: (x["Bandwidth"]*x["Reliability"] - x["Load"]), reverse=True)
        node = scored[0]
        node["Load"] += task["Workload"]
        assignments.append((task["id"], node["id"]))
    return assignments

# QoS and SLA Evaluation
def evaluate(assignments, tasks, nodes):
    results = []
    for task_id, node_id in assignments:
        node = next(n for n in nodes if n["id"] == node_id)
        task = next(t for t in tasks if t["id"] == task_id)

        latency = round(random.uniform(0.1, 1.5) * (10 / node["Bandwidth"]), 3)
        throughput = round(node["Bandwidth"] / (task["Workload"] + 1), 2)
        exec_time = task["Workload"] / node["CPU"]
        reliability = node["Reliability"]

        qos_score = round(((throughput * reliability) / (1 + latency)), 3)
        sla_met = exec_time <= task["SLA_Time"]

        results.append({
            "Task": task_id,
            "Node": node_id,
            "Latency(s)": latency,
            "Throughput(MB/s)": throughput,
            "Reliability": reliability,
            "QoS Score": qos_score,
            "Exec Time": round(exec_time, 2),
            "SLA Time": task["SLA_Time"],
            "SLA Met": "✅" if sla_met else "❌"
        })
    return results

if simulate:
    st.subheader("🧮 Initializing Grid Environment...")
    nodes = create_nodes(num_nodes)
    tasks = create_tasks(num_tasks)

    st.write("### 🖥️ Grid Nodes (Before Scheduling)")
    st.dataframe(pd.DataFrame(nodes))

    st.write("### 📦 Tasks")
    st.dataframe(pd.DataFrame(tasks))

    st.subheader("🔁 Scheduling Simulation")
    with st.spinner("Allocating resources across the grid..."):
        time.sleep(2)
        if algorithm == "Round Robin":
            assign = round_robin(nodes, tasks)
        elif algorithm == "Shortest Job First":
            assign = shortest_job_first(nodes, tasks)
        elif algorithm == "Economic":
            assign = economic(nodes, tasks)
        else:
            assign = predictive_qos(nodes, tasks)

    st.success(f"✅ {algorithm} Scheduling Completed!")

    st.write("### 📊 Simulation Results")
    results = evaluate(assign, tasks, nodes)
    df_results = pd.DataFrame(results)
    st.dataframe(df_results)

    sla_success = sum(1 for r in results if r["SLA Met"] == "✅")
    avg_qos = sum(r["QoS Score"] for r in results) / len(results)
    st.metric("SLA Success Rate", f"{(sla_success/len(results))*100:.1f}%")
    st.metric("Average QoS Score", f"{avg_qos:.3f}")

    st.write("### ⚡ QoS Metrics Visualization")
    st.bar_chart(df_results.set_index("Task")[["QoS Score", "Throughput(MB/s)", "Latency(s)"]])

    st.write("### 💰 Economic Cost Overview")
    total_cost = sum(next(n for n in nodes if n["id"] == r["Node"])["Cost"] for r in results)
    st.metric("Total Virtual Cost", f"${total_cost:.2f}")

    st.markdown("""
    **Interpretation:**
    - Higher QoS → Better resource utilization and SLA compliance.  
    - Predictive QoS-Aware scheduling dynamically adapts to node fluctuations.  
    - Economic scheduling minimizes cost but may risk SLA breaches.  
    """)
else:
    st.info("👈 Adjust parameters and click 'Run Simulation' to visualize intelligent grid resource management.")
