
library(rlang)
library(tidyverse)
# library(plotly)

.import_data <- function(name) {
  url(sprintf('https://raw.githubusercontent.com/tonyelhabr/xengagement/master/inst/extdata/%s.rds', name)) %>% readr::read_rds()
}

# Note that I used to have post-processing for this stuff, hence the sparse looking wrappers now.
import_preds <- function() {
  .import_data('preds')
}

import_shap <- function() {
  .import_data('shap')
}

.upper1 <- function(x) {
  x <- tolower(x)
  substr(x, 1, 1) <- toupper(substr(x, 1, 1))
  x
}

# .shap_colors <- c('favorite' = '#7a5195', 'retweet' = '#ef5675')
.shap_colors <- c('neg' = '#7a5195', 'neutral' = '#7f7f7f', 'pos' = '#ef5675')
.stem_colors <- c('favorite' = '#003f5c', 'retweet' = '#ffa600')

.plot_shap <- function(data, stem, width = 1000, height = 600, ...) {
  shap_sym <- sprintf('%s_shap_value', stem) %>% rlang::sym()
  sign_sym <- sprintf('%s_sign', stem) %>% rlang::sym()
  lab_stem <- sprintf('%ss', .upper1(stem))
  
  rlang::eval_tidy(
    rlang::quo_squash(
      rlang::quo({
        p <-
          data %>% 
          plotly::plot_ly(
            showlegend = FALSE,
            type = 'bar',
            orientation = 'h',
            # color = I(color),
            color = ~ !!sign_sym,
            colors = .shap_colors,
            x = ~ !!shap_sym,
            y = ~ lab,
            hovertemplate = paste(
              '%{y}', 
              '<br>SHAP value: %{x:.2f}</br>', 
              '<extra></extra>'
            ),
            width = width,
            height = height,
            ...
          ) %>% 
          plotly::config(
            displaylogo = FALSE
          ) %>% 
          plotly::layout(
            # autosize = TRUE,
            font = list(
              family = 'Karla',
              size = 14
            ),
            yaxis = list(title = ''), # , type = 'category')
            xaxis = list(
              # title = 'SHAP value',
              title = sprintf('%s SHAP value', lab_stem),
              x = 0,
              y = 0,
              zeroline = TRUE
            )
          )
        p
      })
    )
  )
}

.plot_shap_agg <- function(data, stem, width = 1000, height = 300, ...) {
  shap_sym <- sprintf('%s_shap_value', stem) %>% rlang::sym()
  sign_sym <- sprintf('%s_sign', stem) %>% rlang::sym()
  color <- unname(.shap_colors[stem])
  # lab_stem <- sprintf('%ss', .upper1(stem))
  rlang::eval_tidy(
    rlang::quo_squash(
      rlang::quo({
        p <-
          data %>% 
          plotly::plot_ly(
            showlegend = FALSE,
            type = 'bar',
            text = ~lab,
            color = ~!!sign_sym,
            colors = unname(.shap_colors),
            x = ~!!sign_sym,
            y = ~ !!shap_sym,
            transforms = list(
              type = 'aggregate',
              target = 'y',
              func = 'sum',
              enabled = TRUE
            ),
            hovertemplate = paste(
              '%{text}',
              '<br>SHAP value: %{y:.2f}</br>', 
              '<extra></extra>'
            ),
            width = width,
            height = height,
            ...
          ) %>% 
          plotly::config(
            displaylogo = FALSE
          ) %>% 
          plotly::layout(
            # autosize = TRUE,
            font = list(
              family = 'Karla',
              size = 14
            ),
            yaxis = list(title = ''),
            xaxis = list(title = '')
          )
        p
      })
    )
  )
}

# This is basically exactly `plot_pred()`, but with the transform.
.plot_agg <- function(data, stem, width = 1000, height = 300, ...) {
  pred_sym <- sprintf('%s_pred', stem) %>% rlang::sym()
  actual_sym <- sprintf('%s_count', stem) %>% rlang::sym()
  lab_stem <- sprintf('%ss', .upper1(stem))
  lab_x <- sprintf('Predicted # of %s', lab_stem)
  lab_y <- sprintf('Actual # of %s', lab_stem)
  color <- unname(.stem_colors[stem])
  
  rlang::eval_tidy(
    rlang::quo_squash(
      rlang::quo({
        p <-
          data %>% 
          plotly::plot_ly(
            showlegend = FALSE,
            color = I(color),
            width = width,
            height = height,
            transforms = list(
              type = 'aggregate',
              target = 'y',
              func = 'sum',
              enabled = TRUE
            ),
            ...
          ) %>% 
          plotly::config(
            displaylogo = FALSE
          ) %>% 
          plotly::layout(
            # autosize = TRUE,
            # separators = ',.',
            font = list(
              family = 'Karla',
              size = 14
            ),
            xaxis = list(title = ''),
            yaxis = list(title = '', tickformat = ',.')
          ) %>% 
          plotly::add_markers(
            # hoverinfo = 'x+y',
            hovertemplate = paste(
              sprintf('<br>%s: %%{y:,d}', lab_y),
              sprintf('<br>%s: %%{x:,.0f}', lab_x),
              '<extra></extra>'
            ),
            x = ~ !!pred_sym,
            y = ~ !!actual_sym
          ) %>% 
          plotly::layout(
            xaxis = list(title = lab_x, tickformat = ',.'),
            yaxis = list(title = lab_y)
          )
        p
      })
    )
  )
}

do_plot_shap <- function(w1 = 1500, h1 = 1000, w2 = w1, h2 = 500, w3 = w2, h3 = h2, ...) {
  # data <- shap_key
  w1 = 4500; h1 = 3000; w2 = 1000; h2 = 1000; w3 = w2; h3 = h2
  shap <- import_shap()
  shap_key <- plotly::highlight_key(shap, ~text)
  p1 <- .plot_shap(shap_key, 'favorite', width = w1, height = h1)
  p2 <- .plot_shap(shap_key, 'retweet', width = w1, height = h1)
  p3 <- .plot_shap_agg(shap_key, 'favorite', width = w2, height = h2)
  p4 <- .plot_shap_agg(shap_key, 'retweet', width = w2, height = h2)
  p5 <- .plot_agg(shap_key, 'favorite', width = w3, height = h3)
  p6 <- .plot_agg(shap_key, 'retweet', width = w3, height = h3)
  p12 <- plotly::subplot(p1, p2, nrows = 1, shareX = FALSE, shareY = TRUE, titleX = TRUE, titleY = TRUE, margin = 0.04)
  p34 <- plotly::subplot(p3, p4, nrows = 1, shareX = FALSE, shareY = TRUE, titleX = TRUE, titleY = TRUE, margin = 0.04)
  p56 <- plotly::subplot(p5, p6, nrows = 1, shareX = FALSE, shareY = FALSE, titleX = TRUE, titleY = TRUE, margin = 0.04)
  res <- plotly::subplot(p12, p34, p56, nrows = 3, shareX = FALSE, shareY = FALSE, titleX = TRUE, titleY = TRUE, margin = 0.04)
  suppressWarnings(
    crosstalk::bscols(
      # htmltools::div(style = htmltools::css(width="100%", height="400px", background_color="red")),
      crosstalk::filter_select('id', 'Select a tweet', shap_key, ~text, multiple = FALSE),
      # htmltools::div(style = htmltools::css(width="100%", height="400px", background_color="green")),
      res,
      # widths = c(6, 6, 6, 6)
      widths = c(12, 12)
    )
  )
}

.plot_stem_base <- function(data, stem, width = 600, height = 600, ...) {
  color <- unname(.stem_colors[stem])
  
  base <-
    data %>% 
    plotly::plot_ly(
      showlegend = FALSE,
      text = ~text,
      color = I(color),
      width = width,
      height = height,
      ...
    ) %>% 
    plotly::config(
      displaylogo = FALSE
    ) %>% 
    plotly::layout(
      # autosize = TRUE,
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

.plot_actual_over_time <- function(data, stem, ...) {
  
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

.plot_actual_v_pred <- function(data, stem, ...) {
  
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

.plot_diff_prnk <- function(data, stem, ...) {
  prnk_sym <- sprintf('%s_diff_prnk', stem) %>% rlang::sym()
  diff_sym <- sprintf('%s_diff', stem) %>% rlang::sym()
  lab_stem <- sprintf('%ss', .upper1(stem))
  lab_x <- 'Percentile'
  lab_y <- sprintf('Actual - Predicted, # of %s', lab_stem)
  
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
              sprintf('<br>%s: %%{y:,.1f}', lab_y),
              sprintf('<br>%s: %%{x:,.0%%}', lab_x),
              '<extra></extra>'
            ),
            x = ~ !!prnk_sym,
            y = ~ !!diff_sym
          ) %>% 
          plotly::layout(
            xaxis = list(title = lab_x, tickformat = ',.0%'),
            yaxis = list(title = lab_y)
          )
        p
      })
    )
  )
}

do_plot_data_and_preds <- function(w1 = 1000, h1 = 600, w2 = w1, h2 = 300, w3 = w1, h3 = h2, ...) {
  w1 = 1400; h1 = 800; w2 = w1; h2 = h1; w3 = w1; h3 = h2
  preds <- import_preds()
  preds_key <- plotly::highlight_key(preds, ~text)
  p1 <- .plot_actual_over_time(preds_key, 'favorite', width = w1, height = h1)
  p2 <- .plot_actual_over_time(preds_key, 'retweet', width = w1, height = h1)
  p3 <- .plot_actual_v_pred(preds_key, 'favorite', width = w2, height = h2)
  p4 <- .plot_actual_v_pred(preds_key, 'retweet', width = w2, height = h2)
  p5 <- .plot_diff_prnk(preds_key, 'favorite', width = w3, height = h3)
  p6 <- .plot_diff_prnk(preds_key, 'retweet', width = w3, height = h3)
  p12 <- plotly::subplot(p1, p2, nrows = 2, shareX = FALSE, shareY = FALSE, titleX = TRUE, titleY = TRUE, margin = 0.04)
  p34 <- plotly::subplot(p3, p4, nrows = 2, shareX = FALSE, shareY = FALSE, titleX = TRUE, titleY = TRUE, margin = 0.04)
  p56 <- plotly::subplot(p5, p6, nrows = 2, shareX = FALSE, shareY = FALSE, titleX = TRUE, titleY = TRUE, margin = 0.04)
  res <- plotly::subplot(p12, p34, p56, nrows = 1, shareX = FALSE, shareY = FALSE, titleX = TRUE, titleY = TRUE, margin = 0.04)
  res
}

