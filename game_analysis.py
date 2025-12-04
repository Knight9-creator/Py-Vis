import csv
import pandas as pd
import matplotlib.pyplot as plt

with open("game_sales.csv", 'r', newline="") as f:
    reader = csv.reader(f)
    header = next(reader)
    total = 0
    for row in reader: 
        title = row[1]
        platform = row[2]
        units_sold = int(row[4])
        total += units_sold
        print(f"{title} ({platform}) - Units sold: {units_sold}")
    print(f"Final Total of Products Sold: {total}")


df = pd.read_csv("game_sales.csv")
print(df.info())

df["Revenue"] = df["UnitsSold"] * df["Price"]
print(df.head(9))
total_revenue = df["Revenue"].sum()
print(f"Total revenue across all games: ${total_revenue:.2f}")


revenue_by_platform = df.groupby("Platform")['Revenue'].sum().sort_values(ascending=False)
print(revenue_by_platform)


units_by_title = df.groupby("Title")['UnitsSold'].sum().sort_values(ascending=False)
print(units_by_title)


revenue_by_platform.plot(kind="bar") 
plt.title("Total Revenue by PlatForm") 
plt.xlabel("Platform") 
plt.ylabel("Revenue ($)") 
plt.figure(figsize=(8, 5))
plt.show()

units_by_region = df.groupby("Region")["UnitsSold"].sum() 
units_by_region.plot(kind="bar")
plt.title("Total Units Sold by Region")
plt.xlabel("Region")
plt.ylabel("Units Sold")
plt.tight_layout()
plt.show()