---
name: explain-that
description: Re-explain a word, sentence, or part of the agent's previous response that the user did not understand, using simpler language, necessary context, and a concrete example. Use when the user explicitly invokes this skill or asks what part of the previous response means.
---

# Explain That

Re-explain the part of the previous response identified by the user. If no part is specified, infer the most likely confusing part from the immediately preceding response.

- State the main point again in plain language.
- Add any missing premise or background needed to understand it.
- Give at least one concrete example related to the current task.
- When helpful, map the original terms to their roles in the example.
- Replace unnecessary jargon. Briefly define technical terms that cannot be avoided.
- Preserve the original technical meaning and recommendation.
- Do not continue the task, introduce a new solution, or assume the user now agrees.
- Prefer realistic examples over abstract or childish analogies.

Do not merely shorten or repeat the original wording. Explain it from another angle and include enough detail for the reasoning to make sense.

If no specific passage is given, make a reasonable inference from the previous response. Ask which part the user means only when the ambiguity would materially change the explanation.
