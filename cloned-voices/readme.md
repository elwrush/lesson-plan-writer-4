# Cloned Voices Library

## narrator (US)
- Voice ID: f190f2467bc149f08418844955c44720
- Age: Mature adult, Gender: Male, Region: General American
- Tone: Thoughtful, authoritative, clear documentary narrator; calm measured delivery, warm and engaging
- Created: 2026-08-03
- Used for: READING M2 3 AUGUST — B1 used-electric-vehicles monolog

## Patrick_Stewart
- Voice ID: 134fbc5b934446c5b896b1e07b824e03
- Age: Mature adult, Gender: Male, Region: British (RP)
- Source: Real-audio clone (55s) from Patrick Stewart memoir narration "Making It So"
- Tone: Authoritative, measured audiobook narrator; natural rhythm
- Created: 2026-08-03
- Used for: READING M2 3 AUGUST — B1 used-electric-vehicles monolog v2 (replaced synthetic-designed voice)

## Benedict_Cumberbatch
- Voice ID: 2d3546b7f9424d28ba8d23d90a7bea24
- Age: Mature adult, Gender: Male, Region: British (RP)
- Source: Real-audio clone (60s, 10:24–11:24) from Sherlock Holmes Stories audiobook read by Benedict Cumberbatch
- Tone: Refined, expressive actor-narrator; natural rhythm
- Created: 2026-08-03

## Helen_Mirren
- Voice ID: 6da4ca158cac4f0e8023a26881b4919d
- Age: Mature adult, Gender: Female, Region: British (RP)
- Source: Real-audio clone (60s, from 44s mark) of Helen Mirren reading a fairy tale by Terry Jones
- Tone: Warm, expressive, elegant storyteller; natural rhythm
- Created: 2026-08-03

## RCrowe-adult-Aus-celeb
- Voice ID: 0f00fb73c0c94c6182ed994193dd7ce7
- Age: Adult, Gender: Male, Region: Australian
- Source: Real-audio clone (60s, 12:02–13:02) from YouTube https://www.youtube.com/watch?v=embQ1r9udaI
- Tone: Natural celebrity interview voice; conversational
- Created: 2026-08-16

## scolbert-us-male-celeb
- Voice ID: ecd51fc992bf4a2d9a4b1d1c7aadcfb8
- Age: Adult, Gender: Male, Region: US
- Source: Real-audio clone (78s, 19:02–20:20) from YouTube https://www.youtube.com/watch?v=1p9Hx43P5yE
- Tone: Celebrity talk-show host; conversational
- Created: 2026-08-16

## london-boy
- Voice ID: 311190e1caec4042962da2f9d6eb810a
- Age: Young, Gender: Male, Region: London (UK)
- Source: Real-audio clone (70s) from AUDIO_SAMPLES/London_boy.mp3
- Tone: Youthful London voice; natural conversational
- Created: 2026-08-16
- Used for: M3-VOCAB "Numbers Around School" dialog (student Leo)

## Ana-teen-girl
- Voice ID: 4f12bc0c87464c68b357ee93e3572ee4
- Age: Female teenager (~15), Region: en
- Source: Real-audio clone (50s) from AUDIO_SAMPLES/Ana.mp3, loudnorm-amplified -29.2 -> -16 LUFS before cloning
- Tone: Natural teen girl; conversational
- Created: 2026-08-19
- Used for: INTERVIEW SPEAKING — B1 (Ploy) and B2 (Elle) interview dialogs

## Ana-teen-girl-v2
- Voice ID: 9bad7a8c618344b0b3a441d268addd3f
- Age: Female teenager (~15), Region: en
- Source: Real-audio clone (50s) from AUDIO_SAMPLES/Ana.mp3, preprocessed highpass=60 + afftdn denoise + loudnorm -18 LUFS (supersedes Ana-teen-girl 4f12bc0c — quality was not great)
- Tone: Natural teen girl; conversational
- Created: 2026-08-19

## VOICE REVERT (2026-08-19)
- Ana-teen-girl-v2 (9bad7a8c) DISCARDED — afftdn denoise smeared the voice; quality worse than v1.
- Active student voice: Ana-teen-girl v1 (4f12bc0c), cloned from loudnorm-amplified source (no denoise).
- Dialog lines regenerated with 4f12bc0c; natural-pause stitch (600/400/250ms).

## London-F-teen-1
- Voice ID: f7c181b6c1c146a58c89872c9b30ecb1
- Age: Female teenager (~15), Region: London (UK)
- Source: Real-audio clone (36.6s) from AUDIO_SAMPLES/London_F_teen_1.mp3, cloned as-is (-18.4 LUFS, no preprocessing)
- Tone: Natural teenage girl; conversational
- Created: 2026-08-19
- Used for: INTERVIEW SPEAKING — B1 (Ploy) and B2 (Elle) interview dialogs (replaces Ana)

## Ana clones DELETED (2026-08-19)
- Ana-teen-girl 4f12bc0c and Ana-teen-girl-v2 9bad7a8c both deleted from Fish — voice too degraded (quiet 94kbps source; v2 denoise smeared it further). Replaced by London-F-teen-1.

## US-F-teen-1
- Voice ID: c87c03465e564db9957f25c600895f08
- Age: Female teenager (~15), Region: General American
- Source: Real-audio clone (60s, first 60s of YouTube b_zwemYrgLE, user-downloaded), trimmed to 60s, loudnorm-amplified -24.8 -> -16 LUFS (no denoise)
- Tone: Natural teenage girl; conversational
- Created: 2026-08-19
- Used for: INTERVIEW SPEAKING — B1 (Ploy) and B2 (Elle) interview dialogs

## London-F-teen-1 DELETED (2026-08-19)
- f7c181b6 deleted from Fish — British teen voice not wanted. Replaced by US-F-teen-1.
