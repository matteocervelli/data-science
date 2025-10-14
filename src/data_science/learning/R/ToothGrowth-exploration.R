data("ToothGrowth")
View(ToothGrowth)
filtered_tg <- filter(ToothGrowth, dose == 0.5)
filtered_tg
arrange(filtered_tg, len)
arrange(filter(ToothGrowth, dose == 0.5), len)
filtered_TootGrowth <- ToothGrowth %>% 
  filter(dose == 0.5) %>% 
  arrange(len) %>% 
  group_by(supp) %>% 
  summarize(mean_len = mean(len, na.rm = T), .groups = "drop")
filtered_TootGrowth
View(filtered_TootGrowth)
