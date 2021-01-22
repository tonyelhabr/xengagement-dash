
.upper1 <- function(x) {
  x <- tolower(x)
  substr(x, 1, 1) <- toupper(substr(x, 1, 1))
  x
}

plot_shap <- function(idx_filt = 1, stem_filt = 'favorite') {
  # idx_filt <- 220
  # stem_filt <- 'favorite'
  
  shap_filt <- 
    shap %>% 
    filter(idx == !!idx_filt & stem == !!stem_filt)
  
  # Reference: https://learnui.design/tools/data-color-picker.html#palette
  # config values: 'staticPlot', 'plotlyServerURL', 'editable', 'edits', 'autosizable', 'responsive', 'fillFrame', 'frameMargins', 'scrollZoom', 'doubleClick', 'doubleClickDelay', 'showAxisDragHandles', 'showAxisRangeEntryBoxes', 'showTips', 'showLink', 'linkText', 'sendData', 'showSources', 'displayModeBar', 'showSendToCloud', 'showEditInChartStudio', 'modeBarButtonsToRemove', 'modeBarButtonsToAdd', 'modeBarButtons', 'toImageButtonOptions', 'displaylogo', 'watermark', 'plotGlPixelRatio', 'setBackground', 'topojsonURL', 'mapboxAccessToken', 'logging', 'notifyOnLogging', 'queueLength', 'globalTransforms', 'locale', 'locales'
  rnk_max <- 12L
  colors <- c('neg' = '#003f5c', 'pos' = '#ffa600') # , 'neutral' = '#bc5090')
  
  shap_baseline <-
    shap_filt %>%
    filter(feature == 'baseline')
  
  shap_rnk_init <-
    shap_filt %>%
    anti_join(shap_baseline %>% select(feature), by = c('feature')) %>% 
    mutate(
      abs = shap_value %>% abs(),
      rnk_init = row_number(desc(abs))
    )
  shap_rnk_init
  
  shap_features_small <-
    shap_rnk_init %>% 
    filter(rnk_init >= !!rnk_max) %>% 
    mutate(rnk = !!rnk_max + 1L)
  shap_features_small
  
  shap_rnk_init_nonagg <-
    shap_rnk_init %>% 
    anti_join(shap_features_small %>% select(feature), by = c('feature')) %>% 
    mutate(
      temp = ifelse(shap_value < 0, min(shap_value) - shap_value, shap_value),
      rnk = row_number(desc(temp)),
    ) %>% 
    select(-temp) %>% 
    arrange(rnk)
  shap_rnk_init_nonagg
  
  shap_first_neg <-
    shap_rnk_init_nonagg %>% 
    filter(shap_value < 0) %>% 
    slice_min(rnk)
  shap_first_neg
  
  rnk_crossover <- shap_first_neg$rnk
  rnk_crossover
  
  shap_value_pos <-
    shap_rnk_init_nonagg %>% 
    filter(rnk < !!rnk_crossover) %>% 
    pull(shap_value) %>% 
    sum()
  shap_value_pos
  
  shap_value_baseline <- shap_baseline$shap_value
  
  shap_rnk <-
    list(
      shap_baseline %>% mutate(rnk = 0L),
      shap_rnk_init_nonagg %>% 
        mutate(across(rnk, ~ifelse(.x >= !!rnk_crossover, .x + 1, .x))),
      tibble(feature = NA_character_, lab = ' ', rnk = !!rnk_crossover),
      shap_features_small
    ) %>% 
    reduce(bind_rows) %>% 
    filter(rnk != rnk_crossover) %>% 
    mutate(
      across(shap_value, ~coalesce(.x, 0)),
      # across(rnk, ~ifelse(.x > !!rnk_max, rnk_max + 1L, .x)),
      across(lab, ~ifelse(rnk > !!rnk_max, 'Other Features', .x))
    ) %>% 
    arrange(rnk) %>% 
    fill(stem, .pred, idx)
  shap_rnk
  
  shap_rnk_agg <-
    shap_rnk %>% 
    group_by(stem, idx, .pred, rnk) %>% 
    summarize(shap_value = sum(shap_value)) %>% 
    ungroup() %>% 
    arrange(rnk) %>% 
    left_join(shap_rnk %>% distinct(stem, lab, rnk)) %>% 
    mutate(
      # Have to regenerate this column after aggregating SHAP values for ranks > `rnk_max`.
      sign = case_when(
        shap_value < 0 ~ 'neg', 
        shap_value > 0 ~ 'pos',
        # This is for the added bar in the middle and for any SHAP values that happen to be 0 (very unlikely)
        TRUE ~ 'neutral'
      )
    ) %>% 
    arrange(rnk) %>% 
    mutate(
      across(lab, ~fct_reorder(.x, rnk)),
      # measure = ifelse(rnk == 0L | rnk == !!rnk_crossover, 'total', 'relative
      measure = case_when(rnk == !!rnk_crossover ~ 'relative', TRUE ~ 'relative'),
      # across(shap_value, ~case_when(rnk == !!rnk_crossover ~ !!shap_value_pos + !!shap_value_baseline, TRUE ~ .x))
      across(shap_value, ~case_when(rnk == !!rnk_crossover | rnk == 0L ~ 0, TRUE ~ .x))
    )
  shap_rnk_agg
  
  viz_shap <-
    shap_rnk_agg %>% 
    # filter(lab != 'Baseline') %>% 
    filter(lab != ' ') %>% 
    plotly::plot_ly(
      x = ~ shap_value,
      y = ~ lab,
      # The sign thing throws off the plot.
      # color = ~ sign,
      measure = ~measure,
      # text = ~shap_value,
      # colors = colors,
      type = 'waterfall',
      orientation = 'h', 
      name = 'SHAP values',
      connector = list(
        mode = 'between', 
        line = list(width = 4, color = 'rgb(0, 0, 0)', dash = 0)
      ),
      hovertemplate = paste('%{y}', '<br>SHAP value: %{x:.2f}<br>'),
      showlegend = FALSE
    ) %>%
    plotly::config(
      displaylogo = FALSE
    ) %>% 
    plotly::layout(
      title = sprintf('Prediction Breakdown for %s', .upper1(stem_filt)),
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
      yaxis = list(title = '', type = 'category', autorange = 'reversed')
    )
  viz_shap
}
