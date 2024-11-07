# Pandas-vs-Polars-Analysis
A comparison between the pandas and polars python libraries in data cleaning and exploratory analysis of a dataset.  
The dataset used was scraped with the BeautifulSoup library from the [wikipedia page](https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations))
describing the population of the countries in the United Nations between the 1st July 2022 and the 1st July 2023.  


# Index
- [Web scraping](#web-scraping)  
- [Data Cleaning](#data-cleaning)
- [Exploratory Analysis](#exploratory-analysis)  
- [Execution Times](#execution-times)

# Web scraping
The first step is to extract the dataframe informations through web scraping tools like the BeautifulSoup library:  
```
# url of the wikipedia page 
url = "https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"

# page of the url
page = requests.get(url)
soup = BeautifulSoup(page.text, "html.parser")

# get the first list of the table type
table = soup.find_all('table')[0]

# get the headers in the table
column_names_raw = table.find_all('th')

# get the column names of the table
column_names = [title.text.strip() for title in column_names_raw]
```  


Then utilizing pandas it is possible to create the dataframe and save it in a csv file:  
```
import pandas as pd

# create datafrme with the column names found
df = pd.DataFrame(columns = column_names)

# get the data of all the table rows 
columns_data = table.find_all('tr')

# for each row in all the rows of the table
for row in columns_data[1:]: # exclude first empty row
    row_data = row.find_all('td') # get all the data values of the row
    individual_raw_data = [data.text.strip() for data in row_data] # get the single values from the data of the row, 'strip' to clean the values

    length = len(df)
    df.loc[length] = individual_raw_data # append each row of data at the maximum length of the df up to that point

# saves the file as 'filename' in the 'path' specified
df.to_csv(r'path\filename', index=False, sep=";")
```

This is how the dataframe looks:
```
┌─────────────────────────────────┬─────────────────────────┬─────────────────────────┬───────────┬───────────────────────┬──────────────────────────┐
│ Country                         ┆ Population(1 July 2022) ┆ Population(1 July 2023) ┆ Change[%] ┆ UN Continental Region ┆ UN Statistical Subregion │
│ ---                             ┆ ---                     ┆ ---                     ┆ ---       ┆ ---                   ┆ ---                      │
│ str                             ┆ str                     ┆ str                     ┆ str       ┆ str                   ┆ str                      │
╞═════════════════════════════════╪═════════════════════════╪═════════════════════════╪═══════════╪═══════════════════════╪══════════════════════════╡
│ World                           ┆ 8,021,407,192           ┆ 8,091,734,930           ┆ +0.88%    ┆ null                  ┆ null                     │
│ India                           ┆ 1,425,423,212           ┆ 1,438,069,596           ┆ +0.89%    ┆ Asia                  ┆ Southern Asia            │
│ China[a]                        ┆ 1,425,179,569           ┆ 1,422,584,933           ┆ −0.18%    ┆ Asia                  ┆ Eastern Asia             │
│ United States                   ┆ 341,534,046             ┆ 343,477,335             ┆ +0.57%    ┆ Americas              ┆ Northern America         │
│ Indonesia                       ┆ 278,830,529             ┆ 281,190,067             ┆ +0.85%    ┆ Asia                  ┆ South-eastern Asia       │
│ …                               ┆ …                       ┆ …                       ┆ …         ┆ …                     ┆ …                        │
│ Montserrat (United Kingdom)     ┆ 4,453                   ┆ 4,42                    ┆ −0.74%    ┆ Americas              ┆ Caribbean                │
│ Falkland Islands (United Kingd… ┆ 3,49                    ┆ 3,477                   ┆ −0.37%    ┆ Americas              ┆ South America            │
│ Tokelau (New Zealand)           ┆ 2,29                    ┆ 2,397                   ┆ +4.67%    ┆ Oceania               ┆ Polynesia                │
│ Niue (New Zealand)              ┆ 1,821                   ┆ 1,817                   ┆ −0.22%    ┆ Oceania               ┆ Polynesia                │
│ Vatican City[x]                 ┆ 505                     ┆ 496                     ┆ −1.78%    ┆ Europe                ┆ Southern Europe          │
└─────────────────────────────────┴─────────────────────────┴─────────────────────────┴───────────┴───────────────────────┴──────────────────────────┘
```

# Data Cleaning
The first step needed is to clean the dataframe from unnecessary elements or mistakes.  

First check for the rows with Null values:  
```
# Pandas
print( UN[UN.isnull().any(axis=1)] )
```
```
# Polars
print( UN.filter( pl.any_horizontal( pl.all().is_null() ) ) )
```
```
┌─────────┬─────────────────────────┬─────────────────────────┬───────────┬───────────────────────┬──────────────────────────┐
│ Country ┆ Population(1 July 2022) ┆ Population(1 July 2023) ┆ Change[%] ┆ UN Continental Region ┆ UN Statistical Subregion │
│ ---     ┆ ---                     ┆ ---                     ┆ ---       ┆ ---                   ┆ ---                      │
│ str     ┆ str                     ┆ str                     ┆ str       ┆ str                   ┆ str                      │
╞═════════╪═════════════════════════╪═════════════════════════╪═══════════╪═══════════════════════╪══════════════════════════╡
│ World   ┆ 8,021,407,192           ┆ 8,091,734,930           ┆ +0.88%    ┆ null                  ┆ null                     │
└─────────┴─────────────────────────┴─────────────────────────┴───────────┴───────────────────────┴──────────────────────────┘
```
This shows that only the first row has missing values, which are easily replaceable.  



Other problems to solve are:
- There seem to be at least 2 values at the end of the dataframe with one less 0 then there should be:  
```
# Pandas
def check_0(value):
    value_split = value.split(",")
    if( len( value_split[-1] ) < 3  and  len(value_split) > 1 ):
        return value + "0"
    return value

population_col = ["Population(1 July 2022)", "Population(1 July 2023)"]
for col in population_col: # apply the funciont to both columns
    UN[col] = UN[col].apply(check_0).str.replace(",", "").astype("Int64")
```
```
# Polars
# columns of the dataframe to check
population_col = ["Population(1 July 2022)", "Population(1 July 2023)"]

for col in population_col: # for each column
    UN = UN.with_columns( population_split = pl.col(col).str.split(",") )
    UN = UN.with_columns(
        pl.when(
            (pl.col("population_split").list.eval(pl.element().str.len_chars()).list.last() < 3)
            & 
            (pl.col("population_split").list.len() > 1)
            )
            .then(pl.col(col) + "0") # add 0 if the criteria are met -> problematic number
            .otherwise(pl.col(col)), # otherwise keeps the same number
    )
    UN = UN.select(pl.all().exclude("population_split"))
```
- Some countries have a footnote indicator at the end of their name which is best to be removed:  
```
# Pandas
UN["Country"] = UN["Country"].str.replace(r"\[.*?\]", "", regex=True)
```
```
# Polars
UN = UN.with_columns(
    pl.col("Country").str.replace(r"\[.*?\]", "")
)
```
- The Change column needs to be converted in numeric values, by also removing the special character '−' (different from the minus sign '-'):  
```
# Pandas
# removes the special sign: '−' and returns a float value
def clear_sign(value):
    if("−" in value): return float(value.replace("−","")) * -1
    else: return float(value)

# apply the function to all the elements of the Change column
UN["Change[%]"] = UN["Change[%]"].apply(clear_sign)
```
```
# Polars
UN = UN.with_columns(
    pl.when(pl.col("Change[%]").str.contains("−"))
    .then(pl.col("Change[%]").str.replace("−","").cast(pl.Float64) * -1)
    .otherwise(pl.col("Change[%]")).cast(pl.Float64)
)
```


After all the changes, the dataframe looks like this:  
```
┌─────────────────────────────────┬─────────────────────────┬─────────────────────────┬───────────┬───────────────────────┬──────────────────────────┐
│ Country                         ┆ Population(1 July 2022) ┆ Population(1 July 2023) ┆ Change[%] ┆ UN Continental Region ┆ UN Statistical Subregion │
│ ---                             ┆ ---                     ┆ ---                     ┆ ---       ┆ ---                   ┆ ---                      │
│ str                             ┆ i64                     ┆ i64                     ┆ f64       ┆ str                   ┆ str                      │
╞═════════════════════════════════╪═════════════════════════╪═════════════════════════╪═══════════╪═══════════════════════╪══════════════════════════╡
│ World                           ┆ 8021407192              ┆ 8091734930              ┆ 0.88      ┆ World Total           ┆ World Total              │
│ India                           ┆ 1425423212              ┆ 1438069596              ┆ 0.89      ┆ Asia                  ┆ Southern Asia            │
│ China                           ┆ 1425179569              ┆ 1422584933              ┆ -0.18     ┆ Asia                  ┆ Eastern Asia             │
│ United States                   ┆ 341534046               ┆ 343477335               ┆ 0.57      ┆ Americas              ┆ Northern America         │
│ Indonesia                       ┆ 278830529               ┆ 281190067               ┆ 0.85      ┆ Asia                  ┆ South-eastern Asia       │
│ …                               ┆ …                       ┆ …                       ┆ …         ┆ …                     ┆ …                        │
│ Montserrat (United Kingdom)     ┆ 4453                    ┆ 4420                    ┆ -0.74     ┆ Americas              ┆ Caribbean                │
│ Falkland Islands (United Kingd… ┆ 3490                    ┆ 3477                    ┆ -0.37     ┆ Americas              ┆ South America            │
│ Tokelau (New Zealand)           ┆ 2290                    ┆ 2397                    ┆ 4.67      ┆ Oceania               ┆ Polynesia                │
│ Niue (New Zealand)              ┆ 1821                    ┆ 1817                    ┆ -0.22     ┆ Oceania               ┆ Polynesia                │
│ Vatican City                    ┆ 505                     ┆ 496                     ┆ -1.78     ┆ Europe                ┆ Southern Europe          │
└─────────────────────────────────┴─────────────────────────┴─────────────────────────┴───────────┴───────────────────────┴──────────────────────────┘
```





# Exploratory Analysis
With the cleaned data it is now possible to make an exploratory analysis of the dataset.  
The data is divided in subregions which are divided as such:  
<img src="https://github.com/DakoDC/Pandas-vs-Polars-Analysis/blob/main/United_Nations_geographical_subregions.png">  

A few of the insights gained from the analysis are:  
- Subregions with largest increase and decrease in population in percentage:
```
# Pandas
subregions_change = (
    UN.groupby("UN Statistical Subregion")["Change[%]"]
    .sum()
    .sort_values(ascending=False)
    )
print( subregions_change.head() )
print( subregions_change.tail() )
```
```
# Polars
print(UN
    .group_by("UN Statistical Subregion")
    .agg(pl.col("Change[%]").sum())
    .sort(pl.col("Change[%]"), descending=True)
)
```
```
┌──────────────────────────┬───────────┐
│ UN Statistical Subregion ┆ Change[%] │
│ ---                      ┆ ---       │
│ str                      ┆ f64       │
╞══════════════════════════╪═══════════╡
│ Eastern Africa           ┆ 46.11     │
│ Western Asia             ┆ 41.15     │
│ Western Africa           ┆ 36.63     │
│ Middle Africa            ┆ 24.0      │
│ Northern Europe          ┆ 12.03     │
│ …                        ┆ …         │
│ World Total              ┆ 0.88      │
│ Southern Europe          ┆ 0.27      │
│ Micronesia               ┆ -1.86     │
│ Polynesia                ┆ -2.86     │
│ Eastern Europe           ┆ -8.32     │
└──────────────────────────┴───────────┘
```
Evidently the war in eastern Europe has affected greatly the total population, reducing it by over 8%.  
An interesting duality is found between Northen and Southern Europe, where the North has increased in population sensibly more then the South. 
A position probably caused by the greater amount in percentage of immigrants in the north and the high brain drain in the south.  
Accentuating the need to action from the southern Europe countries to limit the aggravation of the situation.  

Likewise is the position of Polynesia and Micronesia, both of which suffer from some of the highest numbers of brain drain in the world.  



- Countries with the largest difference in population:
```
# Pandas
UN["population_difference"] = UN["Population(1 July 2023)"] - UN["Population(1 July 2022)"]
print(
    UN.sort_values(by = "population_difference",ascending=False)
)
```
```
# Polars
print(
    UN.with_columns(
        population_difference = pl.col("Population(1 July 2023)") - pl.col("Population(1 July 2022)")
    )
    .sort(pl.col("population_difference"), descending=True)
    .select(["Country","population_difference","Change[%]"])
)
```
```
┌──────────┬───────────────────────┬───────────┐
│ Country  ┆ population_difference ┆ Change[%] │
│ ---      ┆ ---                   ┆ ---       │
│ str      ┆ i64                   ┆ f64       │
╞══════════╪═══════════════════════╪═══════════╡
│ World    ┆ 70327738              ┆ 0.88      │
│ India    ┆ 12646384              ┆ 0.89      │
│ Nigeria  ┆ 4732049               ┆ 2.12      │
│ Pakistan ┆ 3803828               ┆ 1.56      │
│ DR Congo ┆ 3392763               ┆ 3.31      │
│ …        ┆ …                     ┆ …         │
│ Greece   ┆ -169572               ┆ -1.63     │
│ Hungary  ┆ -277843               ┆ -2.79     │
│ Japan    ┆ -626631               ┆ -0.5      │
│ China    ┆ -2594636              ┆ -0.18     │
│ Ukraine  ┆ -3315930              ┆ -8.08     │
└──────────┴───────────────────────┴───────────┘
```
As a result of the war, in one year Ukraine has decreased in population of more than 3 milion people.  
A known worrying problem is the situation in Japan, which is the third country with the highest decrease in population in the world and the first in Asia in percentage.  
Another interesting combination is India and China, the two biggest countries in the world.
Where one has the highest increase and the other the highest decerease in popualtion in the world, showing the much different situations in these two countries.  







- Percentage of countries in each continent with a decrease in population:  
```
# Pandas
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

# Percentage of countries in each continent with a decrease in population:
print(cont_decrease.sort_values(by = "Percentage[%]", ascending=False))
```

```
# Polars
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
```
```
┌───────────────────────┬─────────────────┬─────────────────────────┬───────────────┐
│ UN Continental Region ┆ Total Countries ┆ Countries with decrease ┆ Percentage[%] │
│ ---                   ┆ ---             ┆ ---                     ┆ ---           │
│ str                   ┆ u32             ┆ u32                     ┆ f64           │
╞═══════════════════════╪═════════════════╪═════════════════════════╪═══════════════╡
│ Oceania               ┆ 23              ┆ 9                       ┆ 39.13         │
│ Europe                ┆ 50              ┆ 16                      ┆ 32.0          │
│ Americas              ┆ 55              ┆ 13                      ┆ 23.64         │
│ Asia                  ┆ 51              ┆ 7                       ┆ 13.73         │
│ Africa                ┆ 58              ┆ 2                       ┆ 3.45          │
└───────────────────────┴─────────────────┴─────────────────────────┴───────────────┘
```
About 40% of the countries in Oceania have decreased in population, while only 2 out of 58 countries in Africa faced a decrease.  
Also, from also looking at the other tables, it's interesting how in Asia the most developed countries are the ones that decreased the most in population, while in Europe it's the opposite.  








# Execution Times
Mean execution times of the different sections:  
All execution times come within about a hundredth of a second to the following times in seconds.  

Pandas:  
- Data Cleaning: 0.04s  
- Exploratory Analysis: 0.13s  
- Total: 0.17s  

Polars:  
- Data Cleaning: 0.02s  
- Exploratory Analysis: 0.05s  
- Total: 0.07s  

It seems like even for small dataframes polars is quite faster then pandas.  
Though pandas might still be a better option in certain projects, thanks to being more intuitive and easier to learn than polars.  
On top of which, by being widely used, it has a considerable amount of helpful resources on the internet.  



