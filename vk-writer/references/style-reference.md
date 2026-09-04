# vk-writer Style Reference

## 1. Style Position

`vk-writer` is inspired by `khazix-writer`, but it is adapted for `vk`'s writing system.

Keep the following from the reference style:

- human voice instead of corporate voice
- concrete scenes instead of abstract openings
- honest judgment instead of false neutrality
- specific tools, products, and examples instead of generic labels
- rhythm created by short paragraphs and clean transitions

Do not inherit these blindly:

- do not remove structure just to imitate a free-flow essay
- do not force slang or exaggerated emotion into every article
- do not fake personal experience
- do not copy another author's catchphrases mechanically

One-sentence target:

> Write like a person with judgment, explaining something worth writing about.

When drafting Chinese copy, also ban these filler openers:

## 2. Sentence-Level Rules

- Prefer short sentences.
- Prefer conclusion first, explanation second.
- Prefer active verbs over abstract nouns.
- Prefer one paragraph for one micro-idea.
- Keep most paragraphs within 2 to 5 lines.
- Use first person only when the user supplied genuine first-hand material.
- If there is no first-hand material, write as analysis, not fake memoir.

## 3. Opening Rules

Open with one of these:

- a specific problem the reader already feels
- a concrete scene or observation
- a surprising result or contradiction grounded in material
- a direct statement of the payoff

Avoid these openings:

- macro empty talk about the era
- generic AI trend statements
- textbook background paragraphs
- vague hype before the point appears

## 4. Evidence Rules

Every important claim should get at least one of:

- a concrete example
- a mechanism explanation
- a data point with source
- an executable step
- a real quote or observation supplied by the user

When evidence is weak:

- mark it as a hypothesis
- narrow the claim
- ask for more material if the missing evidence is critical

## 5. Tone Rules

Preferred tone:

- direct
- restrained
- credible
- slightly conversational
- useful

Allowed:

- clear personal judgment
- mild rhetorical pressure when pointing out a problem
- light conversational transitions

Avoid:

- slogan-like declarations
- fake objectivity
- over-marketing
- over-dramatic self-performance
- repeated exclamation-driven prose

## 6. Recommended Transitions

Use natural transitions such as:

- Lead with the conclusion
- Back to this point
- What actually matters
- This step is easy to skip
- Split the problem in two layers
- From here you can see

Do not overuse the same transition in every section.

## 7. Hard Bans

- Do not use contrast-template sentences of the form "not X, but Y".
- Do not expose prompt choreography, style mixing, or internal process.
- Do not expose local absolute paths in article body text.
- Do not use Markdown bold `**xx**`; use `<strong>xx</strong>` or styled `<span>`.
- Do not write generic AI filler about "today's fast-changing era", "with continuous technical progress", "it is worth noting", "it is not hard to see", or mechanical first/second/finally ladders.

## 8. Structural Adaptation From Khazix

The original reference style often relies on continuous prose with minimal headings.

`vk-writer` deliberately keeps:

- explicit outline structure
- article-specific `style.md`
- reusable file layout
- visible section hierarchy when it improves scanning and maintenance

Reason:

- the `writing` project is asset-driven and collaborative
- articles need stable files for revision, sync, diagrams, and later reuse
- readability in Markdown editing and Lark sync matters as much as raw prose flow
