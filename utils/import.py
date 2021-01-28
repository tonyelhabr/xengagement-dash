

def import_shap():
    return pd.read_csv('data/shap.csv')


def import_preds():
    preds = pd.read_csv('data/preds.csv')
    preds.sort_values('created_at', ascending=False, inplace=True)
    preds['date'] = pd.to_datetime(preds['created_at']).dt.date
    preds['total_diff_prnk'] = preds['total_diff_prnk'] * 100
    return preds