// The starter is a teaching map. It contains no learner history.
export function initialRoadmap() {
  return {
    kind: "roadmap",
    schema_version: 1,
    field: "Signal processing",
    topic: "Signals & sampling",
    goal: {
      capability: "",
      context: "",
      aids: "",
      timebox: "",
      intensity: "",
      success: "",
      deadline: "",
    },
    skills: [
      {
        id: "sample-clock",
        title: "Sample timing",
        prerequisites: [],
        description:
          "Locate each observation on a timeline. A camera running at a fixed rate measures position at discrete instants.",
        challenge:
          "A camera takes 12 snapshots per second starting at t = 0. Give the times of its first four frames and the time between frames.",
      },
      {
        id: "periodicity",
        title: "Phase & periodicity",
        prerequisites: [],
        description:
          "Describe a rotation in turns and decide when different angles put a point in the same place.",
        challenge:
          "Two markers start at the same angle and rotate counterclockwise at constant speeds of 2 and 7 turns per second. Find the earliest positive time when both point in the same direction.",
      },
      {
        id: "samples",
        title: "Discrete sequences",
        prerequisites: ["sample-clock"],
        description:
          "Write a sequence indexed by frame number. Distinguish what the camera observes from the motion between exposures.",
        challenge:
          "A unit-radius point starts at (1,0) and rotates counterclockwise at a constant 3 turns per second. A camera takes its first frame at t = 0 and records at 12 Hz. Write the first four positions.",
      },
      {
        id: "boundary",
        title: "What a sensor sees",
        prerequisites: ["periodicity"],
        description:
          "A camera can measure a full position or just its horizontal coordinate. Changing the measurement changes which motions can be distinguished.",
        challenge:
          "An ideal horizontal-position sensor watches a point on a unit circle. Can it distinguish clockwise and counterclockwise rotation at equal speeds from the same initial position (1,0)? Defend your answer.",
      },
      {
        id: "aliasing",
        title: "Aliasing",
        prerequisites: ["samples", "periodicity"],
        description:
          "Different continuous motions can leave the same sequence of observations. Identify what a set of samples lets you infer.",
        challenge:
          "A camera tracks a marked wheel at 10 frames per second, starting at t = 0. Could constant speeds of 1 and 11 turns per second produce the same positions in every frame if the initial phase and direction match? Defend your answer for all frames.",
      },
      {
        id: "design",
        title: "Design a measurement",
        prerequisites: ["aliasing", "boundary"],
        description:
          "Choose a measurement that tells two candidate motions apart. State what remains ambiguous after the experiment.",
        challenge:
          "Two unit-radius wheels start at (1,0) at t = 0 and rotate counterclockwise at constant speeds of 1 and 11 turns per second. A camera records at 10 Hz starting at t = 0. Choose one extra exposure time and coordinate that distinguishes them. Would it identify an arbitrary unknown rotation?",
      },
    ],
    evidence: [],
  };
}
