# Copyright 2016 Novo Nordisk Foundation Center for Biosustainability, DTU.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import six
from cameo.core.solver_based_model import SolverBasedModel
from cameo.util import TimeMachine
from functools import partial as p

from pandas import DataFrame

from driven.data_sets.expression_profile import ExpressionProfile
from driven.flux_analysis.transcriptomics import gimme
from driven.vizualization.plotting import plotting


def gimme_sensitivity_analysis(model, expression_profile, condition_exchanges=None, condition_knockouts=None,
                               growth_rates=None, growth_rates_std=None, growth_reaction=None, min_cutoff=0,
                               max_cutoff=None, **kwargs):

    assert isinstance(model, SolverBasedModel)
    assert isinstance(expression_profile, ExpressionProfile)

    if condition_exchanges is None:
        condition_exchanges = {}
    if condition_knockouts is None:
        condition_knockouts = {}

    if max_cutoff is None:
        max_cutoff = expression_profile.minmax()[1]

    data_frame = DataFrame(columns=["cutoff", "inconsistency_score", "fba_dist", "condition"])

    for condition in expression_profile.conditions:
        with TimeMachine() as tm:
            for exchange_condition, ex in six.iteritems(condition_exchanges):
                if exchange_condition == condition:
                    tm(do=p(setattr, ex, "lower_bound", -10), undo=p(setattr, ex, "lower_bound", ex.lower_bound))
                else:
                    tm(do=p(setattr, ex, "lower_bound", 0), undo=p(setattr, ex, "lower_bound", ex.lower_bound))

            for knockout in condition_knockouts.get(condition, []):
                model.reactions.get_by_id(knockout).knock_out(tm)

            if growth_reaction is not None:
                growth_rate = growth_rates[condition]
                growth_std = growth_rates_std[condition]
                if isinstance(growth_reaction, str):
                    growth_reaction = model.reactions.get_by_id(growth_reaction)

                tm(do=p(setattr, growth_reaction, "lower_bound", growth_rate-growth_std),
                   undo=p(setattr, growth_reaction, "lower_bound", growth_reaction.upper_bound))
                tm(do=p(setattr, growth_reaction, "upper_bound", growth_rate+growth_std),
                   undo=p(setattr, growth_reaction, "upper_bound", growth_reaction.upper_bound))

            binwidth = expression_profile.binwidth(condition, min_val=min_cutoff, max_val=max_cutoff)

            for i, exp in enumerate(range(min_cutoff, max_cutoff, binwidth)):
                res = gimme(model, expression_profile=expression_profile, condition=condition, cutoff=exp, **kwargs)
                data_frame.loc[i] = [exp, res.inconsistency_score, res.distance, condition]

    plotting.line(data_frame, x="cutoff", y="inconsistency_score", group="condition",
                  x_axis_label="Cutoff", y_axis_label="Inconsistency Score")
    plotting.line(data_frame, x="cutoff", y="fba_dist", group="condition",
                  x_axis_label="Cutoff", y_axis_label="Distance to FBA")
