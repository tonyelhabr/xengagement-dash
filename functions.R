
library(rlang)
library(tidyverse)
library(plotly)

.import_data <- function(name) {
  url(sprintf('https://raw.githubusercontent.com/tonyelhabr/xengagement/master/inst/extdata/%s.rds', name)) %>% readr::read_rds()
}

import_preds <- memoise::memoise({function() {
  .import_data('preds')
}})

import_shap <- memoise::memoise({function(preds = import_preds()) {
  shap_init <- .import_data('shap')

  shap <-
    shap_init %>% 
    dplyr::mutate(dplyr::across(dplyr::where(is.numeric), ~dplyr::coalesce(.x, 0))) %>% 
    dplyr::left_join(preds %>% dplyr::select(idx, text), by = 'idx') %>% 
    dplyr::filter(feature != 'baseline') %>% 
    dplyr::mutate(across(text, ~forcats::fct_reorder(.x, dplyr::desc(.x))))
  shap
}})

.upper1 <- function(x) {
  x <- tolower(x)
  substr(x, 1, 1) <- toupper(substr(x, 1, 1))
  x
}

.plot_shap_subplot <- function(data, .stem) {
  
  colors <- c('favorite' = '#003f5c', 'retweet' = '#ffa600')
  colors <- c('favorite' = '##7a5195', 'retweet' = '#ef5675')
  color <- unname(colors[stem])
  
  base <-
    data %>% 
    plotly::plot_ly(
      showlegend = FALSE,
      text = ~text,
      color = I(color),
      ...
    ) %>% 
    plotly::config(
      displaylogo = FALSE
    ) %>% 
    plotly::layout(
      autosize = TRUE,
      # separators = ',.',
      font = list(
        family = 'Karla',
        size = 14
      ),
      xaxis = list(title = ''),
      yaxis = list(title = '', tickformat = ',.')
    )
  base
}

plot_shap_subplots <- function(data) {
  
}

# .prep_shap <- function(data, .stem) {
#   # shap_filt <- data %>% dplyr::filter(stem == .stem)
#   shap_filt <- data
#   rnk_max <- 14L
#   
#   shap_baseline <-
#     shap_filt %>%
#     dplyr::filter(feature == 'baseline')
#   
#   shap_rnk_init <-
#     shap_filt %>%
#     dplyr::anti_join(
#       shap_baseline %>% dplyr::select(feature),
#       by = c('feature')
#     ) %>%
#     dplyr::mutate(
#       abs = shap_value %>% abs(),
#       rnk_init = dplyr::row_number(dplyr::desc(abs))
#     )
#   shap_rnk_init
#   
#   shap_features_small <-
#     shap_rnk_init %>%
#     dplyr::filter(rnk_init >= !!rnk_max) %>%
#     dplyr::mutate(rnk = !!rnk_max + 1L)
#   shap_features_small
#   
#   shap_rnk_init_nonagg <-
#     shap_rnk_init %>%
#     dplyr::anti_join(
#       shap_features_small %>%
#         dplyr::select(feature), by = c('feature')
#     ) %>%
#     dplyr::mutate(
#       temp = ifelse(shap_value < 0, min(shap_value) - shap_value, shap_value),
#       rnk = dplyr::row_number(dplyr::desc(temp)),
#     ) %>%
#     dplyr::select(-temp) %>%
#     dplyr::arrange(rnk)
#   shap_rnk_init_nonagg
#   
#   shap_first_neg <-
#     shap_rnk_init_nonagg %>%
#     dplyr::filter(shap_value < 0) %>%
#     dplyr::slice_min(rnk)
#   shap_first_neg
#   rnk_crossover <- shap_first_neg$rnk
#   
#   shap_rnk <-
#     list(
#       shap_baseline %>% dplyr::mutate(rnk = 0L),
#       shap_rnk_init_nonagg %>%
#         dplyr::mutate(
#           dplyr::across(rnk, ~ifelse(.x >= !!rnk_crossover, .x + 1, .x))
#         ),
#       shap_features_small
#     ) %>%
#     purrr::reduce(dplyr::bind_rows) %>%
#     dplyr::mutate(
#       dplyr::across(shap_value, ~dplyr::coalesce(.x, 0)),
#       dplyr::across(lab, ~ifelse(rnk > !!rnk_max, 'Other Features', .x))
#     ) %>%
#     tidyr::fill(.pred)
#   shap_rnk
#   
#   shap_rnk_agg <-
#     shap_rnk %>%
#     dplyr::group_by(.pred, rnk) %>%
#     dplyr::summarize(shap_value = sum(shap_value)) %>%
#     dplyr::ungroup() %>%
#     dplyr::left_join(
#       shap_rnk %>%
#         dplyr::distinct(lab, rnk),
#       by = c('rnk')
#     ) %>%
#     dplyr::mutate(
#       dplyr::across(lab, ~forcats::fct_reorder(.x, rnk)),
#       dplyr::across(shap_value, ~dplyr::case_when(rnk == 0L ~ 0, TRUE ~ .x)),
#       measure = 'relative'
#     ) %>% 
#     dplyr::arrange(rnk)
#   shap_rnk_agg
# }
# 
# plot_stem_shap <- function(data, stem, ...) {
# 
#   p <-
#     data %>%
#     plotly::plot_ly(
#       x = ~ shap_value,
#       y = ~ lab,
#       measure = ~measure,
#       type = 'waterfall',
#       orientation = 'h',
#       name = 'SHAP values',
#       connector = list(
#         mode = 'between',
#         line = list(width = 4, color = 'rgb(0, 0, 0)', dash = 0)
#       ),
#       hovertemplate = paste('%{y}', '<br>SHAP value: %{x:.2f}<br>', '<extra></extra>'),
#       showlegend = FALSE,
#       ...
#     ) %>%
#     plotly::config(
#       displaylogo = FALSE
#     ) %>%
#     plotly::layout(
#       title = sprintf('Prediction Breakdown for %s', .upper1(stem)),
#       font = list(
#         family = 'Karla',
#         size = 14
#       ),
#       xaxis = list(
#         title = 'SHAP value',
#         x = 0,
#         y = 0,
#         zeroline = TRUE
#       ),
#       yaxis = list(title = '', type = 'category')
#     )
#   p
# }

.plot_stem_base <- function(data, stem, ...) {
  
  colors <- c('favorite' = '#003f5c', 'retweet' = '#ffa600')
  color <- unname(colors[stem])
  
  base <-
    data %>% 
    plotly::plot_ly(
      showlegend = FALSE,
      text = ~text,
      color = I(color),
      ...
    ) %>% 
    plotly::config(
      displaylogo = FALSE
    ) %>% 
    plotly::layout(
      autosize = TRUE,
      # separators = ',.',
      font = list(
        family = 'Karla',
        size = 14
      ),
      xaxis = list(title = ''),
      yaxis = list(title = '', tickformat = ',.')
    )
  base
}

plot_stem_time <- function(data, stem, ...) {
  
  pred_sym <- sprintf('%s_pred', stem) %>% rlang::sym()
  actual_sym <- sprintf('%s_count', stem) %>% rlang::sym()
  lab_stem <- sprintf('%ss', .upper1(stem))
  lab_y <- sprintf('Actual # of %s', lab_stem)

  base <- .plot_stem_base(data, stem, ...)
  # browser()
  rlang::eval_tidy(
    rlang::quo_squash(
      rlang::quo({
        p <-
          base %>% 
          plotly::add_markers(
            # hoverinfo = 'y',
            hovertemplate = paste(
              '%{text}',
              sprintf('<br># of %s: %%{y:0,000}', lab_stem),
              '<extra></extra>'
            ),
            x = ~ created_at,
            y = ~ !!actual_sym
          ) %>% 
          plotly::layout(
            # autosize = TRUE,
            xaxis = list(title = 'Time'),
            yaxis = list(title = lab_y)
          )
        p
      })
    )
  )
}

plot_stem_pred <- function(data, stem, ...) {
  
  pred_sym <- sprintf('%s_pred', stem) %>% rlang::sym()
  actual_sym <- sprintf('%s_count', stem) %>% rlang::sym()
  lab_stem <- sprintf('%ss', .upper1(stem))
  lab_y <- sprintf('Actual # of %s', lab_stem)
  
  base <- .plot_stem_base(data, stem, ...)
  rlang::eval_tidy(
    rlang::quo_squash(
      rlang::quo({
        p <-
          base %>%
          plotly::add_markers(
            # hoverinfo = 'x+y',
            hovertemplate = paste(
              '%{text}',
              sprintf('<br>%s: %%{y:,d}', lab_y),
              sprintf('<br>Predicted # of %s: %%{x:,.0f}', lab_stem),
              '<extra></extra>'
            ),
            x = ~ !!pred_sym,
            y = ~ !!actual_sym
          ) %>% 
          plotly::layout(
            xaxis = list(title = sprintf('Predicted # of %s', lab_stem), tickformat = ',.'),
            yaxis = list(title = lab_y)
          )
        p
      })
    )
  )
}


.plot_stem_base2 <- function(data, stem, ...) {
  
  colors <- c('favorite' = '#de425b', 'retweet' = '#488f31')
  color <- unname(colors[stem])
  
  base <-
    data %>% 
    plotly::plot_ly(
      showlegend = FALSE,
      text = ~text,
      color = I(color),
      transforms = list(
        list(
          type = 'aggregate',
          groups = ~idx,
          aggregations = list(
            list(
              target = 'x', func = 'first', enabled = TRUE
            ),
            list(
              target = 'y', func = 'first', enabled = TRUE
            )
          )
        )
      ),
      ...
    ) %>% 
    plotly::config(
      displaylogo = FALSE
    ) %>% 
    plotly::layout(
      autosize = TRUE,
      # separators = ',.',
      font = list(
        family = 'Karla',
        size = 14
      ),
      xaxis = list(title = ''),
      yaxis = list(title = '', tickformat = ',.')
    )
  base
}


plot_stem_pred2 <- function(data, stem, ...) {
  
  pred_sym <- sprintf('%s_pred', stem) %>% rlang::sym()
  actual_sym <- sprintf('%s_count', stem) %>% rlang::sym()
  lab_stem <- sprintf('%ss', .upper1(stem))
  lab_y <- sprintf('Actual # of %s', lab_stem)
  
  base <- .plot_stem_base(data, stem, ...)
  rlang::eval_tidy(
    rlang::quo_squash(
      rlang::quo({
        p <-
          base %>%
          plotly::add_markers(
            # hoverinfo = 'x+y',
            hovertemplate = paste(
              '%{text}',
              sprintf('<br>%s: %%{y:,d}', lab_y),
              sprintf('<br>Predicted # of %s: %%{x:,.0f}', lab_stem),
              '<extra></extra>'
            ),
            x = ~ !!pred_sym,
            y = ~ !!actual_sym
          ) %>% 
          plotly::layout(
            xaxis = list(title = sprintf('Predicted # of %s', lab_stem), tickformat = ',.'),
            yaxis = list(title = lab_y)
          )
        p
      })
    )
  )
}
