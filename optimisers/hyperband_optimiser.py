from math import log, ceil
from typing import Callable, Tuple, List, Dict, Union
from colorama import Style, Fore

from core.optimiser import Optimiser
from core.evaluator import Evaluator
from core.arm import Arm
from core.optimization_goals import OptimizationGoals
from core.problem_def import HyperparameterOptimizationProblem

COL = Fore.MAGENTA


class HyperbandOptimiser(Optimiser):

    """ Examples of resources:
    1 Resource  = 10 000 training examples
    1 Resources = 1 epoch
    """

    def __init__(self, eta: int, max_iter: int = None, max_time: int = None,
                 optimization_goal: str = "test_error", min_or_max: Callable = min):
        super().__init__(max_iter, max_time, optimization_goal, min_or_max)
        self.name = "Hyperband"
        if max_iter is None:
            raise ValueError("For Hyperband max_iter cannot be None")
        self.eta = eta

    def _get_opt_goal_val(self, evaluation: Tuple[Evaluator, OptimizationGoals]) -> float:
        """ Given an evaluator and the result(s) of its evaluate() method retrieves the value of the optimization goal.
        For example: if we are optimizing in terms of validation error (i.e. self.optimization_goal = "val_error")
        this function will return the validation error that corresponds to evaluator.evaluate().val_error.
        :param evaluation: an ordered pair (evaluator, result of evaluator's evaluate() method)
        :return: the value of the optimization goal (Eg. evaluator.evaluate().val_error if we minimize validation error)
        """
        return getattr(evaluation[1], self.optimization_goal)

    def _get_best_n_evaluators(self, n: int, evaluators_and_res: List[Tuple[Evaluator, OptimizationGoals]]) \
            -> List[Evaluator]:
        """ Supposing we want to optimize (min) in terms of validation error (i.e. self.optimization_goal = "val_error")
        Given a list of evaluators and their results [(evaluator, optimization_goals)] this function returns the
        list of the evaluators that yielded the smallest n optimization_goals.val_error(s).
        Note that for minimization we sort in ascending order while for maximization we sort in descending order.
        :param n: number of top "best evaluators" to retrieve
        :param evaluators_and_res: A list of ordered pairs (evaluator, result of evaluator's evaluate() method)
        :return: best n evaluators (those evaluators that gave the best n values on self.optimization_goal)
        """
        is_descending = self.min_or_max == max
        sorted_evaluators_by_res = sorted(evaluators_and_res, key=self._get_opt_goal_val, reverse=is_descending)
        sorted_evaluators = [e_r[0] for e_r in sorted_evaluators_by_res]
        return sorted_evaluators[:n]

    def run_optimization(self, problem: HyperparameterOptimizationProblem, verbosity: bool = False) \
            -> Dict[str, Union[Arm, float]]:
        self._init_optimizer_metrics()

        R = self.max_iter  # maximum amount of resource that can be allocated to a single hyperparameter configuration
        eta = self.eta     # halving rate

        def log_eta(x: int) -> int: return int(log(x)/log(eta))
        s_max = log_eta(R)              # number of unique executions of Successive Halving (minus one)
        s_min = 2 if s_max >= 2 else 0  # skip the rest of the brackets after s_min
        B = (s_max + 1) * R             # total/max resources (without reuse) per execution of Successive Halving

        # Exploration-exploitation trade-off management outer loop
        for s in reversed(range(s_min, s_max + 1)):
            n = int(ceil(int(B/R/(s+1))*eta**s))  # initial number of evaluators/configurations/arms
            r = R*eta**(-s)                       # initial resources allocated to each evaluator/arm

            evaluators = [problem.get_evaluator() for _ in range(n)]
            print(f"{COL}\n{'=' * 73}\n>> Generated {n} evaluators each with a random arm {Style.RESET_ALL}")

            # Successive halving with rate eta - based on values of self.optimization_goal of each evaluation
            for i in range(s+1):
                n_i = n*eta**(-i)  # evaluate n_i evaluators/configurations/arms
                r_i = r*eta**i     # each with r_i resources
                evaluations = [(evaluator, evaluator.evaluate(n_resources=r_i)) for evaluator in evaluators]
                print(f"{COL}** Evaluated {int(n_i)} arms, each with {r_i:.2f} resources {Style.RESET_ALL}")

                # Halving: keep best 1/eta of them, which will be allocated more resources/iterations
                evaluators = self._get_best_n_evaluators(n=int(n_i/eta), evaluators_and_res=evaluations)

                best_evaluator_in_round, goals = self.min_or_max(evaluations, key=self._get_opt_goal_val)
                self._update_evaluation_history(best_evaluator_in_round.arm, **goals.__dict__)

                self._update_optimizer_metrics()
                if verbosity:
                    self._print_evaluation(getattr(goals, self.optimization_goal))

        return self.min_or_max(self.eval_history, key=lambda x: x[self.optimization_goal])

    def __str__(self) -> str:
        return f"\n> Starting Hyperband optimisation\n" \
               f"    Max iterations (R)      = {self.max_iter}\n" \
               f"    Halving rate (eta)      = {self.eta}\n" \
               f"  Optimizing ({self.min_or_max.__name__}) {self.optimization_goal}"
