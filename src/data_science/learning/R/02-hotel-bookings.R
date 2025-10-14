library(tidyverse)
library(skimr)
library(janitor)
setwd("~/dev/projects/data-science/learning/R")
bookings_df <- read_csv("hotel_bookings.csv")
head(bookings_df)
glimpse(bookings_df)
str(bookings_df)
skim(bookings_df)
colnames(bookings_df)
trimmed_df <- bookings_df %>%
  select('hotel', 'is_canceled', 'lead_time', 'arrival_date_year', 'arrival_date_month', 'adults', 'children', 'babies') %>%
  rename('hotel_type' = hotel) %>%
  unite('arrival_year_month', c('arrival_date_year', 'arrival_date_month'), sep = " ") %>%
  mutate(guests = adults + children + babies) %>%
  subset(select = -c(adults, children, babies)) %>%
  drop_na()
skim(trimmed_df)