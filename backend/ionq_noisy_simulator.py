"""
IonQ Noisy Simulator wrapper — selects a hardware-derived noise model on
IonQ's hosted simulator.

Why this exists: pennylane_ionq.SimulatorDevice always submits with
target="simulator" and no noise field, hitting IonQ's *noiseless* simulator.
IonQ's Cloud REST API supports a `noise: {"model": "<system>"}` body field
that switches the simulator to a hardware-derived depolarizing-noise model.
The plugin doesn't expose this kwarg; we inject it by overriding reset().

Usage:
    from backend.ionq_noisy_simulator import IonQNoisySimulator
    dev = IonQNoisySimulator(wires=8, noise_model="forte-1", shots=1024)
    @qml.qnode(dev)
    def circuit(...): ...

Accepted noise_model identifiers (probed against IonQ Cloud 2026-05-01):
    ideal, harmony, harmony-1, harmony-2, aria-1, aria-2,
    forte-1, forte-enterprise-1, ideal-sampled

API key: read from IONQ_API_KEY env var, or pass via api_key=.
"""

from pennylane_ionq import SimulatorDevice


class IonQNoisySimulator(SimulatorDevice):
    """SimulatorDevice with hardware-derived noise model selection."""

    name = "IonQ Noisy Simulator (subclass)"
    short_name = "ionq.simulator.noisy"

    def __init__(self, wires, *, noise_model="forte-1", gateset="qis",
                 shots=1024, api_key=None):
        if shots is None:
            raise ValueError(
                "noisy IonQ simulator requires shots > 0 (analytic mode "
                "not supported server-side for noisy backends)"
            )
        self._noise_model = noise_model
        super().__init__(
            wires=wires, gateset=gateset, shots=shots, api_key=api_key
        )

    def reset(self, circuits_array_length=1):
        """Build job dict via parent, then inject the noise model field."""
        super().reset(circuits_array_length=circuits_array_length)
        # IonQ Cloud API noise field. Schema:
        #   "noise": {"model": "<system_name>"}
        # See https://docs.ionq.com/api-reference/v0.3/jobs (accessed 2026-05-01)
        self.job["noise"] = {"model": self._noise_model}
