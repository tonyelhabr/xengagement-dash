
library(rlang)
library(tidyverse)
library(plotly)

.import_data <- function(name) {
  url(sprintf('https://raw.githubusercontent.com/tonyelhabr/xengagement/master/inst/extdata/%s.rds', name)) %>% readr::read_rds()
}

import_preds <- memoise::memoise({function() {
  .import_data('preds') %>% 
    dplyr::mutate(
      favorite_diff = favorite_pred - favorite_count,
      retweet_diff = retweet_pred - retweet_count,
      dplyr::across(text, ~sprintf('%s: %s (%.2f) %d-%d (%.2f) %s', lubridate::date(created_at), tm_h, xg_h, g_h, g_a, xg_a, tm_a))
    )
}})

import_shap <- memoise::memoise({function(preds = import_preds()) {
  shap_init <- .import_data('shap')
  shap_init %>% 
    dplyr::left_join(preds %>% dplyr::select(idx, text), by = 'idx')
}})

.upper1 <- function(x) {
  x <- tolower(x)
  substr(x, 1, 1) <- toupper(substr(x, 1, 1))
  x
}

.prep_shap <- function(data, .stem) {
  # shap_filt <- data %>% dplyr::filter(stem == .stem)
  shap_filt <- data
  rnk_max <- 14L
  
  shap_baseline <-
    shap_filt %>%
    dplyr::filter(feature == 'baseline')
  
  shap_rnk_init <-
    shap_filt %>%
    dplyr::anti_join(
      shap_baseline %>% dplyr::select(feature),
      by = c('feature')
    ) %>%
    dplyr::mutate(
      abs = shap_value %>% abs(),
      rnk_init = dplyr::row_number(dplyr::desc(abs))
    )
  shap_rnk_init
  
  shap_features_small <-
    shap_rnk_init %>%
    dplyr::filter(rnk_init >= !!rnk_max) %>%
    dplyr::mutate(rnk = !!rnk_max + 1L)
  shap_features_small
  
  shap_rnk_init_nonagg <-
    shap_rnk_init %>%
    dplyr::anti_join(
      shap_features_small %>%
        dplyr::select(feature), by = c('feature')
    ) %>%
    dplyr::mutate(
      temp = ifelse(shap_value < 0, min(shap_value) - shap_value, shap_value),
      rnk = dplyr::row_number(dplyr::desc(temp)),
    ) %>%
    dplyr::select(-temp) %>%
    dplyr::arrange(rnk)
  shap_rnk_init_nonagg
  
  shap_first_neg <-
    shap_rnk_init_nonagg %>%
    dplyr::filter(shap_value < 0) %>%
    dplyr::slice_min(rnk)
  shap_first_neg
  rnk_crossover <- shap_first_neg$rnk
  
  shap_rnk <-
    list(
      shap_baseline %>% dplyr::mutate(rnk = 0L),
      shap_rnk_init_nonagg %>%
        dplyr::mutate(
          dplyr::across(rnk, ~ifelse(.x >= !!rnk_crossover, .x + 1, .x))
        ),
      shap_features_small
    ) %>%
    purrr::reduce(dplyr::bind_rows) %>%
    dplyr::mutate(
      dplyr::across(shap_value, ~dplyr::coalesce(.x, 0)),
      dplyr::across(lab, ~ifelse(rnk > !!rnk_max, 'Other Features', .x))
    ) %>%
    tidyr::fill(.pred)
  shap_rnk
  
  shap_rnk_agg <-
    shap_rnk %>%
    dplyr::group_by(.pred, rnk) %>%
    dplyr::summarize(shap_value = sum(shap_value)) %>%
    dplyr::ungroup() %>%
    dplyr::left_join(
      shap_rnk %>%
        dplyr::distinct(lab, rnk),
      by = c('rnk')
    ) %>%
    dplyr::mutate(
      dplyr::across(lab, ~forcats::fct_reorder(.x, rnk)),
      dplyr::across(shap_value, ~dplyr::case_when(rnk == 0L ~ 0, TRUE ~ .x)),
      measure = 'relative'
    ) %>% 
    dplyr::arrange(rnk)
  shap_rnk_agg
}

plot_stem_shap <- function(data, stem = 'favorite', ...) {
  # data <- shap
  # stem <- 'favorite'

  # shap_filt <-
  #   data %>%
  #   dplyr::filter(stem == !!stem)
  col_sym <- sprintf('%s_shap', stem) %>% sym()
  shap_filt <-
    data %>% 
    dplyr::select(idx, !!col_sym) %>% 
    tidyr::unnest(!!col_sym)
  
  idx_distinct <- shap_filt %>% distinct(idx)
  if(nrow(idx_distinct) != 1L) {
    invisible(NULL)
  }
  
  rnk_max <- 10L

  shap_baseline <-
    shap_filt %>%
    dplyr::filter(feature == 'baseline')

  shap_rnk_init <-
    shap_filt %>%
    dplyr::anti_join(
      shap_baseline %>% dplyr::select(idx, feature),
      by = c('idx', 'feature')
    ) %>%
    dplyr::group_by(idx) %>%
    dplyr::mutate(
      abs = shap_value %>% abs(),
      rnk_init = dplyr::row_number(dplyr::desc(abs))
    ) %>%
    dplyr::ungroup()
  shap_rnk_init

  shap_features_small <-
    shap_rnk_init %>%
    dplyr::filter(rnk_init >= !!rnk_max) %>%
    dplyr::mutate(rnk = !!rnk_max + 1L)
  shap_features_small

  shap_rnk_init_nonagg <-
    shap_rnk_init %>%
    dplyr::anti_join(
      shap_features_small %>%
        dplyr::select(idx, feature), by = c('idx', 'feature')
    ) %>%
    dplyr::group_by(idx) %>%
    dplyr::mutate(
      temp = ifelse(shap_value < 0, min(shap_value) - shap_value, shap_value),
      rnk = dplyr::row_number(dplyr::desc(temp)),
    ) %>%
    dplyr::ungroup() %>%
    dplyr::select(-temp) %>%
    dplyr::arrange(idx, rnk)
  shap_rnk_init_nonagg

  shap_first_neg <-
    shap_rnk_init_nonagg %>%
    dplyr::filter(shap_value < 0) %>%
    dplyr::group_by(idx) %>%
    dplyr::slice_min(rnk) %>%
    dplyr::ungroup()
  shap_first_neg

  shap_rnk <-
    list(
      shap_baseline %>% dplyr::mutate(rnk = 0L),
      shap_rnk_init_nonagg %>%
        dplyr::left_join(
          shap_first_neg %>%
            dplyr::select(idx, rnk_crossover = rnk),
          by = 'idx'
        ) %>%
        dplyr::mutate(
          dplyr::across(rnk, ~ifelse(.x >= rnk_crossover, .x + 1, .x))
        ),
      shap_features_small
    ) %>%
    purrr::reduce(dplyr::bind_rows) %>%
    dplyr::mutate(
      dplyr::across(shap_value, ~dplyr::coalesce(.x, 0)),
      dplyr::across(lab, ~ifelse(rnk > !!rnk_max, 'Other Features', .x))
    ) %>%
    dplyr::arrange(rnk) %>%
    tidyr::fill(.pred, idx)
  shap_rnk

  shap_rnk_agg <-
    shap_rnk %>%
    dplyr::group_by(idx, .pred, rnk) %>%
    dplyr::summarize(shap_value = sum(shap_value)) %>%
    dplyr::ungroup() %>%
    dplyr::arrange(rnk) %>%
    dplyr::left_join(
      shap_rnk %>%
        dplyr::distinct(idx, lab, rnk),
      by = c('idx', 'rnk')
    ) %>%
    dplyr::arrange(rnk) %>%
    dplyr::mutate(
      dplyr::across(lab, ~forcats::fct_reorder2(.x, idx, rnk)),
      dplyr::across(shap_value, ~dplyr::case_when(rnk == 0L ~ 0, TRUE ~ .x)),
      measure = 'relative'
    )
  shap_rnk_agg

  viz_shap <-
    shap_rnk_agg %>%
    # dplyr::filter(idx == 2L) %>%
    # filter(lab != 'Baseline') %>%
    plotly::plot_ly(
      x = ~ shap_value,
      y = ~ lab,
      # The sign thing throws off the plot.
      # color = ~ sign,
      measure = ~measure,
      type = 'waterfall',
      orientation = 'h',
      name = 'SHAP values',
      connector = list(
        mode = 'between',
        line = list(width = 4, color = 'rgb(0, 0, 0)', dash = 0)
      ),
      hovertemplate = paste('%{y}', '<br>SHAP value: %{x:.2f}<br>', '<extra></extra>'),
      showlegend = FALSE,
      ...
    ) %>%
    plotly::config(
      displaylogo = FALSE
    ) %>%
    plotly::layout(
      title = sprintf('Prediction Breakdown for %s', .upper1(stem)),
      font = list(
        family = 'Karla',
        size = 14
      ),
      xaxis = list(
        title = 'SHAP value',
        x = 0,
        y = 0,
        zeroline = TRUE
      ),
      yaxis = list(title = '', type = 'category')
    )
  viz_shap
}


# Reference: https://stackoverflow.com/questions/55505599/combine-formula-and-tidy-eval-plotly
plot_stem <- function(data, stem, ...) {
  
  pred_sym <- sprintf('%s_pred', stem) %>% rlang::sym()
  actual_sym <- sprintf('%s_count', stem) %>% rlang::sym()
  
  colors <- c('favorite' = '#bc5090', 'retweet' = '#ffa600')
  color <- unname(colors[stem])
  
  rlang::eval_tidy(
    rlang::quo_squash(
      rlang::quo({

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
            # separators = ',.',
            font = list(
              family = 'Karla',
              size = 14
            ),
            xaxis = list(title = ''),
            yaxis = list(title = '', tickformat = ',.')
          )
        
        lab_stem <- sprintf('%ss', .upper1(stem))
        lab_y <- sprintf('Actual # of %s', lab_stem)
        p1 <-
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
            xaxis = list(title = 'Time'),
            yaxis = list(title = lab_y)
          )
        
        p2 <-
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
            y = ~!!actual_sym
          ) %>% 
          plotly::layout(
            xaxis = list(title = sprintf('Predicted # of %s', lab_stem), tickformat = ',.'),
            yaxis = list(title = lab_y)
          )

        plotly::subplot(p1, p2, shareX = FALSE, shareY = TRUE, titleX = TRUE, titleY = TRUE)
      })
    )
  )
}

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
      
