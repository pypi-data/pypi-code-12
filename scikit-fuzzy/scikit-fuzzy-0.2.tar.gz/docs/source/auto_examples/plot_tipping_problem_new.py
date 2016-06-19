"""
===========================
The Tipping Problem, Take 2
===========================

This is an updated version of the Tipping Problem, using the new Fuzzy Control
System API. Compare them! This one is dramatically simpler.

The 'tipping problem' is commonly used to illustrate the power of fuzzy logic
principles to generate complex behavior from a compact, intuitive set of
expert rules.

Input variables
---------------

A number of variables play into the decision about how much to tip while
dining. Consider two of them:

* ``food`` : Quality of the food
* ``service`` : Quality of the service

Output variable
---------------

The output variable is simply the tip amount, in percentage points:

* ``tip`` : Percent of bill to add as tip


For the purposes of discussion, let's say we need 'high', 'medium', and 'low'
membership functions for both input variables and our output variable. These
are defined in scikit-fuzzy as follows

"""
import numpy as np
import skfuzzy as fuzz
import matplotlib.pyplot as plt

# Generate universe variables
#   * Quality and service on subjective ranges [0, 10]
#   * Tip has a range of [0, 25] in units of percentage points
food = fuzz.Antecedent(np.linspace(0, 10, 11), 'food quality')
service = fuzz.Antecedent(np.linspace(0, 10, 11), 'service quality')
tip = fuzz.Consequent(np.linspace(0, 25, 26), 'tip')

# Generate and assign fuzzy membership functions
food['Bad'] = fuzz.trimf(food.universe, [0, 0, 5])
food['Decent'] = fuzz.trimf(food.universe, [0, 5, 10])
food['Great'] = fuzz.trimf(food.universe, [5, 10, 10])

service['Poor'] = fuzz.trimf(service.universe, [0, 0, 5])
service['Acceptable'] = fuzz.trimf(service.universe, [0, 5, 10])
service['Amazing'] = fuzz.trimf(service.universe, [5, 10, 10])

tip['Low'] = fuzz.trimf(tip.universe, [0, 0, 13])
tip['Medium'] = fuzz.trimf(tip.universe, [0, 13, 25])
tip['High'] = fuzz.trimf(tip.universe, [13, 25, 25])

# Visualize these universes and membership functions
food.view()
service.view()
tip.view()

"""
.. image:: PLOT2RST.current_figure

Fuzzy rules
-----------

Now, to make these triangles useful, we define the *fuzzy relationship*
between input and output variables. For the purposes of our example, consider
three simple rules:

1. If the food is bad OR the service is poor, then the tip will be low
2. If the service is acceptable, then the tip will be medium
3. If the food is great OR the service is amazing, then the tip will be high.

Most people would agree on these rules, but the rules are fuzzy. Mapping the
imprecise rules into a defined, actionable tip is a challenge. This is the
kind of task at which fuzzy logic excels.

"""

# Define rules
rule1 = fuzz.Rule([food['Bad'], service['Poor']], 
                  tip['Low'])
rule2 = fuzz.Rule(service['Acceptable'],
                  tip['Medium'])
rule3 = fuzz.Rule([food['Great'], service['Amazing']],
                  tip['High'])

# Create fuzzy system with these rules
tip_system = fuzz.ControlSystem([rule1, rule2, rule3])

"""
Rule application
----------------

What would the tip be in the following circumstance:

* *Food* quality was **6.5**
* *Service* quality was **9.8**

"""

# Set inputs
tip_system['food quality'] = 6.5
tip_system['service quality'] = 9.8

"""
Rule aggregation
----------------

With the *activity* of each output membership function known, all output
membership functions must be combined. This is typically done using a
maximum operator. This step is also known as *aggregation*.

Defuzzification
---------------
Finally, to get a real world answer, we return to *crisp* logic from the
world of fuzzy membership functions. For the purposes of this example
the centroid method will be used.

The result is a tip of 20.2%.
-----------------------------

"""

# Compute the result 
tip_system.compute()

# To obtain the output for each Consequent variable, one would execute
# tip_system.output['consequent label'] or in this case,
# tip_system.output['tip']
result = tip_system.output['tip']  # 20.24 percent

# View the consequent again, membership activation visible after computing
tip.view()

"""
.. image:: PLOT2RST.current_figure

Final thoughts
--------------

The power of fuzzy systems is allowing complicated, intuitive behavior based
on a sparse system of rules with minimal overhead. Note our membership
function universes were coarse, only defined at the integers, but
``fuzz.interp_membership`` allowed the effective resolution to increase on
demand. This system can respond to arbitrarily small changes in inputs,
and the processing burden is minimal.

"""
