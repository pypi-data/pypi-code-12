import uuid
import logging

from nose import with_setup, SkipTest
from nose.plugins.attrib import attr
from numpy.testing.utils import (assert_equal, assert_allclose, assert_raises,
                                 assert_array_equal)

from brian2 import *
from brian2.codegen.translation import make_statements
from brian2.core.variables import variables_by_owner, ArrayVariable, Constant
from brian2.core.functions import DEFAULT_FUNCTIONS
from brian2.utils.logger import catch_logs
from brian2.utils.stringtools import get_identifiers, word_substitute, indent, deindent
from brian2.devices.device import reinit_devices, all_devices, get_device, set_device, reset_device
from brian2.codegen.permutation_analysis import check_for_order_independence, OrderDependenceError
from brian2.synapses.parse_synaptic_generator_syntax import parse_synapse_generator


def _compare(synapses, expected):
    conn_matrix = np.zeros((len(synapses.source), len(synapses.target)),
                           dtype=np.int32)
    for _i, _j in zip(synapses.i[:], synapses.j[:]):
        conn_matrix[_i, _j] += 1

    assert_equal(conn_matrix, expected)
    # also compare the correct numbers of incoming and outgoing synapses
    incoming = conn_matrix.sum(axis=0)
    outgoing = conn_matrix.sum(axis=1)
    assert all(synapses.N_outgoing[:] == outgoing[synapses.i[:]]), 'N_outgoing returned an incorrect value'
    assert all(synapses.N_incoming[:] == incoming[synapses.j[:]]), 'N_incoming returned an incorrect value'
    # Compare the "synapse number" if it exists
    if synapses.multisynaptic_index is not None:
        # Build an array of synapse numbers by counting the number of times
        # a source/target combination exists
        synapse_numbers = np.zeros_like(synapses.i[:])
        numbers = {}
        for _i, (source, target) in enumerate(zip(synapses.i[:],
                                                 synapses.j[:])):
            number = numbers.get((source, target), 0)
            synapse_numbers[_i] = number
            numbers[(source, target)] = number + 1
        assert all(synapses.state(synapses.multisynaptic_index)[:] == synapse_numbers), 'synapse_number returned an incorrect value'


@attr('codegen-independent')
def test_creation():
    '''
    A basic test that creating a Synapses object works.
    '''
    G = NeuronGroup(42, 'v: 1', threshold='False')
    S = Synapses(G, G, 'w:1', on_pre='v+=w')
    # We store weakref proxys, so we can't directly compare the objects
    assert S.source.name == S.target.name == G.name
    assert len(S) == 0
    S = Synapses(G, model='w:1', on_pre='v+=w')
    assert S.source.name == S.target.name == G.name


@attr('codegen-independent')
def test_creation_errors():
    G = NeuronGroup(42, 'v: 1', threshold='False')
    # Check that the old Synapses(..., connect=...) syntax raises an error
    assert_raises(TypeError, lambda: Synapses(G, G, 'w:1', on_pre='v+=w',
                                              connect=True))
    # Check that using pre and on_pre (resp. post/on_post) at the same time
    # raises an error
    assert_raises(TypeError, lambda: Synapses(G, G, 'w:1', pre='v+=w',
                                              on_pre='v+=w', connect=True))
    assert_raises(TypeError, lambda: Synapses(G, G, 'w:1', post='v+=w',
                                              on_post='v+=w', connect=True))

@attr('codegen-independent')
def test_name_clashes():
    # Using identical names for synaptic and pre- or post-synaptic variables
    # is confusing and should be forbidden
    G1 = NeuronGroup(1, 'a : 1')
    G2 = NeuronGroup(1, 'b : 1')
    assert_raises(ValueError, lambda: Synapses(G1, G2, 'a : 1'))
    assert_raises(ValueError, lambda: Synapses(G1, G2, 'b : 1'))

    # this should all be ok
    Synapses(G1, G2, 'c : 1')
    Synapses(G1, G2, 'a_syn : 1')
    Synapses(G1, G2, 'b_syn : 1')

@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_incoming_outgoing():
    '''
    Test the count of outgoing/incoming synapses per neuron.
    (It will be also automatically tested for all connection patterns that
    use the above _compare function for testing)
    '''
    G1 = NeuronGroup(5, 'v: 1', threshold='False')
    G2 = NeuronGroup(5, 'v: 1', threshold='False')
    S = Synapses(G1, G2, 'w:1', on_pre='v+=w')
    S.connect(i=[0, 0, 0, 1, 1, 2],
              j=[0, 1, 2, 1, 2, 3])
    run(0*ms)  # to make this work for standalone
    # First source neuron has 3 outgoing synapses, the second 2, the third 1
    assert all(S.N_outgoing[0, :] == 3)
    assert all(S.N_outgoing[1, :] == 2)
    assert all(S.N_outgoing[2, :] == 1)
    assert all(S.N_outgoing[3:, :] == 0)
    # First target neuron receives 1 input, the second+third each 2, the fourth receives 1
    assert all(S.N_incoming[:, 0] == 1)
    assert all(S.N_incoming[:, 1] == 2)
    assert all(S.N_incoming[:, 2] == 2)
    assert all(S.N_incoming[:, 3] == 1)
    assert all(S.N_incoming[:, 4:] == 0)


@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_connection_arrays():
    '''
    Test connecting synapses with explictly given arrays
    '''
    G = NeuronGroup(42, 'v : 1')
    G2 = NeuronGroup(17, 'v : 1')

    # one-to-one
    expected1 = np.eye(len(G2))
    S1 = Synapses(G2)
    S1.connect(i=np.arange(len(G2)), j=np.arange(len(G2)))

    # full
    expected2 = np.ones((len(G), len(G2)))
    S2 = Synapses(G, G2)
    X, Y = np.meshgrid(np.arange(len(G)), np.arange(len(G2)))
    S2.connect(i=X.flatten(), j=Y.flatten())


    # Multiple synapses
    expected3 = np.zeros((len(G), len(G2)))
    expected3[3, 3] = 2
    S3 = Synapses(G, G2)
    S3.connect(i=[3, 3], j=[3, 3])

    run(0*ms)  # for standalone
    _compare(S1, expected1)
    _compare(S2, expected2)
    _compare(S3, expected3)

    # Incorrect usage
    S = Synapses(G, G2)
    assert_raises(TypeError, lambda: S.connect(i=[1.1, 2.2], j=[1.1, 2.2]))
    assert_raises(TypeError, lambda: S.connect(i=[1, 2], j='string'))
    assert_raises(TypeError, lambda: S.connect(i=[1, 2], j=[1, 2], n='i'))
    assert_raises(TypeError, lambda: S.connect([1, 2]))
    assert_raises(ValueError, lambda: S.connect(i=[1, 2, 3], j=[1, 2]))
    assert_raises(ValueError, lambda: S.connect(i=np.ones((3, 3), dtype=np.int32),
                                                j=np.ones((3, 1), dtype=np.int32)))
    assert_raises(IndexError, lambda: S.connect(i=[41, 42], j=[0, 1]))  # source index > max
    assert_raises(IndexError, lambda: S.connect(i=[0, 1], j=[16, 17]))  # target index > max
    assert_raises(IndexError, lambda: S.connect(i=[0, -1], j=[0, 1]))  # source index < 0
    assert_raises(IndexError, lambda: S.connect(i=[0, 1], j=[0, -1]))  # target index < 0
    assert_raises(ValueError, lambda: S.connect('i==j',
                                                j=np.arange(10)))
    assert_raises(TypeError, lambda: S.connect('i==j',
                                               n=object()))
    assert_raises(TypeError, lambda: S.connect('i==j',
                                               p=object()))
    assert_raises(TypeError, lambda: S.connect(object()))

@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_connection_string_deterministic():
    '''
    Test connecting synapses with a deterministic string expression.
    '''
    G = NeuronGroup(17, 'v : 1', threshold='False')
    G.v = 'i'
    G2 = NeuronGroup(4, 'v : 1', threshold='False')
    G2.v = '17 + i'

    # Full connection
    expected_full = np.ones((len(G), len(G2)))

    S1 = Synapses(G, G2, 'w:1', 'v+=w')
    S1.connect(True)

    S2 = Synapses(G, G2, 'w:1', 'v+=w')
    S2.connect('True')

    # Full connection without self-connections
    expected_no_self = np.ones((len(G), len(G))) - np.eye(len(G))

    S5 = Synapses(G, G, 'w:1', 'v+=w')
    S5.connect('i != j')

    S6 = Synapses(G, G, 'w:1', 'v+=w')
    S6.connect('v_pre != v_post')

    S7 = Synapses(G, G, 'w:1', 'v+=w')
    S7.connect(condition='i != j')

    # One-to-one connectivity
    expected_one_to_one = np.eye(len(G))

    S8 = Synapses(G, G, 'w:1', 'v+=w')
    S8.connect('i == j')

    S9 = Synapses(G, G, 'w:1', 'v+=w')
    S9.connect('v_pre == v_post')

    S10 = Synapses(G, G, 'w:1', 'v+=w')
    S10.connect(j='i')

    # Everything except for the upper [2, 2] quadrant
    number = 2
    expected_custom = np.ones((len(G), len(G)))
    expected_custom[:number, :number] = 0
    S11 = Synapses(G, G, 'w:1', 'v+=w')
    S11.connect('(i >= number) or (j >= number)')

    S12 = Synapses(G, G, 'w:1', 'v+=w')
    S12.connect('(i >= explicit_number) or (j >= explicit_number)',
                namespace={'explicit_number': number})

    # check that this mistaken syntax raises an error
    assert_raises(ValueError, lambda: S12.connect('k for k in range(1)'))

    # check that trying to connect to a neuron outside the range raises an error
    if get_device() == all_devices['runtime']:
        assert_raises(IndexError, lambda: S12.connect(j='20'))

    run(0*ms)  # for standalone

    _compare(S1, expected_full)
    _compare(S2, expected_full)
    _compare(S5, expected_no_self)
    _compare(S6, expected_no_self)
    _compare(S7, expected_no_self)
    _compare(S8, expected_one_to_one)
    _compare(S9, expected_one_to_one)
    _compare(S11, expected_custom)
    _compare(S12, expected_custom)


@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_connection_random_with_condition():
    G = NeuronGroup(4, 'v: 1', threshold='False')

    S1 = Synapses(G, G, 'w:1', 'v+=w')
    S1.connect('i!=j', p=0.0)

    S2 = Synapses(G, G, 'w:1', 'v+=w')
    S2.connect('i!=j', p=1.0)
    expected2 = np.ones((len(G), len(G))) - np.eye(len(G))

    S3 = Synapses(G, G, 'w:1', 'v+=w')
    S3.connect('i>=2', p=0.0)

    S4 = Synapses(G, G, 'w:1', 'v+=w')
    S4.connect('i>=2', p=1.0)
    expected4 = np.zeros((len(G), len(G)))
    expected4[2, :] = 1
    expected4[3, :] = 1

    S5 = Synapses(G, G, 'w:1', 'v+=w')
    S5.connect('j<2', p=0.0)
    S6 = Synapses(G, G, 'w:1', 'v+=w')
    S6.connect('j<2', p=1.0)
    expected6 = np.zeros((len(G), len(G)))
    expected6[:, 0] = 1
    expected6[:, 1] = 1

    # Just checking that everything works in principle (we can't check the
    # actual connections)
    S7 = Synapses(G, G, 'w:1', 'v+=w')
    S7.connect('i!=j', p=0.01)

    S8 = Synapses(G, G, 'w:1', 'v+=w')
    S8.connect('i!=j', p=0.03)

    S9 = Synapses(G, G, 'w:1', 'v+=w')
    S9.connect('i!=j', p=0.3)

    S10 = Synapses(G, G, 'w:1', 'v+=w')
    S10.connect('i>=2', p=0.01)

    S11 = Synapses(G, G, 'w:1', 'v+=w')
    S11.connect('i>=2', p=0.03)

    S12 = Synapses(G, G, 'w:1', 'v+=w')
    S12.connect('i>=2', p=0.3)

    S13 = Synapses(G, G, 'w:1', 'v+=w')
    S13.connect('j>=2', p=0.01)

    S14 = Synapses(G, G, 'w:1', 'v+=w')
    S14.connect('j>=2', p=0.03)

    S15 = Synapses(G, G, 'w:1', 'v+=w')
    S15.connect('j>=2', p=0.3)

    S16 = Synapses(G, G, 'w:1', 'v+=w')
    S16.connect('i!=j', p='i*0.1')

    S17 = Synapses(G, G, 'w:1', 'v+=w')
    S17.connect('i!=j', p='j*0.1')

    with catch_logs() as _:  # Ignore warnings about empty synapses
        run(0*ms)  # for standalone

    assert len(S1) == 0
    _compare(S2, expected2)
    assert len(S3) == 0
    _compare(S4, expected4)
    assert len(S5) == 0
    _compare(S6, expected6)
    assert not any(S7.i == S7.j)
    assert not any(S8.i == S8.j)
    assert not any(S9.i == S9.j)
    assert all(S10.i >= 2)
    assert all(S11.i >= 2)
    assert all(S12.i >= 2)
    assert all(S13.j >= 2)
    assert all(S14.j >= 2)
    assert all(S15.j >= 2)
    assert not any(S16.i == 0)
    assert not any(S17.j == 0)


@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_connection_random_with_indices():
    '''
    Test random connections.
    '''
    G = NeuronGroup(4, 'v: 1', threshold='False')
    G2 = NeuronGroup(7, 'v: 1', threshold='False')

    S1 = Synapses(G, G2, 'w:1', 'v+=w')
    S1.connect(i=0, j=0, p=0.)
    expected1 = np.zeros((len(G), len(G2)))

    S2 = Synapses(G, G2, 'w:1', 'v+=w')
    S2.connect(i=0, j=0, p=1.)
    expected2 = np.zeros((len(G), len(G2)))
    expected2[0, 0] = 1

    S3 = Synapses(G, G2, 'w:1', 'v+=w')
    S3.connect(i=[0, 1], j=[0, 2], p=1.)
    expected3 = np.zeros((len(G), len(G2)))
    expected3[0, 0] = 1
    expected3[1, 2] = 1

    # Just checking that it works in principle
    S4 = Synapses(G, G, 'w:1', 'v+=w')
    S4.connect(i=0, j=0, p=0.01)
    S5 = Synapses(G, G, 'w:1', 'v+=w')
    S5.connect(i=[0, 1], j=[0, 2], p=0.01)

    S6 = Synapses(G, G, 'w:1', 'v+=w')
    S6.connect(i=0, j=0, p=0.03)

    S7 = Synapses(G, G, 'w:1', 'v+=w')
    S7.connect(i=[0, 1], j=[0, 2], p=0.03)

    S8 = Synapses(G, G, 'w:1', 'v+=w')
    S8.connect(i=0, j=0, p=0.3)

    S9 = Synapses(G, G, 'w:1', 'v+=w')
    S9.connect(i=[0, 1], j=[0, 2], p=0.3)

    with catch_logs() as _:  # Ignore warnings about empty synapses
        run(0*ms)  # for standalone

    _compare(S1, expected1)
    _compare(S2, expected2)
    _compare(S3, expected3)
    assert 0 <= len(S4) <= 1
    assert 0 <= len(S5) <= 2
    assert 0 <= len(S6) <= 1
    assert 0 <= len(S7) <= 2
    assert 0 <= len(S8) <= 1
    assert 0 <= len(S9) <= 2

@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_connection_random_without_condition():
    G = NeuronGroup(4, '''v: 1
                          x : integer''', threshold='False')
    G.x = 'i'
    G2 = NeuronGroup(7, '''v: 1
                           y : 1''', threshold='False')
    G2.y = '1.0*i/N'

    S1 = Synapses(G, G2, 'w:1', 'v+=w')
    S1.connect(True, p=0.0)

    S2 = Synapses(G, G2, 'w:1', 'v+=w')
    S2.connect(True, p=1.0)

    # Just make sure using values between 0 and 1 work in principle
    S3 = Synapses(G, G2, 'w:1', 'v+=w')
    S3.connect(True, p=0.3)

    # Use pre-/post-synaptic variables for "stochastic" connections that are
    # actually deterministic
    S4 = Synapses(G, G2, 'w:1', on_pre='v+=w')
    S4.connect(True, p='int(x_pre==2)*1.0')

    # Use pre-/post-synaptic variables for "stochastic" connections that are
    # actually deterministic
    S5 = Synapses(G, G2, 'w:1', on_pre='v+=w')
    S5.connect(True, p='int(x_pre==2 and y_post > 0.5)*1.0')

    with catch_logs() as _:  # Ignore warnings about empty synapses
        run(0*ms)  # for standalone

    _compare(S1, np.zeros((len(G), len(G2))))
    _compare(S2, np.ones((len(G), len(G2))))
    assert 0 <= len(S3) <= len(G) * len(G2)
    assert len(S4) == 7
    assert_equal(S4.i, np.ones(7)*2)
    assert_equal(S4.j, np.arange(7))
    assert len(S5) == 3
    assert_equal(S5.i, np.ones(3) * 2)
    assert_equal(S5.j, np.arange(3) + 4)


@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_connection_multiple_synapses():
    '''
    Test multiple synapses per connection.
    '''
    G = NeuronGroup(42, 'v: 1', threshold='False')
    G.v = 'i'
    G2 = NeuronGroup(17, 'v: 1', threshold='False')
    G2.v = 'i'

    S1 = Synapses(G, G2, 'w:1', 'v+=w')
    S1.connect(True, n=0)

    S2 = Synapses(G, G2, 'w:1', 'v+=w')
    S2.connect(True, n=2)

    S3 = Synapses(G, G2, 'w:1', 'v+=w')
    S3.connect(True, n='j')

    S4 = Synapses(G, G2, 'w:1', 'v+=w')
    S4.connect(True, n='i')

    S5 = Synapses(G, G2, 'w:1', 'v+=w')
    S5.connect(True, n='int(i>j)*2')

    S6 = Synapses(G, G2, 'w:1', 'v+=w')
    S6.connect(True, n='int(v_pre>v_post)*2')

    with catch_logs() as _:  # Ignore warnings about empty synapses
        run(0*ms)  # for standalone

    assert len(S1) == 0
    _compare(S2, 2 * np.ones((len(G), len(G2))))
    _compare(S3, np.arange(len(G2)).reshape(1, len(G2)).repeat(len(G),
                                                               axis=0))

    _compare(S4, np.arange(len(G)).reshape(len(G), 1).repeat(len(G2),
                                                             axis=1))
    expected = np.zeros((len(G), len(G2)), dtype=np.int32)
    for source in range(len(G)):
        expected[source, :source] = 2
    _compare(S5, expected)
    _compare(S6, expected)


def test_state_variable_assignment():
    '''
    Assign values to state variables in various ways
    '''

    G = NeuronGroup(10, 'v: volt', threshold='False')
    G.v = 'i*mV'
    S = Synapses(G, G, 'w:volt')
    S.connect(True)

    # with unit checking
    assignment_expected = [
        (5*mV, np.ones(100)*5*mV),
        (7*mV, np.ones(100)*7*mV),
        (S.i[:] * mV, S.i[:]*np.ones(100)*mV),
        ('5*mV', np.ones(100)*5*mV),
        ('i*mV', np.ones(100)*S.i[:]*mV),
        ('i*mV +j*mV', S.i[:]*mV + S.j[:]*mV),
        # reference to pre- and postsynaptic state variables
        ('v_pre', S.i[:]*mV),
        ('v_post', S.j[:]*mV),
        #('i*mV + j*mV + k*mV', S.i[:]*mV + S.j[:]*mV + S.k[:]*mV) #not supported yet
    ]

    for assignment, expected in assignment_expected:
        S.w = 0*volt
        S.w = assignment
        assert_allclose(S.w[:], expected,
                        err_msg='Assigning %r gave incorrect result' % assignment)
        S.w = 0*volt
        S.w[:] = assignment
        assert_allclose(S.w[:], expected,
                        err_msg='Assigning %r gave incorrect result' % assignment)

    # without unit checking
    assignment_expected = [
        (5, np.ones(100)*5*volt),
        (7, np.ones(100)*7*volt),
        (S.i[:], S.i[:]*np.ones(100)*volt),
        ('5', np.ones(100)*5*volt),
        ('i', np.ones(100)*S.i[:]*volt),
        ('i +j', S.i[:]*volt + S.j[:]*volt),
        #('i + j + k', S.i[:]*volt + S.j[:]*volt + S.k[:]*volt) #not supported yet
    ]

    for assignment, expected in assignment_expected:
        S.w = 0*volt
        S.w_ = assignment
        assert_allclose(S.w[:], expected,
                        err_msg='Assigning %r gave incorrect result' % assignment)
        S.w = 0*volt
        S.w_[:] = assignment
        assert_allclose(S.w[:], expected,
                        err_msg='Assigning %r gave incorrect result' % assignment)


def test_state_variable_indexing():
    G1 = NeuronGroup(5, 'v:volt')
    G1.v = 'i*mV'
    G2 = NeuronGroup(7, 'v:volt')
    G2.v= '10*mV + i*mV'
    S = Synapses(G1, G2, 'w:1', multisynaptic_index='k')
    S.connect(True, n=2)
    S.w[:, :, 0] = '5*i + j'
    S.w[:, :, 1] = '35 + 5*i + j'

    #Slicing
    assert len(S.w[:]) == len(S.w[:, :]) == len(S.w[:, :, :]) == len(G1)*len(G2)*2
    assert len(S.w[0:, 0:]) == len(S.w[0:, 0:, 0:]) == len(G1)*len(G2)*2
    assert len(S.w[0::2, 0:]) == 3*len(G2)*2
    assert len(S.w[0, :]) == len(S.w[0, :, :]) == len(G2)*2
    assert len(S.w[0:2, :]) == len(S.w[0:2, :, :]) == 2*len(G2)*2
    assert len(S.w[:2, :]) == len(S.w[:2, :, :]) == 2*len(G2)*2
    assert len(S.w[0:4:2, :]) == len(S.w[0:4:2, :, :]) == 2*len(G2)*2
    assert len(S.w[:4:2, :]) == len(S.w[:4:2, :, :]) == 2*len(G2)*2
    assert len(S.w[:, 0]) == len(S.w[:, 0, :]) == len(G1)*2
    assert len(S.w[:, 0:2]) == len(S.w[:, 0:2, :]) == 2*len(G1)*2
    assert len(S.w[:, :2]) == len(S.w[:, :2, :]) == 2*len(G1)*2
    assert len(S.w[:, 0:4:2]) == len(S.w[:, 0:4:2, :]) == 2*len(G1)*2
    assert len(S.w[:, :4:2]) == len(S.w[:, :4:2, :]) == 2*len(G1)*2
    assert len(S.w[:, :, 0]) == len(G1)*len(G2)
    assert len(S.w[:, :, 0:2]) == len(G1)*len(G2)*2
    assert len(S.w[:, :, :2]) == len(G1)*len(G2)*2
    assert len(S.w[:, :, 0:2:2]) == len(G1)*len(G2)
    assert len(S.w[:, :, :2:2]) == len(G1)*len(G2)

    # 1d indexing is directly indexing synapses!
    assert len(S.w[:]) == len(S.w[0:])
    assert len(S.w[[0, 1]]) == len(S.w[3:5]) == 2
    assert len(S.w[:]) == len(S.w[np.arange(len(G1)*len(G2)*2)])

    #Array-indexing (not yet supported for synapse index)
    assert_equal(S.w[:, 0:3], S.w[:, [0, 1, 2]])
    assert_equal(S.w[:, 0:3], S.w[np.arange(len(G1)), [0, 1, 2]])

    #string-based indexing
    assert_equal(S.w[0:3, :], S.w['i<3'])
    assert_equal(S.w[:, 0:3], S.w['j<3'])
    assert_equal(S.w[:, :, 0], S.w['k == 0'])
    assert_equal(S.w[0:3, :], S.w['v_pre < 3*mV'])
    assert_equal(S.w[:, 0:3], S.w['v_post < 13*mV'])

    #invalid indices
    assert_raises(IndexError, lambda: S.w.__getitem__((1, 2, 3, 4)))
    assert_raises(IndexError, lambda: S.w.__getitem__(object()))


def test_indices():
    G = NeuronGroup(10, 'v : 1')
    S = Synapses(G, G, '')
    S.connect()
    G.v = 'i'

    assert_equal(S.indices[:], np.arange(10*10))
    assert len(S.indices[5, :]) == 10
    assert_equal(S.indices['v_pre >=5'], S.indices[5:, :])
    assert_equal(S.indices['j >=5'], S.indices[:, 5:])


def test_subexpression_references():
    '''
    Assure that subexpressions in targeted groups are handled correctly.
    '''
    G = NeuronGroup(10, '''v : 1
                           v2 = 2*v : 1''')
    G.v = np.arange(10)
    S = Synapses(G, G, '''w : 1
                          u = v2_post + 1 : 1
                          x = v2_pre + 1 : 1''')
    S.connect('i==(10-1-j)')
    assert_equal(S.u[:], np.arange(10)[::-1]*2+1)
    assert_equal(S.x[:], np.arange(10)*2+1)


def test_delay_specification():
    # By default delays are state variables (i.e. arrays), but if they are
    # specified in the initializer, they are scalars.
    G = NeuronGroup(10, 'v:1', threshold='False')

    # Array delay
    S = Synapses(G, G, 'w:1', on_pre='v+=w')
    S.connect('i==j')
    assert len(S.delay[:]) == len(G)
    S.delay = 'i*ms'
    assert_equal(S.delay[:], np.arange(len(G))*ms)
    S.delay = 5*ms
    assert_equal(S.delay[:], np.ones(len(G))*5*ms)

    # Scalar delay
    S = Synapses(G, G, 'w:1', on_pre='v+=w', delay=5*ms)
    assert_equal(S.delay[:], 5*ms)
    S.connect('i==j')
    S.delay = 10*ms
    assert_equal(S.delay[:], 10*ms)
    # S.delay = '3*ms'
    # assert_equal(S.delay[:], 3*ms)

    # Invalid arguments
    assert_raises(DimensionMismatchError, lambda: Synapses(G, G, 'w:1',
                                                           on_pre='v+=w',
                                                           delay=5*mV))
    assert_raises(TypeError, lambda: Synapses(G, G, 'w:1', on_pre='v+=w',
                                              delay=object()))
    assert_raises(ValueError, lambda: Synapses(G, G, 'w:1', delay=5*ms))
    assert_raises(ValueError, lambda: Synapses(G, G, 'w:1', on_pre='v+=w',
                                               delay={'post': 5*ms}))

@attr('codegen-independent')
def test_pre_before_post():
    # The pre pathway should be executed before the post pathway
    G = NeuronGroup(1, '''x : 1
                          y : 1''', threshold='True')
    S = Synapses(G, G, '', on_pre='x=1; y=1', on_post='x=2')
    S.connect()
    run(defaultclock.dt)
    # Both pathways should have been executed, but post should have overriden
    # the x value (because it was executed later)
    assert G.x == 2
    assert G.y == 1


@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_pre_post_simple():
    # Test that pre and post still work correctly
    G1 = SpikeGeneratorGroup(1, [0], [1]*ms)
    G2 = SpikeGeneratorGroup(1, [0], [2]*ms)
    with catch_logs() as l:
        S = Synapses(G1, G2, '''pre_value : 1
                                post_value : 1''',
                     pre='pre_value +=1',
                     post='post_value +=2')
    S.connect()
    syn_mon = StateMonitor(S, ['pre_value', 'post_value'], record=[0],
                           when='end')
    run(3*ms)
    assert_equal(syn_mon.pre_value[0][syn_mon.t < 1*ms], 0)
    assert_equal(syn_mon.pre_value[0][syn_mon.t >= 1*ms], 1)
    assert_equal(syn_mon.post_value[0][syn_mon.t < 2*ms], 0)
    assert_equal(syn_mon.post_value[0][syn_mon.t >= 2*ms], 2)


@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_transmission_simple():
    source = SpikeGeneratorGroup(2, [0, 1], [2, 1] * ms)
    target = NeuronGroup(2, 'v : 1')
    syn = Synapses(source, target, on_pre='v += 1')
    syn.connect(j='i')
    mon = StateMonitor(target, 'v', record=True, when='end')
    run(2.5*ms)
    assert_equal(mon[0].v[mon.t<2*ms], 0.)
    assert_equal(mon[0].v[mon.t>=2*ms], 1.)
    assert_equal(mon[1].v[mon.t<1*ms], 0.)
    assert_equal(mon[1].v[mon.t>=1*ms], 1.)

@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_transmission_custom_event():
    source = NeuronGroup(2, '',
                         events={'custom': 't>=(2-i)*ms and t<(2-i)*ms + dt'})
    target = NeuronGroup(2, 'v : 1')
    syn = Synapses(source, target, on_pre='v += 1',
                   on_event='custom')
    syn.connect(j='i')
    mon = StateMonitor(target, 'v', record=True, when='end')
    run(2.5*ms)
    assert_equal(mon[0].v[mon.t<2*ms], 0.)
    assert_equal(mon[0].v[mon.t>=2*ms], 1.)
    assert_equal(mon[1].v[mon.t<1*ms], 0.)
    assert_equal(mon[1].v[mon.t>=1*ms], 1.)

@attr('codegen-independent')
def test_invalid_custom_event():
    group1 = NeuronGroup(2, 'v : 1',
                         events={'custom': 't>=(2-i)*ms and t<(2-i)*ms + dt'})
    group2 = NeuronGroup(2, 'v : 1', threshold='v>1')
    assert_raises(ValueError, lambda: Synapses(group1, group1, on_pre='v+=1',
                                               on_event='spike'))
    assert_raises(ValueError, lambda: Synapses(group2, group2, on_pre='v+=1',
                                               on_event='custom'))

@with_setup(teardown=reinit_devices)
def test_transmission():
    default_dt = defaultclock.dt
    delays = [[0, 0, 0, 0] * ms,
              [1, 1, 1, 0] * ms,
              [0, 1, 2, 3] * ms,
              [2, 2, 0, 0] * ms,
              [2, 1, 0, 1] * ms]
    for delay in delays:
        # Make sure that the Synapses class actually propagates spikes :)
        source = NeuronGroup(4, '''dv/dt = rate : 1
                                   rate : Hz''', threshold='v>1', reset='v=0')
        source.rate = [51, 101, 101, 51] * Hz
        target = NeuronGroup(4, 'v:1', threshold='v>1', reset='v=0')

        source_mon = SpikeMonitor(source)
        target_mon = SpikeMonitor(target)

        S = Synapses(source, target, on_pre='v+=1.1')
        S.connect(j='i')
        S.delay = delay
        net = Network(S, source, target, source_mon, target_mon)
        net.run(50*ms+default_dt+max(delay))
        # All spikes should trigger spikes in the receiving neurons with
        # the respective delay ( + one dt)
        for d in range(len(delay)):
            assert_allclose(source_mon.t[source_mon.i==d],
                            target_mon.t[target_mon.i==d] - default_dt - delay[d])


@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_transmission_all_to_one_heterogeneous_delays():
    source = SpikeGeneratorGroup(6,
                                 [0, 1, 4, 5, 2, 3, 4, 5, 0, 1, 2, 3, 4, 5],
                                 [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2]*defaultclock.dt)
    target = NeuronGroup(1, 'v:1')
    synapses = Synapses(source, target, on_pre='v_post += (i_pre+1)')
    synapses.connect()
    synapses.delay = [0, 0, 0, 1, 2, 1] * defaultclock.dt

    mon = StateMonitor(target, 'v', record=True, when='end')
    run(4*defaultclock.dt)
    assert mon[0].v[0] == 3
    assert mon[0].v[1] == 12
    assert mon[0].v[2] == 33
    assert mon[0].v[3] == 48


@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_transmission_one_to_all_heterogeneous_delays():
    source = SpikeGeneratorGroup(1, [0, 0], [0, 2]*defaultclock.dt)
    target = NeuronGroup(6, 'v:integer')
    synapses = Synapses(source, target, on_pre='v_post += (i_pre+1)')
    synapses.connect()
    synapses.delay = [0, 0, 1, 3, 2, 1] * defaultclock.dt

    mon = StateMonitor(target, 'v', record=True, when='end')
    run(4*defaultclock.dt)
    assert_equal(mon[0].v, [1, 1, 2, 2])
    assert_equal(mon[1].v, [1, 1, 2, 2])
    assert_equal(mon[2].v, [0, 1, 1, 2])
    assert_equal(mon[3].v, [0, 0, 0, 1])
    assert_equal(mon[4].v, [0, 0, 1, 1])
    assert_equal(mon[5].v, [0, 1, 1, 2])


@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_transmission_scalar_delay():
    inp = SpikeGeneratorGroup(2, [0, 1], [0, 1]*ms)
    target = NeuronGroup(2, 'v:1')
    S = Synapses(inp, target, on_pre='v+=1', delay=0.5*ms)
    S.connect(j='i')
    mon = StateMonitor(target, 'v', record=True, when='end')
    run(2*ms)
    assert_equal(mon[0].v[mon.t<0.5*ms], 0)
    assert_equal(mon[0].v[mon.t>=0.5*ms], 1)
    assert_equal(mon[1].v[mon.t<1.5*ms], 0)
    assert_equal(mon[1].v[mon.t>=1.5*ms], 1)


@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_transmission_scalar_delay_different_clocks():

    inp = SpikeGeneratorGroup(2, [0, 1], [0, 1]*ms, dt=0.5*ms,
                              # give the group a unique name to always
                              # get a 'fresh' warning
                              name='sg_%d' % uuid.uuid4())
    target = NeuronGroup(2, 'v:1', dt=0.1*ms)
    S = Synapses(inp, target, on_pre='v+=1', delay=0.5*ms)
    S.connect(j='i')
    mon = StateMonitor(target, 'v', record=True, when='end')

    if get_device() == all_devices['runtime']:
        # We should get a warning when using inconsistent dts
        with catch_logs() as l:
            run(2*ms)
            assert len(l) == 1, 'expected a warning, got %d' % len(l)
            assert l[0][1].endswith('synapses_dt_mismatch')

    run(0*ms)
    assert_equal(mon[0].v[mon.t<0.5*ms], 0)
    assert_equal(mon[0].v[mon.t>=0.5*ms], 1)
    assert_equal(mon[1].v[mon.t<1.5*ms], 0)
    assert_equal(mon[1].v[mon.t>=1.5*ms], 1)


@attr('codegen-independent')
def test_clocks():
    '''
    Make sure that a `Synapse` object uses the correct clocks.
    '''
    source_dt = 0.05*ms
    target_dt = 0.1*ms
    synapse_dt = 0.2*ms
    source = NeuronGroup(1, 'v:1', dt=source_dt, threshold='False')
    target = NeuronGroup(1, 'v:1', dt=target_dt, threshold='False')
    synapse = Synapses(source, target, 'w:1', on_pre='v+=1', on_post='v+=1',
                       dt=synapse_dt)
    synapse.connect()

    assert synapse.pre.clock is source.clock
    assert synapse.post.clock is target.clock
    assert synapse.pre._clock.dt == source_dt
    assert synapse.post._clock.dt == target_dt
    assert synapse._clock.dt == synapse_dt


@with_setup(teardown=restore_initial_state)
def test_changed_dt_spikes_in_queue():
    defaultclock.dt = .5*ms
    G1 = NeuronGroup(1, 'v:1', threshold='v>1', reset='v=0')
    G1.v = 1.1
    G2 = NeuronGroup(10, 'v:1', threshold='v>1', reset='v=0')
    S = Synapses(G1, G2, on_pre='v+=1.1')
    S.connect(True)
    S.delay = 'j*ms'
    mon = SpikeMonitor(G2)
    net = Network(G1, G2, S, mon)
    net.run(5*ms)
    defaultclock.dt = 1*ms
    net.run(3*ms)
    defaultclock.dt = 0.1*ms
    net.run(2*ms)
    # Spikes should have delays of 0, 1, 2, ... ms and always
    # trigger a spike one dt later
    expected = [0.5, 1.5, 2.5, 3.5, 4.5, # dt=0.5ms
                6, 7, 8, #dt = 1ms
                8.1, 9.1 #dt=0.1ms
                ] * ms
    assert_equal(mon.t[:], expected)


@attr('codegen-independent')
def test_no_synapses():
    # Synaptic pathway but no synapses
    G1 = NeuronGroup(1, '', threshold='True')
    G2 = NeuronGroup(1, 'v:1')
    S = Synapses(G1, G2, on_pre='v+=1', name='synapses_'+str(uuid.uuid4()).replace('-', '_'))
    net = Network(G1, G2, S)
    with catch_logs() as l:
        net.run(defaultclock.dt)
        assert len(l) == 1, 'expected 1 warning, got %d' % len(l)
        assert l[0][1].endswith('.no_synapses')


@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_summed_variable():
    source = NeuronGroup(2, 'v : volt', threshold='v>1*volt', reset='v=0*volt')
    source.v = 1.1*volt  # will spike immediately
    target = NeuronGroup(2, 'v : volt')
    S = Synapses(source, target, '''w : volt
                                    x : volt
                                    v_post = 2*x : volt (summed)''', on_pre='x+=w',
                 multisynaptic_index='k')
    S.connect('i==j', n=2)
    S.w['k == 0'] = 'i*volt'
    S.w['k == 1'] = '(i + 0.5)*volt'
    net = Network(source, target, S)
    net.run(1*ms)

    # v of the target should be the sum of the two weights
    assert_equal(target.v, np.array([1.0, 5.0])*volt)


def test_summed_variable_errors():
    G = NeuronGroup(10, '''dv/dt = -v / (10*ms) : volt
                           sub = 2*v : volt
                           p : volt''')

    # Using the (summed) flag for a differential equation or a parameter
    assert_raises(ValueError, lambda: Synapses(G, G, '''dp_post/dt = -p_post / (10*ms) : volt (summed)'''))
    assert_raises(ValueError, lambda: Synapses(G, G, '''p_post : volt (summed)'''))

    # Using the (summed) flag for a variable name without _pre or _post suffix
    assert_raises(ValueError, lambda: Synapses(G, G, '''p = 3*volt : volt (summed)'''))

    # Using the name of a variable that does not exist
    assert_raises(ValueError, lambda: Synapses(G, G, '''q_post = 3*volt : volt (summed)'''))

    # Target equation is not a parameter
    assert_raises(ValueError, lambda: Synapses(G, G, '''sub_post = 3*volt : volt (summed)'''))
    assert_raises(ValueError, lambda: Synapses(G, G, '''v_post = 3*volt : volt (summed)'''))

    # Unit mismatch between synapses and target
    assert_raises(DimensionMismatchError,
                  lambda: Synapses(G, G, '''p_post = 3*second : second (summed)'''))

    # Two summed variable equations targetting the same variable
    assert_raises(ValueError,
                  lambda: Synapses(G, G, '''p_post = 3*volt : volt (summed)
                                            p_pre = 3*volt : volt (summed)'''))


def test_scalar_parameter_access():
    G = NeuronGroup(10, '''v : 1
                           scalar : Hz (shared)''', threshold='False')
    S = Synapses(G, G, '''w : 1
                          s : Hz (shared)
                          number : 1 (shared)''',
                 on_pre='v+=w*number')
    S.connect()

    # Try setting a scalar variable
    S.s = 100*Hz
    assert_equal(S.s[:], 100*Hz)
    S.s[:] = 200*Hz
    assert_equal(S.s[:], 200*Hz)
    S.s = 's - 50*Hz + number*Hz'
    assert_equal(S.s[:], 150*Hz)
    S.s[:] = '50*Hz'
    assert_equal(S.s[:], 50*Hz)

    # Set a postsynaptic scalar variable
    S.scalar_post = 100*Hz
    assert_equal(G.scalar[:], 100*Hz)
    S.scalar_post[:] = 100*Hz
    assert_equal(G.scalar[:], 100*Hz)

    # Check the second method of accessing that works
    assert_equal(np.asanyarray(S.s), 50*Hz)

    # Check error messages
    assert_raises(IndexError, lambda: S.s[0])
    assert_raises(IndexError, lambda: S.s[1])
    assert_raises(IndexError, lambda: S.s[0:1])
    assert_raises(IndexError, lambda: S.s['i>5'])

    assert_raises(ValueError, lambda: S.s.set_item(slice(None), [0, 1]*Hz))
    assert_raises(IndexError, lambda: S.s.set_item(0, 100*Hz))
    assert_raises(IndexError, lambda: S.s.set_item(1, 100*Hz))
    assert_raises(IndexError, lambda: S.s.set_item('i>5', 100*Hz))


def test_scalar_subexpression():
    G = NeuronGroup(10, '''v : 1
                           number : 1 (shared)''', threshold='False')
    S = Synapses(G, G, '''s : 1 (shared)
                          sub = number_post + s : 1 (shared)''',
                 on_pre='v+=s')
    S.connect()
    S.s = 100
    G.number = 50
    assert S.sub[:] == 150

    assert_raises(SyntaxError, lambda: Synapses(G, G, '''s : 1 (shared)
                                                     sub = v_post + s : 1 (shared)''',
                                                on_pre='v+=s'))


@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_external_variables():
    # Make sure that external variables are correctly resolved
    source = SpikeGeneratorGroup(1, [0], [0]*ms)
    target = NeuronGroup(1, 'v:1')
    w_var = 1
    amplitude = 2
    syn = Synapses(source, target, 'w=w_var : 1',
                   on_pre='v+=amplitude*w')
    syn.connect()
    run(defaultclock.dt)
    assert target.v[0] == 2


@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_event_driven():
    # Fake example, where the synapse is actually not changing the state of the
    # postsynaptic neuron, the pre- and post spiketrains are regular spike
    # trains with different rates
    pre = NeuronGroup(2, '''dv/dt = rate : 1
                            rate : Hz''', threshold='v>1', reset='v=0')
    pre.rate = [1000, 1500] * Hz
    post = NeuronGroup(2, '''dv/dt = rate : 1
                             rate : Hz''', threshold='v>1', reset='v=0')
    post.rate = [1100, 1400] * Hz
    # event-driven formulation
    taupre = 20 * ms
    taupost = taupre
    gmax = .01
    dApre = .01
    dApost = -dApre * taupre / taupost * 1.05
    dApost *= gmax
    dApre *= gmax
    # event-driven
    S1 = Synapses(pre, post,
                  '''w : 1
                     dApre/dt = -Apre/taupre : 1 (event-driven)
                     dApost/dt = -Apost/taupost : 1 (event-driven)''',
                  on_pre='''Apre += dApre
                         w = clip(w+Apost, 0, gmax)''',
                  on_post='''Apost += dApost
                          w = clip(w+Apre, 0, gmax)''')
    S1.connect(j='i')
    # not event-driven
    S2 = Synapses(pre, post,
                  '''w : 1
                     Apre : 1
                     Apost : 1''',
                  on_pre='''Apre=Apre*exp((lastupdate-t)/taupre)+dApre
                         Apost=Apost*exp((lastupdate-t)/taupost)
                         w = clip(w+Apost, 0, gmax)''',
                  on_post='''Apre=Apre*exp((lastupdate-t)/taupre)
                          Apost=Apost*exp((lastupdate-t)/taupost) +dApost
                          w = clip(w+Apre, 0, gmax)''')
    S2.connect(j='i')
    S1.w = 0.5*gmax
    S2.w = 0.5*gmax
    run(25*ms)
    # The two formulations should yield identical results
    assert_allclose(S1.w[:], S2.w[:])


@attr('codegen-independent')
def test_repr():
    G = NeuronGroup(1, 'v: volt', threshold='False')
    S = Synapses(G, G,
                 '''w : 1
                    dApre/dt = -Apre/taupre : 1 (event-driven)
                    dApost/dt = -Apost/taupost : 1 (event-driven)''',
                 on_pre='''Apre += dApre
                        w = clip(w+Apost, 0, gmax)''',
                 on_post='''Apost += dApost
                         w = clip(w+Apre, 0, gmax)''')
    # Test that string/LaTeX representations do not raise errors
    for func in [str, repr, sympy.latex]:
        assert len(func(S.equations))


@attr('codegen-independent')
def test_variables_by_owner():
    # Test the `variables_by_owner` convenience function
    G = NeuronGroup(10, 'v : 1')
    G2 = NeuronGroup(10, '''v : 1
                            w : 1''')
    S = Synapses(G, G2, 'x : 1')

    # Check that the variables returned as owned by the pre/post groups are the
    # variables stored in the respective groups. We only compare the `Variable`
    # objects, as the names may be different (e.g. ``v_post`` vs. ``v``)
    G_variables = {key: value for key, value in G.variables.items()
                   if value.owner.name==G.name}  # exclude dt
    G2_variables = {key: value for key, value in G2.variables.items()
                    if value.owner.name==G2.name}
    assert set(G_variables.values()) == set(variables_by_owner(S.variables, G).values())
    assert set(G2_variables.values()) == set(variables_by_owner(S.variables, G2).values())
    assert len(set(variables_by_owner(S.variables, S)) & set(G_variables.values())) == 0
    assert len(set(variables_by_owner(S.variables, S)) & set(G2_variables.values())) == 0
    # Just test a few examples for synaptic variables
    assert all(varname in variables_by_owner(S.variables, S)
               for varname in ['x', 'N', 'N_incoming', 'N_outgoing'])


@attr('codegen-independent')
def check_permutation_code(code):
    from collections import defaultdict
    vars = get_identifiers(code)
    indices = defaultdict(lambda: '_idx')
    for var in vars:
        if var.endswith('_syn'):
            indices[var] = '_idx'
        elif var.endswith('_pre'):
            indices[var] ='_presynaptic_idx'
        elif var.endswith('_post'):
            indices[var] = '_postsynaptic_idx'
        elif var.endswith('_const'):
            indices[var] = '0'
    variables = dict()
    variables.update(DEFAULT_FUNCTIONS)
    for var in indices:
        if var.endswith('_const'):
            variables[var] = Constant(var, 1, 42, owner=device)
        else:
            variables[var] = ArrayVariable(var, 1, None, 10, device)
    variables['_presynaptic_idx'] = ArrayVariable(var, 1, None, 10, device)
    variables['_postsynaptic_idx'] = ArrayVariable(var, 1, None, 10, device)
    scalar_statements, vector_statements = make_statements(code, variables, float64)
    check_for_order_independence(vector_statements, variables, indices)


def numerically_check_permutation_code(code):
    # numerically checks that a code block used in the test below is permutation-independent by creating a
    # presynaptic and postsynaptic group of 3 neurons each, and a full connectivity matrix between them, then
    # repeatedly filling in random values for each of the variables, and checking for several random shuffles of
    # the synapse order that the result doesn't depend on it. This is a sort of test of the test itself, to make
    # sure we didn't accidentally assign a good/bad example to the wrong class.
    code = deindent(code)
    from collections import defaultdict
    vars = get_identifiers(code)
    indices = defaultdict(lambda: '_idx')
    vals = {}
    for var in vars:
        if var.endswith('_syn'):
            indices[var] = '_idx'
            vals[var] = zeros(9)
        elif var.endswith('_pre'):
            indices[var] ='_presynaptic_idx'
            vals[var] = zeros(3)
        elif var.endswith('_post'):
            indices[var] = '_postsynaptic_idx'
            vals[var] = zeros(3)
        elif var.endswith('_shared'):
            indices[var] = '0'
            vals[var] = zeros(1)
        elif var.endswith('_const'):
            indices[var] = '0'
            vals[var] = 42
    subs = dict((var, var+'['+idx+']')
                for var, idx in indices.items()
                if not var.endswith('_const'))
    code = word_substitute(code, subs)
    code = '''
from numpy import *
from numpy.random import rand, randn
for _idx in shuffled_indices:
    _presynaptic_idx = presyn[_idx]
    _postsynaptic_idx = postsyn[_idx]
{code}
    '''.format(code=indent(code))
    ns = vals.copy()
    ns['shuffled_indices'] = arange(9)
    ns['presyn'] = arange(9)%3
    ns['postsyn'] = arange(9)/3
    for _ in range(10):
        origvals = {}
        for k, v in vals.items():
            if not k.endswith('_const'):
                v[:] = randn(len(v))
                origvals[k] = v.copy()
        exec(code, ns)
        endvals = {}
        for k, v in vals.items():
            endvals[k] = copy(v)
        for _ in range(10):
            for k, v in vals.items():
                if not k.endswith('_const'):
                    v[:] = origvals[k]
            shuffle(ns['shuffled_indices'])
            exec(code, ns)
            for k, v in vals.items():
                try:
                    assert_allclose(v, endvals[k])
                except AssertionError:
                    raise OrderDependenceError()

SANITY_CHECK_PERMUTATION_ANALYSIS_EXAMPLE = False

permutation_analysis_good_examples = [
    'v_post += w_syn',
    'v_post *= w_syn',
    'v_post = v_post + w_syn',
    'v_post = v_post * w_syn',
    'v_post = w_syn * v_post',
    'v_post += 1',
    'v_post = 1',
    'v_post = c_const',
    'v_post = x_shared',
    'v_post += v_post # NOT_UFUNC_AT_VECTORISABLE',
    'v_post += c_const',
    'v_post += x_shared',
    #'v_post += w_syn*v_post', # this is a hard one (it is good for w*v but bad for w+v)
    'v_post += sin(-v_post) # NOT_UFUNC_AT_VECTORISABLE',
    'v_post += u_post',
    'v_post += w_syn*v_pre',
    'v_post += sin(-v_post) # NOT_UFUNC_AT_VECTORISABLE',
    'v_post -= sin(v_post) # NOT_UFUNC_AT_VECTORISABLE',
    'v_post += v_pre',
    'v_pre += v_post',
    'v_pre += c_const',
    'v_pre += x_shared',
    'w_syn = v_pre',
    'w_syn = a_syn',
    'w_syn += a_syn',
    'w_syn *= a_syn',
    'w_syn -= a_syn',
    'w_syn /= a_syn',
    'w_syn += 1',
    'w_syn += c_const',
    'w_syn += x_shared',
    'w_syn *= 2',
    'w_syn *= c_const',
    'w_syn *= x_shared',
    '''
    w_syn = a_syn
    a_syn += 1
    ''',
    '''
    w_syn = a_syn
    a_syn += c_const
    ''',
    '''
    w_syn = a_syn
    a_syn += x_shared
    ''',
    'v_post *= 2',
    'v_post *= w_syn',
    '''
    v_pre = 0
    w_syn = v_pre
    ''',
    '''
    v_pre = c_const
    w_syn = v_pre
    ''',
    '''
    v_pre = x_shared
    w_syn = v_pre
    ''',
    '''
    ge_syn += w_syn
    Apre_syn += 3
    w_syn = clip(w_syn + Apost_syn, 0, 10)
    ''',
    '''
    ge_syn += w_syn
    Apre_syn += c_const
    w_syn = clip(w_syn + Apost_syn, 0, 10)
    ''',
    '''
    ge_syn += w_syn
    Apre_syn += x_shared
    w_syn = clip(w_syn + Apost_syn, 0, 10)
    ''',
    '''
    a_syn = v_pre
    v_post += a_syn
    ''',
    '''
    v_post += v_post # NOT_UFUNC_AT_VECTORISABLE
    v_post += v_post
    ''',
    '''
    v_post += 1
    x = v_post
    ''',
    ]

permutation_analysis_bad_examples = [
    'v_pre = w_syn',
    'v_post = v_pre',
    'v_post = w_syn',
    'v_post += w_syn+v_post',
    'v_post += rand()', # rand() has state, and therefore this is order dependent
    '''
    a_syn = v_post
    v_post += w_syn
    ''',
    '''
    x = w_syn
    v_pre = x
    ''',
    '''
    x = v_pre
    v_post = x
    ''',
    '''
    v_post += v_pre
    v_pre += v_post
    ''',
    '''
    b_syn = v_post
    v_post += a_syn
    ''',
    '''
    v_post += w_syn
    u_post += v_post
    ''',
    '''
    v_post += 1
    w_syn = v_post
    ''',
    ]


@attr('codegen-independent')
def test_permutation_analysis():
    # Examples that should work
    for example in permutation_analysis_good_examples:
        if SANITY_CHECK_PERMUTATION_ANALYSIS_EXAMPLE:
            try:
                numerically_check_permutation_code(example)
            except OrderDependenceError:
                raise AssertionError(('Test unexpectedly raised a numerical '
                                      'OrderDependenceError on these '
                                      'statements:\n') + example)
        try:
            check_permutation_code(example)
        except OrderDependenceError:
            raise AssertionError(('Test unexpectedly raised an '
                                  'OrderDependenceError on these '
                                  'statements:\n') + example)

    for example in permutation_analysis_bad_examples:
        if SANITY_CHECK_PERMUTATION_ANALYSIS_EXAMPLE:
            try:
                assert_raises(OrderDependenceError, numerically_check_permutation_code, example)
            except AssertionError:
                raise AssertionError("Order dependence not raised numerically for example: "+example)
        try:
            assert_raises(OrderDependenceError, check_permutation_code, example)
        except AssertionError:
            raise AssertionError("Order dependence not raised for example: "+example)


@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_vectorisation():
    source = NeuronGroup(10, 'v : 1', threshold='v>1')
    target = NeuronGroup(10, '''x : 1
                                y : 1''')
    syn = Synapses(source, target, 'w_syn : 1',
                   on_pre='''v_pre += w_syn
                          x_post = y_post
                       ''')
    syn.connect()
    syn.w_syn = 1
    source.v['i<5'] = 2
    target.y = 'i'
    run(defaultclock.dt)
    assert_equal(source.v[:5], 12)
    assert_equal(source.v[5:], 0)
    assert_equal(target.x[:], target.y[:])


@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_vectorisation_STDP_like():
    # Test the use of pre- and post-synaptic traces that are stored in the
    # pre/post group instead of in the synapses
    w_max = 10
    neurons = NeuronGroup(6, '''dv/dt = rate : 1
                                ge : 1
                                rate : Hz
                                dA/dt = -A/(1*ms) : 1''', threshold='v>1', reset='v=0')
    # Note that the synapse does not actually increase the target v, we want
    # to have simple control about when neurons spike. Also, we separate the
    # "depression" and "facilitation" completely. The example also uses
    # subgroups, which should complicate things further.
    # This test should try to capture the spirit of indexing in such a use case,
    # it simply compares the results to fixed pre-calculated values
    syn = Synapses(neurons[:3], neurons[3:], '''w_dep : 1
                                                w_fac : 1''',
                   on_pre='''ge_post += w_dep - w_fac
                          A_pre += 1
                          w_dep = clip(w_dep + A_post, 0, w_max)
                       ''',
                   on_post='''A_post += 1
                           w_fac = clip(w_fac + A_pre, 0, w_max)
                        ''')
    syn.connect()
    neurons.rate = 1000*Hz
    neurons.v = 'abs(3-i)*0.1 + 0.7'
    run(2*ms)
    # Make sure that this test is invariant to synapse order
    indices = np.argsort(np.array(list(zip(syn.i[:], syn.j[:])),
                                  dtype=[('i', '<i4'), ('j', '<i4')]),
                         order=['i', 'j'])
    assert_allclose(syn.w_dep[:][indices],
                    [1.29140162, 1.16226149, 1.04603529, 1.16226149, 1.04603529,
                     0.94143176, 1.04603529, 0.94143176, 6.2472887],
                    rtol=1e-6, atol=1e-12)
    assert_allclose(syn.w_fac[:][indices],
                    [5.06030369, 5.62256002, 6.2472887, 5.62256002, 6.2472887,
                     6.941432, 6.2472887, 6.941432, 1.04603529],
                    rtol=1e-6, atol=1e-12)
    assert_allclose(neurons.A[:],
                    [1.69665715, 1.88517461, 2.09463845, 2.32737606, 2.09463845,
                     1.88517461],
                    rtol=1e-6, atol=1e-12)
    assert_allclose(neurons.ge[:],
                    [0., 0., 0., -7.31700015, -8.13000011, -4.04603529],
                    rtol=1e-6, atol=1e-12)




@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_synaptic_equations():
    # Check that integration works for synaptic equations
    G = NeuronGroup(10, '')
    tau = 10*ms
    S = Synapses(G, G, 'dw/dt = -w / tau : 1 (clock-driven)')
    S.connect(j='i')
    S.w = 'i'
    run(10*ms)
    assert_allclose(S.w[:], np.arange(10) * np.exp(-1))


@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_synapses_to_synapses():
    source = SpikeGeneratorGroup(3, [0, 1, 2], [0, 0, 0]*ms, period=2*ms)
    modulator = SpikeGeneratorGroup(3, [0, 2], [1, 3]*ms)
    target = NeuronGroup(3, 'v : integer')
    conn = Synapses(source, target, 'w : integer', on_pre='v += w')
    conn.connect(j='i')
    conn.w = 1
    modulatory_conn = Synapses(modulator, conn, on_pre='w += 1')
    modulatory_conn.connect(j='i')
    run(5*ms)
    # First group has its weight increased to 2 after the first spike
    # Third group has its weight increased to 2 after the second spike
    assert_array_equal(target.v, [5, 3, 4])


def test_ufunc_at_vectorisation():
    if prefs.codegen.target != 'numpy':
        raise SkipTest('numpy-only test')
    for code in permutation_analysis_good_examples:
        should_be_able_to_use_ufunc_at = not 'NOT_UFUNC_AT_VECTORISABLE' in code
        if should_be_able_to_use_ufunc_at:
            use_ufunc_at_list = [False, True]
        else:
            use_ufunc_at_list = [True]
        code = deindent(code)
        vars = get_identifiers(code)
        vars_src = []
        vars_tgt = []
        vars_syn = []
        vars_shared = []
        vars_const = {}
        for var in vars:
            if var.endswith('_pre'):
                vars_src.append(var[:-4])
            elif var.endswith('_post'):
                vars_tgt.append(var[:-5])
            elif var.endswith('_syn'):
                vars_syn.append(var[:-4])
            elif var.endswith('_shared'):
                vars_shared.append(var[:-7])
            elif var.endswith('_const'):
                vars_const[var[:-6]] = 42
        eqs_src = '\n'.join(var+':1' for var in vars_src)
        eqs_tgt = '\n'.join(var+':1' for var in vars_tgt)
        eqs_syn = '\n'.join(var+':1' for var in vars_syn)
        eqs_syn += '\n' + '\n'.join(var+':1 (shared)' for var in vars_shared)
        origvals = {}
        endvals = {}
        try:
            BrianLogger._log_messages.clear()
            with catch_logs(log_level=logging.INFO) as caught_logs:
                for use_ufunc_at in use_ufunc_at_list:
                    NumpyCodeGenerator._use_ufunc_at_vectorisation = use_ufunc_at
                    src = NeuronGroup(3, eqs_src, threshold='True', name='src')
                    tgt = NeuronGroup(3, eqs_tgt, name='tgt')
                    syn = Synapses(src, tgt, eqs_syn,
                                   on_pre=code.replace('_syn', '').replace('_const', '').replace('_shared', ''),
                                   name='syn', namespace=vars_const)
                    syn.connect()
                    for G, vars in [(src, vars_src), (tgt, vars_tgt), (syn, vars_syn)]:
                        for var in vars:
                            fullvar = var+G.name
                            if fullvar in origvals:
                                G.state(var)[:] = origvals[fullvar]
                            else:
                                val = rand(len(G))
                                G.state(var)[:] = val
                                origvals[fullvar] = val.copy()
                    Network(src, tgt, syn).run(defaultclock.dt)
                    for G, vars in [(src, vars_src), (tgt, vars_tgt), (syn, vars_syn)]:
                        for var in vars:
                            fullvar = var+G.name
                            val = G.state(var)[:].copy()
                            if fullvar in endvals:
                                assert_allclose(val, endvals[fullvar])
                            else:
                                endvals[fullvar] = val
                numpy_generator_messages = [l for l in caught_logs
                                            if l[1]=='brian2.codegen.generators.numpy_generator']
                if should_be_able_to_use_ufunc_at:
                    assert len(numpy_generator_messages) == 0
                else:
                    assert len(numpy_generator_messages) == 1
                    log_lev, log_mod, log_msg = numpy_generator_messages[0]
                    assert log_msg.startswith('Failed to vectorise code')
        finally:
            NumpyCodeGenerator._use_ufunc_at_vectorisation = True # restore it


@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_synapses_to_synapses_summed_variable():
    source = NeuronGroup(5, '', threshold='False')
    target = NeuronGroup(5, '')
    conn = Synapses(source, target, 'w : integer')
    conn.connect(j='i')
    conn.w = 1
    summed_conn = Synapses(source, conn, '''w_post = x : integer (summed)
                                            x : integer''')
    summed_conn.connect('i>=j')
    summed_conn.x = 'i'
    run(defaultclock.dt)
    assert_array_equal(conn.w[:], [10, 10, 9, 7, 4])


@attr('codegen-independent')
def test_synapse_generator_syntax():
    parsed = parse_synapse_generator('k for k in sample(1, N, p=p) if abs(i-k)<10')
    assert parsed['element'] == 'k'
    assert parsed['iteration_variable'] == 'k'
    assert parsed['iterator_func'] == 'sample'
    assert parsed['iterator_kwds']['low'] == '1'
    assert parsed['iterator_kwds']['high'] == 'N'
    assert parsed['iterator_kwds']['step'] == '1'
    assert parsed['iterator_kwds']['p'] == 'p'
    assert parsed['iterator_kwds']['size'] is None
    assert parsed['iterator_kwds']['sample_size'] == 'random'
    assert parsed['if_expression'] == 'abs(i - k) < 10'
    parsed = parse_synapse_generator('k for k in sample(N, size=5) if abs(i-k)<10')
    assert parsed['element'] == 'k'
    assert parsed['iteration_variable'] == 'k'
    assert parsed['iterator_func'] == 'sample'
    assert parsed['iterator_kwds']['low'] == '0'
    assert parsed['iterator_kwds']['high'] == 'N'
    assert parsed['iterator_kwds']['step'] == '1'
    assert parsed['iterator_kwds']['p'] is None
    assert parsed['iterator_kwds']['size'] == '5'
    assert parsed['iterator_kwds']['sample_size'] == 'fixed'
    assert parsed['if_expression'] == 'abs(i - k) < 10'
    parsed = parse_synapse_generator('k+1 for k in range(i-100, i+100, 2)')
    assert parsed['element'] == 'k + 1'
    assert parsed['iteration_variable'] == 'k'
    assert parsed['iterator_func'] == 'range'
    assert parsed['iterator_kwds']['low'] == 'i - 100'
    assert parsed['iterator_kwds']['high'] == 'i + 100'
    assert parsed['iterator_kwds']['step'] == '2'
    assert parsed['if_expression'] == 'True'
    assert_raises(SyntaxError, parse_synapse_generator, 'mad rubbish')
    assert_raises(SyntaxError, parse_synapse_generator, 'k+1')
    assert_raises(SyntaxError, parse_synapse_generator, 'k for k in range()')
    assert_raises(SyntaxError, parse_synapse_generator, 'k for k in range(1,2,3,4)')
    assert_raises(SyntaxError, parse_synapse_generator, 'k for k in range(1,2,3) if ')
    assert_raises(SyntaxError, parse_synapse_generator, 'k[1:3] for k in range(1,2,3)')
    assert_raises(SyntaxError, parse_synapse_generator, 'k for k in x')
    assert_raises(SyntaxError, parse_synapse_generator, 'k for k in x[1:5]')
    assert_raises(SyntaxError, parse_synapse_generator, 'k for k in sample()')
    assert_raises(SyntaxError, parse_synapse_generator, 'k for k in sample(N, p=0.1, size=5)')
    assert_raises(SyntaxError, parse_synapse_generator, 'k for k in sample(N, q=0.1)')


@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_synapse_generator_deterministic():
    # Same as "test_connection_string_deterministic" but using the generator
    # syntax
    G = NeuronGroup(16, 'v : 1', threshold='False')
    G.v = 'i'
    G2 = NeuronGroup(4, 'v : 1', threshold='False')
    G2.v = '16 + i'

    # Full connection
    expected_full = np.ones((len(G), len(G2)))

    S1 = Synapses(G, G2, 'w:1', 'v+=w')
    S1.connect(j='k for k in range(N_post)')

    # Full connection without self-connections
    expected_no_self = np.ones((len(G), len(G))) - np.eye(len(G))

    S2 = Synapses(G, G, 'w:1', 'v+=w')
    S2.connect(j='k for k in range(N_post) if k != i')

    S3 = Synapses(G, G, 'w:1', 'v+=w')
    # slightly confusing with j on the RHS, but it should work...
    S3.connect(j='k for k in range(N_post) if j != i')

    S4 = Synapses(G, G, 'w:1', 'v+=w')
    S4.connect(j='k for k in range(N_post) if v_post != v_pre')

    # One-to-one connectivity
    expected_one_to_one = np.eye(len(G))

    S5 = Synapses(G, G, 'w:1', 'v+=w')
    S5.connect(j='k for k in range(N_post) if k == i')  # inefficient

    S6 = Synapses(G, G, 'w:1', 'v+=w')
    # slightly confusing with j on the RHS, but it should work...
    S6.connect(j='k for k in range(N_post) if j == i')  # inefficient

    S7 = Synapses(G, G, 'w:1', 'v+=w')
    S7.connect(j='k for k in range(N_post) if v_pre == v_post')  # inefficient

    S8 = Synapses(G, G, 'w:1', 'v+=w')
    S8.connect(j='i for _ in range(1)')  # efficient

    S9 = Synapses(G, G, 'w:1', 'v+=w')
    S9.connect(j='i')  # short form of the above

    # A few more tests of deterministic connections where the generator syntax
    # is particularly useful

    # Ring structure
    S10 = Synapses(G, G, 'w:1', 'v+=w')
    S10.connect(j='(i + (-1)**k) % N_post for k in range(2)')
    expected_ring = np.zeros((len(G), len(G)), dtype=np.int32)
    expected_ring[np.arange(15), np.arange(15)+1] = 1  # Next cell
    expected_ring[np.arange(1, 16), np.arange(15)] = 1  # Previous cell
    expected_ring[[0, 15], [15, 0]] = 1  # wrap around the ring

    # Diverging connection pattern
    S11 = Synapses(G2, G, 'w:1', 'v+=w')
    S11.connect(j='i*4 + k for k in range(4)')
    expected_diverging = np.zeros((len(G2), len(G)), dtype=np.int32)
    for source in range(4):
        expected_diverging[source, np.arange(4) + source*4] = 1

    # Converging connection pattern
    S12 = Synapses(G, G2, 'w:1', 'v+=w')
    S12.connect(j='int(i/4)')
    expected_converging = np.zeros((len(G), len(G2)), dtype=np.int32)
    for target in range(4):
        expected_converging[np.arange(4) + target*4, target] = 1

    # skip if invalid
    S13 = Synapses(G2, G2, 'w:1', 'v+=w')
    S13.connect(j='i+(-1)**k for k in range(2)', skip_if_invalid=True)
    expected_offdiagonal = np.zeros((len(G2), len(G2)), dtype=np.int32)
    expected_offdiagonal[np.arange(len(G2)-1), np.arange(len(G2)-1)+1] = 1
    expected_offdiagonal[np.arange(len(G2)-1)+1, np.arange(len(G2)-1)] = 1

    with catch_logs() as _:  # Ignore warnings about empty synapses
        run(0*ms)  # for standalone

    _compare(S1, expected_full)
    _compare(S2, expected_no_self)
    _compare(S3, expected_no_self)
    _compare(S4, expected_no_self)
    _compare(S5, expected_one_to_one)
    _compare(S6, expected_one_to_one)
    _compare(S7, expected_one_to_one)
    _compare(S8, expected_one_to_one)
    _compare(S9, expected_one_to_one)
    _compare(S10, expected_ring)
    _compare(S11, expected_diverging)
    _compare(S12, expected_converging)
    _compare(S13, expected_offdiagonal)


@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_synapse_generator_random():
    # The same tests as test_connection_random_without_condition, but using
    # the generator syntax
    G = NeuronGroup(4, '''v: 1
                          x : integer''', threshold='False')
    G.x = 'i'
    G2 = NeuronGroup(7, '''v: 1
                           y : 1''', threshold='False')
    G2.y = '1.0*i/N'

    S1 = Synapses(G, G2, 'w:1', 'v+=w')
    S1.connect(j='k for k in sample(N_post, p=0)')

    S2 = Synapses(G, G2, 'w:1', 'v+=w')
    S2.connect(j='k for k in sample(N_post, p=1)')

    # Just make sure using values between 0 and 1 work in principle
    S3 = Synapses(G, G2, 'w:1', 'v+=w')
    S3.connect(j='k for k in sample(N_post, p=0.3)')

    # Use pre-/post-synaptic variables for "stochastic" connections that are
    # actually deterministic
    S4 = Synapses(G, G2, 'w:1', on_pre='v+=w')
    S4.connect(j='k for k in sample(N_post, p=int(x_pre==2)*1.0)')

    with catch_logs() as _:  # Ignore warnings about empty synapses
        run(0*ms)  # for standalone

    assert len(S1) == 0
    _compare(S2, np.ones((len(G), len(G2))))
    assert 0 <= len(S2) <= len(G) * len(G2)
    assert len(S4) == 7
    assert_equal(S4.i, np.ones(7)*2)
    assert_equal(S4.j, np.arange(7))


@attr('standalone-compatible')
@with_setup(teardown=reinit_devices)
def test_synapse_generator_random_with_condition():
    G = NeuronGroup(4, 'v: 1', threshold='False')

    S1 = Synapses(G, G, 'w:1', 'v+=w')
    S1.connect(j='k for k in sample(N_post, p=0) if i != k')

    S2 = Synapses(G, G, 'w:1', 'v+=w')
    S2.connect(j='k for k in sample(N_post, p=1) if i != k')
    expected2 = np.ones((len(G), len(G))) - np.eye(len(G))

    S3 = Synapses(G, G, 'w:1', 'v+=w')
    S3.connect(j='k for k in sample(N_post, p=0) if i >= 2')

    S4 = Synapses(G, G, 'w:1', 'v+=w')
    S4.connect(j='k for k in sample(N_post, p=1.0) if i >= 2')
    expected4 = np.zeros((len(G), len(G)))
    expected4[2, :] = 1
    expected4[3, :] = 1

    S5 = Synapses(G, G, 'w:1', 'v+=w')
    S5.connect(j='k for k in sample(N_post, p=0) if j < 2')  # inefficient

    S6 = Synapses(G, G, 'w:1', 'v+=w')
    S6.connect(j='k for k in sample(2, p=0)')  # better

    S7 = Synapses(G, G, 'w:1', 'v+=w')
    expected7 = np.zeros((len(G), len(G)))
    expected7[:, 0] = 1
    expected7[:, 1] = 1
    S7.connect(j='k for k in sample(N_post, p=1.0) if j < 2')  # inefficient

    S8 = Synapses(G, G, 'w:1', 'v+=w')
    S8.connect(j='k for k in sample(2, p=1.0)')  # better

    # Just checking that everything works in principle (we can't check the
    # actual connections)
    S9 = Synapses(G, G, 'w:1', 'v+=w')
    S9.connect(j='k for k in sample(N_post, p=0.001) if i != k')

    S10 = Synapses(G, G, 'w:1', 'v+=w')
    S10.connect(j='k for k in sample(N_post, p=0.03) if i != k')

    S11 = Synapses(G, G, 'w:1', 'v+=w')
    S11.connect(j='k for k in sample(N_post, p=0.1) if i != k')

    S12 = Synapses(G, G, 'w:1', 'v+=w')
    S12.connect(j='k for k in sample(N_post, p=0.9) if i != k')

    S13 = Synapses(G, G, 'w:1', 'v+=w')
    S13.connect(j='k for k in sample(N_post, p=0.001) if i >= 2')

    S14 = Synapses(G, G, 'w:1', 'v+=w')
    S14.connect(j='k for k in sample(N_post, p=0.03) if i >= 2')

    S15 = Synapses(G, G, 'w:1', 'v+=w')
    S15.connect(j='k for k in sample(N_post, p=0.1) if i >= 2')

    S16 = Synapses(G, G, 'w:1', 'v+=w')
    S16.connect(j='k for k in sample(N_post, p=0.9) if i >= 2')

    S17 = Synapses(G, G, 'w:1', 'v+=w')
    S17.connect(j='k for k in sample(N_post, p=0.001) if j < 2')

    S18 = Synapses(G, G, 'w:1', 'v+=w')
    S18.connect(j='k for k in sample(N_post, p=0.03) if j < 2')

    S19 = Synapses(G, G, 'w:1', 'v+=w')
    S19.connect(j='k for k in sample(N_post, p=0.1) if j < 2')

    S20 = Synapses(G, G, 'w:1', 'v+=w')
    S20.connect(j='k for k in sample(N_post, p=0.9) if j < 2')

    S21 = Synapses(G, G, 'w:1', 'v+=w')
    S21.connect(j='k for k in sample(2, p=0.001)')

    S22 = Synapses(G, G, 'w:1', 'v+=w')
    S22.connect(j='k for k in sample(2, p=0.03)')

    S23 = Synapses(G, G, 'w:1', 'v+=w')
    S23.connect(j='k for k in sample(2, p=0.1)')

    S24 = Synapses(G, G, 'w:1', 'v+=w')
    S24.connect(j='k for k in sample(2, p=0.9)')

    # Some more tests specific to the generator syntax
    S25 = Synapses(G, G, 'w:1', on_pre='v+=w')
    S25.connect(j='i+1 for _ in sample(1, p=0.5) if i < N_post-1')

    S26 = Synapses(G, G, 'w:1', on_pre='v+=w')
    S26.connect(j='i+k for k in sample(N_post-i, p=0.5)')


    with catch_logs() as _:  # Ignore warnings about empty synapses
        run(0 * ms)  # for standalone

    assert len(S1) == 0
    _compare(S2, expected2)
    assert len(S3) == 0
    _compare(S4, expected4)
    assert len(S5) == 0
    assert len(S6) == 0
    _compare(S7, expected7)
    _compare(S8, expected7)
    assert not any(S9.i == S9.j)
    assert 0 <= len(S9) <= len(G) * (len(G) - 1)
    assert not any(S10.i == S10.j)
    assert 0 <= len(S10) <= len(G) * (len(G) - 1)
    assert not any(S11.i == S11.j)
    assert 0 <= len(S11) <= len(G) * (len(G) - 1)
    assert not any(S12.i == S12.j)
    assert 0 <= len(S12) <= len(G) * (len(G) - 1)
    assert all(S13.i[:] >= 2)
    assert 0 <= len(S13) <= len(G) * (len(G) - 1)
    assert all(S14.i[:] >= 2)
    assert 0 <= len(S14) <= len(G) * (len(G) - 1)
    assert all(S15.i[:] >= 2)
    assert 0 <= len(S15) <= len(G) * (len(G) - 1)
    assert all(S16.i[:] >= 2)
    assert 0 <= len(S16) <= len(G) * (len(G) - 1)
    assert all(S17.j[:] < 2)
    assert 0 <= len(S17) <= len(G) * (len(G) - 1)
    assert all(S18.j[:] < 2)
    assert 0 <= len(S18) <= len(G) * (len(G) - 1)
    assert all(S19.j[:] < 2)
    assert 0 <= len(S19) <= len(G) * (len(G) - 1)
    assert all(S20.j[:] < 2)
    assert 0 <= len(S20) <= len(G) * (len(G) - 1)
    assert all(S21.j[:] < 2)
    assert 0 <= len(S21) <= len(G) * (len(G) - 1)
    assert all(S22.j[:] < 2)
    assert 0 <= len(S22) <= len(G) * (len(G) - 1)
    assert all(S23.j[:] < 2)
    assert 0 <= len(S23) <= len(G) * (len(G) - 1)
    assert all(S24.j[:] < 2)
    assert 0 <= len(S24) <= len(G) * (len(G) - 1)
    assert 0 <= len(S25) <= len(G)
    assert_equal(S25.j[:], S25.i[:] + 1)
    assert 0 <= len(S26) <= (1 + len(G)) * (len(G) / 2)
    assert all(S26.j[:] >= S26.i[:])


if __name__ == '__main__':
    SANITY_CHECK_PERMUTATION_ANALYSIS_EXAMPLE = True
    from brian2 import prefs
    # prefs.codegen.target = 'numpy'
    # prefs._backup()
    import time
    start = time.time()

    test_creation()
    test_name_clashes()
    test_incoming_outgoing()
    test_connection_string_deterministic()
    test_connection_random_with_condition()
    test_connection_random_without_condition()
    test_connection_random_with_indices()
    test_connection_multiple_synapses()
    test_connection_arrays()
    reinit_devices()
    test_state_variable_assignment()
    test_state_variable_indexing()
    test_indices()
    test_subexpression_references()
    test_delay_specification()
    test_pre_before_post()
    test_pre_post_simple()
    test_transmission_simple()
    test_transmission_custom_event()
    test_invalid_custom_event()
    test_transmission()
    test_transmission_all_to_one_heterogeneous_delays()
    test_transmission_one_to_all_heterogeneous_delays()
    test_transmission_scalar_delay()
    test_transmission_scalar_delay_different_clocks()
    test_clocks()
    test_changed_dt_spikes_in_queue()
    test_no_synapses()
    test_summed_variable()
    test_summed_variable_errors()
    test_scalar_parameter_access()
    test_scalar_subexpression()
    test_external_variables()
    test_event_driven()
    test_repr()
    test_variables_by_owner()
    test_permutation_analysis()
    test_vectorisation()
    test_vectorisation_STDP_like()
    test_synaptic_equations()
    test_synapses_to_synapses()
    test_synapses_to_synapses_summed_variable()
    try:
        test_ufunc_at_vectorisation()
    except SkipTest:
        print('Skipping numpy-only test')
    test_synapse_generator_syntax()
    test_synapse_generator_deterministic()
    test_synapse_generator_random()
    test_synapse_generator_random_with_condition()

    print('Tests took', time.time()-start)
