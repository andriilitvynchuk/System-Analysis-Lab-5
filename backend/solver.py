import os
from typing import NoReturn, Tuple, Union, List

from matplotlib import pyplot as plt
import numpy as np


class Solver:
    def __init__(
        self, input_folder: str, classification_thresholds: Tuple[float] = (0.3, 0.7)
    ) -> NoReturn:
        self.a_hat: np.ndarray = np.loadtxt(os.path.join(input_folder, "a.txt"))
        self.i_d_hat: np.ndarray = np.loadtxt(os.path.join(input_folder, "i_d.txt"))
        self.i_p_hat: np.ndarray = np.loadtxt(os.path.join(input_folder, "i_p.txt"))
        self.i_t_hat: np.ndarray = np.loadtxt(os.path.join(input_folder, "i_t.txt"))
        self.mask = self.a_hat != 0
        self.alpha: np.ndarray = np.empty(0)
        self.beta: np.ndarray = np.empty(0)
        self.gamma: np.ndarray = np.empty(0)
        self.t_0: List[List[List[float], str]] = [
            [[0, 0] for _ in range(self.a_hat.shape[1])]
            for _ in range(self.a_hat.shape[0])
        ]
        self.classification_thresholds: Tuple[float] = classification_thresholds
        self.situation_classification: List[str] = []

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

    def eta(self, t: float) -> np.ndarray:
        output: np.ndarray = np.zeros(self.a_hat.shape)
        output[self.mask] = 1 - np.log(
            1 + (self.alpha[self.mask] + 220) * self.i(t)[self.mask]
        )
        return output

    def solve(
        self, eta_max: float = 0.9, t_max: int = 20
    ) -> Tuple[List[List[List[float], str]], List[str]]:
        self.alpha: np.ndarray = self.count_alpha()
        self.beta: np.ndarray = self.count_beta()
        self.gamma: np.ndarray = self.count_gamma()

        for s_index in range(self.a_hat.shape[0]):
            t_0_min = np.inf
            for f_index in range(self.a_hat.shape[1]):
                if self.a_hat[s_index, f_index] != 0:
                    tmp_t_range = []
                    for t_index in np.arange(0, 20, 0.1):
                        if 0 < self.eta(t_index)[s_index][f_index] < eta_max:
                            tmp_t_range.append(t_index)
                    if len(tmp_t_range) > 0:
                        self.t_0[s_index][f_index] = (
                            min(tmp_t_range),
                            max(tmp_t_range),
                        )
                        t_0_min = min(t_0_min, max(tmp_t_range))
                    else:
                        self.t_0[s_index][f_index] = "Not exist"
                        t_0_min = 0
                else:
                    self.t_0[s_index][f_index] = "Not available"
            if t_0_min < self.classification_thresholds[0]:
                self.situation_classification.append("Особливо небезпечна ситуація")
            elif t_0_min < self.classification_thresholds[1]:
                self.situation_classification.append(
                    "Клас потенційно небезпечних ситуацій"
                )
            else:
                self.situation_classification.append("Клас майже безпечних ситуацій")
        return self.t_0, self.situation_classification

    def plot_i(
        self,
        s: int = 0,
        f: int = 0,
        t_range_edges: Tuple[Union[int, float]] = (0, 50),
        delta: float = 0.01,
    ) -> NoReturn:
        t_min, t_max = t_range_edges[0], t_range_edges[1]
        t_range: np.ndarray = np.arange(t_min, t_max, delta)
        i_t_range: np.ndarray = np.array([self.i_t(t)[s, f] for t in t_range])
        i_d_range: np.ndarray = np.array([self.i_d(t)[s, f] for t in t_range])
        i_p_range: np.ndarray = np.array([self.i_p(t)[s, f] for t in t_range])
        fig, axis = plt.subplots(3, sharey=True, figsize=(12, 8))
        fig.suptitle("Зміна показників інформованості у процесі формування рішення")
        axis[0].plot(t_range[i_d_range < 1], i_d_range[i_d_range < 1])
        axis[1].plot(t_range[i_p_range < 1], i_p_range[i_p_range < 1])
        axis[2].plot(t_range[i_t_range > 0], i_t_range[i_t_range > 0])
        axis[0].set_title("І_Д")
        axis[1].set_title("І_П")
        axis[2].set_title("І_Т")
        plt.show()
