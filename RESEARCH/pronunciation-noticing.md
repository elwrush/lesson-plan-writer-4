# Pronunciation Noticing (Shape L) — Research & Design Notes

Research base and hard-earned design principles behind Shape L
(Pronunciation Noticing, Noticing-First). Use when planning any
pronunciation lesson targeting a specific L1-transfer feature.

## Research base

- **Noticing hypothesis** (Schmidt, 1990; Schmidt & Frota, 1986): input must be
  consciously noticed to become intake; instruction primes noticing; perceptual
  salience triggers it. Thai final stops are unreleased but phonologically
  present, so learners believe they pronounce the consonant when listeners hear
  nothing — the gap must be made *audible* first.
- **Intelligibility-based targeting** (Levis, 2005; Munro & Derwing, 1995): teach
  features that threaten comprehension, not accent reduction.
- **Thai-accented English** (Setter, 2005; Suntornsawet, 2022): final-consonant
  deletion and missing clusters are the strongest intelligibility threats;
  deletion in clusters threatens intelligibility more than substitution/addition.
- **Perception precedes production** (final-consonant-deletion intervention
  literature): auditory discrimination must come before production drills.

## In-class evidence (grounds feature selection + justification)

From `speaking_assessment_cambridge.pronunciation_feedback`:
- 417 feedback rows; 261 (63%) mention word-ending problems; 255 are
  t/d/id-specific; **112 unique students (27% of cohort)** flagged.
- Audio URLs are mostly NULL in this table — they live in
  `student_submissions.url` (with `speaking_pron_comment`), usually as Drive
  **folder** links → `gdown --folder <id> -O <dir>`.
- Exemplar: student 33168 (Rome), Book Review CA — "repetitive dropping of
  final consonant sounds… /d/ in called, would, friend; /t/ in complicated".
  Audited result of his recording: only 4 of 24 targets correct.

## Design principles (learned in practice)

1. **Salience is designed, not assumed.** Model sentences place every target
   before a vowel or a pause (audible release). Traps: "wanted to" → /ˈwɒntə/,
   "fight game" → /t/ before /g/ unreleased, "last night" → /lɑːs naɪt/. A good
   model: *I started my game at eight and played it all night.*
2. **Contrast pair for the trigger.** Join the L1-transfer version and the
   native model into one track; a narrator labels each ("Thai English" /
   "Standard English"). Normalise loudness (`loudnorm=I=-16:TP=-1.5:LRA=11`).
3. **Numbered targets, audited keys.** Noticing texts underline + number targets
   ([0] example, [1]-[n] scored). The tick/cross key MUST be verified by a
   teacher listening to the audio — neither LLM judges nor regex hear dropped
   consonants (deepseek-v4-flash judge output is also shape-unreliable:
   normalise keys, retry ≤3, keep `model_validate()` as the gate).
4. **Authentic student input closes the lesson.** Use a real past-student
   recording (assessment audio). Correct the transcript ONLY in the target
   feature; leave all other grammar verbatim (authenticity is the point).
5. **TTS mispronunciation.** Feed homophone respellings for dropped-final
   versions (night→nigh, fight→fie, played→play, wanted→want). Audition every
   respelling (vowel drift risk).
6. **Voice roles.** Narrator announces labels/numbers; a second voice reads the
   words. Student-facing slides say "the model", never the celebrity name.

## Key references

- Levis, J. (2005). Changing contexts and shifting paradigms in pronunciation
  teaching. *TESOL Quarterly, 39*(3), 369-377.
- Munro, M. J., & Derwing, T. M. (1995). Foreign accent, comprehensibility, and
  intelligibility in the speech of second language learners. *Language
  Learning, 45*(1), 73-97.
- Schmidt, R. (1990). The role of consciousness in second language learning.
  *Applied Linguistics, 11*(2), 129-158.
- Schmidt, R., & Frota, S. (1986). Developing basic conversational ability in a
  second language. In *Talking to Learn*.
- Setter, J. (2005). Communicative balance: Rhythm in the speech of Hong Kong
  English. *World Englishes, 24*(1), 75-94.
- Suntornsawet, J. (2022). Thai-accented English phonology: Intelligibility
  threats. *PASAA.*
