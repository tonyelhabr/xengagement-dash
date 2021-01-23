
library(fresh)
create_theme(
  theme = "default",
  output_file = "default-custom.css",

  bs_vars_navbar(
    default_bg = "#003f5c",
    inverse_bg = "#003f5c",
    default_color = "#FFFFFF",
    default_link_color = "#FFFFFF",
    default_link_active_color = "#FFFFFF",
    default_link_hover_color = "#003f5c"
  ),
  bs_vars_color(
    gray_base = "#354e5c",
    brand_primary = "#ffa600"
  )
)
