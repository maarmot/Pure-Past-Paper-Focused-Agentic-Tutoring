"""Numerically integrate the three generated H3 forces without using the tutors' antiderivatives.

The caller supplies force in N, time in s, mass in kg and initial velocity in m/s.
The forward integrator then uses only endpoint accelerations and velocities.
"""
from math import isclose, sqrt


def trace(end, force, mass, velocity, steps=12000):
    dt = end / steps
    x, distance = 0.0, 0.0
    positions = [x]
    reversals = []
    for j in range(steps):
        t = j * dt
        next_v = velocity + dt * (force(t) + force(t + dt)) / (2 * mass)
        dx = (next_v + velocity) * dt / 2
        x += dx
        distance += abs(dx)
        positions.append(x)
        if velocity * next_v < 0:
            reversals.append(t + dt * abs(velocity)/(abs(velocity) + abs(next_v)))
        velocity = next_v
    return x, distance, positions, reversals


def close(observed, expected):
    if not isclose(observed, expected, rel_tol=2e-6, abs_tol=2e-7):
        raise ValueError("Expected {} but integrated {}".format(expected, observed))


def verify():
    for mass, parameter, T in [(1, 1, 1), (3, 7, 2.5)]:
        # X specifies a force and asks for an initial velocity that closes the path.
        F0 = parameter
        force_x = lambda t: F0*(t/T - 1)
        drift = trace(2*T, force_x, mass, 0)[0]
        u = -drift/(2*T)
        close(u, F0*T/(3*mass))
        x, travel, xs, times = trace(2*T, force_x, mass, u)
        close(x, 0)
        B = F0*T*T/mass
        close(travel, 4*B/(9*sqrt(3)))
        close(max(xs), B/(9*sqrt(3)))
        close(min(xs), -B/(9*sqrt(3)))
        if len(times) != 2:
            raise ValueError("Wrong reversal count")
        for t, ref in zip(times, [T*(1-1/sqrt(3)), T*(1+1/sqrt(3))]):
            close(t, ref)
        close(trace(2*T, force_x, mass, u+0.4)[0], 2*T*0.4)

        # Y instead specifies initial velocity and asks for the force amplitude.
        u = parameter
        unit_force = lambda t: 1-2*t/T
        base = trace(T, lambda t: 0, mass, -u)[0]
        gain = trace(T, unit_force, mass, 0)[0]
        amplitude = -base/gain
        close(amplitude, 6*mass*u/T)
        end, distance, xs, times = trace(T, lambda t: amplitude*unit_force(t), mass, -u)
        close(end, 0)
        close(xs[len(xs)//2], 0)
        close(distance, 2*sqrt(3)*u*T/9)
        close(max(xs), sqrt(3)*u*T/18)
        close(min(xs), -sqrt(3)*u*T/18)
        if len(times) != 2:
            raise ValueError("Wrong reversal count")
        for t, ref in zip(times, [T*(3-sqrt(3))/6, T*(3+sqrt(3))/6]):
            close(t, ref)

        # The final replay specifies a return at rest. Independently test its
        # analytic candidate lambda=2 against motion over the full interval.
        final_x, travel, xs, times = trace(2*T, lambda t: mass*u/T*(6*t/T-4), mass, u, steps=24000)
        close(xs[len(xs)//2], 0)
        close(min(xs), 0)
        close(final_x, 2*u*T)
        close(travel, 62*u*T/27)
        close(travel/abs(final_x), 31/27)
        if len(times) != 2:
            raise ValueError("Wrong final replay reversal count")
        for t, ref in zip(times, [T/3,T]):
            close(t, ref)

        # A mistaken use of signed displacement as distance must be rejected.
        try:
            close(end, 2*sqrt(3)*u*T/9)
        except ValueError:
            continue
        raise AssertionError("Distance-versus-displacement fault escaped")
    print("Three H3 keys matched integration at two parameter sets. Signed-distance fault rejected.")


if __name__ == "__main__":
    verify()
