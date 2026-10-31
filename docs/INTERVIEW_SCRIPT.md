# Gate 2 interview script and screener

**Status: optional.** The owner waived Gate 2 on 2026-10-31 (portfolio project, demand not validated). Use this only if the project is later pursued as a real product.

Purpose: find out whether people really have the problem and whether they would use this tool, before more is built. This is a draft for the owner to review. **No outreach has happened and there are no results.** Log only real conversations.

## Ground rules

- Ask about the past, not the future. "Tell me about the last time" beats "would you use".
- Do not pitch before the problem section is finished. Do not lead ("don't you hate...").
- Never ask people to share real bills or health details. Use their descriptions, or the synthetic samples in `data/generated` during the demo.
- Recruit honestly and within each community's rules. No spam, no pressure, no incentives that skew answers beyond a modest thank-you.
- Record who was contacted, who replied, and who was interviewed, including the no-replies. Silence is data.
- 20 minutes. Take notes in the template, not a recording, unless the person agrees.

## Screener (3 questions, to decide who to interview)

1. In the last 12 months, did you or someone you help receive a medical bill you did not understand or thought was wrong? (Yes/No)
2. Did you compare it with an insurance explanation of benefits (EOB)? (Yes/No/Don't know what that is)
3. Roughly how much time did you spend on it? (under 30 min / 30 min to 2 hours / more than 2 hours / gave up)

Interview people who answer Yes to question 1. People who answer No are still worth counting for the "how common" tally.

## Part 1: the problem (10 min, no pitch)

1. Tell me about the last medical bill that confused you or looked wrong. What happened?
2. What did you do first? Then what? (Follow each step with "what happened next?")
3. Did you find a mistake, or did you not know? How did you decide?
4. How long did it take, and what did it cost you in time, money or stress?
5. What tools, people or websites did you use? What was annoying about them?
6. Have you paid a bill without checking it? Why?
7. Is this still unresolved? What stopped you?

## Part 2: the idea (7 min, show the demo on sample data)

Show the case screen with a synthetic bill and EOB. Say it is a prototype on made-up data.

8. In your own words, what do you think this does?
9. Where would you not trust it? What would you want to see before relying on it?
10. The tool reads documents using an online AI service. How do you feel about uploading a bill? (Listen; do not defend.)
11. What would you do next if it flagged something?
12. What do you use today that this would replace, and what would it need to beat?

## Part 3: commitment (3 min)

13. If this existed next time, what would trigger you to open it?
14. Would you try it on a real bill in the next month? (Note the answer, but weight actions over words.)
15. Do you know anyone else who has dealt with this recently? (Only to ask, never to pressure.)

## How answers are counted (decided now, before any data)

- **Real recent problem:** the person describes a specific bill in the last 12 months, with actions taken.
- **Would use:** gives a concrete trigger in Q13 and says yes to Q14 with a date or situation. "Sounds nice" does not count.
- **Pass (from `VALIDATION_PLAN.md`):** at least 5 of 8 interviewees have a real recent problem, and at least 3 would use it with a concrete trigger.
- **Kill:** fewer than 3 of 8 have a real problem.

## Note on what privacy answers mean

Q10 matters. If most people refuse to upload a bill to an online AI service, the free-API design fails regardless of accuracy, and the product must change (redaction, or a different domain).

## Log template

Copy `validation/interviews/_TEMPLATE.md` to a new file per interview. Use an anonymous ID only.
