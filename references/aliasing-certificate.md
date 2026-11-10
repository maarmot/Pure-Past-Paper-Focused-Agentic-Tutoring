# Optional formal layer: same snapshots, different motion

Use this after exploring the picture, or whenever the learner asks for the mathematics. The initial question needs no formula: can the same photographs be consistent with two different motions?

## What the camera measures

A dot travels counterclockwise on a unit circle, starting at the rightmost point. The camera records its full two-dimensional position at exact times. Position coordinates are dimensionless multiples of radius; time is seconds. The two candidate motions have fixed frequencies 1 and 11 turns per second:

\[
p_f(t)=(\cos(2\pi ft),\ \sin(2\pi ft)).
\]

This is an ideal model with exact timing and point observations, without exposure blur or measurement noise. A video of a real rotating object can have additional ambiguities and sensor effects.

At 10 snapshots per second, \(t_n=n/10\). The faster dot makes one extra complete revolution between each pair of camera exposures:

\[
2\pi\,11\frac n{10}=2\pi\frac n{10}+2\pi n.
\]

Whole turns leave both coordinates unchanged. Thus \(p_{11}(n/10)=p_1(n/10)\) for every integer \(n\), not just the displayed sample. This is an exact identity, independent of a numerical sweep.

## A photograph that distinguishes these two candidates

Halfway between the first two exposures, \(t=1/20=0.05\) seconds, their angles differ by \(\pi\). The dots are opposite each other:

\[
p_{11}(1/20)=-p_1(1/20),\qquad \|p_{11}-p_1\|_2=2.
\]

Changing the camera rate to 12 snapshots per second while keeping both motions fixed also distinguishes the pair. At the first nonzero exposure:

\[
p_1(1/12)=(\sqrt3/2,1/2),\quad
p_{11}(1/12)=(\sqrt3/2,-1/2).
\]

Their position distance is 1 radius. Both still coincide at some later times. The claim is that the sequences differ, not that every photograph differs.

## A further question about what is measured

If the sensor records only horizontal position, the two candidates still agree at every 12 Hz sample:

\[
\cos(2\pi\,11n/12)=\cos(2\pi n-2\pi n/12)=\cos(2\pi n/12).
\]

Their vertical coordinates generally have opposite signs. A sampling rate alone does not describe the experiment; the measured quantity matters too. This is why the prototype compares full 2D positions rather than only horizontal coordinates.

One extra measurement can reject one of these two motions. It does not prove which arbitrary continuous motion occurred. At any fixed uniform rate, adding a whole number of turns per exposure creates another compatible rotation. Recovering a general signal needs assumptions about the allowed signal class, and ideal recovery theorems impose conditions such as a frequency bound and sufficiently fast sampling. See [MIT's Image Sampling and Aliasing chapter](https://visionbook.mit.edu/sampling_and_aliasing.html). Finite noisy data require further care.

## Check a tempting implementation error

Keep the candidate frequencies fixed when changing the camera rate. If the code changes the faster frequency to `1 + current_sample_rate`, the samples will always agree because the demonstration changed the world alongside the measurement. Such a result would answer a different question.

Test actual displayed point coordinates at the three cases above. A correct hidden formula cannot rescue a marker drawn at the wrong location. Numerical tolerance should be fixed before evaluation; the analytic identities establish the expected results.
