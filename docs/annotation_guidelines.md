# Content Safety Annotation Guidelines

## 1 Purpose

These guidelines define how English and Chinese text should be assigned to one of five mutually exclusive safety labels.

Annotators should classify the content that is explicitly present. They should not infer unsupported intent or missing context.

## 2 General Rules

- Assign exactly one label to each example.
- Select the most severe applicable label when multiple labels appear.
- Use only the information available in the text.
- Do not classify quoted harmful language as harmful automatically.
- Consider whether the speaker supports, condemns, reports, or neutrally discusses the content.
- Mark genuinely ambiguous cases for adjudication.
- Do not include personally identifying or private information in the dataset.

## 3 Label Definitions

### SAFE

Content that does not contain hate, targeted harassment, violence, or self-harm encouragement.

Includes:

- Neutral discussion
- Constructive disagreement
- News reporting
- Educational discussion
- Condemnation of harmful behavior
- Non-targeted frustration

Excludes:

- Direct attacks against a person
- Attacks against a protected group
- Credible violent threats
- Encouragement of self-harm

Examples:

- EN: I strongly disagree with this proposal.
- ZH: 我不同意这个观点，但愿意听听你的理由。

### HATE

Content that attacks, dehumanizes, excludes, or promotes hostility toward people based on a protected characteristic.

Protected characteristics may include:

- Race
- Ethnicity
- Nationality
- Religion
- Gender
- Sexual orientation
- Disability

Important distinction:

HATE targets a protected group or a person because of group identity. HARASSMENT targets a specific person without requiring a protected characteristic.

### HARASSMENT

Content that directly insults, humiliates, degrades, or intimidates a specific person or identifiable target.

Includes:

- Direct personal insults
- Repeated humiliation
- Targeted degradation
- Encouraging others to attack an individual

Excludes:

- Criticism of an idea
- General frustration without a target
- Reasonable criticism of public conduct

Boundary example:

- This idea is terrible: likely SAFE.
- You are worthless and nobody wants you here: HARASSMENT.

### VIOLENCE

Content that threatens, praises, encourages, or provides meaningful support for physical harm against people.

Includes:

- Direct threats
- Encouragement of physical attacks
- Celebration of serious physical harm
- Instructions intended to facilitate violence

Excludes:

- Fictional violence without real-world encouragement
- News reporting
- Historical discussion
- Condemnation of violence

### SELF_HARM

Content that encourages, instructs, glorifies, or expresses an immediate intention to engage in self-harm or suicide.

Includes:

- Encouragement of self-harm
- Instructions for self-harm
- Glorification of suicide
- Statements indicating immediate personal risk

Excludes:

- Recovery discussion
- Prevention resources
- Academic discussion
- Supportive responses encouraging professional help

Sensitive examples should be paraphrased and should not contain actionable instructions.

## 4 Label Priority

For the single-label MVP, use this provisional severity order:

1. SELF_HARM
2. VIOLENCE
3. HATE
4. HARASSMENT
5. SAFE

The priority order is a product simplification and should be reviewed during error analysis.

## 5 Ambiguous Cases

Annotators should flag an example when:

- The target is unclear.
- The content appears sarcastic.
- The content quotes someone else.
- The text lacks necessary context.
- Cultural or linguistic meaning is uncertain.
- Two labels appear equally applicable.

Use the following fields:

- `needs_adjudication`: true
- `ambiguity_reason`: short explanation

## 6 Annotation Process

1. Read the entire text.
2. Identify the speaker, target, and apparent context.
3. Determine whether a safety category applies.
4. Assign one label.
5. Record uncertainty or ambiguity.
6. Do not consult the model prediction before assigning the human label.

## 7 Disagreement Resolution

When two annotators disagree:

1. Each annotator records a brief rationale.
2. The case is reviewed against the written definitions.
3. A final adjudicated label is assigned.
4. Repeated disagreement patterns are used to revise the guidelines.

