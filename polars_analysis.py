
########################## Polars - Data Cleaning ##########################

print("######################## Polars - Data Cleaning #################################\n")

import polars as pl
import time

pl_start = time.time()

# read the dataframe from the csv file created earlier
UN = pl.read_csv(
    r"path of the file",
    separator=";",
    null_values=["NaN"]
    ).rename(
        {"UN Continental Region[1]": "UN Continental Region",
         "UN Statistical Subregion[1]": "UN Statistical Subregion",
         "Change":"Change[%]"
         })

print("United Nations Dataframe:")
print(UN)

# Check for Null values
print("\nRows of the dataframe with Null values:")
print(
    UN.filter( pl.any_horizontal( pl.all().is_null() ) )
)
# All the Null values are in the World row


# Replace the Null values assigned to the World row in the continental and statistical subregion columns
UN = UN.with_columns(
    pl.col("*").fill_null("World Total")
)


# It seems like there are some values in the last rows missing a '0' at the end of the value:
# checks if a value is missing a zero in the end, and if so, it adds the zero (3,45 -> 3,450)

# columns of the dataframe to check
population_col = ["Population(1 July 2022)", "Population(1 July 2023)"]

for col in population_col: # for each column
    # Create a temporary column with the lists of numbers composing the original (es. 278,830,529   ->   [278, 830, 529] )
    UN = UN.with_columns( population_split = pl.col(col).str.split(",") )
    
    # add the 0 only to the problematic numbers
    UN = UN.with_columns(
        pl.when(
            # verifies if there are less then 3 digits in every element of the list of numbers fro each row of the population_split column
            (pl.col("population_split").list.eval(pl.element().str.len_chars()).list.last() < 3) 
            & 
            # verifies for each number in the population column if it has a "," in the string, meaning the number is larger then 1 thousand
            (pl.col("population_split").list.len() > 1)
            )
            .then(pl.col(col) + "0") # add 0 if the criteria are met -> problematic number
            .otherwise(pl.col(col)), # otherwise keeps the same number
    )
    # remove the temporary column of the splitted numbers
    UN = UN.select(pl.all().exclude("population_split"))



# clean and transform column values
UN = UN.with_columns(
    pl.col("Population(1 July 2022)").str.replace_all(",", "").cast(pl.Int64), 
    pl.col("Population(1 July 2023)").str.replace_all(",", "").cast(pl.Int64),
    
    pl.col("Change[%]").str.replace("%",""),
)


# Clean and transform the Change column
UN = UN.with_columns(
    pl.when(pl.col("Change[%]").str.contains("−"))
    .then(pl.col("Change[%]").str.replace("−","").cast(pl.Float64) * -1)
    .otherwise(pl.col("Change[%]")).cast(pl.Float64)
)

# In the Country column some countries have [letter] after the name of the country, to remove them:
# remove all the text between square brackets (included)
UN = UN.with_columns(
    pl.col("Country").str.replace(r"\[.*?\]", "")
    # \[  and  \] indicates the literals for the square brackets
    # .*? indicates any sequence of characters 
)

print("Cleaned dataframe:")
print(UN)



pl_middle_1 = time.time()






########################## Polars - Exploratory Analysis ##########################

print("\n\n\n\n\n\n#################### Polars - Exploratory Analysis ####################\n")
input("Press Enter to continue...\n")

pl_middle_2 = time.time()

print("Total continental region population on 1 July 2023:")
print(
    UN
    .group_by("UN Continental Region")
    .agg(pl.col("Population(1 July 2023)").sum())
    .sort(pl.col("Population(1 July 2023)"), descending=True)
)


print("Subregions with highest and lowest population on 1 July 2023:")
print(UN
    .group_by("UN Statistical Subregion")
    .agg(pl.col("Population(1 July 2023)").sum())
    .sort(pl.col("Population(1 July 2023)"), descending=True)
)

print("Percenatge of the change in population in the continental regions from 1 July 2022 to 1 July 2023:")
print(UN
    .group_by("UN Continental Region")
    .agg(pl.col("Change[%]").sum())
    .sort(pl.col("Change[%]"), descending=True)
)

print("Subregions with largest increase and decrease in population in percentage:")
print(UN
    .group_by("UN Statistical Subregion")
    .agg(pl.col("Change[%]").sum())
    .sort(pl.col("Change[%]"), descending=True)
)

# Between July 2022 and July 2023 only 3 subregions diminuished in population:
# Micronesia, Polynesia and Eastern Europe


# in each continental region, the countries with the largest increase/decrease in population
continents = ["Asia", "Americas", "Africa", "Europe", "Oceania"]
for cont in continents:
    print(
        f"\n\nCountries in {cont} with the largest increase and decrease in population:\n ",
        UN
        .filter(pl.col("UN Continental Region") == cont)
        .sort(pl.col("Change[%]"), descending=True)
    )


# In Asia the most developed countries are also the ones with the biggest decrease in population in percentage
# In Africa only 2 countries diminuished in number, Mauritius and Saint Helena


# Countries with the largest difference in population
print("\nCountries with the largest difference in population:")
print(
    UN.with_columns(
        population_difference = pl.col("Population(1 July 2023)") - pl.col("Population(1 July 2022)")
    )
    .sort(pl.col("population_difference"), descending=True)
    .select(["Country","population_difference","Change[%]"])
)
# As a result of the war, in one year Ukraine has decreased in population of more than 3 milion people.  


# Percantage of countries per continental region with a decrease in population
print("\nPercentage of countries in each continent with a decrease in population:")
print(
    UN
    # Create dataframe with total amount of countries per Continental Region
    .group_by("UN Continental Region")
    .agg(pl.col("Change[%]").count().alias("Total Countries"))

    # Join a dataframe with the amount of countries per Continental Region that encountered a decrease in population
    .join(
        other = UN.group_by("UN Continental Region").agg(pl.col("Change[%]").filter(pl.col("Change[%]") < 0).count()),
        on = "UN Continental Region"
    )

    # remove the world total row 
    .filter(pl.col("UN Continental Region") != "World Total")

    # create column of the percentage of countries with a decrease in population
    .with_columns(
        (pl.col("Change[%]") / pl.col("Total Countries") * 100).alias("Percentage[%]").round(2)
    )

    # sort dataframe by percentage 
    .sort(pl.col("Percentage[%]"), descending=True)

    .rename({"Change[%]":"Countries with decrease"})
)


pl_end = time.time()







########################## Comparison of execution time ##########################

print("\n\n\n\n\n\n############## Comparison of execution time ############\n")
input("Press Enter to continue...\n")

# Comparison between pandas and polars

print("Data cleaning")
print("Polars: ", pl_middle_1 - pl_start)

print("\nExploratory Analysis")
print("Polars: ", pl_end - pl_middle_2)

print("\nTotal")
print("Polars: ", (pl_end - pl_middle_2) + (pl_middle_1 - pl_start))

