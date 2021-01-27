
# setup ----
# install.packages('remotes')
# install.packages('pak')
remotes::install_github('tonyelhabr/xengagement')
# pak::pkg_install('tonyelhabr/xengagement')

# suppressPackageStartupMessages({
#   library(xengagement)
#   library(dplyr)
#   library(forcats)
#   library(tidyr)
#   library(purrr)
#   library(arrow)
#   library(readr)
#   library(yardstick)
# })

library(xengagement)
options(xengagement.dir_data = 'data')
dir_data <- xengagement::get_dir_data()
valid_stems <- xengagement::get_valid_stems()
cols_lst <- xengagement::get_cols_lst(valid_stems[1]) # Doesn't matter what the target variable is.

# data refresh ----
.f_transform <- function() {
  tweets <- xengagement:::retrieve_tweets(method = 'new')
  tweets %>% xengagement:::transform_tweets(train = FALSE)
}

tweets_transformed <-
  xengagement:::do_get(
    f = .f_transform,
    path = file.path(dir_data, 'tweets_transformed.parquet'),
    f_import = arrow::read_parquet,
    f_export = arrow::write_parquet,
    overwrite = TRUE,
    export = TRUE
  )
tweets_transformed

res_preds <-
  dplyr::tibble(
    stem = valid_stems,
    fit = list(xengagement::fit_favorites, xengagement::fit_retweets)
  ) %>% 
  dplyr::mutate(
    res = purrr::map2(
      stem, fit,
      ~ xengagement::do_predict(
        tweets_transformed = tweets_transformed,
        stem = ..1,
        fit = ..2,
        .overwrite = list(preds = TRUE, shap = TRUE)
      )
    )
  )
res_preds

# dashboard predp ---
.path_data_csv <- purrr::partial(xengagement:::.path_data, ext = 'csv', ... = )

# shap export ----
# Maybe this should be exported tweets_transformed (with `usethis::use_data()`)?
cols_x <- 
  dplyr::tibble(
    lab = c(cols_lst$cols_x_names, 'Baseline'),
    feature = c(cols_lst$cols_x, 'baseline')
  )
cols_x

tweets_transformed <- file.path(dir_data, 'tweets_transformed.parquet') %>% arrow::read_parquet()
tweets_transformed

tweets_rescaled_long <-
  tweets_transformed %>% 
  dplyr::select(
    dplyr::all_of(cols_lst$cols_id),
    dplyr::any_of(cols_lst$cols_x)
  ) %>% 
  as.data.frame() %>% 
  dplyr::mutate(dplyr::across(-idx, scales::rescale)) %>% 
  tidyr::gather(
    'feature',
    'value',
    -c(idx)
  ) %>% 
  dplyr::as_tibble()
tweets_rescaled_long

.f_import_shap <- function(stem) {
  path <- file.path(dir_data, sprintf('shap_%s.parquet', stem))
  shap <- path %>% arrow::read_parquet()
  shap_long <-
    shap %>%
    tidyr::pivot_longer(
      -c(idx, .pred, .actual),
      names_to = 'feature',
      values_to = 'shap_value'
    ) %>%
    dplyr::mutate(sign = dplyr::if_else(shap_value < 0, 'neg', 'pos') %>% factor())
  shap_long
  
  res <-
    shap_long %>% 
    dplyr::full_join(
      tweets_rescaled_long, by = c('idx', 'feature')
    ) %>% 
    dplyr::left_join(cols_x, by = c('feature'))
  res
}

shap <-
  valid_stems %>%
  setNames(., .) %>% 
  purrr::map_dfr(.f_import_shap, .id = 'stem') %>% 
  dplyr::rename(pred = .pred, count = .actual) %>% 
  tidyr::pivot_wider(
    names_from = stem,
    values_from = c(pred, count, sign, shap_value),
    names_glue = '{stem}_{.value}'
  ) %>% 
  dplyr::mutate(dplyr::across(where(is.numeric), ~dplyr::coalesce(.x, 0))) %>% 
  dplyr::left_join(preds %>% dplyr::select(idx, text), by = 'idx') %>% 
  dplyr::filter(feature != 'baseline') %>% 
  dplyr::mutate(dplyr::across(text, ~forcats::fct_reorder(.x, dplyr::desc(.x)))) %>% 
  dplyr::arrange(idx, feature)
shap
readr::write_csv(shap, .path_data_csv(file = 'shap'))

# preds export ----
.f_import_preds <- function(stem) {
  path <- file.path(dir_data, sprintf('preds_%s.parquet', stem))
  col_res_sym <- sprintf('%s_diff', stem) %>% dplyr::sym()
  res <- 
    path %>% 
    arrow::read_parquet() %>% 
    dplyr::rename_with(~sprintf('%s_pred', stem), .cols = c(.pred)) %>% 
    dplyr::select(-dplyr::matches('_log$')) %>% 
    dplyr::mutate(
      !!col_res_sym := !!dplyr::sym(sprintf('%s_count', stem)) - !!dplyr::sym(sprintf('%s_pred', stem)),
    ) %>% 
    dplyr::mutate(
      dplyr::across(
        !!col_res_sym,
        list(prnk = ~dplyr::percent_rank(.x))
      )
    )
  res
}

suppressMessages(
  preds <-
    valid_stems %>%
    purrr::map(.f_import_preds) %>%
    purrr::reduce(dplyr::full_join) %>%
    dplyr::select(
      dplyr::one_of(cols_lst$cols_id),
      dplyr::one_of(cols_lst$cols_extra),
      dplyr::matches('^(favorite|retweet)_')
    )
)
preds <-
  preds %>% 
  dplyr::mutate(
    favorite_diff = favorite_count - favorite_pred,
    retweet_diff = retweet_count - retweet_pred,
    dplyr::across(dplyr::matches('_diff$'), list(prnk = ~dplyr::percent_rank(.x))),
    dplyr::across(
      text,
      ~ sprintf(
        '%s: %s (%.2f) %d-%d (%.2f) %s',
        lubridate::date(created_at),
        # lubridate::hour(created_at),
        # lubridate::wday(created_at, label = TRUE),
        tm_h,
        xg_h,
        g_h,
        g_a,
        xg_a,
        tm_a
      )
    ),
    lab_hover = 
      sprintf(
        '%s (%.2f) %d-%d (%.2f) %s',
        tm_h,
        xg_h,
        g_h,
        g_a,
        xg_a,
        tm_a
      )
  ) %>% 
  dplyr::arrange(idx)
preds
# readr::write_csv(preds, .path_data_csv(file = 'preds'))

# TODO
mape_favorite <-
  preds %>% 
  yardstick::mape(favorite_pred, favorite_count)

mape_retweet <-
  preds %>% 
  yardstick::mape(retweet_pred, retweet_count)

mapes <- mape_favorite$.estimate + mape_retweet$.estimate
# Yes, flip the weights so that the more accurate one gets higher weighting
wt_favorite <- mape_retweet$.estimate / mapes
wt_retweet <- mape_favorite$.estimate / mapes

# # Need the actual ranges? Or can use pranks of differences
preds_agg <-
  preds %>%
  dplyr::summarize(
    dplyr::across(dplyr::matches('^(favorite|retweet)_(count)$'), range)
  ) %>%
  dplyr::mutate(
    idx = dplyr::row_number(),
    stat = dplyr::if_else(idx == 1L, 'min', 'max')
  ) %>%
  dplyr::select(-idx)
preds_agg

preds_agg <-
  preds %>%
  dplyr::summarize(
    dplyr::across(dplyr::matches('^(favorite|retweet)_(count)$'), list(min = min, max = max))
  )
preds_agg

scaling_factor <-
  preds_agg %>% 
  dplyr::transmute(
    z = (favorite_count_max - favorite_count_min) / (retweet_count_max - retweet_count_min)
  ) %>% 
  dplyr::pull(z)
scaling_factor

res <-
  preds %>%
  # TODO: This is just an approximation for now. Should actually use a re-scaling function (with `preds_agg`).
  dplyr::mutate(
    retweet_diff_scaled = !!scaling_factor * retweet_diff
  ) %>%
  dplyr::mutate(
    total_diff = !!wt_favorite * favorite_diff + !!wt_retweet * retweet_diff_scaled,
    # total_diff_frac = total_diff / (favorite_count + retweet_count)
    dplyr::across(total_diff, list(prnk = ~dplyr::percent_rank(.x), rnk = ~dplyr::row_number(dplyr::desc(.x))))
  ) %>%
  dplyr::select(-dplyr::matches('_scaled$')) %>% 
  dplyr::arrange(total_diff_rnk)
res %>% dplyr::select(total_diff_prnk, total_diff, text, tm_h, tm_a) %>% dplyr::arrange(total_diff_prnk)
readr::write_csv(res, file.path(dir_data, 'preds.csv'), na = '')
