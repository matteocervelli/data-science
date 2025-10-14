# Analisi di Concentrazione Venditori (Pareto)

```r
# Load required libraries
library(dplyr)
library(ggplot2)
library(scales)

# ===================================================================
# SELLER CONCENTRATION ANALYSIS - PARETO
# ===================================================================

print("=== ANALISI DI CONCENTRAZIONE VENDITORI ===")

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
print(paste("Totale venditori:", total_sellers))
print(paste("80% del fatturato viene da", pareto_80$seller_rank, "venditori"))
print(paste("Questo rappresenta il", round(pareto_80$seller_pct, 1), "% di tutti i venditori"))

# Top 10 concentration
top_10_revenue <- sum(head(seller_metrics$total_revenue, 10))
top_10_pct <- top_10_revenue / total_revenue * 100
print(paste("I primi 10 venditori controllano il", round(top_10_pct, 1), "% del mercato"))

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
    title = "Analisi di Concentrazione Venditori - Curva di Pareto",
    x = "% Venditori",
    y = "% Fatturato Cumulativo"
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

print("Concentrazione del mercato:")
print(concentration_summary)
```