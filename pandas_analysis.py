
########################## Pandas - Data Cleaning ##########################

print("######################## Pandas - Data Cleaning #################################\n")

import pandas as pd
import time

pd_start = time.time() # start of the pandas timer

# read the dataframe from the csv file created earlier
UN = pd.read_csv(
    r"path of the file",
    sep=";",
    na_values=["NaN"]
    ).rename(
        columns={"UN Continental Region[1]": "UN Continental Region",
                 "UN Statistical Subregion[1]": "UN Statistical Subregion",
                 "Change":"Change[%]"
                 })
print("United Nations Dataframe:")
print(UN)

# Check for Null values
print("\nRows of the dataframe with Null values:")
print(UN[UN.isnull().any(axis=1)])
# All the Null values are in the World row


# Replace the Null values assigned to the World row in the continental and statistical subregion columns
UN = UN.fillna("World Total") 

# It seems like there are some values in the last rows missing a '0' at the end of the value:
# checks if a value is missing a zero in the end, and if so, it adds the zero (3,45 -> 3,450)
def check_0(value):
    value_split = value.split(",")
    if( len( value_split[-1] ) < 3  and  len(value_split) > 1 ): # checks if a value is missing a '0', while avoiding possibile 2 or 1 digit numbers
        return value + "0"
    return value

# columns of the dataframe to check
population_col = ["Population(1 July 2022)", "Population(1 July 2023)"]

# apply the funciont to both columns
for col in population_col:
    UN[col] = UN[col].apply(check_0).str.replace(",", "").astype("Int64") 

# remove the '%' sign from the change column
UN["Change[%]"] = UN["Change[%]"].str.replace("%","")


# removes the special sign: '−' and returns a float value
def clear_sign(value):
    if("−" in value):
        return float(value.replace("−","")) * -1
    else:
        return float(value)

# apply the function to all the elements of the Change column
UN["Change[%]"] = UN["Change[%]"].apply(clear_sign)

# remove all the letters between brackets (included) from the countries strings
UN["Country"] = UN["Country"].str.replace(r"\[.*?\]", "", regex=True)
# \[  and  \] indicates the literals for the square brackets
# .*? indicates any sequence of characters 

print("\nCleaned dataframe:")
print(UN)


pd_middle_1 = time.time()






########################## Pandas - Exploratory Analysis ##########################

print("\n\n\n\n\n\n######################## Pandas - Exploratory Analysis #################################\n")
input("Press Enter to continue...\n")

pd_middle_2 = time.time()

print("Total continental region population on 1 July 2023:")
print(
    UN
    .groupby("UN Continental Region")["Population(1 July 2023)"]
    .sum()
    .sort_values(ascending=False)
)

# Total subregion population on 1 July 2023
subregions_total = (
    UN
    .groupby("UN Statistical Subregion")["Population(1 July 2023)"]
    .sum()
    .sort_values(ascending=False)
    )

print(
    "\nSubregions with highest population on 1 July 2023:\n",
    subregions_total.head(),
    "\n\nSubregions with lowest population on 1 July 2023:\n",
    subregions_total.tail()
)


print("\nPercenatge of the change in population in the continental regions from 1 July 2022 to 1 July 2023:")
print(
    UN.groupby("UN Continental Region")["Change[%]"]
    .sum()
    .sort_values(ascending=False)
)


print("Percenatge of the change in population in the subregions:")
subregions_change = (
    UN.groupby("UN Statistical Subregion")["Change[%]"]
    .sum()
    .sort_values(ascending=False)
    )
print(
    "\nSubregions with largest increase in population in percentage:\n",
    subregions_change.head(),
    "\n\nSubregions with largest decrease in population in percentage:\n",
    subregions_change.tail()
    )

# Between July 2022 and July 2023 only 3 subregions diminuished in population:
# Micronesia, Polynesia and Eastern Europe



# in each continental region, the countries with the largest increase/decrease in population
continents = ["Asia", "Americas", "Africa", "Europe", "Oceania"]
for cont in continents:
    cont_table = UN[UN["UN Continental Region"] == cont].sort_values(by="Change[%]",ascending=False).reset_index().drop("index", axis=1)
    print(
        f"\nCountries in {cont} with the largest increase in population:\n", 
        cont_table.head(),
        f"\n\nCountries in {cont} with the largest decrease in population:\n", 
        cont_table.tail()
    )
print()
# In Asia the most developed countries are also the ones with the biggest decrease in population in percentage
# In Africa only 2 countries diminuished in number, Mauritius and Saint Helena


# Countries with the largest difference in population
print("Countries with the largest difference in population:")
UN["population_difference"] = UN["Population(1 July 2023)"] - UN["Population(1 July 2022)"]
print(
    UN.sort_values(by = "population_difference",ascending=False),"\n"
)
print()
UN = UN.drop(columns=["population_difference"])

# As a result of the war, in one year Ukraine has decreased in population of more than 3 milion people.  



# Percentage of countries in each continent with a decrease in population
Total_countries = (
    UN
    .groupby("UN Continental Region")["Change[%]"]
    .count()
    .reset_index()
    .rename(columns={"Change[%]": "Total countries"})
    )

countries_with_decrease = (
    UN[UN["Change[%]"] < 0]
    .groupby("UN Continental Region")["Change[%]"]
    .count()
    .reset_index()
    .rename(columns={"Change[%]": "Countries with decrease"})
    )

cont_decrease = pd.merge(Total_countries, countries_with_decrease, on="UN Continental Region")
cont_decrease["Percentage[%]"] = cont_decrease["Countries with decrease"] / cont_decrease["Total countries"] * 100

print("Percentage of countries in each continent with a decrease in population:")
print(cont_decrease.sort_values(by = "Percentage[%]", ascending=False))




pd_end = time.time()






########################## Comparison of execution time ##########################

print("\n\n\n\n\n\n############## Comparison of execution time ############\n")
input("Press Enter to continue...\n")

# Comparison between pandas and polars

print("Data cleaning")
print("Pandas: ", pd_middle_1 - pd_start)

print("\nExploratory Analysis")
print("Pandas: ", pd_end - pd_middle_2)

print("\nTotal")
print("Pandas: ", (pd_end - pd_middle_2) + (pd_middle_1 - pd_start))

