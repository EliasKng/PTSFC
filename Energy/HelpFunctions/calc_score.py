def evaluate_quantile(q, tau, y):
    l_score = None

    if q > y:
        l_score = 2 * (1 - tau) * (q - y)
    else:
        l_score = 2 * tau * (y - q)

    return l_score


def evaluate_horizon(quantiles, y):
    taus = [0.025, 0.25, 0.5, 0.75, 0.975]

    if len(quantiles) != 5:
        raise ValueError("The quantiles must consist of five elements.")

    total_sum = 0

    for q, tau in zip(quantiles, taus):
        l_score = evaluate_quantile(q, tau, y)
        total_sum += l_score
        print(f"Calculate score for: q = {q}, tau = {tau}: {l_score}")

    return total_sum

print(evaluate_horizon([32, 35, 37, 41, 47], 42))
