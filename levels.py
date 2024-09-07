
def get_columns_based_on_score(score):
    if score == 1:
        return 3
    elif score >= 2:
        return 6
    else:
        return 1
