import argparse
import os
import pickle

from autotune.benchmarks.dltk_problem import DLTKProblem
from autotune.optimisers.sequential.hyperband_optimiser import HyperbandOptimiser

data_dir = '/home/jopasserat/postdoc/openmole/hyperparam-tuning/datasets'
output_dir = '/tmp/exp1'

parser = argparse.ArgumentParser(description='DLTK Synapse Training')
parser.add_argument('-i', '--input_dir', default=data_dir, type=str, help='input dir')
parser.add_argument('-o', '--output_dir', default=output_dir, type=str, help='output dir')
parser.add_argument('-res', '--n_resources', default=3, type=int, help='n_resources')
parser.add_argument('--cuda_devices', '-c', default='0')

args = parser.parse_args()

print(args.input_dir)
print(args.output_dir)

# GPU allocation options
os.environ["CUDA_VISIBLE_DEVICES"] = args.cuda_devices

# Define maximum units of resource assigned to each optimisation iteration
n_resources = args.n_resources

problem = DLTKProblem(args.input_dir, args.output_dir)
problem.log_domain()

# Run hyperband
hyperband_opt = HyperbandOptimiser()
hyperband_opt.run_optimisation(problem, max_iter=n_resources, verbosity=True)

print("Optimal arm: "
      "parameters = {}"
      "top losses = {}"
      "opt res = {}".format(hyperband_opt.arm_opt, hyperband_opt.Y_best, hyperband_opt.fx_opt))

# Constrain random optimisation to the same time budget
time_budget = hyperband_opt.checkpoints[-1]
print("Time budget = {}s".format(time_budget))

filename = os.path.join(args.output_dir, 'results.pkl')
with open(filename, 'wb') as f:
    pickle.dump([hyperband_opt], f)
