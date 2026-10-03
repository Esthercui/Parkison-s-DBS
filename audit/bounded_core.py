"""Review components, not a replacement performance experiment.

The objective is supplied as a callable. Optimizers receive only BudgetedOracle
or LegacyOracleView, never the complete objective table. Domain choice is
explicit; no default chooses the scientific answer about no stimulation.
"""
from dataclasses import dataclass
import math
from numbers import Integral
import time
import numpy as np

class BudgetExceeded(RuntimeError):
    pass

class InfeasibleMask(ValueError):
    pass

@dataclass(frozen=True)
class Domain:
    n_bits: int
    allow_empty: bool

    def __post_init__(self):
        if not isinstance(self.n_bits, int) or not 1 <= self.n_bits <= 16:
            raise ValueError("This bounded review supports 1–16 bits")
        if not isinstance(self.allow_empty, bool):
            raise TypeError("allow_empty must be explicitly True or False")

    def validate(self, mask):
        if isinstance(mask, bool) or not isinstance(mask, Integral):
            raise TypeError("mask must be an integer")
        if not 0 <= mask < (1 << self.n_bits):
            raise ValueError("mask outside domain")
        if mask == 0 and not self.allow_empty:
            raise InfeasibleMask("empty mask excluded by declared domain")
        return int(mask)

    @property
    def size(self):
        return (1 << self.n_bits) - (not self.allow_empty)

def decode_threshold(x, domain, threshold=0.5):
    x = np.asarray(x, dtype=float)
    if x.shape != (domain.n_bits,) or not np.isfinite(x).all():
        raise ValueError("one finite value per contact is required")
    bits = (x > threshold).astype(int)
    if not domain.allow_empty and not bits.any():
        bits[int(np.argmax(x))] = 1
    return bits

class BudgetedOracle:
    """Cache unique masks and charge every attempted underlying evaluation.

    Cached reads remain available after exhaustion and are logged. Unseen
    post-budget reads fail before invoking the objective. Failed/nonfinite
    objective calls consume an attempt and are not cached. This is an API
    accounting contract, not a security sandbox or a concurrent worker API.
    """
    def __init__(self, evaluator, budget, domain, *, evaluation_kind):
        if isinstance(budget, bool) or not isinstance(budget, Integral) or not 0 <= budget <= domain.size:
            raise ValueError("budget must fit the declared finite domain")
        self.__evaluator = evaluator
        self.budget = int(budget)
        self.domain = domain
        self.evaluation_kind = evaluation_kind
        self.__cache = {}
        self.records = []
        self.events = []
        self.attempted = 0
        self.completed = 0
        self.resources = dict(surrogate_predictions=0, surrogate_fits=0, optimizer_steps=0,
                              circuit_executions=0, shots=0)
        self.unmeasured_resources=set(self.resources)
        self.started = time.perf_counter()

    def evaluate(self, mask, *, phase="optimizer"):
        stamp = time.perf_counter()
        event = dict(request=len(self.events)+1, phase=phase,
                     at_seconds=stamp-self.started,
                     post_budget=self.attempted >= self.budget)
        try:
            mask = self.domain.validate(mask)
        except (ValueError, TypeError) as error:
            event.update(status="invalid_or_infeasible", error=str(error))
            self.events.append(event)
            raise
        event["mask"] = mask
        if mask in self.__cache:
            event.update(status="cache_hit", value=self.__cache[mask], charged=False)
            self.events.append(event)
            return self.__cache[mask]
        if self.attempted >= self.budget:
            event.update(status="budget_denied", charged=False)
            self.events.append(event)
            raise BudgetExceeded("unseen objective evaluation would exceed budget")
        self.attempted += 1
        try:
            value = float(self.__evaluator(mask))
            if not math.isfinite(value):
                raise ValueError("objective returned nonfinite cost")
        except Exception as error:
            event.update(status="objective_error", error=type(error).__name__, charged=True,
                         evaluation_seconds=time.perf_counter()-stamp)
            self.events.append(event)
            raise
        self.completed += 1
        self.__cache[mask] = value
        self.records.append((mask,value))
        event.update(status="evaluated", value=value, charged=True,
                     evaluation_seconds=time.perf_counter()-stamp)
        self.events.append(event)
        return value

    def count(self, resource, amount=1):
        if resource not in self.resources or not isinstance(amount, Integral) or amount < 0:
            raise ValueError("invalid resource counter")
        self.resources[resource] += int(amount)
        self.unmeasured_resources.discard(resource)

    def report(self):
        return dict(budget=self.budget, evaluation_kind=self.evaluation_kind,
                    objective_attempts=self.attempted, objective_completed=self.completed,
                    cache_hits=sum(e['status']=='cache_hit' for e in self.events),
                    denied=sum(e['status']=='budget_denied' for e in self.events),
                    objective_seconds=sum(e.get('evaluation_seconds',0) for e in self.events),
                    wall_seconds=time.perf_counter()-self.started,
                    resources={k:None if k in self.unmeasured_resources else v
                               for k,v in self.resources.items()}, events=list(self.events))

class LegacyOracleView:
    """Read-only scalar-lookup adapter for *all* historical Stage 3 methods.

    It blocks table export and unaccounted slices. Historical functions may
    raise BudgetExceeded; return the oracle's records when auditing that case.
    It does not repair historical feasibility rules or claim optimizer parity.
    """
    def __init__(self, oracle):
        self.oracle = oracle
        self.size = 1 << oracle.domain.n_bits

    def __len__(self):
        return self.size

    def __getitem__(self, mask):
        return self.oracle.evaluate(mask, phase="legacy_lookup")

    def __array__(self, *args, **kwargs):
        raise TypeError("full-table access is forbidden")

    def __iter__(self):
        raise TypeError("full-table iteration is forbidden")

def _coefficients(linear, pairs):
    linear = np.asarray(linear, dtype=float)
    pairs = np.asarray(pairs, dtype=float)
    n = len(linear)
    if linear.ndim != 1 or pairs.shape != (n,n) or not 1 <= n <= 16:
        raise ValueError("expected linear vector and square pair matrix, 1–16 bits")
    if not np.isfinite(linear).all() or not np.isfinite(pairs).all():
        raise ValueError("nonfinite coefficient")
    if np.any(np.tril(pairs) != 0):
        raise ValueError("pairs must be strictly upper triangular; avoid double counting")
    return linear, pairs

def quadratic_values(masks, offset, linear, pairs):
    linear, pairs = _coefficients(linear,pairs)
    if not math.isfinite(offset): raise ValueError("nonfinite offset")
    masks=np.asarray(masks, dtype=np.int64)
    if np.any(masks<0) or np.any(masks>=1<<len(linear)):
        raise ValueError("mask outside coefficient domain")
    bits=((masks[:,None] >> np.arange(len(linear))) & 1).astype(float)
    result=np.full(len(masks),offset,dtype=float)
    # Fixed summation order; no 65536 x 137 feature matrix needed.
    for i in range(len(linear)):
        result += linear[i]*bits[:,i]
        for j in range(i+1,len(linear)):
            result += pairs[i,j]*bits[:,i]*bits[:,j]
    return result

def minimize_surrogate_exhaustive(offset, linear, pairs, domain, *, excluded=(), accounting=None):
    """Enumerate every feasible, unexcluded 16-bit-or-smaller surrogate mask.

    This certifies the minimum of this supplied *floating-point fitted model*
    over the declared finite set. It does not solve an unknown true objective.
    With exclusions, it is the best unevaluated point, not an unrestricted min.
    """
    linear,pairs=_coefficients(linear,pairs)
    if len(linear)!=domain.n_bits: raise ValueError("domain/coefficients mismatch")
    excluded={domain.validate(x) for x in excluded}
    best_mask=None; best_value=math.inf; evaluated=0
    for start in range(0,1 << domain.n_bits,4096):
        masks=np.array([m for m in range(start,min(start+4096,1<<domain.n_bits))
                        if (domain.allow_empty or m) and m not in excluded],dtype=np.int64)
        if not len(masks): continue
        values=quadratic_values(masks,offset,linear,pairs)
        evaluated+=len(masks)
        index=int(np.argmin(values))
        if values[index]<best_value:
            best_mask=int(masks[index]);best_value=float(values[index])
    if accounting: accounting.count('surrogate_predictions',evaluated)
    if best_mask is None: raise ValueError("no unexcluded feasible masks")
    return dict(mask=best_mask,value=best_value,masks_evaluated=evaluated,
                scope="finite fitted surrogate, floating-point enumeration")

def qubo_to_ising(offset, linear, pairs):
    """x_i=(1-Z_i)/2; contact i is mask bit i (little endian)."""
    linear,pairs=_coefficients(linear,pairs)
    if not math.isfinite(offset): raise ValueError("nonfinite offset")
    constant=float(offset+linear.sum()/2+pairs.sum()/4)
    h=-linear/2-(pairs.sum(axis=0)+pairs.sum(axis=1))/4
    return constant,h,pairs/4

def run_surrogate_exhaustive(oracle, initial_masks, *, ridge=1e-3):
    """Budgeted fitted-surrogate baseline with complete finite enumeration.

    Initial data are explicitly provided and charged, including a zero control
    if the prespecified domain permits and the caller includes it. No random
    pool, true-objective table, or uncharged historical training data are used.
    """
    if not math.isfinite(ridge) or ridge<=0: raise ValueError("ridge must be positive")
    initial_masks=tuple(oracle.domain.validate(m) for m in initial_masks)
    if not initial_masks or len(set(initial_masks))>oracle.budget:
        raise ValueError("nonempty initial design must fit the budget")
    for resource in oracle.resources: oracle.count(resource,0)
    for m in initial_masks: oracle.evaluate(m,phase='initialization')
    n=oracle.domain.n_bits
    while oracle.attempted<oracle.budget:
        masks=np.array([m for m,_ in oracle.records],dtype=np.int64)
        bits=((masks[:,None]>>np.arange(n))&1).astype(float)
        cols=[np.ones(len(bits))]+[bits[:,i] for i in range(n)]
        cols += [bits[:,i]*bits[:,j] for i in range(n) for j in range(i+1,n)]
        design=np.column_stack(cols)
        y=np.array([v for _,v in oracle.records])
        coef=np.linalg.solve(design.T@design+ridge*np.eye(design.shape[1]),design.T@y)
        pairs=np.zeros((n,n));col=1+n
        for i in range(n):
            for j in range(i+1,n): pairs[i,j]=coef[col];col+=1
        oracle.count('surrogate_fits')
        result=minimize_surrogate_exhaustive(coef[0],coef[1:1+n],pairs,oracle.domain,
                                            excluded=masks,accounting=oracle)
        oracle.count('optimizer_steps')
        oracle.evaluate(result['mask'],phase='surrogate_proposal')
    return tuple(oracle.records)

def append_cost_phase(circuit, gamma, offset, linear, pairs):
    """Append exp(-i gamma H), including its constant global phase."""
    if not math.isfinite(gamma): raise ValueError("nonfinite gamma")
    constant,h,j=qubo_to_ising(offset,linear,pairs)
    circuit.global_phase -= gamma*constant
    for i,w in enumerate(h):
        if w: circuit.rz(2*gamma*float(w),i)
    for i in range(len(h)):
        for k in range(i+1,len(h)):
            if j[i,k]: circuit.rzz(2*gamma*float(j[i,k]),i,k)
