
from .moving_average import moving_average_crossover

STRATEGIES = {
    "ma_crossover": moving_average_crossover,
}

def get_strategy(name: str):
    if name not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {name}")
    return STRATEGIES[name]
