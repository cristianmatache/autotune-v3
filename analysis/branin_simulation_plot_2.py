from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
from typing import Union


from autotune.core import Domain, Param

PLOT_SURFACE = False
HYPERPARAMS_DOMAIN = Domain(
    x=Param('x', -5, 10, distrib='uniform', scale='linear'),
    y=Param('y', 1, 15, distrib='uniform', scale='linear'))


def branin(x1: Union[int, np.ndarray], x2: Union[int, np.ndarray]) -> Union[int, np.ndarray]:
    a = 1
    b = 5.1 / (4 * np.pi ** 2)
    c = 5 / np.pi
    r = 6
    s = 10
    t = 1 / (8 * np.pi)

    f = a * (x2 - b * x1 ** 2 + c * x1 - r) ** 2 + s * (1 - t) * np.cos(x1) + s
    return f


def get_aggressiveness_from_gamma_distrib(time: int, n: int, k: int) -> float:
    sqrt_beta_component = np.sqrt(k**2 + 4 * (n - time))
    beta_t = (k + sqrt_beta_component) / (2*(n-time))  # beta is increasing in terms of time so variance is decreasing
    alpha_t = k * beta_t + 1  # mode is always k (threshold for 0 aggressiveness)

    shape = alpha_t
    scale = 1 / beta_t

    aggresiveness = np.random.gamma(shape, scale)

    # x = np.linspace(0, 20, 200)
    # y = stats.gamma.pdf(x, a=shape, scale=scale)
    # plt.plot(x, y, "y-", label=r'$\alpha=29, \beta=3$')
    return aggresiveness


def branin_simulate_ml(x1: Union[int, np.ndarray], x2: Union[int, np.ndarray], time: int = 0,
                       n: int = 81) -> Union[int, np.ndarray]:
    k = 2      # mode of gamma distribution - corresponds to 0 aggressiveness
    h1 = 0.6   # proportion of ml aggressiveness (the higher h1 the more it bites from function debt)
    h2 = 2     # necessary aggressiveness (the higher h2 the later necessary aggressiveness starts-flattens tail later)
    h3 = 0.15  # up spikiniess (the lower h3 the smoother the function - up spikes, the higher h3 the more up spikes)

    if time == 0:
        return branin(x1, x2)

    f_n = branin(x1, x2) - 200
    fs = [branin(x1, x2)]
    print(f"Starting from: {branin(x1, x2)}  and aiming to finish at: {f_n}")

    for t in range(time):
        agg = get_aggressiveness_from_gamma_distrib(t, n + 1, k)
        if agg == k:  # be neutral
            f_next_time = fs[-1]
        elif agg > k:  # be aggressive - go down with different aggressivenesses
            absolute_aggressiveness = agg - k
            function_debt = f_n - fs[-1]
            ml_aggressed = fs[-1] + absolute_aggressiveness * h1 * function_debt / 100
            time_aggressed = (f_n - ml_aggressed) * ((t / (n - 1)) ** h2)
            f_next_time = ml_aggressed + time_aggressed
        else:  # aggressiveness < k - go up
            time_left = n - t
            f_next_time = fs[-1] + h3 * time_left
            if time_left == 1:
                f_next_time = f_n
        fs.append(f_next_time)

    plt.plot(list(range(time+1)), fs)
    return fs[-1]


def plot_branin_surface(n_resources: int, n_simulations: int) -> None:
    xs = []
    ys = []
    for i in range(n_simulations):
        xs.append(HYPERPARAMS_DOMAIN["x"].get_param_range(1, stochastic=True)[0])
        ys.append(HYPERPARAMS_DOMAIN["y"].get_param_range(1, stochastic=True)[0])

    xs = np.array(xs, dtype="float64")
    ys = np.array(ys, dtype="float64")

    if n_resources == 0:
        zs = branin(xs, ys)  # just to check branin works in vectorial form
    else:
        zs = []
        for i in range(n_simulations):
            z = branin_simulate_ml(xs[i], ys[i], time=n_resources, n=n_resources)
            assert z == branin(xs[i], ys[i]) - 200
            zs.append(branin(xs[i], ys[i]))
        zs = np.array(zs, dtype="float64")

    fig = plt.figure()
    ax = fig.gca(projection=Axes3D.name)
    surf = ax.plot_trisurf(xs, ys, zs, cmap="coolwarm", antialiased=True)
    fig.colorbar(surf, shrink=0.5, aspect=5)

    plt.show()


def plot_simulations(n_resources: int, n_simulations: int) -> None:
    def evaluate_once() -> None:
        x = HYPERPARAMS_DOMAIN["x"].get_param_range(1, stochastic=True)[0]
        y = HYPERPARAMS_DOMAIN["y"].get_param_range(1, stochastic=True)[0]
        branin_simulate_ml(x, y, time=n_resources, n=n_resources)

    [evaluate_once() for _ in range(n_simulations)]
    plt.show()


if __name__ == "__main__":
    if PLOT_SURFACE:
        plot_branin_surface(n_resources=81, n_simulations=1000)
    else:
        plot_simulations(n_resources=81, n_simulations=5)
