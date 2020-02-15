import os
from typing import NoReturn, Tuple, Union

from matplotlib import pyplot as plt
import numpy as np


class Solver:
    def __init__(self, input_folder: str) -> NoReturn:
        self.a_hat: np.ndarray = np.loadtxt(os.path.join(input_folder, "a.txt"))
        self.i_d_hat: np.ndarray = np.loadtxt(os.path.join(input_folder, "i_d.txt"))
        self.i_p_hat: np.ndarray = np.loadtxt(os.path.join(input_folder, "i_p.txt"))
        self.i_t_hat: np.ndarray = np.loadtxt(os.path.join(input_folder, "i_t.txt"))
        self.mask = self.a_hat != 0
        self.alpha: np.ndarray = np.empty(0)
        self.beta: np.ndarray = np.empty(0)
        self.gamma: np.ndarray = np.empty(0)

    def count_alpha(self) -> np.ndarray:
        alpha: np.ndarray = np.zeros(self.a_hat.shape)
        alpha[self.mask] = (1 + self.a_hat[self.mask] * self.i_p_hat[self.mask]) / (
            1 + 0.05 * self.a_hat[self.mask]
        )
        return alpha

    def count_beta(self) -> np.ndarray:
        beta: np.ndarray = np.zeros(self.a_hat.shape)
        beta[self.mask] = (1 + 0.01 * self.i_p_hat[self.mask]) / (
            1 + self.i_t_hat[self.mask] ** 2 * (1 + self.a_hat[self.mask])
        )
        return beta

    def count_gamma(self) -> np.ndarray:
        gamma: np.ndarray = np.zeros(self.a_hat.shape)
        gamma[self.mask] = (
            1 + self.a_hat[self.mask] * self.i_d_hat[self.mask]
        ) ** 2 / (1 + 10 * self.beta[self.mask] + 5 * (1 + self.a_hat[self.mask] ** 3))
        return gamma

    def i_p(self, t: float) -> np.ndarray:
        output: np.ndarray = np.zeros(self.a_hat.shape)
        output[self.mask] = (
            self.i_p_hat[self.mask]
            * (1 + self.alpha[self.mask] ** 2 * t)
            * (1 + self.beta[self.mask] ** 2)
            * (1 + self.gamma[self.mask] ** 2)
        )
        output[output > 1] = 1
        return output

    def i_d(self, t: float) -> np.ndarray:
        output: np.ndarray = np.zeros(self.a_hat.shape)
        output[self.mask] = (
            0.01
            * self.i_d_hat[self.mask]
            * (1 + self.alpha[self.mask] + self.gamma[self.mask]) ** 2
            * (1 + self.beta[self.mask] * t) ** 2
        )
        output[output > 1] = 1
        return output

    def i_t(self, t: float) -> np.ndarray:
        output: np.ndarray = np.zeros(self.a_hat.shape)
        output[self.mask] = (
            self.i_t_hat[self.mask] * (1 - self.beta[self.mask] * t) ** 3
        )
        output[output < 0] = 0
        return output

    def i(self, t: float) -> np.ndarray:
        return self.i_t(t) * self.i_p(t) * self.i_d(t)

    def solve(self):
        self.alpha: np.ndarray = self.count_alpha()
        self.beta: np.ndarray = self.count_beta()
        self.gamma: np.ndarray = self.count_gamma()

    def plot_i(
        self,
        s: int = 0,
        f: int = 0,
        t_range_edges: Tuple[Union[int, float]] = (0, 5),
        delta: float = 0.01,
    ) -> NoReturn:
        t_min, t_max = t_range_edges[0], t_range_edges[1]
        t_range: np.ndarray = np.arange(t_min, t_max, delta)
        i_t_range: np.ndarray = np.array([self.i_t(t)[s, f] for t in t_range])
        i_d_range: np.ndarray = np.array([self.i_d(t)[s, f] for t in t_range])
        i_p_range: np.ndarray = np.array([self.i_p(t)[s, f] for t in t_range])
        plt.plot(t_range, i_p_range)
        plt.show()