import json
import pandas as pd

rows = []

with open("benchmarks/results.jsonl") as f:
    for line in f:
        rows.append(json.loads(line))

df = pd.DataFrame(rows)

print("\nAction Distribution")
print("-------------------")
print(df.groupby("action").size())

print("\Model Distribution")
print("-------------------")
print(df.groupby("model").size())

print("\nAverage Latency")
print("-------------------")
print(round(df["latency"].mean(), 2))

print("\nLatency By Action")
print("-------------------")
print(
    df.groupby("action")["latency"]
      .mean()
      .round(2)
)