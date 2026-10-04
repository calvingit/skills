---
name: teach
description: Build or continue a course with lessons and learning records across sessions.
---

# Teach

Use for an explicitly requested ongoing course or to resume an existing learning
workspace. A one-off question does not establish a course or authorize records.

## Teaching workspace

Use the named learning directory or resume the existing course. Use the current
directory only when it is already a teaching workspace or explicitly selected;
otherwise establish the location before writing. Resolve these paths there and
create artifacts only when they have useful content:

| Artifact | Purpose |
| --- | --- |
| `MISSION.md` | The learner's reason, observable goal and constraints; use [the mission format](MISSION-FORMAT.md). |
| `RESOURCES.md` | Trusted knowledge sources and communities, with context for reuse; use [the resource format](RESOURCES-FORMAT.md). |
| `learning-records/*.md` | Demonstrated understanding, stated prior knowledge and non-obvious insights that guide later lessons; use [the learning-record format](LEARNING-RECORD-FORMAT.md). |
| `lessons/*.html` | Short, self-contained interactive lessons, numbered `0001-<dash-case-name>.html` onward. |
| `reference/*.html` | Readable, printable quick references: syntax, algorithms, routines, glossaries or other compressed learning. |
| `assets/*` | Styles and widgets genuinely shared by lessons. |
| `NOTES.md` | Teaching preferences and working notes for future sessions. |

## Choose and teach one lesson

1. Read the mission and relevant learning records. Use a requested topic, or choose
   the most useful next skill within the learner's demonstrated reach. Reuse the
   stated goal; ask only when a missing goal would change the lesson. Confirm a
   mission change with the user, update `MISSION.md` and record why it changed.
2. Ground the lesson in trusted resources recorded in `RESOURCES.md`, not model
   recall. Find suitable sources first when that file is sparse; make gaps visible.
3. Teach only the knowledge needed for this skill, then let the learner practice
   through a tight feedback loop. Use retrieval and spacing for retention, with
   interleaving for related skills. Read [teaching principles](references/teaching-principles.md)
   when selecting practice or handling a question that needs practical judgement.
4. Produce one short lesson with a tangible outcome tied to the mission. Use clean,
   readable typography and layout, reuse existing assets, link related lessons and
   references with HTML anchors, recommend a primary source, and invite follow-up questions. Support
   factual claims with source links. Open the lesson using an available command
   when practical.
5. Create useful quick references while authoring lessons. Follow an established
   glossary consistently. Extract shared styles or widgets only when lessons
   actually share them and keep their appearance consistent through that source;
   do not prebuild a component library.
6. Record learning only when supported by demonstrated understanding, stated prior
   knowledge, corrected misconceptions or a mission change, following the record
   format. Material merely presented is not evidence of learning. Preserve teaching
   preferences in `NOTES.md` for subsequent sessions.

For questions that require wisdom, offer an answer and find reputable communities
for real-world practice. Respect the learner's preference if they decline.
