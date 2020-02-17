import sys
from typing import NoReturn


sys.path.append("../")
if True:
    from backend import Solver, CustomSolver


def main() -> NoReturn:
    parameters = dict(input_folder="../data/variant_5")
    solver = CustomSolver(**parameters)
    solver.solve()
    solver.plot_i()


if __name__ == "__main__":
    main()
