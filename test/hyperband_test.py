import tempfile
import numpy as np
from typing import Tuple, Dict, Any

from core.params import Param
from core.arm import Arm
from core.problem_def import HyperparameterOptimizationProblem
from core.optimization_goals import OptimizationGoals
from core.evaluator import Evaluator
from datasets.dataset_loader import DatasetLoader
from benchmarks.torch_model_builders import LogisticRegressionBuilder
from util.io import print_evaluation

from optimisers.hyperband_optimiser import HyperbandOptimiser

ETA = 3
MAX_ITER = 9

LEARNING_RATE = Param('learning_rate', np.log(10 ** -6), np.log(10 ** 0), distrib='uniform', scale='log')
WEIGHT_DECAY = Param('weight_decay', np.log(10 ** -6), np.log(10 ** -1), distrib='uniform', scale='log')
MOMENTUM = Param('momentum', 0.3, 0.999, distrib='uniform', scale='linear')
BATCH_SIZE = Param('batch_size', 20, 2000, distrib='uniform', scale='linear', interval=1)
HYPERPARAMS_DOMAIN = {
    'learning_rate': LEARNING_RATE,
    'weight_decay': WEIGHT_DECAY,
    'momentum': MOMENTUM,
    'batch_size': BATCH_SIZE
}


class HyperbandTestEvaluator(Evaluator):

    @print_evaluation(verbose=True, goals_to_print=("test_correct",))
    def evaluate(self, n_resources: int) -> OptimizationGoals:
        return OptimizationGoals(validation_error=1, test_error=1)

    def _train(self, *args: Any, **kwargs: Any) -> None:
        pass

    def _test(self, *args: Any, **kwargs: Any) -> Tuple[float, ...]:
        pass

    def _save_checkpoint(self, epoch: int, val_error: float, test_error: float) -> None:
        pass


class HyperbandTestProblem(HyperparameterOptimizationProblem):

    def __init__(self, output_dir: str,
                 hyperparams_domain: Dict[str, Param] = HYPERPARAMS_DOMAIN, hyperparams_to_opt: Tuple[str, ...] = ()):
        dataset_loader = DatasetLoader()
        super().__init__(hyperparams_domain, dataset_loader, hyperparams_to_opt)
        self.output_dir = output_dir

    def get_evaluator(self, arm: Arm = None) -> HyperbandTestEvaluator:
        if arm is None:  # if no arm is provided, generate a random arm
            arm = Arm()
            arm.draw_hp_val(domain=self.domain, hyperparams_to_opt=self.hyperparams_to_opt)
        model_builder = LogisticRegressionBuilder(arm)
        return HyperbandTestEvaluator(model_builder, self.dataset_loader, output_dir=self.output_dir)


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        problem = HyperbandTestProblem(output_dir=tmp_dir_name)
        optimizer = HyperbandOptimiser(eta=ETA, max_iter=MAX_ITER, optimization_goal="validation_error", min_or_max=min)
        res = optimizer.run_optimization(problem, verbosity=True)
        print("TEST " + "PASSED" if optimizer.eval_history[0]['arm'] == res['arm'] else "FAILED")
