from __future__ import annotations

from types import SimpleNamespace
from typing import Tuple, cast

from autotune.core.hyperparams_domain import Domain


class Arm(SimpleNamespace):
    """
    Records hyperparameters and random/default values for each
    Example:
    arm.batch_size = 100
    arm.learning_rate = 0.123
    These attributes are set dynamically in draw_hp_val but, for type consistency reasons,it is recommended to inherit
    from this class and to set the hyperparameters as None attributes (Eg. CNNArm, LogisticRegressionArm)
    """

    def __init__(self, **kwargs: float):  # pylint: disable=useless-super-delegation  # Used for type hints only
        """If a custom arm is needed, the hyperparameter values can be set from a dictionary. For example, for all
        informed optimisation methods creating Arm this way is required. If one needs random values for each hyperparam,
        please use draw_hp_val.

        :param kwargs: {"hyperparameter_name": hyperparameter value}
        """
        super().__init__(**kwargs)

    def set_default_values(self, *, domain: Domain, hyperparams_to_opt: Tuple[str, ...]) -> None:
        """Sets the hyperparameters that appear in the domain but we don't want to optimise to their default values if
        they are not already set.

        :param domain: domain of hyperparameters with names, ranges, distributions etc
                       Eg. Domain(momentum=Param(...), learning_rate=Param(...))
        :param hyperparams_to_opt: hyperparameters to optimise
        """
        for hp_name in domain.hyperparams_names():
            if not hasattr(self, hp_name) and hp_name not in hyperparams_to_opt:
                # if we do not need to optimise hp_name, set Arm value to its default (if not already set)
                hp_val = domain[hp_name].init_val
                if hp_val is None:
                    raise ValueError(f"No default value for param {hp_name} was supplied")
                setattr(self, hp_name, hp_val)

    def draw_hp_val(self, *, domain: Domain, hyperparams_to_opt: Tuple[str, ...]) -> None:
        """Draws random values for the hyperparameters that we want to optimise.

        :param domain: domain of hyperparameters with names, ranges, distributions etc
                       Eg. Domain(momentum=Param(...), learning_rate=Param(...))
        :param hyperparams_to_opt: hyperparameters to optimise
        """
        self.set_default_values(domain=domain, hyperparams_to_opt=hyperparams_to_opt)
        for hp_name in domain.hyperparams_names():
            if hp_name in hyperparams_to_opt:  # draw random value if we need to optimise the current hyperparameter
                hp_val = domain[hp_name].get_param_range(1, stochastic=True)[0]
                setattr(self, hp_name, hp_val)

    @staticmethod
    def normalize(arm: Arm, *, domain: Domain) -> Arm:
        """Normalizes values of an arm as specified by the given domain.

        :param arm: arm to be normalized
        :param domain: domain of hyperparameters with names, ranges, distributions etc
                       Eg. Domain(momentum=Param(...), learning_rate=Param(...))
        """
        normalized_arm_dict = {}
        arm_hp_names = arm.__dict__.keys()
        for hp_name in set(domain.hyperparams_names()) & set(arm_hp_names):
            hp = domain[hp_name]
            normalized_arm_dict[hp_name] = (arm[hp_name] - hp.min_val) / (hp.max_val - hp.min_val)
        return Arm(**normalized_arm_dict)

    def __str__(self) -> str:
        """
        :return: human readable string representation of an Arm
        """
        longest_hp = max([len(hp_name) for hp_name in self.__dict__])

        def padding(hp_name: str) -> int:
            return longest_hp - len(hp_name) + 1

        return '\n'.join(
            [f"   - {hp_name}:{' '*padding(hp_name)}{hp_val}" for hp_name, hp_val in self.__dict__.items()])

    def __hash__(self) -> int:
        return hash(str(self))

    def __getitem__(self, hyperparam_name: str) -> float:
        """Allow dictionary-like access to attributes.

        That is: instead of getattr(arm, hyperparam_name), one can use arm[hyperparam_name]
        """
        return cast(float, getattr(self, hyperparam_name))
