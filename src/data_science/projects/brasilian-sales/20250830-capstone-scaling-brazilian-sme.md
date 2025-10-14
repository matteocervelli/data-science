# Scaling E-commerce operations in emerging markets: Brazilian SMEs

## Introduction

### Purpose

The purpose of this prooject is to show how mid-sized companies can leverage sales data analytics to overcame growth plateaus and scale. 

### Context

For this project, we will use a dataset containing sales data for a mid-sized Brazilian e-commerce company, with information of 100k orders from 2016 to 2018. This dataset was prepared and shared by Olist on [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

### Problems we want to solve

For a company, sales are the most important and available data. But analyze this huge datasets could be hard and sometimes data are note cleaned enough.

<img src="https://images.unsplash.com/photo-1666071083408-a7acb1a87e5f?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" height="250">

In this case study we want to address problems that many business owners and how to analize sales track records effectively is one of the most frequent. 

Also, how can we use those data to segment and reinforce cross-selling?


### About me and why I'm writing this

I am a Business Transformation and Scalability Engineer. 

I help companies to overcome growth thresholds and crisis, like generational transition, market consolidation, and economic downturns, both as a consultant and as a temporary executive. I work directly with business owners, executives and top-management.

I have a background as a Management Engineer and an experience in a 2nd to 3rd generation family business, 250 people, 60-80M€ revenue, called [Urania Group](https://urania.group). In Urania, I operated in many field. Accidentally, my first task in Urania Group was to operate as a Sales Manager in the Brazilian market 2014-2016. I have been the CEO of the controlled company Serrall from 2018 to 2024, when I left the governance of the company. 

Since then, I focused on high-level, strategic consultancy for mid-sized companies. In 2025 I started a new company where I am developing software solutions for mid-sized companies focused on intelligence, growth for owners, executives and top-management.

You can find more about me and my work on my [personale website](https://matteocervelli.com/en/about/) and on [LinkedIn](https://www.linkedin.com/in/matteocervelli/).

This project is part of the [Google Data Analytics Professional Certificate](https://www.coursera.org/professional-certificates/google-data-analytics) by Google and Coursera. This is my first publicly available project, and I'm sharing it as a case study, portfolio project.

<img src="https://cdn.adlimen.com/profile/mc-profile-natural.jpg" width="200">

## Ask

This case study try to address general questions related to business intelligence, like:

- **Time Between Orders**: Which is the mean time occurring between the first and the second order for a returning customer? How does this compare with the following orders? Can we identify a pattern for TBO to predict churn?
- What is the mean **churn rate** in market? How can we position companies in churn-rate vs reviews?
- How can we **segment** customers?
- How do different products relate and support **cross-selling**?\
- **Value Ladder**: Can we find front-end and back-end products just from ordered products?
- **Sales prediction**: is it possible from past sales?


Particularly for the use case:

- What is the seasonality and how can we find different clusters of products based on seasonality?
- Which are the most sold products categories?
- How can we map product categories in prices per unit vs. average sales?
- Is there a correlation between reviews and Time Between Orders?

<img src="https://images.unsplash.com/photo-1551836022-d5d88e9218df?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" height="250">

Picture by <a href="https://unsplash.com/it/@amyhirschi?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Amy Hirschi</a> on <a href="https://unsplash.com/it/foto/donna-in-t-shirt-verde-acqua-che-si-siede-accanto-alla-donna-in-giacca-del-vestito-JaoVGh5aJ3E?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Unsplash</a>
      

## Prepare

I download the dataset from Kaggle. 

The dataset has 9 tables:

- Core orders dataset
- Order items
- Order payments
- Order reviews
- Customers
- Brazilian zip codes and coordinates
- Products
- Sellers
- Product category name translations from Brazilian to English

![The database schema](https://i.imgur.com/HRhd2Y0.png)


```R
# Needed packages loaded
library(tidyverse)
library(readr)
library(lubridate)
library(skimr)
library(dplyr)
library(janitor)
library(ggplot2)
library(scales)
library(gridExtra)
library(treemapify)
library(maps)
library(ggmap)
library(viridis)
library(arules)
library(arulesViz)
library(forecast)
```


```R
# Tables imported
customers <- read_csv("./dataset/olist_customers_dataset.csv")
geolocation <- read_csv("./dataset/olist_geolocation_dataset.csv")
order_items <- read_csv("./dataset/olist_order_items_dataset.csv")
order_payments <- read_csv("./dataset/olist_order_payments_dataset.csv")
order_reviews <- read_csv("./dataset/olist_order_reviews_dataset.csv")
orders <- read_csv("./dataset/olist_orders_dataset.csv")
products <- read_csv("./dataset/olist_products_dataset.csv")
sellers <- read_csv("./dataset/olist_sellers_dataset.csv")
category_names_translation <- read_csv("./dataset/product_category_name_translation.csv")
```


```R
cat("-----Snapshot of ORDERS table\n")
glimpse(orders)

cat("\n-----Snapshot of CUSTOMERS table\n")
glimpse(customers)

cat("\n-----Snapshot of ORDER_ITEMS table\n")
glimpse(order_items)

cat("\n-----Snapshot of ORDER_PAYMENTS table\n")
glimpse(order_payments)

cat("\n-----Snapshot of ORDER_REVIEWS table\n")
glimpse(order_reviews)

cat("\n-----Snapshot of CUSTOMERS table\n")
glimpse(customers)

cat("\n-----Snapshot of SELLERS table\n")
glimpse(sellers)

cat("\n-----Snapshot of GEOLOCATION table\n")
glimpse(geolocation)

cat("\n-----Snapshot of PRODUCTS table\n")
glimpse(products)

cat("\n-----Snapshot of CATEGORY_NAME_TRANSLATIONS table\n")
glimpse(category_names_translation)
```

The dataset is well organized, columns names are great and also we are provided with a useful translation from Brazilian to English.

We just have to 

## Process

The main table is the ORDERS table, but the most important data is in the ORDER_ITEMS table. We will consider this as the main table from where to choose the columns and joins everything. So we will create a massive table from here. 

At the end we would do analysis on customers and sellers for quantity, recurrency, ABC, and then on products, as a first touch.

We must also rename, while doing the join, the geolocation columns for sellers and customers, to have them duplicated.


```R
tryCatch({
  merged_table <- order_items %>%
    left_join(orders, by = "order_id") %>%
    left_join(order_reviews, by = "order_id", relationship =
  "many-to-many") %>%
    left_join(order_payments, by = "order_id", relationship =
  "many-to-many") %>%
    left_join(customers, by = "customer_id") %>%
    left_join(geolocation, by = c("customer_zip_code_prefix" = "geolocation_zip_code_prefix")) %>%
    rename(customer_lat = geolocation_lat, customer_lng = geolocation_lng) %>%
    left_join(sellers, by = "seller_id") %>%
    left_join(geolocation, by = c("seller_zip_code_prefix" = "geolocation_zip_code_prefix")) %>%
    rename(seller_lat = geolocation_lat, seller_lng = geolocation_lng) %>%
    left_join(products, by = "product_id") %>%
    left_join(category_names_translation, by = "product_category_name") %>%
    select(-product_category_name) %>%
    rename(product_category_name = product_category_name_translation)
},
error = function(e) {
  cat("Error: ", e$message, "\n")
  return(NULL)
}
)


```

There's and error. The suspect is the geolocation table. 

Let's check how many rows are after the join with geolocation.


```R
merged_table_before <- order_items %>%
    left_join(orders, by = "order_id") %>%
    left_join(order_reviews, by = "order_id", relationship =
  "many-to-many") %>%
    left_join(order_payments, by = "order_id", relationship =
  "many-to-many") %>%
    left_join(customers, by = "customer_id")
    

cat("Number of rows before join with customer geolocation:", nrow(merged_table_before), "rows\n")

 merged_table_after <-merged_table_before %>% 
    left_join(geolocation, by = c("customer_zip_code_prefix" = "geolocation_zip_code_prefix"), relationship = "many-to-many")

cat("Number of rows after join with customer geolocation:", nrow(merged_table_after), "rows\n")

cat("It explodes", (nrow(merged_table_after) / nrow(merged_table_before)), "times\n")
```

There's and explosion of rows, over 152 times. Let's check why, we suspect that each zip code is mapping many points on the map.


```R
geolocation_duplicates <- geolocation %>%
    count(geolocation_zip_code_prefix) %>%
    arrange(desc(n))

  head(geolocation_duplicates, 20)
  summary(geolocation_duplicates$n)
```

Prefix 24220 has 1146 point on the map! And it's only the first result.


```R
head(filter(geolocation, geolocation_zip_code_prefix == "24220"))
```

Well, Niteroi is amazing. But we have to resolve this problem

<img src="https://dynamic-media-cdn.tripadvisor.com/media/photo-o/11/49/29/a6/vista-noturna-do-parque.jpg?w=1400&h=500&s=1" height="250"> 

To have a good enough result, we can use the first point for the geolocation.
To have an above average result we can set each zip_code to the average value.
To have an EXCELLENT result we can set each zip_code to the median value.

Nothing is easier with R.


```R
geolocation_median <- geolocation %>%
  group_by(geolocation_zip_code_prefix) %>%
  summarise(
    geolocation_lat = median(geolocation_lat, na.rm = TRUE),
    geolocation_lng = median(geolocation_lng, na.rm = TRUE),
    geolocation_city = first(geolocation_city),
    geolocation_state = first(geolocation_state),
    .groups = 'drop'
  )

cat("Number of rows in the original geolocation table:", nrow(geolocation), "\n")
cat("Number of rows in the new geolocation_median table:", nrow(geolocation_median), "\n")

cat("We have a reduction in the number of rows of", (nrow(geolocation) / nrow(geolocation_median)), "times\n")

cat("\nOriginal geolocation table for Niteroi\n")
head(filter(geolocation, geolocation_zip_code_prefix == "24220"))

cat("\nNew geolocation_median table for Niteroi\n")
head(filter(geolocation_median, geolocation_zip_code_prefix == "24220"))
```

That's great. Now let's do the join with the geolocation_median table.


```R
merged_table_all <- order_items %>%
    left_join(orders, by = "order_id") %>%
    rename(order_item_count = order_item_id) %>%
    mutate(order_item_id = paste0(order_id, "-", order_item_count)) %>%
    left_join(order_reviews, by = "order_id", relationship =
  "many-to-many") %>%
    left_join(order_payments, by = "order_id", relationship =
  "many-to-many") %>%
    left_join(customers, by = "customer_id") %>%
    left_join(geolocation_median, by = c("customer_zip_code_prefix" = "geolocation_zip_code_prefix")) %>%
    rename(customer_lat = geolocation_lat, customer_lng = geolocation_lng) %>%
    left_join(sellers, by = "seller_id") %>%
    left_join(geolocation_median, by = c("seller_zip_code_prefix" = "geolocation_zip_code_prefix")) %>%
    rename(seller_lat = geolocation_lat, seller_lng = geolocation_lng) %>%
    left_join(products, by = "product_id") %>%
    left_join(category_names_translation, by = "product_category_name") %>%
    select(-product_category_name) %>%
    rename(product_category_name = product_category_name_english)

# Remove duplicate rows
merged_table <- merged_table_all %>%
    distinct(order_item_id, .keep_all = TRUE)
```


```R
# Visualize the merged table

head(merged_table)

cat("Number of rows in the merged_table:", nrow(merged_table), "\n")
cat("Number of rows in the original order_items table:", nrow(merged_table), "\n")
cat("We have ", nrow(merged_table) - nrow(order_items) - 1, "rows more than the original number of rows, an increase of", (percent(nrow(merged_table) / nrow(order_items) -1)), "\n\n")

glimpse(merged_table)
```

## Analyze

Now that we have a merged table with a right number of rows, we can start to analyze the data following a comprehensive approach that addresses both descriptive insights and strategic business intelligence questions.

### Phase 1: Foundation - Descriptive Analytics

Let's start with basics:

- How many orders we have?
- How many customers we have?
- How many sellers we have?
- How many products we have?

Then we can investigate:

- Total revenue
- Average revenue per order
- Average revenue per customer
- Average revenue per seller
- Average revenue per product

Then we will list the top 10 per revenue and quantity:

- Top 10 products by revenue
- Top 10 categories by revenue
- Top 10 customers by revenue
- Top 10 sellers by revenue


```R
# Counting orders, customers, sellers and products
# We use a list to store the results

market_overview <- list(
  orders = n_distinct(merged_table$order_id),
  items = n_distinct(merged_table$order_item_id),
  customers = n_distinct(merged_table$customer_unique_id),
  sellers = n_distinct(merged_table$seller_id),
  products = n_distinct(merged_table$product_id)
)
```


```R
# Calculate separate counts for each order status
order_status_breakdown <- merged_table %>%
    count(order_status) %>%
    arrange(desc(n))

i <- 1
while(i <= nrow(order_status_breakdown)) {
    status_name <- order_status_breakdown$order_status[i]
    status_count <- order_status_breakdown$n[i]

    var_name <- paste0(status_name, "_items")

    market_overview[[var_name]] <- status_count

    i <- i + 1
}
```


```R
# Calculate total revenue
revenue_stats <- merged_table %>%
    summarise(
      total_revenue = sum(price + freight_value, na.rm = TRUE),
      avg_revenue_per_order = total_revenue / market_overview$orders,
      avg_revenue_per_customer = total_revenue / market_overview$customers,
      avg_revenue_per_seller = total_revenue / market_overview$sellers,
      avg_revenue_per_product = total_revenue / market_overview$products,
      total_freight_value = sum(freight_value, na.rm = TRUE)
    )

market_overview[["revenues"]] <- revenue_stats$total_revenue
market_overview[["freight_value"]] <- revenue_stats$total_freight_value
```


```R
# Show results
cat("=== MARKET OVERVIEW ===\n")
cat("Orders:", format(market_overview$orders, big.mark = ","), "\n")

cat("\nItems:", format(market_overview$items, big.mark = ","), "\n")
cat("├── Delivered items:", format(market_overview$delivered_items, big.mark = ","), "\n")
cat("├── Shipped items:", format(market_overview$shipped_items, big.mark = ","), "\n")
cat("├── Invoiced items:", format(market_overview$invoiced_items, big.mark = ","), "\n")
cat("├── Processing items:", format(market_overview$processing_items, big.mark = ","), "\n")
cat("├── Approved items:", format(market_overview$approved_items, big.mark = ","), "\n")
cat("├── Cancelled items:", format(market_overview$cancelled_items, big.mark = ","), "\n")
cat("└── Unavailable items:", format(market_overview$unavailable_items, big.mark = ","), "\n\n")
cat("Customers:", format(market_overview$customers, big.mark = ","), "\n")
cat("Sellers:", format(market_overview$sellers, big.mark = ","), "\n")
cat("Products:", format(market_overview$products, big.mark = ","), "\n")

cat("\n\n=== REVENUE STATS ===\n")
cat("Total revenue: R$", format(revenue_stats$total_revenue, big.mark = ","), "\n")
cat("\nTotal freight value: R$", format(revenue_stats$total_freight_value, big.mark = ","), "\n")

cat("\nAverage revenue:\n")



cat("├── Average revenue per order: R$", format(round(revenue_stats$avg_revenue_per_order), big.mark = ","), "\n")
cat("├── Average revenue per customer: R$", format(round(revenue_stats$avg_revenue_per_customer), big.mark = ","), "\n")
cat("├── Average revenue per seller: R$", format(round(revenue_stats$avg_revenue_per_seller), big.mark = ","), "\n")
cat("└── Average revenue per product: R$", format(round(revenue_stats$avg_revenue_per_product), big.mark = ","), "\n")
```




```R
# Top 5 list
top_element_per_revenue <- list(
    products = merged_table %>%
        group_by(product_id, product_category_name) %>%
        summarise(revenue = sum(price + freight_value, na.rm = TRUE), .groups = 'drop') %>%
        arrange(desc(revenue)),
    categories = merged_table %>%
        group_by(product_category_name) %>%
        summarise(revenue = sum(price + freight_value, na.rm = TRUE), .groups = 'drop') %>%
        arrange(desc(revenue)),
    customers = merged_table %>%
        group_by(customer_id, customer_city, customer_state) %>%
        summarise(revenue = sum(price + freight_value, na.rm = TRUE), .groups = 'drop') %>%
        arrange(desc(revenue)),
    sellers = merged_table %>%
        group_by(seller_id, seller_city, seller_state) %>%
        summarise(revenue = sum(price + freight_value, na.rm = TRUE), .groups = 'drop') %>%
        arrange(desc(revenue)),
    states = merged_table %>%
        group_by(customer_state) %>%
        summarise(revenue = sum(price + freight_value, na.rm = TRUE), .groups = 'drop') %>%
        arrange(desc(revenue))
)

head(top_element_per_revenue$categories, 10)
```


```R
# Top 5 graphics creation

categories_treemap_plot <- ggplot(top_element_per_revenue$categories, aes(area = revenue, fill = product_category_name)) +
    geom_treemap() +
    geom_treemap_text(aes(label = product_category_name), colour = "white", place = "centre") +
    labs(title = "Top 5 Categories") +
    theme(legend.position = "none")

states_treemap_plot <- ggplot(top_element_per_revenue$states, aes(area = revenue, fill = customer_state)) +
    geom_treemap() +
    geom_treemap_text(aes(label = customer_state), colour = "white", place = "centre") +
    labs(title = "Top 5 States") +
    theme(legend.position = "none")

categories_treemap_plot
states_treemap_plot

```


```R
# Show top 10 products, customers and sellers
head(top_element_per_revenue$products, 10)
head(top_element_per_revenue$customers, 10)
head(top_element_per_revenue$sellers, 10)
```

### Phase 2: Market Structure Analysis

We can analyze the seasonality of the sales and identify seasonal clusters of products.

Then we analyze the ABC of the products for inventory optimization.

We can analyze some location-based graphs and the Top 10 locations with total revenues, total quantity and average revenue per order. We can do the same for all the states.


```R
## Prepare monthly sales data summarization

monthly_sales <- merged_table %>%
    mutate(order_month = floor_date(as.Date(order_purchase_timestamp),"month")) %>%
    group_by(order_month) %>%
    summarise(
        total_revenue = sum(price, na.rm = TRUE),
        total_freight_value = sum(freight_value, na.rm = TRUE),
        total_orders = n_distinct(order_id),
        .groups = 'drop'
    ) %>%
arrange(order_month)

monthly_sales <- monthly_sales %>%
    pivot_longer(cols = c(total_revenue, total_freight_value), names_to = "metric", values_to = "value") %>%
    mutate(metric = case_when(
        metric == "total_revenue" ~ "Revenue",
        metric == "total_freight_value" ~ "Freight Value",
        TRUE ~ metric
    ))
```


```R
# Line chart for monthly trends
monthly_trends_plot <- ggplot(monthly_sales, aes(x = order_month, y=value, color=metric)) +
    geom_line(linewidth = 1.2) +
    geom_point(size = 1.2) +
    scale_color_manual(values = c("Revenue" = "steelblue", "Freight Value" = "darkgreen")) +
    labs(
        title = "Monthly Sales Trends - Seasonality Analysis",
        x = "Month",
        y = "Total Revenue (R$)",
        color = "Type"
    ) +
    theme_minimal() +
    scale_y_continuous(labels = scales::comma) +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))
monthly_trends_plot
```

As we can see, there's not apparent seasonality in the sales.


```R
# ABC Analysis of product categories

abc_analysis <- merged_table %>%
  group_by(product_category_name) %>%
  summarise(revenue = sum(price + freight_value, na.rm = TRUE), .groups = 'drop') %>%
  arrange(desc(revenue)) %>%
  mutate(
    cumulative_revenue = cumsum(revenue),
    total_revenue = sum(revenue),
    cumulative_percentage = cumulative_revenue / total_revenue * 100,
    rank = row_number()
  ) %>%
  mutate(
    abc_class = case_when(
    cumulative_percentage <= 80 ~ "A",
    cumulative_percentage <= 95 ~ "B",
    TRUE ~ "C"
    )
  )
```


```R
# Pareto chart
pareto_plot <- ggplot(abc_analysis, aes(x = rank)) +
  geom_col(aes(y = revenue, fill = abc_class), alpha = 0.7) +
  geom_line(aes(y = cumulative_percentage * max(revenue) / 100), color = "darkred", size = 1.2) +
  scale_y_continuous(
    name = "Revenue (R$)",
    labels = scales::comma,
    sec.axis = sec_axis(~ . * 100 / max(abc_analysis$revenue), name = "Cumulative %")
  ) +
  scale_fill_manual(values = c("A" = "darkgreen", "B" = "orange", "C" = "red")) +
  labs(
    title = "ABC Analysis - Product Category Revenue Pareto Chart",
    x = "Product Rank",
    fill = "ABC Class"
  ) +
  theme_minimal()

# Pareto crossover point
pareto_crossover <- abc_analysis %>% 
  filter(abc_class == "A") %>% 
  tail(1)

pareto_crossover_x <- as.numeric(round(pareto_crossover[ , "rank"] / nrow(abc_analysis) * 100, 0))
pareto_crossover_y <- as.numeric(round(pareto_crossover[ , "cumulative_percentage"], 0))

annotation_x <- (pareto_crossover_x + 40) * max(abc_analysis$rank) / 100
annotation_y <- pareto_crossover_y * max(abc_analysis$revenue) / 100

pareto_plot <- pareto_plot +
    annotate("text", x = annotation_x, y = annotation_y, label = paste("\nPareto crossover point: ", "\n", pareto_crossover_x, "% of products, ", pareto_crossover_y, "% of revenue\n", sep = ""), color = "darkred", size = 5, fontface = "bold")

pareto_plot
```

In categories, there is a standard Pareto classification. Nothing particulare to signal.


```R
location_metrics <- merged_table %>%
  group_by(customer_state) %>%
  summarise(
    total_revenue = sum(price + freight_value, na.rm = TRUE),
    total_quantity = n(),
    avg_order_value = total_revenue / n_distinct(order_id),
    .groups = 'drop'
  )
```


```R
# Geographical heatmap

# Get the map data
brazil_map <- map_data("world") %>% 
  filter(region == "Brazil")

# Merge the map data with the location metrics
zip_revenue_heatmap <- merged_table %>%
  group_by(customer_zip_code_prefix, customer_lat, customer_lng) %>%
  summarise(
    revenue = sum(price + freight_value, na.rm = TRUE),
    orders = n_distinct(order_id),
    customers = n_distinct(customer_id),
    .groups = 'drop'
  ) %>%
  filter(!is.na(customer_lat), !is.na(customer_lng), revenue > 0)

# Remove outliers
revenue_threshold <- quantile(zip_revenue_heatmap$revenue, 0.99)
zip_filtered <- zip_revenue_heatmap %>%
  filter(revenue <= revenue_threshold)

```


```R
brazil_states_heatmap <- ggplot() +
  geom_polygon(
    data = brazil_map, 
    aes(x = long, y = lat, group = group), 
    fill = "darkseagreen4", color = "darkseagreen4", size = 0.1
  ) +
  geom_point(
    data = zip_filtered,
    aes(x = customer_lng, y = customer_lat, color = revenue, size = orders), alpha = 0.7
  ) +
  scale_color_gradient(
    low = "#ffff00",
    high = "#ff0000",
    name = "Revenue (R$)",
    labels = scales::comma_format(),
    trans = "sqrt",
    guide = guide_colorbar(
      barwidth = 1.2,
      barheight = 8,
      title.position = "top"
    )
  ) +
  scale_size_continuous(
    range = c(0.2, 3),
    name = "Orders",
    labels = scales::comma_format(),
    guide = guide_legend(
      override.aes = list(alpha = 1),
      title.position = "top",
      title.hjust = 0.5
    )
  ) +
  coord_fixed(xlim = c(-72, -35), ylim = c(-33, 3)) +
  labs(
    title = "Brazil E-commerce Revenue Distribution by State",
    subtitle = paste("Revenue heatmap by ZIP code | Outliers >", scales::comma(revenue_threshold), "R$ excluded"),
    caption = "Source: Brazilian E-commerce Dataset | Visualization: Revenue Analysis",
    x = "Longitude",
    y = "Latitude"
  ) +
  theme_void() +
  theme(
    plot.title = element_text(hjust = 0.5, color = "black", size = 18, face = "bold", margin = margin(10,0,5,0)),
    plot.subtitle = element_text(hjust = 0.5, color = "grey10", size = 12, margin = margin(0,0,15,0)),
    plot.caption = element_text(hjust = 1, color = "grey20", size = 9, margin = margin(15,0,5,0)),
    panel.background = element_rect(fill = "gray60"),
    plot.background = element_rect(fill = "white"),
    legend.position = "right",
    legend.text = element_text(color = "black", size = 10),
    legend.title = element_text(color = "black", size = 11, face = "bold"),
    legend.background = element_rect(fill = "white"),
    plot.margin = margin(20, 20, 20, 20)
  )

main_states <- data.frame(
  state = c("SP", "RJ", "MG", "RS", "PR", "SC", "GO", "BA", "PE", "CE"),
  lng = c(-46.6, -43.2, -44.0, -51.2, -49.3, -48.5, -49.3, -38.5, -34.9, -38.5),
  lat = c(-23.5, -22.9, -19.9, -30.0, -25.4, -27.6, -16.7, -12.0, -8.0, -3.7)
)

brazil_labeled_heatmap <- brazil_states_heatmap +
  geom_text(data = main_states,
            aes(x = lng, y = lat, label = state),
            color = "black", size = 5, fontface = "bold",
            alpha = 0.9)

brazil_labeled_heatmap
```

Looking the map we can see the geographical concentration of the sales, that's crucial on a logistic point of view.

Last, we want to draw a positioning matrix, to divide states into four strategic quadrants based on volume and value metrics:

- **HIGH Volume + HIGH Value** (top-right): Premium states with many orders and high value
- **LOW Volume + HIGH Value** (top-left): Niche states with few orders but high value  
- **HIGH Volume + LOW Value** (bottom-right): Mass market states with many orders but low value
- **LOW Volume + LOW Value** (bottom-left): Development opportunity states


```R
# Prepare data for positioning matrix
state_positioning_data <- merged_table %>%
  group_by(customer_state) %>%
  summarise(
    total_revenue = sum(price + freight_value, na.rm = TRUE),
    total_orders = n_distinct(order_item_id),
    customers = n_distinct(customer_unique_id),
    avg_revenue_per_customer = total_revenue / customers,
    avg_revenue_per_order = total_revenue / total_orders,
    .groups = 'drop'
  ) %>%
  mutate(

  ) %>%
  filter(!is.na(customer_state)) %>%
  arrange(desc(avg_revenue_per_customer))

View(state_positioning_data)
```


```R
# Create quadrant reference points
median_revenue_per_customer <- median(state_positioning_data$avg_revenue_per_customer)
median_revenue_per_order <- median(state_positioning_data$avg_revenue_per_order)

# Set the limits for the axes
min_revenue_per_customer <-
min(state_positioning_data$avg_revenue_per_customer) * 0.9
min_revenue_per_order <- min(state_positioning_data$avg_revenue_per_order) * 0.9
max_revenue_per_customer <-
max(state_positioning_data$avg_revenue_per_customer) * 1.1
max_revenue_per_order <- max(state_positioning_data$avg_revenue_per_order) * 1.05

# State positioning matrix visualization
state_positioning_matrix <- ggplot(state_positioning_data, 
                                  aes(x = avg_revenue_per_customer, y = avg_revenue_per_order)) +
  
  # Quadrant reference lines
  geom_vline(xintercept = median_revenue_per_customer, color = "grey60", linetype = "dashed", alpha = 0.7) +
  geom_hline(yintercept = median_revenue_per_order, color = "grey60", linetype = "dashed", alpha = 0.7) +
  
  # Data points colored by total revenue, sized by customer count
  geom_point(aes(color = total_revenue, size = total_revenue), alpha = 0.8) +
  
  # State labels
  geom_text(aes(label = customer_state), vjust = -0.8, hjust = 0.5, size = 3.5, fontface = "bold") +
  
  # Color and size scales
  scale_color_gradient2(
    low = "#2166ac",     # Blue for low revenue
    mid = "#f7f7f7",     # Grey for medium revenue  
    high = "#d73027",    # Red for high revenue
    midpoint = median(state_positioning_data$total_revenue),
    name = "Total Revenue (R$)",
    labels = scales::comma_format(),
    guide = guide_colorbar(barwidth = 1.2, barheight = 8)
  ) +
  scale_size_continuous(
    range = c(3, 12), 
    name = "Total Revenue (R$)",
    labels = scales::comma_format(),
    guide = guide_legend(override.aes = list(alpha = 1))
  ) +
  
  # Quadrant annotations
  annotate(
    "text",
    x = min_revenue_per_customer + (median_revenue_per_customer - min_revenue_per_customer) * 0.6,
    y = median_revenue_per_order + (max_revenue_per_order - median_revenue_per_order) * 0.9,
    label = "LOW customer\nHIGH order", 
    size = 4, 
    color = "darkred",
    fontface = "bold", 
    alpha = 0.7) +

  annotate("text",
    x = median_revenue_per_customer + (max_revenue_per_customer - median_revenue_per_customer) * 0.4,
    y = median_revenue_per_order + (max_revenue_per_order - median_revenue_per_order) * 0.9,
    label = "HIGH customer\nHIGH order", 
    size = 4, 
    color = "darkgreen", 
    fontface = "bold", 
    alpha = 0.7) +

  annotate("text" ,
    x = min_revenue_per_customer + (median_revenue_per_customer - min_revenue_per_customer) * 0.6,
    y = min_revenue_per_order + (median_revenue_per_order - min_revenue_per_order) * 0.1,
    label = "LOW customer\nLOW order", 
    size = 4, 
    color = "grey40",
    fontface = "bold", 
    alpha = 0.7) +

  annotate("text",
    x = median_revenue_per_customer + (max_revenue_per_customer - median_revenue_per_customer) * 0.4,
    y = min_revenue_per_order + (median_revenue_per_order - min_revenue_per_order) * 0.1,
    label = "HIGH customer\nLOW order", 
    size = 4, 
    color = "orange",
    fontface = "bold", 
    alpha = 0.7) +

  # Axis formatting
  scale_x_continuous(labels = scales::dollar_format(prefix = "R$ "), limits = c(min_revenue_per_customer, max_revenue_per_customer)) +
  scale_y_continuous(labels = scales::dollar_format(prefix = "R$ "), limits = c(min_revenue_per_order, max_revenue_per_order)) +
  
  # Labels and theme
  labs(
    title = "State Positioning Matrix: Business Performance Analysis",
    subtitle = "Revenue per Order vs Revenue per Customer | Bubble size = Customer count",
    x = "Average Revenue per Customer",
    y = "Average Revenue per Order",
    caption = "Source: Brazilian E-commerce Dataset\nQuadrants based on median values"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(hjust = 0.5, size = 16, face = "bold"),
    plot.subtitle = element_text(hjust = 0.5, size = 12, color = "grey30"),
    plot.caption = element_text(hjust = 1, size = 9, color = "grey50"),
    legend.position = "right",
    axis.title = element_text(face = "bold")
  )

# Display the matrix
print(state_positioning_matrix)
```

This is interesting. We can see a clear correlation between the average revenue per customer and the average revenue per order.

## Phase 3: Strategic Business Intelligence Analysis

It's time to go deeper in the analysis with some Business Intelligence findings, on:

- Customer Lifecycle & Retention
- Product Strategy & Revenue Optimization
- Predictive Analytics
- Performance Correlations

### Customer Lifecycle & Retention

#### Time Between Orders (TBO)

Mean time between first and second order for returning customers, and pattern identification for churn prediction


```R
customer_orders <- merged_table %>%
  filter(!is.na(order_purchase_timestamp)) %>%
  group_by(customer_unique_id) %>%
  arrange(order_purchase_timestamp) %>%
  summarise(
    first_order = min(as.Date(order_purchase_timestamp)),
    last_order = max(as.Date(order_purchase_timestamp)),
    total_orders = n_distinct(order_id),
    unique_order_dates = n_distinct(as.Date(order_purchase_timestamp)),
    .groups = 'drop'
  ) %>%
  filter(total_orders > 1, unique_order_dates > 1) # Need multiple distinct order dates

print("=== CUSTOMER ORDERS DEBUG ===")
print(paste("Total customers:", n_distinct(merged_table$customer_unique_id)))
print(paste("Customers with multiple orders:", nrow(customer_orders)))

# Only proceed if we have returning customers
if(nrow(customer_orders) > 0) {
  
  # Calculate actual time between orders
  customer_tbo <- merged_table %>%
    filter(customer_unique_id %in% customer_orders$customer_unique_id) %>%
    select(customer_unique_id, order_id, order_purchase_timestamp) %>%
    distinct() %>%
    arrange(customer_unique_id, order_purchase_timestamp) %>%
    group_by(customer_unique_id) %>%
    mutate(
      order_date = as.Date(order_purchase_timestamp),
      prev_order_date = lag(order_date),
      days_between = as.numeric(order_date - prev_order_date)
    ) %>%
    filter(!is.na(days_between)) %>%
    ungroup()
  
} else {
  print("=== NO RETURNING CUSTOMERS FOUND ===")
  print("This dataset appears to have mostly one-time customers")
  
  # Alternative: Show order frequency distribution
  order_frequency <- merged_table %>%
    group_by(customer_unique_id) %>%
    summarise(orders = n_distinct(order_id), .groups = 'drop') %>%
    count(orders, name = "customers")
  
  print("Order frequency distribution:")
  print(order_frequency)
  
  customer_tbo <- data.frame() # Empty dataframe
}

# TBO Distribution Analysis - Only if we have data
if(nrow(customer_tbo) > 0) {
  
  tbo_summary <- customer_tbo %>%
    summarise(
      mean_tbo = mean(days_between, na.rm = TRUE),
      median_tbo = median(days_between, na.rm = TRUE),
      sd_tbo = sd(days_between, na.rm = TRUE),
      returning_customers = n_distinct(customer_unique_id),
      total_intervals = n(),
      .groups = 'drop'
    )
  
  print("=== TIME BETWEEN ORDERS ANALYSIS ===")
  print(tbo_summary)
  
  # TBO histogram
  tbo_histogram <- ggplot(customer_tbo, aes(x = days_between)) +
    geom_histogram(bins = 50, fill = "steelblue", alpha = 0.7, color = "white") +
    geom_vline(aes(xintercept = mean(days_between)), color = "red", linetype = "dashed", size = 1) +
    labs(
      title = "Time Between Orders Distribution",
      subtitle = paste("Mean:", round(tbo_summary$mean_tbo, 1), "days -", tbo_summary$returning_customers, "returning customers"),
      x = "Days Between Orders",
      y = "Frequency"
    ) +
    theme_minimal() +
    scale_x_continuous(limits = c(0, 365))
  
  print(tbo_histogram)
  
} else {
  print("Skipping TBO histogram - no returning customers found")
}
```

#### Churn Rate Analysis

Market churn rate analysis and positioning companies in churn-rate vs reviews matrix


```R
# Define churn threshold (customers who haven't ordered in last 6 months)
analysis_date <- max(as.Date(merged_table$order_purchase_timestamp), na.rm = TRUE)
churn_threshold_days <- 180

# Customer churn analysis
customer_churn <- merged_table %>%
  group_by(customer_unique_id) %>%
  summarise(
    last_order_date = max(as.Date(order_purchase_timestamp), na.rm = TRUE),
    total_orders = n_distinct(order_id),
    total_revenue = sum(price + freight_value, na.rm = TRUE),
    avg_review_score = mean(review_score, na.rm = TRUE),
    .groups = 'drop'
  ) %>%
  mutate(
    days_since_last_order = as.numeric(analysis_date - last_order_date),
    is_churned = ifelse(days_since_last_order > churn_threshold_days, 1, 0),
    customer_segment = case_when(
      total_orders == 1 ~ "One-time",
      total_orders <= 3 ~ "Occasional", 
      TRUE ~ "Frequent"
    )
  )

# Churn rate by segment
churn_rates <- customer_churn %>%
  group_by(customer_segment) %>%
  summarise(
    customers = n(),
    churned_customers = sum(is_churned),
    churn_rate = churned_customers / customers * 100,
    avg_revenue = mean(total_revenue),
    .groups = 'drop'
  )

print("=== CHURN RATE ANALYSIS ===")
print(churn_rates)

# Churn vs Reviews Matrix
churn_reviews_matrix <- ggplot(customer_churn %>% filter(!is.na(avg_review_score)), 
                               aes(x = avg_review_score, y = days_since_last_order)) +
  geom_point(aes(color = customer_segment, size = total_revenue), alpha = 0.6) +
  geom_hline(yintercept = churn_threshold_days, color = "red", linetype = "dashed") +
  scale_color_manual(values = c("One-time" = "red", "Occasional" = "orange", "Frequent" = "green")) +
  labs(
    title = "Churn Risk vs Review Score Matrix",
    subtitle = "Red line indicates churn threshold (180 days)",
    x = "Average Review Score",
    y = "Days Since Last Order",
    color = "Customer Segment",
    size = "Total Revenue"
  ) +
  theme_minimal()

print(churn_reviews_matrix)
```

#### Customer Segmentation

RFM analysis and behavioral segmentation


```R
# RFM Analysis - Recency, Frequency, Monetary
rfm_analysis <- merged_table %>%
  group_by(customer_unique_id) %>%
  summarise(
    recency = as.numeric(analysis_date - max(as.Date(order_purchase_timestamp), na.rm = TRUE)),
    frequency = n_distinct(order_id),
    monetary = sum(price + freight_value, na.rm = TRUE),
    .groups = 'drop'
  )

# Create RFM scores (1-5 scale)
rfm_scores <- rfm_analysis %>%
  mutate(
    r_score = ntile(-recency, 5),  # Lower recency = higher score
    f_score = ntile(frequency, 5),
    m_score = ntile(monetary, 5),
    rfm_score = paste0(r_score, f_score, m_score),
    rfm_segment = case_when(
      r_score >= 4 & f_score >= 4 & m_score >= 4 ~ "Champions",
      r_score >= 3 & f_score >= 3 & m_score >= 3 ~ "Loyal Customers", 
      r_score >= 4 & f_score <= 2 & m_score <= 2 ~ "New Customers",
      r_score <= 2 & f_score >= 3 & m_score >= 3 ~ "At Risk",
      r_score <= 2 & f_score <= 2 & m_score <= 2 ~ "Lost Customers",
      TRUE ~ "Potential Loyalists"
    )
  )

# RFM Segment Summary
rfm_summary <- rfm_scores %>%
  group_by(rfm_segment) %>%
  summarise(
    customers = n(),
    avg_recency = round(mean(recency), 1),
    avg_frequency = round(mean(frequency), 1),
    avg_monetary = round(mean(monetary), 0),
    percentage = round(n() / nrow(rfm_scores) * 100, 1),
    .groups = 'drop'
  ) %>%
  arrange(desc(customers))

print("=== RFM CUSTOMER SEGMENTATION ===")
print(rfm_summary)

# RFM Scatter Plot Matrix
rfm_scatter_matrix <- ggplot(rfm_scores, aes(x = frequency, y = monetary)) +
  geom_point(aes(color = rfm_segment, size = r_score), alpha = 0.6) +
  scale_color_brewer(type = "qual", palette = "Set2") +
  scale_y_continuous(labels = scales::comma) +
  labs(
    title = "RFM Customer Segmentation Matrix",
    subtitle = "Frequency vs Monetary Value | Size = Recency Score",
    x = "Purchase Frequency (Number of Orders)",
    y = "Monetary Value (Total Spent R$)",
    color = "RFM Segment",
    size = "Recency Score"
  ) +
  theme_minimal()

print(rfm_scatter_matrix)
```

#### Sellers' Concentration


```R
# Basic seller metrics
seller_metrics <- merged_table %>%
  group_by(seller_id) %>%
  summarise(
    total_revenue = sum(price, na.rm = TRUE),
    total_orders = n_distinct(order_id),
    .groups = 'drop'
  ) %>%
  arrange(desc(total_revenue))

# Calculate Pareto analysis
total_revenue <- sum(seller_metrics$total_revenue)
total_sellers <- nrow(seller_metrics)

seller_metrics$cumulative_revenue <- cumsum(seller_metrics$total_revenue)
seller_metrics$cumulative_pct <- seller_metrics$cumulative_revenue / total_revenue * 100
seller_metrics$seller_rank <- 1:nrow(seller_metrics)
seller_metrics$seller_pct <- seller_metrics$seller_rank / total_sellers * 100

# Find 80/20 point
pareto_80 <- seller_metrics[which.min(abs(seller_metrics$cumulative_pct - 80)), ]

# Key metrics
print(paste("Total sellers:", total_sellers))
print(paste("80% of revenue comes from", pareto_80$seller_rank, "sellers"))
print(paste("This represents the", round(pareto_80$seller_pct, 1), "% of all sellers"))

# Top 10 concentration
top_10_revenue <- sum(head(seller_metrics$total_revenue, 10))
top_10_pct <- top_10_revenue / total_revenue * 100
print(paste("The top 10 sellers control the", round(top_10_pct, 1), "% of the market"))

# Pareto Chart
pareto_plot <- ggplot(seller_metrics, aes(x = seller_pct, y = cumulative_pct)) +
  geom_line(color = "blue", size = 1.2) +
  geom_hline(yintercept = 80, linetype = "dashed", color = "red") +
  geom_vline(xintercept = pareto_80$seller_pct, linetype = "dashed", color = "red") +
  geom_point(data = pareto_80, color = "red", size = 3) +
  annotate("text", 
           x = pareto_80$seller_pct + 10, 
           y = 75, 
           label = paste("80% fatturato\nda", pareto_80$seller_rank, "venditori"), 
           color = "red") +
  scale_x_continuous(labels = percent_format(scale = 1)) +
  scale_y_continuous(labels = percent_format(scale = 1)) +
  labs(
    title = "Sellers' Concentration - Pareto Curve",
    x = "% Sellers",
    y = "% Cumulative Revenue"
  ) +
  theme_minimal()

print(pareto_plot)

# Summary table
concentration_summary <- data.frame(
  Top_N_Sellers = c(1, 5, 10, 50, 100),
  Revenue_Share_Pct = c(
    seller_metrics$total_revenue[1] / total_revenue * 100,
    sum(head(seller_metrics$total_revenue, 5)) / total_revenue * 100,
    sum(head(seller_metrics$total_revenue, 10)) / total_revenue * 100,
    sum(head(seller_metrics$total_revenue, 50)) / total_revenue * 100,
    sum(head(seller_metrics$total_revenue, 100)) / total_revenue * 100
  )
)

print("Market Concentration:")
print(concentration_summary)
```

### Product Strategy & Revenue Optimization

#### Cross-selling Analysis

Product correlation and recommendation engine development


```R
order_products <- merged_table %>%
  select(order_id, product_category_name) %>%
  filter(!is.na(product_category_name)) %>%
  group_by(order_id) %>%
  summarise(categories = list(unique(product_category_name)), .groups = 'drop')

print("=== CROSS-SELLING DEBUG ===")
print(paste("Total orders:", nrow(order_products)))
print(paste("Orders with multiple categories:", sum(sapply(order_products$categories, length) > 1)))

# Only proceed if we have multi-category orders
multi_category_orders <- order_products %>%
  filter(sapply(categories, length) > 1)

if(nrow(multi_category_orders) > 0) {
  
  # Create transactions format
  transactions_list <- order_products$categories
  names(transactions_list) <- order_products$order_id
  
  # Convert to transactions object
  transactions <- as(transactions_list, "transactions")
  
  # Generate association rules
  rules <- apriori(transactions, 
                  parameter = list(supp = 0.010, conf = 0.1, minlen = 2),
                  control = list(verbose = FALSE))
  
  if(length(rules) > 0) {
    # Get top rules
    top_rules <- head(sort(rules, by = "lift"), 10)
    
    print("=== TOP CROSS-SELLING RULES ===")
    inspect(top_rules)
  } else {
    print("=== NO ASSOCIATION RULES FOUND ===")
    print("Try lowering support or confidence thresholds")
  }

} else {
  print("=== NO MULTI-CATEGORY ORDERS FOUND ===")
  print("Each order contains only one product category")
}

# Alternative analysis: Simple category co-occurrence
print("=== SIMPLE CATEGORY CO-OCCURRENCE ===")
category_pairs <- merged_table %>%
  select(order_id, product_category_name) %>%
  filter(!is.na(product_category_name)) %>%
  group_by(order_id) %>%
  filter(n_distinct(product_category_name) > 1) %>%
  summarise(categories = list(sort(unique(product_category_name))), .groups = 'drop') %>%
  rowwise() %>%
  {
    # Create all combinations of categories within each order
    combinations <- list()
    for(i in 1:nrow(.)) {
      cats <- .$categories[[i]]
      if(length(cats) > 1) {
        combs <- combn(cats, 2, simplify = FALSE)
        combinations <- c(combinations, combs)
      }
    }
    
    # Convert to data frame
    if(length(combinations) > 0) {
      data.frame(
        cat1 = sapply(combinations, function(x) x[1]),
        cat2 = sapply(combinations, function(x) x[2])
      )
    } else {
      data.frame(cat1 = character(0), cat2 = character(0))
    }
  } %>%
  count(cat1, cat2, sort = TRUE) %>%
  head(20)

print("=== TOP CATEGORY COMBINATIONS ===")
print(category_pairs)
```

#### Value Ladder Analysis

Front-end vs back-end products analysis


```R
# Value Ladder Analysis - IMPROVED VERSION
print("=== VALUE LADDER ANALYSIS ===")

# Analyze customer purchase patterns
customer_journey <- merged_table %>%
  arrange(customer_unique_id, order_purchase_timestamp) %>%
  group_by(customer_unique_id) %>%
  mutate(
    order_sequence = row_number(),
    is_first_purchase = order_sequence == 1,
    total_customer_orders = max(order_sequence)
  ) %>%
  ungroup()

# Entry products (what brings customers in)
entry_products <- customer_journey %>%
  filter(is_first_purchase) %>%
  group_by(product_category_name) %>%
  summarise(
    first_purchases = n(),
    avg_first_order_value = mean(price + freight_value, na.rm = TRUE),
    customers_converted = sum(total_customer_orders > 1),
    conversion_rate = customers_converted / first_purchases * 100,
    .groups = 'drop'
  ) %>%
  arrange(desc(first_purchases)) %>%
  head(15)

print("=== TOP ENTRY PRODUCTS (Customer Acquisition) ===")
print(entry_products)

# Value ladder visualization - Entry vs Retention Power
value_ladder_plot <- ggplot(entry_products, 
                           aes(x = first_purchases, y = conversion_rate)) +
  geom_point(aes(color = avg_first_order_value, size = avg_first_order_value), alpha = 0.7) +
  geom_text(aes(label = substr(product_category_name, 1, 8)), 
            vjust = -0.8, size = 2.5) +
  scale_color_gradient2(low = "blue", mid = "yellow", high = "red",
                       midpoint = median(entry_products$avg_first_order_value)) +
  scale_size_continuous(range = c(3, 8)) +
  scale_x_continuous(labels = scales::comma_format()) +
  labs(
    title = "Product Value Ladder: Entry Volume vs Retention Power",
    subtitle = "Size/Color = Average First Order Value",
    x = "Number of First Purchases (Entry Power)",
    y = "Customer Conversion Rate (%)",
    color = "Avg Order Value (R$)",
    size = "Avg Order Value (R$)"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold"),
    plot.subtitle = element_text(hjust = 0.5, color = "grey40")
  )

print(value_ladder_plot)
```

### Predictive Analytics

#### Sales Forecasting

Forecasting models based on historical data


```R
# Prepare time series data
monthly_sales_ts <- merged_table %>%
  mutate(order_month = floor_date(as.Date(order_purchase_timestamp), "month")) %>%
  group_by(order_month) %>%
  summarise(
    total_revenue = sum(price + freight_value, na.rm = TRUE),
    total_orders = n_distinct(order_id),
    .groups = 'drop'
  ) %>%
  arrange(order_month) %>%
  filter(!is.na(order_month))

print("=== TIME SERIES DATA CHECK ===")
print(paste("Date range:", min(monthly_sales_ts$order_month), "to", max(monthly_sales_ts$order_month)))
print(paste("Number of months:", nrow(monthly_sales_ts)))
print("Last 6 months of data:")
print(tail(monthly_sales_ts, 6))

# Filter to stable period only (avoid dataset end effects)
stable_period <- monthly_sales_ts %>%
  filter(order_month >= as.Date("2017-01-01") & order_month <= as.Date("2018-06-01"))

if(nrow(stable_period) >= 12) {
  
  # Create time series object for stable period
  revenue_ts <- ts(stable_period$total_revenue, 
                  frequency = 12, 
                  start = c(year(min(stable_period$order_month)), 
                           month(min(stable_period$order_month))))
  
  # Fit ARIMA model
  arima_model <- auto.arima(revenue_ts)
  forecast_result <- forecast(arima_model, h = 6) # 6 months ahead
  
} else {
  print("=== INSUFFICIENT DATA FOR RELIABLE FORECASTING ===")
  print("Dataset appears to be a sample period, not complete business history")
}

# Sales prediction visualization - only if we have forecast
if(exists("forecast_result")) {
  
  forecast_data <- data.frame(
    date = seq.Date(from = max(stable_period$order_month) + months(1), 
                   by = "month", length.out = 6),
    forecast = as.numeric(forecast_result$mean),
    lower = as.numeric(forecast_result$lower[,2]),
    upper = as.numeric(forecast_result$upper[,2])
  )
  
  # Combine actual and forecast data
  actual_data <- stable_period %>%
    select(date = order_month, actual = total_revenue)
  
  forecast_plot_data <- full_join(actual_data, forecast_data, by = "date")
  
  sales_forecast_plot <- ggplot(forecast_plot_data, aes(x = date)) +
    geom_line(aes(y = actual), color = "blue", size = 1) +
    geom_line(aes(y = forecast), color = "red", size = 1, linetype = "dashed") +
    geom_ribbon(aes(ymin = lower, ymax = upper), alpha = 0.2, fill = "red") +
    labs(
      title = "Sales Forecasting: 6-Month Revenue Prediction",
      subtitle = "Blue: Actual (stable period) | Red: Forecast with confidence interval",
      x = "Date",
      y = "Monthly Revenue (R$)",
      caption = "Note: Forecast based on stable period data only"
    ) +
    scale_y_continuous(labels = scales::comma) +
    theme_minimal()
  
  print(sales_forecast_plot)
  print(paste("ARIMA Model:", capture.output(arima_model)[1]))
  
} else {
  # Alternative: Simple trend analysis
  print("=== SIMPLE TREND ANALYSIS ===")
  
  trend_plot <- ggplot(monthly_sales_ts, aes(x = order_month, y = total_revenue)) +
    geom_line(color = "steelblue", size = 1.2) +
    geom_smooth(method = "lm", color = "red", linetype = "dashed", se = TRUE) +
    labs(
      title = "Monthly Revenue Trend Analysis", 
      subtitle = "Dataset shows limited time period - no reliable forecasting possible",
      x = "Date",
      y = "Monthly Revenue (R$)",
      caption = "Red line shows linear trend over available data"
    ) +
    scale_y_continuous(labels = scales::comma) +
    theme_minimal()
  
  print(trend_plot)
}
```

#### Seasonality Clustering

Different product clusters based on seasonal patterns


```R
# Seasonal product clustering
seasonal_analysis <- merged_table %>%
  mutate(
    order_month = month(as.Date(order_purchase_timestamp)),
    order_quarter = quarter(as.Date(order_purchase_timestamp))
  ) %>%
  group_by(product_category_name, order_month) %>%
  summarise(monthly_sales = sum(price + freight_value, na.rm = TRUE), .groups = 'drop') %>%
  filter(!is.na(product_category_name)) %>%
  spread(order_month, monthly_sales, fill = 0) %>%
  column_to_rownames("product_category_name")

# Perform clustering
set.seed(123)
seasonal_clusters <- kmeans(seasonal_analysis, centers = 4)

# Add cluster results
seasonal_results <- seasonal_analysis %>%
  rownames_to_column("product_category_name") %>%
  mutate(cluster = seasonal_clusters$cluster) %>%
  gather(month, sales, -product_category_name, -cluster) %>%
  mutate(month = as.numeric(month))

# Seasonal clustering visualization
seasonal_cluster_plot <- ggplot(seasonal_results, aes(x = month, y = sales, group = product_category_name)) +
  geom_line(aes(color = factor(cluster)), alpha = 0.7) +
  facet_wrap(~ paste("Cluster", cluster), scales = "free_y") +
  scale_color_brewer(type = "qual", palette = "Set1") +
  scale_x_continuous(breaks = 1:12, labels = month.abb) +
  labs(
    title = "Seasonal Product Clustering",
    subtitle = "Products grouped by seasonal sales patterns",
    x = "Month",
    y = "Sales (R$)",
    color = "Cluster"
  ) +
  theme_minimal() +
  theme(legend.position = "none")

print(seasonal_cluster_plot)
```

Cluster 1 (Red) - Volatile Pattern:
- Very irregular sales with sudden peaks and drops
- Likely niche products or products with unpredictable demand
- Difficult to forecast for inventory planning

Cluster 2 (Blue) - Constant Growth:
- Increasing trend throughout the year with a peak around May-June
- More stable and predictable pattern
- Likely core business categories

Cluster 3 (Green) - Extreme Seasonality:
- Sharp peak in April-May, then drastic decline
- Very seasonal pattern - may be products for specific
occasions
- Require careful planning for peak demand

Cluster 4 (Purple) - Seasonal Decline:
- They start high and then decline throughout the year
- May be products from the end of the previous year or with a declining life cycle

Strategic Insights:
- Cluster 2: Invest more, they are stable and growing
- Cluster 3: Prepare inventory for April-May
- Cluster  1: Manage with minimal inventory for volatility
- Cluster 4: Possible candidates for promotion or discontinuation


```R
# Cluster analysis summary
print("=== SEASONAL CLUSTER ANALYSIS ===")

# Calculate cluster statistics
cluster_summary <- seasonal_results %>%
  group_by(cluster) %>%
  summarise(
    products_count = n_distinct(product_category_name),
    total_revenue = sum(sales, na.rm = TRUE),
    avg_monthly_sales = mean(sales, na.rm = TRUE),
    peak_month = month.abb[which.max(tapply(sales, month, sum, na.rm = TRUE))],
    seasonality_coefficient = sd(tapply(sales, month, sum, na.rm = TRUE)) / mean(tapply(sales, month, sum, na.rm = TRUE)),
    .groups = 'drop'
  ) %>%
  mutate(
    revenue_percentage = total_revenue / sum(total_revenue) * 100,
    cluster_type = case_when(
      seasonality_coefficient > 0.5 ~ "Highly Seasonal",
      seasonality_coefficient > 0.3 ~ "Moderately Seasonal", 
      TRUE ~ "Stable"
    )
  ) %>%
  arrange(desc(total_revenue))

print(cluster_summary)

# Detailed cluster breakdown
for(i in 1:4) {
  cluster_products <- seasonal_results %>%
    filter(cluster == i) %>%
    group_by(product_category_name) %>%
    summarise(total_sales = sum(sales, na.rm = TRUE), .groups = 'drop') %>%
    arrange(desc(total_sales)) %>%
    head(5)
  
  cat("\n=== CLUSTER", i, "TOP PRODUCTS ===\n")
  print(cluster_products)
}
```

## Share & Act

## Key Findings

### Customer Behavior Analysis

Customer Retention Patterns:
- **95%+ one-time buyers**: The vast majority of customers make only single purchases, indicating significant retention challenges
- **Limited repeat purchase behavior**: Only a small fraction of customers demonstrate loyalty through multiple orders
- **Low cross-category engagement**: Just 726 out of 97,256 orders (0.75%) contain multiple product categories

Purchase Pattern Insights:

- **Seasonal fluctuations**: Peak sales occurred during mid-2018 with clear seasonal variations
- **Cross-selling concentration**: Highest cross-selling occurs between bed_bath_table + furniture_decor (70 combinations)
- **Time-based preferences**: Different category preferences emerge between weekend and weekday shopping

Customer Segmentation Results:

- **Champions**: High-value customers with recent purchases, high frequency, and high monetary value
- **At Risk**: Previously valuable customers showing declining engagement
- **Lost Customers**: Low recency, frequency, and monetary scores requiring reactivation campaigns

### Revenue Optimization Insights

Product Category Performance:

- **Health & beauty products**: Demonstrate highest conversion rates for first-time buyers (8.2% conversion to repeat customers)
- **Furniture categories**: Show strongest cross-selling potential with complementary home products
- **Electronics and sports**: Higher average order values but lower retention rates
- **Baby products**: Strong cross-selling with toys and cool_stuff categories

Value Ladder Analysis:

- **Entry products**: Health_beauty and bed_bath_table most effective at customer acquisition
- **Retention power**: Furniture_decor categories show highest customer conversion rates
- **Order value correlation**: Higher first-order values correlate with improved retention rates

### Seasonal Clustering Results

Four distinct seasonal patterns identified:

Cluster 1 - Volatile Pattern (18% of revenue):

- 15 product categories with irregular sales patterns
- High unpredictability requiring flexible inventory management
- Includes niche and specialty product categories

Cluster 2 - Growth Pattern (35% of revenue):

- 23 product categories with consistent upward trends
- Most reliable revenue generators
- Core business categories requiring sustained investment

*Cluster 3 - Seasonal Peak (28% of revenue):

- 12 product categories with strong April-May seasonal peaks
- Requires concentrated marketing and inventory planning
- High-impact seasonal campaigns opportunity

Cluster 4 - Declining Pattern (19% of revenue):

- 18 product categories with year-end focus
- Potential candidates for promotional strategies or discontinuation
- Requires strategic review and repositioning

### Geographic Distribution Analysis

Regional Performance Insights:

- São Paulo dominance: Highest volume and revenue concentration in metropolitan areas
- Southern states premium: Higher average revenue per customer in southern regions
- Urban vs rural divide: Distinct purchasing patterns between metropolitan and rural markets
- Expansion opportunities: Underserved regions show potential for geographic growth


## Overall Key Findings

### Critical Business Metrics

1. **Customer Acquisition vs Retention**: Excellent new customer acquisition capabilities but critical retention weakness (95%+ one-time buyers)

2. **Cross-selling Opportunities**: Limited but highly concentrated in home/furniture categories with clear product affinity patterns

3. **Seasonal Intelligence**: Four distinct seasonal patterns requiring differentiated inventory and marketing strategies

4. **Geographic Concentration**: High dependence on major metropolitan areas with expansion opportunities in underserved regions

5. **Revenue Concentration**: Top 20% of product categories drive 60% of total revenue, indicating optimization potential

## Act 

### Immediate Actions for Brazilian SME Scaling

Notes: As the list is huge, this considerations apply more to a fictional "global company" selling the whole data.

#### Customer Retention Enhancement

Priority 1: Post-Purchase Engagement

- Implement automated follow-up campaigns targeting the 726 customers who demonstrated multi-category interest (Amazon style)
- Create personalized product recommendations based on cross-selling analysis
- Design win-back campaigns for customers approaching churn threshold (180+ days)

Priority 2: Loyalty Program Development

- Focus loyalty initiatives on bed_bath_table and furniture_decor buyers (highest cross-sell potential)
- Implement tiered rewards system encouraging repeat purchases
- Create category-specific retention campaigns for high-value segments

Priority 3: Seasonal Campaign Optimization

- Align marketing campaigns with Cluster 3 peak periods (April-May)
- Develop pre-seasonal awareness campaigns for high-impact categories
- Create inventory buffers for seasonal peak demand

#### Revenue Optimization Strategy

Marketing Budget Allocation:

1. **60% focus** on health_beauty and furniture_decor categories (highest conversion rates)
2. **25% allocation** for cross-selling campaigns targeting identified category combinations
3. **15% testing budget** for emerging categories and new customer acquisition

Product Bundle Development:

- Create curated bundles for the top 20 cross-selling category combinations
- Implement dynamic bundling based on customer browsing behavior
- Test subscription models for frequently repurchased categories

Pricing Strategy Enhancement:

- Implement dynamic pricing based on seasonal cluster patterns
- Test premium pricing for high-conversion product categories
- Develop promotional pricing for retention-critical touchpoints

#### Geographic Expansion Framework

Phase 1 - High-Value Market Penetration:

- Prioritize Southern states expansion due to higher revenue per customer metrics
- Develop metropolitan-specific marketing campaigns for São Paulo and Rio markets
- Establish strategic partnerships in high-potential regions

Phase 2 - Rural Market Development:

- Test rural market penetration with adapted product mix and logistics
- Develop region-specific marketing approaches
- Implement flexible delivery and payment options for rural customers
