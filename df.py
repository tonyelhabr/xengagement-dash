#%%
import pandas as pd
import numpy as np
# from jupyter_dash import JupyterDash
import datetime
#%%
shap = pd.read_csv('shap.csv')
shap

#%%
shap.columns
#%%
df = pd.read_csv('preds.csv')

#%%
df['lab_hover'] = df['tm_h'] + ' ' + df['g_h'].astype(str) + '-' + df[
    'g_a'].astype(str) + ' ' + df['tm_a']
df['lab_hover']
#%%
preds.sort_values('created_at', ascending=False, inplace=True)
preds['date'] = pd.to_datetime(preds['created_at']).dt.date
preds['date'][0]
#%%
created_at_max = preds['created_at'].max()
initial_text = preds.loc[preds['created_at'] ==
                         created_at_max, :]['text'].to_string()
initial_text
#%%
preds['date'] = pd.to_datetime(preds['created_at'], format='%Y-%m-%d')
preds.sort_values('created_at', ascending=False, inplace=True)
preds['date'].iloc[-1]
min_date = preds['date'][:-100].min()
max_date = preds['date'][100:].max()
start_date, end_date = min_date, max_date
start_date, end_date

#%%
preds['date'][100:]
#%%

mask = ((preds['date'] >= start_date) & (preds['date'] <= end_date))
preds_filt = preds.loc[mask, :]
preds_filt

# %%

# %%
preds['date'].min().date
#%%
today = pd.to_datetime('today')
opts = {}
days = [7, 30, 90, 180, 365]

for d in days:
    x = preds[preds['date'] >= (today - pd.Timedelta(days=d))]
    x = np.sort(x['text'].unique())
    opts[f'Past {d} days'] = x

opts['All'] = np.sort(preds['text'].unique())
# %%
opts
# %%
preds.iloc[::-1]
# %%

preds
# %%

# %%
