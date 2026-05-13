Gemini
User Interview Prep for Release Notes
Enterprise logo
New chat
My stuff
Gems
Chats
User Interview Prep for Release Notes
Walk or Drive to Car Wash?
Improving CI Docs Test Validation
Automating Kubernetes Patch Notices
Deprecation Notice: Tense and Clarity
Meta Description for Kubernetes Upgrade
Summarize PR for Release Notes
Automate Release Notes with AI
Inline Links for Readability and Maintenance
Ubuntu Firmware Update Postponed
Evaluating Documentation Sections
Copilot Edits Stuck In VS Code
Bash Conditional Logic for File Checks

Settings and help
Conversation with Gemini
You are helping a hackathon team prepare to interview the users for a prototype.



Project description: Automate release notes patch notices. Currently we manually download the Canonical Kubernetes snap once a month and see what has changed and then update the release notes. We want to automate this as much as possible. Not all changes land in the release notes patch notices. If it does not have a user facing impact, it is skipped so this is where the human element comes in. We have to decide if it is "release notes worthy".

Known facts about the users: This has mostly fallen on the technical writer on the team (me) to maintain although it should belong to the engineers. Not having up to date patch notices leads to questions from our users as there is no CHANGELOG or anything like that to say what changes have occurred. There is also a lead time from when a back port lands on the feature branch and when the change is available as a snap/charm in the snap store / charmhub.



Produce:



1. Eight to twelve interview questions, broad to specific, designed to surface real workflow rather than confirm the team's assumptions. Each question should be open-ended, experience-focused, and anchored in a specific past instance rather than a hypothetical. Flag any question that is binary, leading, or primes the user with a candidate solution.

2. Among the questions above, include at least two in the form "tell me about the last time you ..." and at least one "walk me through your process for ...". These tend to surface real behaviour rather than self-image.

3. The top five assumptions the team appears to be making about these users, with one concrete way to check each during the interview. Treat anything you have written about how a user thinks or feels as a hypothesis on this list, not a fact.



Do not propose solutions. Do not phrase any question as a hypothetical about a feature that does not yet exist.

To help your team move from "building what you think they need" to "building what they actually do," these questions focus on the The Mom Test philosophy—avoiding compliments and hypotheticals in favor of hard data from the past.

1. User Interview Questions
These questions are designed to move from the broad context of the workflow to the specific friction points of the manual process.

"Tell me about the last time you sat down to update the Kubernetes release notes." * Goal: Establish a concrete anchor in time to prevent the user from describing an "idealized" version of their workflow.

"Walk me through your process for determining which changes from the snap download make it into the final patch notice."

Goal: Uncover the "invisible" logic used to filter for user-facing impact.

"Think back to the last release cycle; how did you find out that a backport had officially landed in the snap store or Charmhub?"

Goal: Understand how they bridge the gap between the code landing and the product being "live."

"Tell me about the last time you had to reach out to an engineer to clarify if a change was 'release note worthy'."

Goal: Identify the specific technical triggers that cause the technical writer to seek help.

"Describe a situation where a change was excluded from the notes, but later resulted in questions from users or support tickets."

Goal: Surface the cost of "missing" information and how "user-facing impact" is defined in hindsight.

"When you are looking at the manual snap download, what specific signals or keywords are you looking for to identify a change?"

Goal: To see if there are already "if/then" rules in their head that could be scripted.

"Tell me about the last time the release notes were delayed. What were the primary hurdles that week?"

Goal: Identify external dependencies (e.g., waiting for builds, waiting for approvals).

"How do you currently track which changes have already been documented versus those that are still 'pending' in the queue?"

Goal: To see if they use a separate tool (spreadsheets, Jira, sticky notes) to manage the state.

"What happens to your workflow when a backport lands on a feature branch but hasn't yet appeared in the snap store?"

Goal: Investigate the "lead time" pain point.

"Do you think engineers would be better at identifying 'release note worthy' changes than the current process?"

🚩 FLAG: Leading / Priming. This question nudges the user toward the team's assumption that engineers should own this. Use this only if you want to see the user’s reaction to the idea of ownership, but be wary of "polite" agreement.

2. Identifying Team Assumptions
Below are the five core hypotheses your team is currently operating under. Validating these is critical before writing any code.

Assumption	How to check it during the interview
1. The "Ownership" Gap: The technical writer feels this task should belong to engineers.	Ask: "Who currently feels responsible for the accuracy of these notes, and how has that responsibility changed over the last few releases?"
2. The Filtering Logic: The "human element" of deciding what is "release note worthy" is the primary reason this isn't already automated.	Ask: "If you had a list of every single commit today, what would be the hardest part of turning that into a patch notice?"
3. User Pain: Users are primarily frustrated by the absence of a changelog.	Ask: "What are the most common questions you see in support channels or GitHub issues regarding new releases?"
4. The Lead-Time Problem: The delay between backports and the snap store is a major source of confusion for the writer.	Ask: "How do you handle it when a user asks about a feature that you can see in the code but isn't in the store yet?"
5. The Manual Bottleneck: The act of downloading and comparing the snap is the most time-consuming part of the process.	Ask: "If the download and comparison happened instantly, how much of your total 'release note' time would be left?"
3. Interviewing Strategy: The Funnel Approach
When conducting these interviews, imagine a funnel. Start with the broad "Tell me about..." questions to see where the user's mind naturally goes. Only move to the specific questions about "lead times" or "filtering" once they have established the context.

Pro Tip: If the user says, "It would be great if..." or "I wish the tool did...", politely acknowledge it and redirect them back to the past: "That’s interesting. Tell me about the last time that specific issue caused a problem for you." Focus on their past pain, not their future wishes.

Ask me these questions one by one, record my answers and provide a summary of key findings at the end

Let’s get into character. I’ll act as the interviewer to help you "stress test" the workflow and see what surfaces. I'll keep track of everything and give you that synthesized summary once we’ve touched on all the points.

Since you’re the one currently carrying the torch for these release notes, you're the perfect person to start with.

Question 1:
Tell me about the last time you sat down to update the Kubernetes release notes. What was the specific trigger that told you it was time to start, and what were the first few things you did?

It hasn't been done since November so it was well overdue. I created a recurring Jira ticket and decided to take the first turn. I start by downloading the latest snap for the version I am updating and navigate to the BOM which is located at  /snap/k8s/current/bom.json. From there I can see the commit hash of the last commit included in the release. I then compare the difference between the latest commit in this release and the patch notices in the release notes. I then update the release notes patch notices with the changes. I then repeat the process for the remainder of the versions that have also had a new version on stable. There usually ends up being some overlap in the changes. I create a separate PR which targets main for each version and add labels to backport to the appropriate release branches.

That’s a very clear starting point. It sounds like a lot of "context switching" between the bom.json file, the commit history, and the existing documentation.

Question 2:

Walk me through your process for determining which changes in that "diff" actually make it into the final patch notice. When you're looking at a list of commits or changes between the current snap and the last documented version, how do you decide what is "release note worthy" and what gets left on the cutting room floor?

We then aim to make a document a human would enjoy reading - highlighting any major changes, depreciations and new features. This can be quite time consuming and requires a lot of context on the project.  If there is a major change backported, I will include the PR number and link so people can find out more. For smaller changes, listing what it entailed is enough. I also don't include every change in the patch notices. Minor inconsequential to the user changes don't make it into the patch notices. E.g. we updated the formatting of this docs page. While important, the info has not changed so the user does not need to be alerted in the patch notices.

It sounds like you’re doing a significant amount of editorial filtering to maintain a "high signal-to-noise" ratio for the users. You’re essentially acting as a curator.

Question 3:

Think back to the last time you were working on these updates; how did you find out that a backport had officially landed in the snap store or Charmhub? Was it a notification, a manual check, or did someone tell you?

I manually checked. On the snap, I download, get the commit SHA from the BOM and then go to the commit history for that branch. For charms, I get the revision number from charmhub, then go to github, get that release that corresponds to the revision number, get the commit SHA and then go to the commit history for that branch

That is a lot of "sleuthing" across multiple platforms—Snap Store, Charmhub, and GitHub—just to establish a baseline of what actually changed. It sounds like you're playing digital detective before you even start writing.

Question 4:

Tell me about the last time you had to reach out to an engineer to clarify if a change was "release note worthy." What was the specific commit or PR that sparked the confusion, and how did that conversation go?

I pinged an engineer on the team. I linked to the PR, explained my understanding of it and asked if that was correct. When he provided more context and explained further I then asked should the user be made aware (i.e add to release notes?) and he said yes

It sounds like the engineer acts as the "final filter" when the technical documentation doesn't tell the whole story. You’re translating technical PRs into user value, but sometimes the translation requires a second opinion to ensure nothing important is missed.

Question 5:

Describe a situation (perhaps from that November gap or earlier) where a change was excluded from the notes—either intentionally or accidentally—but later resulted in questions from users, support tickets, or confusion in the community. What was the change, and how did the team realize it should have been included?

We haven't got much questions now that we are updating the release notes patch notices but we do not have a major user base yet.

That’s an important insight—the "silence" might be due to the early stage of the project rather than the perfection of the process. It means you’re essentially building the foundation before the house gets crowded.

Question 6:

When you are looking at that list of commits (the diff between the bom.json hashes), what specific signals, keywords, or labels are you scanning for to quickly flag a change as "potentially release-note worthy"? (e.g., are you looking for "fix:", "feat:", specific Jira IDs, or certain file paths?)

I am generally looking for feat: and fix: . Updates can be from dependabot or manual backports so they can differ. Sometimes they are called ci: so I cannot write off any label automatically. While we do use labels, we are not great at the description in these PR titles. Sometimes it can be misleading so I often have to read the commit message

It sounds like you're essentially performing "semantic forensic work"—you can't trust the labels at face value, so you’re forced to dig into the actual commit messages to find the truth. That adds a huge layer of cognitive load.

Question 7:

Tell me about the last time the release notes were delayed (like the gap between November and now). Aside from just being busy with other tasks, what were the primary technical or process hurdles that made it difficult to sit down and "just get them done" that week?

There was a time where the release process where we promote to stable was broken so there were no updates to stable so no updates to write in the release notes. I did not manually check when this was resolved so I don't know when it was but it should have been checked before last week. It also should fall on the engineers to do this

The "silent failure" of the promotion process seems like a major visibility gap—if the pipeline breaks, the documentation pipeline breaks too, but without an alarm going off. It also highlights that tension regarding ownership; if it's "your" task but "their" infrastructure, the coordination becomes a hurdle.

Question 8:

How do you currently track which changes have already been documented versus those that are still "pending" in the queue? Specifically, when you are looking at a version that has had multiple updates over several months, how do you make sure you haven't missed a commit or accidentally duplicated a notice from a previous manual run?

Manual review mostly. I got to the previous release notes patches. I see the date. I go back to that date in the commit history. I then check the patch notices and try find the latest PR that was included. As we do not include every PR, it is an estimate where we left off. To be sure I don't miss any, I usually take the next PR from the last known PR, even if this means including some PRs again. The release notes are marked with the date on the top of the patch notice as today's date. It represents what is on stable as of today. It does not list the date of the commit as it may take several days from a commit landing on the release branch to get to stable

It sounds like you’re essentially "re-indexing" the history every time you sit down to work. Because there isn't a hard marker in the code saying "documented up to here," you're forced to rely on dates and visual recognition of PR titles to guess your starting point. That seems like it would create a lot of "double-work" just to ensure no gaps are left.

Question 9:

You mentioned there is a lead time between a backport landing on a feature branch and when it’s available in the snap store. Tell me about the last time you saw a critical backport land in the repo but noticed it hadn't hit the snap store yet. How did that affect your documentation plan for that day?

A major security vulnerability was found in a source we use so we updated the version immediately. It took a few days to land on stable. I wanted to wait until the fix landed in stable but I was asked to update the release notes right away

That is a tough spot to be in—documenting a fix as "live" when the user can’t actually access it yet creates a major source of truth conflict.

This brings us to the final question in our set:

Question 10: You’ve mentioned a few times that this process "should belong to the engineers." Tell me about the last time an engineer actually contributed to or drafted a patch notice. How did that handoff work, and what did the "raw" info they provided look like compared to the final version you published?

Once you answer this one, I’ll wrap everything up into a summary of key findings for your hackathon team.

An engineer updated them adhoc when he backported an important change. He did not go back and check all changes though. The engineers make the release notes majority of the time though

This interview session has surfaced several critical insights that move far beyond the initial project description. While the goal is "automation," the findings suggest that the data retrieval and state-tracking are actually more painful than the writing itself.

Here is the summary of key findings for your hackathon team.

Executive Summary: The "Detective Work" Bottleneck
The primary friction isn't just "writing notes"; it is a forensic accounting problem. The Technical Writer (and occasionally engineers) must act as a digital detective to reconcile three different sources of truth: the Snap Store/Charmhub revision, the GitHub commit history, and the existing documentation.

Key Findings
1. The "Re-Indexing" Tax
There is no "bookmark" in the system. Every time the notes are updated, the user has to manually re-establish the starting point by looking at the last published date and visually scanning GitHub for the last included PR.

Impact: This leads to "accidental duplication" where the user intentionally re-reviews PRs just to be safe, creating significant redundant work.

2. Label Unreliability (The "feat:" Fallacy)
While the team uses conventional commit-style labels (feat:, fix:, ci:), they cannot be trusted for automation.

The Reality: Important changes are sometimes hidden under ci: or have misleading titles.

The Workflow: The user is forced to read actual commit messages and PR descriptions because the metadata is too "noisy" or inaccurate to filter programmatically.

3. The Temporal "No-Man's Land"
There is a high-friction gap between a backport landing on a branch and it appearing in the Stable channel.

The Conflict: Pressure exists to document "critical" items (like security fixes) before they are actually live for the user. This creates a risk of the documentation claiming a fix exists that the user cannot yet download.

4. Silent Pipeline Failures
Because the documentation process is disconnected from the release infrastructure, a break in the "promotion to stable" pipeline goes unnoticed by the documentation owner.

The Result: The writer might wait weeks for "new" things to document, unaware that the release pipe is actually clogged, leading to large "documentation debt" (like the November to now gap).

5. Ad-hoc vs. Systematic Ownership
Engineers do contribute, but only for "the big stuff" they personally backport.

The Gap: The "forensic sweep" (checking every single minor fix/change to ensure nothing was missed) is seen as a separate, more tedious task that falls on the Technical Writer by default.

User Experience Comparison
Task Phase	Current Manual Reality	The "Ideal" Future State
Finding the 'Start'	Visual scan of dates & PR titles.	System knows the last documented SHA.
Filtering	Reading commit messages one-by-one.	Auto-surface everything except known noise.
Verification	Manually downloading Snaps to find bom.json.	Automated diffing between Snap versions.
Truth Timing	Guessing when "Stable" is actually updated.	Real-time alerts when a SHA hits Stable.
Critical "Hack" Opportunity
The team should focus on automated discovery and delta-tracking. If the tool can accurately say, "Here are the 14 commits that landed in Stable since your last PR, and here is the summarized text from their descriptions," 80% of the manual "detective tax" is eliminated, even if a human still has to do the final "release note worthy" toggle.

Final Thought: You aren't just automating a document; you're building a state-tracker for a multi-platform release cycle.

Please create a problem statement for this project

A strong problem statement focuses on the gap between the current reality and the desired outcome. Based on our interview, your team’s challenge isn't just "automation"—it’s a visibility and reconciliation problem.

Problem Statement
The Current Reality
Currently, the process of generating patch notices for Canonical Kubernetes is a manual, "forensic" task that requires a technical writer to reconcile three disconnected sources of truth: the Snap/Charm metadata (bom.json), the GitHub commit history, and the existing documentation.

The Core Friction
Because there is no persistent state-tracking to show where the last update left off, the contributor must manually re-index the history for every release. This is exacerbated by unreliable metadata (labels and PR titles), forcing a deep-dive into commit messages to determine "user-facing impact." Furthermore, the variable lead time between code landing and "Stable" promotion creates a visibility gap where it is unclear exactly what is live for the user at any given moment.

The Impact
Documentation Lag: Critical updates can go undocumented for months (e.g., November to May), leaving users without a reliable CHANGELOG.

High Cognitive Load: The process relies on "detective work" rather than editorial work, making the task unattractive for engineers and burdensome for technical writers.

Support Burden: A lack of up-to-date notices leads to avoidable user inquiries and reduced confidence in the transparency of the release cycle.

The Goal
To build a system that automates the discovery and diffing of changes between release versions, providing a "human-in-the-loop" interface to filter for "release-note-worthy" content. The solution must bridge the gap between GitHub backports and Snap Store promotions, ensuring that documentation accurately reflects the user's reality in the Stable channel.

Based on the interview notes and the questions we just worked through, produce:



1. A one-paragraph problem statement naming the user, the trigger context, and the unmet need expressed as a verb the user is trying to do (not a feature the team would ship), with a one-line tail on why the need matters to that user. Do not propose a solution.

2. Three success criteria the prototype must demonstrate by end of day. Each must be observable in a five-minute demo.

3. Three things explicitly out of scope, with a one-line justification each.



Before returning, run a naivety check on the problem statement: would a careful reader accept the need as a real human goal, or does it read as circular (user needs X so that X happens)? If circular, rewrite once and return the rewritten version.

This is a classic "invisible labor" problem. You’re currently spending all your time on the archaeology of the release, which leaves very little energy for the actual writing.

Here is the refined project framing for your hackathon.

1. Problem Statement
When a recurring update cycle triggers the need for new patch notices, the Technical Writer needs to reconcile disparate versioning metadata across multiple platforms to distinguish impactful user-facing changes from background infrastructure noise. This matters because the current "forensic" manual process is so labor-intensive that it creates months of documentation debt, leaving users without a reliable map of the security fixes and features currently live in their production environments.

Naivety Check: The goal is not "to have an automated tool"; the goal is "to reconcile and distinguish data." These are human cognitive tasks currently buried under manual labor. This passes the check.

2. Success Criteria (5-Minute Demo)
To prove the prototype works by the end of the day, it must demonstrate:

The Delta Discovery: The user inputs a specific Snap/Charm channel (e.g., 1.29/stable), and the tool successfully fetches and displays the list of commits that have landed since the last documented "bookmark."

The Signal Filter: A user can view a list of raw commits and, with a single action, flag specific items as "Release Note Worthy" while hiding "noise" (like CI or formatting changes).

The "Live" Verification: The tool pulls the current SHA directly from the Snap Store or Charmhub API to confirm that the changes being documented are actually accessible to the user in the "Stable" channel.

3. Out of Scope
AI-Generated Summaries: While "writing" takes time, the interview revealed that the "detective work" of finding and verifying the data is the primary bottleneck we are solving today.

Automated Pull Request (PR) Submission: We are focusing on the discovery and curation of content; the final act of pushing code to the docs repo can remain manual for this prototype.

Support for External Ecosystems: The prototype will strictly handle the Snap Store and Charmhub workflows for Canonical Kubernetes, rather than attempting to support generic GitHub or Docker-based releases.

Expert Guide Question:
When you are doing your "forensic" review, is there a specific piece of information (like a Jira ID or a specific file path) that—if seen in a commit—makes you 100% certain it must be in the release notes?

This was my sketch of the approach:

Have a way of tracking what is the latest commit on stable for each revision for the snap and charm - maybe some sort of polling periodically and updating a file? This can probably be a go or python script.

Have a way of knowing what was the latest commit included in the patch notices - maybe a file on the repo? This can probably be a go or python script.

Automatically gather all commits from the current commit on stable to the latest included commit in the release notes. This can probably be a go or python script.

Format the commits. This could be done with AI

Version bumps should be grouped together at the beginning of the notice. This should include image bumps, kubernetes version bumps, component bumps etc. 

If the change is significant and we think the user will want to learn more, include a link to the PR 

The entry for each commit should briefly describe what was done and how it impacts the user. 

Not every commit needs to be included. If it is a very minor change that will not have a user impact we can exclude it.  

We need to have a human in the loop at some point. We should record any commits excluded and provide a justification as to why they were excluded 

The updated patch notices need to be added to the release notes for each version. 

A PR needs to be made to main and then backported to the relevant versions.



I want to make the process as streamlined as possible. While I do want a human in the loop I am open to AI interpretting the data first and providing their discarded results too. I see this as possibly being a local tool that can be run by a human and checked before putting up a PR

This sketch bridges the gap between "forensic archaeology" and actual technical writing. You’ve identified the most important pivot: moving from a "pull" model (manually hunting for changes) to a "push" model (the system presenting you with a pre-filtered list).

Here is a refined look at your approach, focused on streamlining the "Human-in-the-Loop" experience.

The Workflow Architecture
Stage	Logic	AI Role	Human Role
1. The Diff	Compare GitHub HEAD of the stable branch vs. the "Last Documented" SHA stored in a local state.json.	None (Deterministic)	None
2. Triage	Group commits by type: Version Bumps, Features, Fixes, and "Noise" (CI/Docs).	Classify: Identify which category a commit belongs to based on message/diff.	None
3. Draft & Prune	Summarize PR descriptions into "User Impact" statements. Mark low-impact items for "Discard."	Summarize: Translate dev-speak into user-benefit.	Review: Toggle "Keep/Discard" on a curated list.
4. Justification	Record why an item was discarded (e.g., "Internal CI change").	Predict: Propose a reason for exclusion.	Verify: Confirm or edit the justification.
5. Packaging	Format into Markdown; group version bumps at the top.	Format: Apply the specific style guide/template.	Final Polish: Do the actual writing/editing.
Observations & Streamlining Opportunities
The "State" File: Instead of polling, your local tool could simply query the Snap Store API for the current revision’s SHA at the moment you run it. This ensures you are documented up to the exact second of the "Stable" reality.

The "Discarded" Pile: This is your strongest idea. Providing a "Rejected" list is the only way to build trust in the AI. If the AI hides things completely, you’ll never stop feeling the urge to go back to GitHub to double-check its work.

The PR Chain: Since you need to backport to multiple versions, your script could generate a "Backport Plan" as part of the output, listing exactly which branches the PR labels should target.

AI as an Interpreter, Not a Creator: Rather than asking AI to "write the notes," ask it to "Identify the delta." * Input: PR Title, PR Description, File Diffs.

Prompt: "Does this change affect how a user interacts with the Kubernetes cluster? If yes, explain why in one sentence. If no, categorize it as internal."

Refining the "Human-in-the-Loop" Interface
Since you envision a local tool, imagine a simple CLI or a lightweight local web UI where:

You see a list of "Candidates."

Each has a checkbox (Keep) and a text box (Justification for Discard).

Once you hit "Generate," it spits out the Markdown and updates your local state.json.

Critical Considerations
The Metadata Trap: Remember your interview insight—labels (feat:, fix:) can be misleading. Your AI prompt should prioritize the File Diff and PR Description over the Commit Message to avoid missing those "stealth" changes hidden in CI commits.

Expert Guide Question:
If the tool finds a "Version Bump" (e.g., K8s 1.28.1 to 1.28.2), do you want the AI to automatically go and fetch the release notes for that version to include in your summary, or is simply stating the version change enough?

Please run these again with this further insight:

1. A one-paragraph problem statement naming the user, the trigger context, and the unmet need expressed as a verb the user is trying to do (not a feature the team would ship), with a one-line tail on why the need matters to that user. Do not propose a solution.

2. Three success criteria the prototype must demonstrate by end of day. Each must be observable in a five-minute demo.

3. Three things explicitly out of scope, with a one-line justification each.

Applying the insights from our "detective work" conversation, here is the refined framing for your hackathon project.

1. Problem Statement
When a new software version is promoted to the stable channel, the Technical Writer must reconcile disparate versioning metadata to distill a curated list of user-facing changes from high-volume technical noise. This matters because the current "archaeological" manual process is so exhaustive that it creates months of documentation lag, leaving users without the transparency required to safely manage their production infrastructure.

Naivety Check: This avoids circularity by focusing on the cognitive tasks of reconciling (aligning different data sources) and distilling (extracting value), rather than just "needing a tool to make things faster."

2. Success Criteria (5-Minute Demo)
By the end of the day, the prototype must be able to:

Identify the Delta: The user provides a snap channel (e.g., 1.29/stable), and the tool successfully retrieves all GitHub commits that have landed since the "last documented" SHA stored in the local state.

Verify "Stable" Reality: The tool demonstrates a "Live Check" by querying the Snap Store/Charmhub API to confirm the current revision and its associated bom.json hash, ensuring the documented changes match what the user can actually download.

Perform "Human-in-the-Loop" Triage: The tool displays a list of changes categorized by the AI into "Release Note Worthy" vs. "Discarded," including a brief AI-generated justification for why an item (like a CI update) was suggested for exclusion.

3. Out of Scope
Automated PR Submission: The tool will generate the Markdown content and the backport plan, but it will not automatically open GitHub Pull Requests to avoid complications with repo permissions and branch management.

Historical Backlog Processing: We are focusing on the "current-to-future" workflow; using the tool to retroactively fill the gap from November to today is a manual application of the tool rather than a core feature to build today.

External Ecosystem Support: The logic will be strictly limited to Kubernetes snaps and charms to keep the "BOM parsing" logic focused and reliable within the specific Canonical Kubernetes architecture.

Expert Guide Question:
When you’re reviewing those "discarded" results, what is the one thing you’re most afraid the AI will miss—a specific type of bug fix, a security patch, or something else?

You are helping a hackathon team ideate solutions.



Problem statement: When a new software version is promoted to the stable channel, the Technical Writer must reconcile disparate versioning metadata to distill a curated list of user-facing changes from high-volume technical noise. This matters because the current "archaeological" manual process is so exhaustive that it creates months of documentation lag, leaving users without the transparency required to safely manage their production infrastructure.



Success criteria: By the end of the day, the prototype must be able to:



Identify the Delta: The user provides a snap channel (e.g., 1.29/stable), and the tool successfully retrieves all GitHub commits that have landed since the "last documented" SHA stored in the local state.

Verify "Stable" Reality: The tool demonstrates a "Live Check" by querying the Snap Store/Charmhub API to confirm the current revision and its associated bom.json hash, ensuring the documented changes match what the user can actually download.

Perform "Human-in-the-Loop" Triage: The tool displays a list of changes categorized by the AI into "Release Note Worthy" vs. "Discarded," including a brief AI-generated justification for why an item (like a CI update) was suggested for exclusion.

Out of scope: Automated PR Submission: The tool will generate the Markdown content and the backport plan, but it will not automatically open GitHub Pull Requests to avoid complications with repo permissions and branch management.



Historical Backlog Processing: We are focusing on the "current-to-future" workflow; using the tool to retroactively fill the gap from November to today is a manual application of the tool rather than a core feature to build today.

External Ecosystem Support: The logic will be strictly limited to Kubernetes snaps and charms to keep the "BOM parsing" logic focused and reliable within the specific Canonical Kubernetes architecture.

Team skills and constraints: The team is very good at categorizing what is important and what is not. They are usually very busy and release notes are not a high priority.



Produce:



1. Twelve solution sketches, each two or three sentences. Span "obvious and safe" to "weird and unlikely to work". Number them. Do not pre-rank. At least two of the twelve must borrow from how a similar problem is solved in an unrelated domain (waiting rooms, pit crews, airport check-in, pharmacy queues, hotel concierges, and so on); name the domain so the team can trace the borrow.

2. For each sketch, one line on what would make it fail in a one-day hackathon.

3. Two extra "constraint sketches" outside the twelve, each framed as "what if this had to work [under an unusual constraint]?" (offline, in five seconds, on a phone in airplane mode, narrated by audio only, etc.). Constraints sharpen creative output; pick ones that pressure the actual problem.

4. Three pairs of sketches that combine into something stronger, with one line on what the combination adds.



Do not pick a winner. Express each sketch in terms of what the user gets to do (a verb), not what the team ships (a feature).

To help your team move from "forensic archaeology" to "curation," here is a range of solution sketches that explore different ways the user can interact with the data.

1. Solution Sketches
The Detective’s Ledger: The user runs a local script that generates a temporary interactive text file containing the "delta" commits. They move lines between "Release-Worthy" and "Discarded" headers, and the tool then appends their justifications to the state file and exports the final Markdown.

Failure Point: Managing file-state and accidental deletions in a raw text editor can get messy quickly.

The Concierge Brief (Domain: Hotel Concierge): Instead of looking at raw code, the user receives a "morning brief" where the AI has pre-vetted commits for "VIP status" (high user impact). The user "checks in" the VIPs to the release notes and sends the rest to the "luggage hold" for quick secondary review.

Failure Point: The AI might lack the nuance to distinguish between a "VIP" feature and a high-priority internal refactor.

The Swipe-to-Stable Interface: The user views AI-summarized PR cards one at a time and swipes right to "Include" or left to "Discard." This forces a binary decision on every item in the delta, ensuring nothing is missed while minimizing cognitive load.

Failure Point: Front-end UI polish and "swiping" logic usually consume too much development time in a 24-hour sprint.

The Live-Sync Auditor: The user monitors a dashboard that highlights discrepancies between the GitHub main branch and the Snap Store stable revision. They click "Acknowledge and Draft" only for the specific versions where a hash mismatch is detected.

Failure Point: API rate limits or authentication hurdles with the Snap Store/Charmhub APIs.

The Pit Crew Huddle (Domain: Racing Pit Crew): When the "Stable" reality changes, the user triggers a 60-second "sync session" where an engineer and the writer see a shared rapid-fire list. They use keyboard shortcuts to tag changes as a team, leveraging their existing "categorization" skills in a high-speed burst.

Failure Point: Coordinating a real-time "shared session" state between two users is technically complex for a one-day build.

The Sentiment Filter: The user reads a feed of commits that have been pre-filtered by an AI model trained to detect "User Value" sentiment. The user only sees items that the AI calculates as having >70% likelihood of impacting an end-user.

Failure Point: Building or tuning a reliable sentiment model for technical K8s commits takes more than a day.

The Ghostwriter Branch-Manager: The user triggers a tool that automatically creates a local Git branch with a "Draft" patch notice based on the current delta. The user then opens the file to prune the AI-generated "Discarded" list before pushing.

Failure Point: Local Git automation and branch management can become brittle if the user's local environment is non-standard.

The "Plain English" Translator: The user reviews commit messages that the AI has translated from technical jargon into "User Impact" statements (e.g., "Updated Go version" becomes "Improved cluster security and performance"). This allows the user to judge worthiness without needing to read the underlying PR code.

Failure Point: AI hallucinations where the "User Impact" translation becomes factually incorrect.

The Negative-Space Log: The user focuses exclusively on the "Discarded" pile, where the AI has already drafted justifications for exclusion. The user "rescues" any items they disagree with, turning the workflow into a safety audit rather than an authorship task.

Failure Point: If the AI "Include" logic is too aggressive, the user ends up doing more work to prune the "Keep" list.

The Commit Radio: The user listens to a text-to-speech narration of the AI-summarized delta and speaks "Keep" or "Discard" to categorize items while multitasking. This treats the "high-volume noise" as an audio stream to be filtered.

Failure Point: Speech-to-text accuracy with specialized Kubernetes terminology (e.g., "Kubelet," "Etcd").

The Slackbot Triage: The user interacts with a bot that pings them only when a stable channel hash changes. The bot asks, "Does the user need to know about [PR Title]?" and records the answer directly into the project's tracking file.

Failure Point: Slack API app approval and webhook configuration can be a time-sink for a hackathon team.

The "Bounty Board" Distributor: The user publishes the delta list to a simple internal board where engineers can "claim" their own commits and tag them as "Release Note Worthy" in five seconds. The user then reviews the "unclaimed" leftovers.

Failure Point: Getting other "very busy" team members to engage with a new dashboard during the hackathon.

2. Constraint Sketches
Constraint: The "Blink" Filter (5-Second Interaction): What if the user only had five seconds to decide on each commit? This forces the prototype to provide a single icon (category) and a three-word summary for every change, pressuring the AI to be extremely concise.

Constraint: Offline-Only (The "Subway" Mode): What if the tool had to work without an internet connection? This forces the prototype to pre-fetch and cache all metadata (BOMs, Commits, PRs) in a single "sync" event, allowing the user to do the curation work during a commute.

3. Strong Combinations
The Negative-Space Log + The "Plain English" Translator: The user audits why the AI excluded certain technical changes by reading simplified impact summaries.

Value: Reduces the "fear of missing out" (FOMO) by making the discarded list easy to scan and verify.

The Swipe-to-Stable + The Concierge Brief: The user triages a "curated" shortlist using a high-speed interface.

Value: Maximizes efficiency for busy users by focusing human energy only on the "maybe" and "yes" items.

The Ghostwriter + The "Bounty Board": The system drafts the notes, but engineers can "hop in" to fix descriptions of their own work before the writer finalizes.

Value: Shares the load without requiring a meeting, moving the "human-in-the-loop" closer to the source of the change.

Expert Guide Question:
Out of the "obvious" (CLI/Ledger) and "weird" (Swipe/Radio) options, which interaction style aligns best with how you actually spend your energy—do you prefer a deep-dive "power hour" once a month, or five minutes of triage every few days?

I think once a month is a good. In a month there should not be that many changes to need to be documented

The "once a month" cadence suggests a batch-processing workflow rather than a continuous one. This is a crucial distinction for your hackathon team because it changes the goal from "notifying the user" to "facilitating a deep-dive session."

If you only sit down once every 30 days, your biggest enemy isn't the number of notes—it’s the volume of noise you have to clear away to find those few nuggets of gold. Even if only five things are "release-worthy," you might still have to look at 200 commits to find them.

Refining the "Power Hour" Workflow
Since you’re leaning toward a monthly "Power Hour," here is how the prototype should prioritize its features:

The "Context-Restorer": Since a month has passed, the tool needs to remind you exactly where you left off. It should show the last published notice side-by-side with the new delta.

The "Mass-Discard" Feature: In a monthly batch, you need a way to "select all" and unselect the few you want to keep, rather than swiping one-by-one through 200 items.

The "Memory Jogger": The AI's job in a monthly cycle is to summarize the entire month's theme (e.g., "This month was heavy on security backports for the Kubelet").

A New "Monthly Batch" Solution Sketch: The Editorial Review Board
The Sketch: The user triggers the tool, which generates a single, comprehensive "Review Document" (like a Google Doc or Markdown file). This document is pre-populated with AI-drafted notes and a "Table of Discards" at the bottom. The user spends their "Power Hour" simply deleting what they don't want and polishing what remains, rather than hunting for data.

Why it fits: It respects the "busy professional" constraint by assuming you want to do all the work in one sitting and then be done with it for another four weeks.

The Reality Check: "Not that many changes?"
One risk of the "once a month" approach is the Accumulated Noise. | Duration | Est. Raw Commits (Noise) | Est. Release Notes (Signal) |
| :--- | :--- | :--- |
| 1 Week | ~20–50 | 1–2 |
| 1 Month | ~80–200+ | 4–8 |

If the "noise" is 200 commits, the "archaeology" feeling returns. The prototype must be excellent at that initial "AI-Triage" so that when you sit down for your Power Hour, you are looking at 15 "Strong Candidates" rather than 200 "Possibilities."

Expert Guide Question:

When you sit down for that monthly session, do you prefer to start with a blank page and "pull" in the changes you find, or would you rather start with a full draft and "prune" it down to the essentials?

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Take into account the rough sketch of a plan I proposed and the interview we did. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.



Ask the questions one at a time.



If a question can be answered by exploring the codebase, explore the codebase instead.

I’ve internalized the mission: move the "archaeology" burden from the human to the machine so you can focus on curation. I’ll now walk us down the design tree. For each question, I’ll provide my Recommended Answer—this is the path I suggest based on the constraints of a one-day hackathon and the need for reliability. You can agree, or push us onto a different branch.

Branch 1: The Anchor Point (Identifying the Delta)
Before we can find "what changed," the tool must know exactly where the previous documentation effort ended.

Question 1:
How should the tool store and retrieve the "Last Documented SHA" for each version/channel to ensure there are no gaps or overlaps when you sit down for your monthly session?

Option A: Parse the existing Markdown release notes on GitHub and look for the last mentioned PR link or date.

Option B: Use a standalone state.json file committed to the repository that acts as a "bookmark" for the tool.

Option C: Query the GitHub API for the most recent PR that has a specific "documented" label.

My Recommended Answer:
Option B (The Metadata Bookmark). Parsing Markdown (Option A) is fragile—one typo in a manual edit breaks the tool. Labels (Option C) are unreliable if someone forgets to tag a PR. A simple JSON file like docs/patch-metadata.json that maps 1.29/stable to a specific commit_sha is the most robust way to ensure the tool always knows its starting line. It also allows multiple team members to run the tool without losing sync.

Do you accept this recommendation, or do you have concerns about adding a metadata file to the repo?

How would this file look? The repo in question is https://github.com/canonical/k8s-snap

Since we are aiming for a robust "Power Hour" once a month, the metadata file needs to be a clear, non-fussy record.

Branch 1: The Anchor Point (Resolved)
The patch-metadata.json file would likely reside in a metadata/ or docs/ folder. Based on the k8s-snap repo's structure, which manages multiple tracks (1.29, 1.30, etc.), it would look like this:

JSON
{
  "project": "k8s-snap",
  "tracks": {
    "1.29/stable": {
      "last_documented_sha": "a1b2c3d4...",
      "last_documented_date": "2024-04-15T10:00:00Z"
    },
    "1.30/stable": {
      "last_documented_sha": "e5f6g7h8...",
      "last_documented_date": "2024-05-01T14:30:00Z"
    }
  }
}
Branch 2: The Source of Reality (Live Check)
Now that we have the "starting line" (the SHA from that JSON file), we need to determine the "finish line" for the current batch.

Question 2:
Where should the tool look to find the "Current Reality" of what is actually live for the user to ensure you don't document things that haven't hit the Snap Store yet?

Option A: Use the current git log of your local branches (e.g., origin/1.29).

Option B: Use the GitHub "Releases" or "Tags" page as the source of truth.

Option C: Query the Snap Store API for the specific channel (e.g., 1.29/stable) to get the live revision, then fetch the bom.json from that revision to find the actual commit SHA.

My Recommended Answer:
Option C (Snap Store API). In your interview, you mentioned the "lead time" pain point—where a backport lands but isn't in the store yet. Option A and B will lead to "false documentation" where you tell the user a fix is live when it’s still stuck in the promotion pipeline. Option C is the only way to achieve your success criterion of Verifying "Stable" Reality. The tool should programmatically "do the detective work" you currently do manually: ask the Snap Store what is live, find the revision, and grab the SHA from the BOM.

Does this approach to fetching the "finish line" match your vision for verifying the stable reality?

Yes. But I am not sure if the SHA commit included in the BOM is available from the snap store API. For the charm, I believe we can query charmhub for revision and cross reference to github releases but for this but it is something we should explore further. Getting direct from source is how we will ensure it is on stable and not in the promotion pipeline

That "direct from source" requirement is the most important part of the Live Check success criterion. If we don't get the SHA from the actual revision in the stable channel, we risk documenting "phantom" features that aren't actually in the user's hands yet.

Branch 2: The Source of Reality (Refining the Implementation)
Since the Snap Store API doesn't let us "peak" inside a file like bom.json without downloading the snap, and a 500MB+ download is too heavy for a fast script, we have a technical fork in the road.

Question 2.1:
How should the tool verify the "Stable" SHA for the Live Check without a full snap download?

Option A: Use snapcraft info k8s to get the Revision Number for the stable channel, then query GitHub for a tag or commit message that matches that revision (assuming the CI process tags it).

Option B: Use a lightweight "BOM-mirror"—a small helper service or a GitHub Action that extracts the bom.json SHA every time a snap is promoted and stores it in a public text file.

Option C (The "Download-Light" approach): Use a tool like unsquashfs or a Python library to download only the metadata headers of the snap to extract that one specific file (bom.json) if the store protocol supports it (rarely possible/reliable for a 24h hack).

My Recommended Answer:
Option A (Revision-to-Git Mapping). If your current CI process isn't tagging releases with their Snap Store revision number, the first hour of the hackathon should be spent adding a simple "Tag on Release" step. Once a revision is promoted to stable, the CI should tag the repo (e.g., rev-1234). The tool then simply asks the Snap Store "What is the current stable revision?" (1234) and then asks Git "Show me the commits between the last_documented_sha and tag rev-1234." This is 100% accurate, requires zero large downloads, and establishes a clear link between the store and the source.

Does your current CI/Release process support tagging, or should we make "Adding Revision Tags" part of the project scope?

Branch 3: The Editorial Triage (Filtering the Noise)
Once we have the list of commits between those two points, we face the "200-commit pile."

Question 3:
How should the AI categorize these commits to minimize your "Power Hour" fatigue?

Option A (Keyword/Label Only): The AI only flags things with feat: or fix: and hides the rest.

Option B (Contextual Classification): The AI receives the PR Title + File Diff Summary. It classifies them into "User Facing," "Internal Infrastructure," or "Security Fix," and provides a 1-sentence justification for its choice.

Option C (The "Negative Space" Audit): The AI drafts the entire release note, and your job is only to look at the Discarded list to see if it missed anything.

My Recommended Answer:
Option B (Contextual Classification). As you noted, labels like ci: can hide important changes, and feat: can be misleading. By feeding the AI a summary of which files changed (e.g., "Changed files in cmd/k8s/ vs internal/linting/"), it can make much smarter guesses. The tool should present you with a Triage Report where the "Noise" is collapsed but still visible, and the "Signal" is highlighted with the AI’s draft description.

Do you agree that seeing the "Justification" for why something was discarded is critical for your trust in the tool?

Question 2.1 - I think tagging the repo with revision numbers is not possible. We have so many channels and risk levels that it would be too much on the repo. Question 3 - I think the AI should try classify the changes. I am not sure if those three categories are enough. We can expand on those. It should definitely get as much context as possible to make the best possible note about the change. It should also show what was excluded for human review

That is a fair critique—adding tags for every revision across every track (edge, beta, candidate, stable) would turn the Git history into a cluttered mess of metadata.

Branch 2: The Source of Reality (Mapping without Tags)
If we can't use Tags, we need a reliable way to map the Snap Revision Number (e.g., 1234) back to a Git SHA (e.g., a1b2c3d) without downloading the 500MB snap.

Question 2.2:
Since we won't tag the repo, how should the tool find which commit SHA corresponds to the revision currently in the Stable channel?

Option A: Query the GitHub Actions API. Since the CI is what pushes the snap to the store, we search for the specific "Promotion" or "Release" workflow run that targeted the stable channel and extract the SHA from that run's metadata.

Option B: Query the Snap Store API for the revision-info. Some store implementations include a "source" field in the metadata if it was built via a linked GitHub repo.

Option C: Have the tool perform a "Partial Download" using a range-request (if supported) to just grab the bom.json from the squashfs header.

My Recommended Answer:
Option A (GitHub Actions API). In the k8s-snap repo, your releases are driven by workflows. When a build is pushed to a channel, GitHub Actions logs that event. The tool should query the GitHub workflow_runs API for successful "release" jobs. By matching the track/channel, it can find the specific workflow run that updated the Snap Store and grab the SHA associated with that run. This keeps the metadata in the CI logs where it belongs, rather than cluttering the Git tags.

Does your current GitHub Action workflow record which channel it is pushing to in a way that the API could filter for?

Branch 3: The Editorial Triage (Expanding the Taxonomy)
You’re right—"User Facing" is too broad. To make a "document a human would enjoy reading," the AI needs a more granular taxonomy to group changes logically.

Question 3.1:
Which categories should the AI use to organize the draft, and how should it handle the "Excluded" items?

My Recommended Answer:
I recommend an 8-Category Taxonomy based on standard Kubernetes community expectations:

High Level: Major Features or "Headline" changes.

Deprecations & Removals: Critical "heads up" for users.

Bug Fixes: Corrected behaviors.

Security: Vulnerability patches (requires high visibility).

Component Bumps: Updates to K8s, Go, CNI, etc.

Performance: Resource or speed improvements.

Documentation: Only if the change is significant (e.g., a new tutorial).

Internal (Discarded): CI, linting, refactors, unit tests.

The Interface Recommendation:
The tool should output a "Triage Dashboard" (a local HTML file or a structured Markdown file).

The Draft: Top section showing the first 7 categories with AI-written summaries.

The Audit Log: A bottom section titled "Excluded Changes" listing everything in Category 8. Each item here must have a 1-sentence "Reason for Exclusion" (e.g., "This PR only updated the GitHub Action version and does not affect the snap runtime").

Does this 8-category breakdown cover the "human-friendly" structure you are looking for, or are we missing project-specific categories like "Charm-specific updates"?

Question 3.1 - I like the more granular approach. Question 2.2. From what I understand, we use launchpad to push our snap releases. Can it be used to get the BOM?

Branch 2: The Source of Reality (Launchpad Integration)
You've identified a key architectural detail: Launchpad is your build engine. While the Snap Store tells us which revision is stable (e.g., Revision 1234), Launchpad is the "factory" that knows exactly which Git SHA was used to manufacture that specific revision.

Question 2.2: Can Launchpad be used to get the bom.json or the commit SHA without downloading the full snap?

My Recommended Answer:
No for the bom.json, but Yes for the Git SHA. Launchpad does not typically expose individual files from inside a built .snap (which is a compressed SquashFS image) via its API. However, it does store the "Source Revision" for every build it performs.

The most efficient "Direct from Source" path for your hackathon prototype is:

Query Snap Store API: "What is the current revision for k8s in 1.29/stable?" (Result: 1234)

Query Launchpad API: "Show me the build record for k8s revision 1234."

Extract the commit_sha1: Every SnapBuild object in Launchpad contains a reference to the specific Git commit it pulled from GitHub to start the build.

This bypasses the need to find the bom.json entirely because the SHA you were looking for in the BOM is already recorded as metadata on the Launchpad build record.

Does this "Launchpad Build Metadata" approach feel like a viable shortcut to you, or is the bom.json containing information beyond just the Git SHA that we would miss?

Branch 3: The Editorial Triage (The "Human-in-the-Loop" Interface)
Now that we have the SHA delta, we need to address how the AI presents the data to you during your monthly "Power Hour."

Question 3.1: Where should the triage happen? Since you want this to be a "local tool," how should the AI present its "Candidate" vs "Discarded" lists to you?

Option A (The Interactive CLI): A terminal-based wizard that shows you one commit at a time with a [y/n] prompt and an optional text field for justifications.

Option B (The Local Web UI): A simple Python-based Flask/FastAPI page that runs on localhost. It shows two columns: "The Draft" (editable) and "The Cutting Room Floor" (collapsible).

Option C (The Markdown Workbook): The tool generates a review_this_month.md file. You edit the Markdown directly (deleting lines or moving them), and a "Finalize" command parses your edits to update the state.

My Recommended Answer:
Option C (The Markdown Workbook). For a "Power Hour" once a month, you likely want to see the flow of the document, not click "Yes/No" 100 times in a CLI. By generating a Markdown file with a specific structure, you can use your existing text editor skills to polish the notes. The tool can use "Comment Tags" (e.g., ``) to keep track of which commits you kept or deleted. When you're done, you run tool finalize, and it extracts the clean notes and updates your patch-metadata.json.

How does the idea of an "editable Markdown workbook" strike you compared to a specialized UI?

Branch 4: The "Human Enjoyment" Factor (AI Styling)
You mentioned wanting to create a document a human would "enjoy reading."

Question 4:
When the AI summarizes a commit, should it focus on what was changed (technical) or why it matters to the user (benefit-centric)?

My Recommended Answer:
Benefit-centric. * Technical: "Updated the kubelet garbage collection threshold from 10% to 15%."

Benefit-centric: "Improved node stability by adjusting the default disk-space thresholds for garbage collection."

I recommend the AI prompt be structured to provide a "User Impact" summary. If the impact is "none" (e.g., a refactor), the AI should automatically flag it for Category 8 (Internal/Discarded).

Do you want the AI to also suggest a "Headline" for the month to give the patch notice more personality?

Question 2.2 - we only need the latest commit so the BOM itself is not needed. Question 3.1 I agree that the markdown file is the best. I don't understand the comment tags. Please explain that more. Question 4 - I think benefit centric is good. What do you mean by headline of the month?

We are narrowing in on a workflow that feels less like a chore and more like a high-level editorial review.

Branch 2: The Source of Reality (Confirmed)
We’ll proceed with the Snap Store → Launchpad → GitHub path. Since the Git SHA is the only "anchor" we need to calculate the delta, Launchpad's build metadata is our perfect shortcut.

Branch 3: The Markdown Workbook (The "Comment Tags")
The challenge with an "editable Markdown file" is that once you start moving text around or deleting bullets, the script might lose track of which commit it’s looking at. Comment tags are hidden "ID badges" for the machine that stay out of the reader's way.

In Markdown, anything wrapped in `` is an HTML comment. It won't show up when the file is rendered on GitHub or in a browser, but your script can still "see" it.

How it looks in your Workbook:

Markdown
### Bug Fixes
* **Improved node stability** during high disk pressure. * **Fixed a race condition** in the CNI provider. ### Internal (Excluded for review)
Why this is helpful:
When you run the finalize command at the end of your "Power Hour," the script scans the file for those tags.

If a sha tag is present in a "Keep" section, the script knows that commit is officially "documented."

If you delete a line entirely, the script notices the sha is missing and asks, "Hey, did you mean to discard this?"

It allows the machine to update your patch-metadata.json state file accurately based on your manual edits.

Branch 4: The "Headline of the Month"
Since patch notices can sometimes feel like a dry list of chores, a Headline provides a "TL;DR" (Too Long; Didn't Read) for the user. It gives the update a theme.

The AI’s Role:
The AI looks at the 5–10 "release-worthy" commits and suggests a punchy, professional title.

Example 1: "May 2026: Focus on Core Security & Secret Encryption"

Example 2: "June 2026: Performance Optimizations for Large-Scale Clusters"

It turns a "patch notice" into a "release highlight," making it much more "human-friendly" as you initially intended.

Branch 5: The "Justification Log" (The Final Filter)
One of your requirements was to record any commits excluded and provide a justification. This is the "safety net" to ensure that if a user later asks, "Why wasn't fix X mentioned?", you have an audit trail.

Question 5:
How and where should the "Discarded Justification Log" be stored?

Option A: In the patch-metadata.json file. Every time you finalize a release, the file grows with a list of "discarded" SHAs and their reasons.

Option B: In a separate, hidden .csv or .log file that users never see, but the team can query.

Option C: As a "Hidden" section at the very bottom of the actual Release Notes on GitHub (wrapped in a <details> tag), so the audit trail is public but doesn't clutter the page.

My Recommended Answer:
Option A (State File). Keeping the justifications in your patch-metadata.json keeps your documentation repo clean. Since this is mainly for the team's internal peace of mind (and to help the AI learn over time what you like to skip), there's no need to publish it to the users. It keeps all the "machine state" in one single source of truth.

Does storing the "Why we skipped this" log in the internal JSON file work for you, or do you want that audit trail to be more visible to the rest of the engineering team?

Expert Guide Question:
When you are editing the AI’s "Benefit-centric" summaries, what is your biggest pet peeve? (e.g., Is it when the AI is too "marketing-heavy," or when it gets the technical specific of a Kubernetes resource wrong?)

Question 3 : I am still confused as to how the user will edit the file. They will be presented with what the AI thinks are changes to be included and what should not be. Does the user then comment on the lines rather than delete them? Question 4 - while I like the personality, I don't think this is necessary. Question 5 - I wasn't planning on keeping a discarded log. I just want to be able to see at edit time what has been excluded so I can add them back in if necessary. Expert question: when I ran this before, AI made assumptions due to poor naming of the PR title. An example would be that we updated the documentation that is show with a help command on the terminal output to reflect how the product actually works. AI decided that was a new feature rather than a fix to the docs. Another annoying thing was the AI did not look at the file diff. In one instance, we had a PR title say update technology y to version X. It was actually updated to version W in the file and this was a typo in the PR title

This is where we move from "automation" to "augmentation." You’re pointing out the two biggest killers of AI trust: misleading labels and hallucinations caused by missing data (the file diffs).

Branch 3: The Editing Flow (The "Workbook" Experience)
To clear up the confusion on how you actually edit the file: the Markdown file is essentially a "Drafting Canvas."

The Workflow:

The Tool Generates the File: You open monthly_review.md.

Section A (The Signal): It lists the commits the AI thinks should be in the notes, already categorized (Bug Fixes, Security, etc.).

Section B (The Noise): At the bottom, under a header called ## Discarded (Review to Rescue), it lists everything else.

Your Action:

If the AI is right: You do nothing to those lines.

If the AI is wrong (False Negative): You "Cut" the line from the Discarded section and "Paste" it into the Bug Fixes section.

If the AI is wrong (False Positive): You simply delete the line or move it to the Discarded section.

Finalize: You run tool finalize monthly_review.md. The tool looks at which `` tags are currently sitting under the "Signal" headers and marks those as documented.

Recommended Answer:
You should delete or move lines, not comment on them. The Markdown file is a temporary scratchpad. The script uses the "Comment Tags" (the hidden IDs) only so it knows which Git SHA corresponds to which bullet point, regardless of where you move it in the file.

Branch 4: The Hierarchy of Truth (Solving the AI Hallucinations)
Your expert answer highlights that the PR Title is often a lie. If we only give the AI the title, it will hallucinate based on that lie. To fix this, we need to establish a "Source of Truth Hierarchy."

Question 4:
How should we structure the context we give the AI to ensure it prioritizes the actual code changes over the potentially misleading PR titles?

Option A: Provide only the PR Title and Body (Fast, but prone to typos/mislabeling).

Option B: Provide the Title, Body, and the git diff --stat (Shows which files changed, helps categorize "Docs" vs. "Code").

Option C: Provide the Title, Body, and the full patch/diff content for small-to-medium PRs.

My Recommended Answer:
Option C (The Full Context). For a "once a month" tool, we aren't worried about saving a few pennies on AI tokens. To prevent the "Version X vs Version W" error you mentioned, the AI must see the actual diff.

The Prompt Strategy: We tell the AI: "If the PR Title and the Code Diff disagree, the Code Diff is the truth. Look at the version strings changed in the files to verify the version numbers."

The Categorization Strategy: If the diff --stat shows only .md or .rst files changed, the AI should be instructed to deprioritize it as "Documentation" regardless of if the title says "New Feature."

Do you agree that the AI should be forced to "read the code" (the diff) as the primary source of truth, even if it makes the processing slightly slower?

Branch 5: The "Human-in-the-Loop" Verification
Since you don't want a permanent discarded log, but you do want to verify the AI's logic during your Power Hour:

Question 5:
In the "Discarded" section of your workbook, how much information do you need the AI to give you so you can quickly "Rescue" a commit without having to go back to GitHub?

My Recommended Answer:
Each item in the Discarded section should include:

The PR Title.

A "Reason for Rejection": (e.g., "Discarded: This change only affects internal CI linting and has zero impact on the K8s snap runtime.")

A "Confidence Score": (e.g., "Confidence: 95%"). If the AI is only 60% sure, you know to look at that one more closely.

Does this provide enough "at-a-glance" info for you to feel safe ignoring the discarded list?

3. I agree with this methodology. Commenting is inefficient. Question 4. I think we should get full context. I used documentation as an example but it should not just be deprioritized by default. If we add a new how to guide that is worth documenting. Slightly slower is fine if we are doing this once a month. 5. You made a very good point. Maybe we should include the AI summary as well as the actual PR title and PR number so you can go investigate further if you need to. It will bring to the surface quicker if AI has misinterpretted a PR title/ content. I think this could actually be a good feature of 3 as well. We should the AI summary of included, then in the next section the actual PR titles that correspond to those entries. Next section is the AI summary of excluded with the actual PR titles. On the clean up, the actual PR titles section will be deleted and the discarded will also be deleted. What do you think?

We’re building a "Trust but Verify" engine. By providing the PR titles alongside the AI summaries, we’re essentially giving you a "Back of the Book" answer key to check the AI’s homework in real-time.

Branch 3 & 5: The "Verification" Layout (Resolved)
Your proposed structure for the Markdown Workbook is excellent. It turns the file into a side-by-side audit tool.

The Workbook Layout (How it will look when you open it):

## 📝 The Draft (Included)

AI Summary 1: [Benefit-centric text] ``

AI Summary 2: [Benefit-centric text] ``

## 🔍 Verification: Included PRs

sha: 123 | Title: "Fix kubelet disk pressure" | PR #89

sha: 456 | Title: "Add new how-to for external CNI" | PR #90

## 🛑 The Cutting Room Floor (Excluded)

AI Reason: Internal CI update. ``

AI Reason: Doc typo fix. ``

## 🔍 Verification: Excluded PRs

sha: 789 | Title: "ci: update linting" | PR #91

sha: 012 | Title: "docs: fix spelling in readme" | PR #92

The Cleanup Logic:
When you’re done, you delete everything except Section 1. The script then reads Section 1, finds those hidden sha tags, and knows exactly what to mark as "done" in your patch-metadata.json.

Branch 4: The "Doc Nuance" Logic (Resolved)
To solve the "Help Command" vs. "Typo Fix" problem, we need to instruct the AI to look for Value Shift.

The Recommended Instruction:
"Evaluate Documentation changes by 'Value Shift.' If a change merely fixes grammar or formatting, discard it. If a change modifies instructions, adds a guide, or corrects a help command to reflect actual behavior, categorize it as a 'Bug Fix' or 'Feature' because the user's understanding of the product has changed."

Branch 6: The Data Pipeline (Launching the Hack)
Since we are doing a "Power Hour" once a month, we have one final major decision to make regarding The Prompting Strategy.

Question 6:
How should the AI process the 200+ commits? Should it process them all at once (Large Batch), or one by one (Individual Analysis)?

Option A (The Batch): Send all 200 commit messages and diff summaries to the AI in one giant "context window" and ask it to categorize and summarize the whole month.

Option B (The Assembly Line): The script sends each PR individually to the AI. The AI returns a structured JSON for that one PR. The script then assembles the Markdown workbook at the end.

My Recommended Answer:
Option B (The Assembly Line). While Option A is cheaper and faster, Option B is much more "hallucination-proof."

Accuracy: By focusing on one PR at a time, the AI is less likely to get overwhelmed by a 200-commit wall of text and "Version X vs W" errors become much rarer.

Rich Context: You can send the full file diff for each PR without hitting the context limit.

Resilience: If the script fails on commit #150, you don't lose the work for the first 149. You can just resume.

Does an "Assembly Line" approach (processing PRs one by one to ensure the highest accuracy) feel like the right trade-off for your monthly session?

Expert Guide Question:
When the "Assembly Line" is running, do you want to see a progress bar in your terminal, or should it just ping you (via Slack or a system notification) when the "Workbook" is ready for your review?

The assembly line sounds fine if it is more accurate. I suspect this will be triggered from an AI IDE or AI CLI so maybe it can just run in the background? Do we need to notify furhter?

Since you’re doing this in an AI IDE (like Cursor or VS Code) or a CLI, the "Background Task" approach is perfect. It fits the "busy engineer" persona—you trigger it, go grab a coffee or answer an email, and it does the heavy lifting while you're away.

Branch 6: The "Background" Experience (Resolved)
Question 6.1:
If the tool is running in the background, how should it "hand off" the work to you once the assembly line is finished?

Option A (Passive): It just finishes the process and leaves the monthly_review.md file in your folder. You have to remember to go check it.

Option B (Active CLI): It prints a final summary in the terminal with a "🔔 Ding" or a "Success" message and a link to the file.

Option C (The IDE "Auto-Focus"): Since you're likely in an IDE, the script finishes by automatically opening the monthly_review.md file in your active editor window.

My Recommended Answer:
Option C (Auto-open). This is the ultimate "low friction" move. You trigger the command, and 2–5 minutes later, the Markdown workbook simply "pops up" on your screen. It’s the digital equivalent of a butler handing you a prepared folder. No need for Slack pings or extra notifications; the appearance of the file is the signal.

Branch 7: Closing the Loop (The Finalize Step)
We’ve solved how to start and how to edit, but we need a clean way to finish.

Question 7:
Once you have finished editing the monthly_review.md and you’re happy with the notes, how should the tool "Close the Loop" to ensure next month’s archaeology doesn't start from zero?

My Recommended Answer:
You run a simple command: k8s-notes finalize monthly_review.md.

What the script does in those 2 seconds:

Reads the Markdown: It finds all the `` tags you kept in the "Included" sections.

Updates the Source of Truth: It writes the latest SHA it found into your patch-metadata.json state file. This "bookmarks" your progress.

Outputs the Final Markdown: It generates a clean final_patch_notes.md (stripping out all the triage/verification noise and hidden tags) that you can simply copy-paste into your PR.

Self-Destructs: It offers to delete the monthly_review.md scratchpad to keep your repo clean.

Branch 8: Error Handling (The "Missing SHA" Safety Net)
Question 8:
What should happen if the Launchpad API or the Snap Store API is down, or if it can't find a SHA for a specific revision?

My Recommended Answer:
Graceful Degradation. The tool shouldn't just crash. It should:

Print a warning: "⚠️ Could not verify SHA for Revision 1234 via Launchpad."

Fallback: It should ask GitHub for the most recent commit on that branch as a "Best Guess" and highlight that specific commit in your workbook with a 🚩 flag so you know it needs a manual check.

Final Design Tree Summary
We have reached a shared understanding on a system that:

Tracks State: Uses a patch-metadata.json bookmark.

Verifies Reality: Checks the Snap Store/Launchpad for the "Stable" SHA.

Processes with Precision: Uses an AI "Assembly Line" (PR-by-PR) with full File Diff context.

Augments the Human: Provides a Markdown Workbook with "Verification" sections and hidden SHA tags for editing.

Streamlines the Finale: Automates the state update and final formatting.

Expert Guide Question:
Now that we have the full architectural map, which part of this plan feels like the "riskiest" thing to build in a 24-hour hackathon—is it the Launchpad API integration or the AI-driven triage logic?

Question 6.1 I think a success message witha link to the file is fine. I like question 7 flow. Question 8: It should gracefully fail and tell you try again later. expert question: launchpad integration is the riskiest as I have not done that before and not sure how it will work. Please provide a summary of all these design choices that I could feed into a VS Code agent to help start the coding

This summary is formatted as a technical specification. You can paste this directly into a VS Code agent (like Cursor, GitHub Copilot, or Windsurf) to scaffold the project.

System Specification: K8s-Snap Release Notes Automator
1. Goal
Automate the "archaeology" of identifying, categorizing, and summarizing user-facing changes for Canonical Kubernetes snaps/charms. The tool moves the burden from manual discovery to editorial review.

2. State Management
File: metadata/patch-metadata.json

Structure:

JSON
{
  "tracks": {
    "1.29/stable": { "last_documented_sha": "string", "last_documented_date": "ISO-8601" }
  }
}
Purpose: Acts as a "bookmark" so the tool knows where the last monthly update ended.

3. Data Pipeline (The "Archaeology")
To find the "Stable Reality" (the finish line for the delta), the tool must:

Query Snap Store API: Find the current revision for a specific track (e.g., 1.30/stable).

Query Launchpad API: Look up the build record for that revision to extract the specific GitHub Commit SHA used for that build.

Calculate Delta: Fetch all GitHub PRs/Commits between the last_documented_sha (from state) and the current_stable_sha (from Launchpad).

4. AI Triage (The "Assembly Line")
Process the delta PR-by-PR for maximum accuracy:

Context Provided: PR Title, PR Body, and Full File Diff.

Logic:

Truth Hierarchy: File Diffs > PR Body > PR Title. Ignore misleading titles if the code shows otherwise.

Categorization: Group into: Major Features, Deprecations, Bug Fixes, Security, Component Bumps, Performance, Documentation, and Internal (Discarded).

Value Shift: Only include Documentation changes if they modify user-facing instructions or help commands.

5. User Interface: The Markdown Workbook
The tool generates a local monthly_review.md file and alerts the user with a terminal success message and a clickable link.

Layout:
Included Section: AI-generated "Benefit-centric" summaries with hidden tags: ``.

Verification Section: A list of actual PR titles and numbers corresponding to the included summaries for quick fact-checking.

Discarded Section: Items the AI thinks are "noise," including a 1-sentence Reason for Exclusion and the original PR title.

6. Closing the Loop (Finalization)
When the user runs the finalize command:

Parse Workbook: Scan for `` tags in the "Included" sections.

Update State: Write the most recent "Included" SHA to patch-metadata.json.

Clean Export: Generate a final .md snippet stripped of all internal tags and verification noise, ready for copy-pasting into a PR.

7. Implementation Notes & Risks
Riskiest Component: Launchpad API Integration. The agent needs to help investigate the lp.snaps API to map Snap Store revisions to Git SHAs.

Error Handling: Graceful failure. If APIs are unreachable, print a clear error and exit without corrupting the state file.

Tech Stack: Python or Go (suggested for ease of API handling and file manipulation).

Expert Guide Question:
Since Launchpad is the "Great Unknown" for this build, would you like the first task for the AI agent to be a proof-of-concept script that specifically tests retrieving a Git SHA from a Launchpad Snap revision?

You are helping a hackathon team pick its tooling for a one-day prototype.



What the team is building: Automate the "archaeology" of identifying, categorizing, and summarizing user-facing changes for Canonical Kubernetes snaps/charms. The tool moves the burden from manual discovery to editorial review.

Stack and constraints: This should be a python or go script as much as possible. 

Team skills: I have used copilot on VSCode IDE a good bit. I have played a bit with copilot CLI in a workshop container. I have limited experience with openrouter

Demo target: Identify the Delta, present the user with AI filtered results, user manually filters, tidy up ran patch notices are ready for a PR 

Available tools: Copilot with Claude, GPT, Gemini of various versions; openrouter with various models, Gemini chat



Recommend:



1. A primary AI coding tool to drive the implementation, with a one-paragraph justification grounded in skills and demo target.

2. A secondary model from a different provider for adversarial review. Explain in one paragraph what that means here and at what points in the day to invoke it.

3. The two or three configuration files to write before starting (instructions, plan, agent personas, skills), with a one-line description of each.

4. The three tooling questions you are least confident about, and what additional information would resolve each.

To maximize your 24-hour hackathon, you need to minimize "context loss" between your IDE and your thinking. Since you are comfortable in VS Code, we will double down on that ecosystem but swap the "brain" for the strongest available model.

1. Primary AI Coding Tool: Copilot with Claude 3.5 Sonnet
Recommendation: Use Copilot within VS Code, specifically selecting Claude 3.5 Sonnet as the active model.

Justification: While you have GPT and Gemini available, Claude 3.5 Sonnet is currently the gold standard for logical reasoning in code, particularly for "Assembly Line" tasks where the AI must understand the relationship between different API responses (Snap Store → Launchpad → GitHub). Since your demo target relies on a multi-step logic chain, Sonnet’s superior ability to follow complex, multi-file instructions will save you from the "hallucination loops" that often plague GPT-4o in mid-sized scripts.

2. Secondary Model: Gemini 1.5 Pro (Adversarial Review)
Recommendation: Use Gemini 1.5 Pro via the chat interface or OpenRouter as your "Adversarial Reviewer."

Justification: Adversarial review means treating a second model as a skeptical senior engineer whose only job is to find flaws in the primary model's work. Because Gemini has a massive context window and a different training architecture than Claude, it is excellent at spotting "blind spots." You should invoke it at two specific points:

10:00 AM: Paste your Launchpad API integration plan and ask: "What specific API edge cases or authentication hurdles am I ignoring here?"

3:00 PM: Paste your "Benefit-centric" AI prompt and ask: "Show me three ways a misleading PR title could still trick this prompt into documenting a CI change."

3. Pre-Flight Configuration Files
Before you write a single line of Python or Go, create these three files in your root directory:

.copilot-instructions.md: Defines the "Truth Hierarchy" (Diff > Body > Title) and the 8-category taxonomy to keep Copilot from guessing.

development-roadmap.md: A step-by-step checklist of the "Design Tree" decisions we just made, serving as the "anchor" for the AI agent if it gets lost.

api-contracts.md: A file containing sample JSON responses from the Snap Store and Launchpad APIs so the AI knows exactly what fields (revision, commit_sha1) it is looking for.

4. High-Risk Tooling Questions
These are the three "unknowns" that could sink your demo if not resolved in the first 90 minutes:

Launchpad Anonymous Access: Does the Launchpad API allow unauthenticated GET requests for snap build metadata, or will you spend three hours wrestling with OAuth?

Resolution: Run a curl test against a known k8s snap build URL immediately.

The "Partial Download" Fallback: If Launchpad metadata is missing for a specific revision, can you successfully use git-archive or a similar tool to fetch only the bom.json from GitHub without a full clone?

Resolution: Check if the bom.json path is consistent across all K8s versions in the k8s-snap repo.

Context Window vs. Diff Size: Will the AI "Assembly Line" choke if a single PR contains a 2,000-line dependency bump?

Resolution: Determine a "Max Diff Size" threshold (e.g., 50KB) where the script truncates the diff and provides only the file names to the AI to prevent crashing the prompt.

Expert Guide Question:
Since you’ve used the Copilot CLI in a workshop, would you prefer the "Finalize" step to be a command-line tool you trigger yourself, or would you like it to be a GitHub Action that triggers automatically when you save the Markdown file?

Can you summarize the plan into one paragraph

The project will deliver a local Python/Go tool that eliminates documentation lag by automating the reconciliation of release state between a local patch-metadata.json bookmark and the live "Stable" reality queried through the Snap Store and Launchpad APIs. Instead of manual archaeology, you will trigger an AI "Assembly Line" that analyzes each PR’s full file diff to generate a benefit-centric draft, presented to you in an editable Markdown workbook designed for high-speed curation. By verifying the AI’s work against original PR titles and "Discarded" justifications, you can finalize a month’s worth of changes in a single "Power Hour," while the tool handles the invisible labor of updating the tracking state and formatting the final, PR-ready output.

You are helping a hackathon team commit its working approach into written form.



Problem statement: When a new software version is promoted to the stable channel, the Technical Writer must reconcile disparate versioning metadata to distill a curated list of user-facing changes from high-volume technical noise. This matters because the current "archaeological" manual process is so exhaustive that it creates months of documentation lag, leaving users without the transparency required to safely manage their production infrastructure.



Chosen solution:The project will deliver a local Python/Go tool that eliminates documentation lag by automating the reconciliation of release state between a local patch-metadata.json bookmark and the live "Stable" reality queried through the Snap Store and Launchpad APIs. Instead of manual archaeology, you will trigger an AI "Assembly Line" that analyzes each PR’s full file diff to generate a benefit-centric draft, presented to you in an editable Markdown workbook designed for high-speed curation. By verifying the AI’s work against original PR titles and "Discarded" justifications, you can finalize a month’s worth of changes in a single "Power Hour," while the tool handles the invisible labor of updating the tracking state and formatting the final, PR-ready output.



Tooling decision: Copilot within VS Code, specifically selecting Claude 3.5 Sonnet as the active model.



Team size and split: Just me 



Produce a short document (under 400 words) titled "How we are working today" with these sections:



1. Driver tool and why.

2. The one or two configuration files we are writing before starting, and what each contains.

3. The agent personas or roles we are defining.

4. How we run adversarial review, if we do: which secondary model, at what points, against what kind of output.

5. How we split the work: one screen with rotating driver, parallel forks, or a hybrid. Be explicit about when we converge.

6. What we are deliberately not doing today, with one line each.



Output Markdown.

How we are working today
1. Driver Tool and Why
We are using Claude 3.5 Sonnet via VS Code Copilot. Its superior reasoning capabilities are essential for navigating the multi-platform "Assembly Line" logic (Snap Store to Launchpad to GitHub). Sonnet follows the "Truth Hierarchy" more reliably than other models, ensuring code diffs override misleading PR titles.

2. Primary Configuration Files
.copilot-instructions.md: Contains the 8-category taxonomy and the explicit rule that file diffs are the source of truth for versioning and impact.

api-contracts.md: Defines the expected JSON schemas for Snap Store and Launchpad responses to prevent the AI from hallucinating field names like revision or commit_sha1.

3. Agent Personas
The Forensic Analyst: Responsible for the "Archaeology" phase—reliably mapping Snap revisions to Git SHAs and fetching the correct commit deltas.

The Technical Editor: Responsible for the "Triage" phase—translating technical diffs into "Benefit-Centric" summaries and accurately categorizing them for the user.

4. Adversarial Review
We will use Gemini 1.5 Pro as a skeptical peer reviewer at two critical junctions:

10:00 AM: To stress-test the Launchpad API integration plan and identify potential authentication or rate-limiting "gotchas."

3:00 PM: To audit the AI-generated summaries against a sample of "messy" PR titles to find hallucinations or misinterpretations of the "Value Shift."

5. Work Split
As a solo developer, the split is between Automation and Curation. The "Assembly Line" acts as the parallel worker, handling the high-volume data retrieval in the background. Convergence happens at the Markdown Workbook, where the human "Driver" performs the final editorial review and triggers the finalize command.

6. Out of Scope
Automated PR Submission: We are stopping at the "PR-ready output" to maintain a final manual safety gate.

GUI/Web Dashboard: To ensure delivery today, we are using a local CLI and Markdown-based workflow exclusively.

Historical Backlog: We are building the engine for the current month; retroactively documenting the November gap is a post-hackathon application.

You are helping a small team set up a repository for a one-day hackathon prototype.



Project description: A patch notices updater that automatically pulls commits, tracks latest commit used in the patch notices, refines the output for a human to approve and then tidies the output even further.

Stack and constraints: I think this should live on the k8s-snap repo

Team size and split: just me



Propose a repo layout: a directory tree with a one-line purpose for each top-level entry, plus the three or four files that should exist on day one (README, planning files, configuration). Optimise for a team that needs to onboard each other quickly and produce a recorded demo by end of day.



Then list the three decisions in your proposed layout that you are least sure about, and explain what would change them. Wait for me to react before producing anything else.

Since this tool is intended to live within the existing k8s-snap repository, we want to ensure it is self-contained enough to not clutter the main codebase, yet accessible enough for a CI/CD process to find it later.

Here is the proposed layout for the tools/patch-noticer/ directory:

Proposed Directory Tree
Plaintext
tools/patch-noticer/
├── metadata/           # Persistent state: stores patch-metadata.json (the "bookmark").
├── prompts/            # System prompts for the AI "Assembly Line" and categorization logic.
├── src/                # Core logic (Python or Go) for API orchestration and diffing.
├── templates/          # Markdown templates for the "Workbook" and final output.
├── .copilot-instructions.md # The "Rulebook" for the AI agent (Taxonomy, Truth Hierarchy).
├── api-contracts.md    # Mock JSON responses for Snap Store/Launchpad for AI context.
├── development-roadmap.md  # The 24-hour checklist and demo script.
└── README.md           # Quick-start guide and the "How to Demo" instructions.
Day-One Essential Files
README.md: This serves as your demo storyboard. It should contain the "one-command" execution instructions and the exact steps to follow during your recorded demo to show the "Delta Discovery" and "Human-in-the-Loop" triage.

.copilot-instructions.md: Essential for your solo work with Claude 3.5 Sonnet. It encodes the design decisions we made (e.g., "File Diffs > PR Titles") so you don't have to repeat yourself to the AI agent all day.

api-contracts.md: Since Launchpad is your highest risk, having a file that documents the expected fields (commit_sha1 from the build record) allows the AI to write the integration code correctly even before you've fully mastered the API.

development-roadmap.md: Your "north star" for the hackathon. It breaks the day into: Phase 1: Archaeology (API Linkage), Phase 2: Assembly Line (AI Triage), Phase 3: The Workbook (UI/UX).

Three Decisions I am Least Sure About
Placement of patch-metadata.json: I’ve put it in tools/patch-noticer/metadata/. However, if this tool eventually supports other Canonical products (like k8s-bundles or charms), it might need to live in a more global repository root. I’d change this if you anticipate this tool becoming a "multi-repo" standard.

Language Choice (Python vs. Go): I am leaning toward Python for the prototype because its library support for "Assembly Line" AI tasks (OpenAI/Anthropic SDKs) and string manipulation for Markdown is generally faster for a 24-hour sprint. I’d switch to Go if the tool must strictly match the k8s-snap build-tooling style from hour one.

Launchpad "Build Record" Mapping: I’m assuming we can easily find the specific Launchpad build object from a Snap Store revision. If the Snap Store API doesn't provide a direct link to the Launchpad build ID, we might have to switch to a "time-window" search on GitHub, which is less precise.

What do you think of this layout and the "Assembly Line" focus for the src/ folder?

Please draft a .copilot-instructions.md based on what we have already decided

This .copilot-instructions.md is designed specifically for Claude 3.5 Sonnet. It focuses on the "Truth Hierarchy" to prevent the hallucinations you encountered previously and enforces the "Assembly Line" logic to ensure precision.

Markdown
# Copilot Instructions: K8s-Snap Patch Noticer

You are acting as a Senior Technical Architect and Technical Writer at Canonical. Your goal is to build a "Trust but Verify" automation tool that reconciles release state and generates benefit-centric patch notices.

## 1. Core Principles & Truth Hierarchy
To prevent hallucinations and miscategorization, follow this strict hierarchy:
1. **File Diffs (Highest Truth):** Always analyze the actual code changes to determine version numbers and impact.
2. **PR Body:** Use for context on "Why" a change was made.
3. **PR Title (Lowest Truth):** Treat titles as potentially misleading or containing typos.

**Rule:** If a PR Title and a File Diff disagree (e.g., version numbers), the File Diff MUST override the title in the final summary.

## 2. Release Taxonomy
Classify every commit/PR into exactly one of these 8 categories:
1. **High Level:** Major features or headline changes.
2. **Deprecations & Removals:** Breaking changes or deprecated APIs.
3. **Bug Fixes:** Corrected behaviors or race condition resolutions.
4. **Security:** Vulnerability patches (CVEs, security-critical bumps).
5. **Component Bumps:** Updates to K8s, Go, CNI, or other dependencies.
6. **Performance:** Improvements to resource usage or execution speed.
7. **Documentation:** Significant guide updates or help-command corrections (see "Value Shift" rule).
8. **Internal (Discarded):** CI updates, linting, refactors, and unit tests.

**The "Value Shift" Rule for Docs:** Exclude typo fixes or formatting. Only include documentation changes if they modify instructions, add new guides, or correct terminal help output to reflect current product behavior.

## 3. Data Pipeline Logic (The Assembly Line)
The tool must operate in a linear, background-friendly flow:
- **Anchor:** Read `last_documented_sha` from `metadata/patch-metadata.json`.
- **Verify Stable:** Query Snap Store for the current revision, then query Launchpad Build Metadata to find the corresponding `current_stable_sha`.
- **Fetch:** Get all GitHub PRs/Commits between those two SHAs.
- **Process:** Send each PR individually to the AI for categorization and benefit-centric summarization.

## 4. Markdown Workbook Structure
When generating `monthly_review.md`, follow this exact UI pattern:
- Use `## 📝 The Draft (Included)` for categories 1-7.
- Use `## 🛑 The Cutting Room Floor (Excluded)` for category 8.
- **Hidden Tags:** Every bullet point MUST end with a hidden HTML comment: ``.
- **Verification Sections:** Below the Draft and Excluded sections, provide a `🔍 Verification` table listing the original PR Title and Number for quick human auditing.

## 5. Coding Standards
- **Language:** Python (preferred for AI/API SDKs) or Go.
- **Resilience:** Implement "Graceful Failure." If Launchpad is down, notify the user and exit without corrupting `patch-metadata.json`.
- **Summarization Style:** "Benefit-centric." Instead of "Updated X to Y," write "Improved node stability by updating X to Y."

## 6. Project Context
- **Repository:** https://github.com/canonical/k8s-snap
- **APIs:** Refer to `api-contracts.md` for JSON schemas of Snap Store and Launchpad Build objects.
Why this works for your demo:
Safety: The "Truth Hierarchy" directly addresses your concern about the AI believing a typo in a PR title over the actual code.

Auditability: The "Verification Sections" in the workbook mean that during your 5-minute demo, you can show exactly how you "catch" the AI if it makes a mistake.

Efficiency: The "Value Shift" rule for docs ensures the tool doesn't annoy you with 50 spelling-fix commits during your Power Hour.

Ready to start the Launchpad Proof-of-Concept script?

I only have sonnet 4.6. Does this need to be adjusted for that?

You are absolutely right to check—since we are in May 2026, Claude Sonnet 4.6 is actually a significant step up from the 3.5 version I mentioned earlier. Released back in February, 4.6 is specifically optimized for "Long-horizon planning" and agentic workflows.  
+1

The good news? Sonnet 4.6 is even better suited for this project. Its 1M token context window means it can hold your entire k8s-snap repository and months of history in its head at once, and its Adaptive Reasoning mode makes it much less likely to trip over those "Version X vs W" typos you saw before.  

Here is the adjusted .copilot-instructions.md tailored for the 4.6 capabilities:

Markdown
# Copilot Instructions: K8s-Snap Patch Noticer (Sonnet 4.6 Optimized)

You are a Senior Technical Architect at Canonical. You are leveraging your Sonnet 4.6 "Adaptive Reasoning" and 1M context window to build a high-fidelity release notes engine.

## 1. Contextual Intelligence (1M Window)
- **Repo Awareness:** You have the capacity to see the entire `k8s-snap` codebase. When evaluating a PR, cross-reference it against existing patterns in the repo to ensure consistency.
- **State Management:** Prioritize the `metadata/patch-metadata.json` as your absolute anchor for temporal "Delta Discovery."

## 2. Reasoning & Truth Hierarchy (Anti-Hallucination)
Use **Extended Thinking** to resolve discrepancies:
1. **File Diffs (Primary):** The code is the source of truth. If a version bump in a `.go` or `Makefile` contradicts a PR title, use the file data.
2. **Commit History:** Look at related commits in the branch to understand the "Value Shift" of a PR.
3. **PR Metadata (Secondary):** Use titles only for initial categorization, but verify every "Benefit-centric" summary against the diff.

## 3. Advanced Taxonomy & "Value Shift"
Categorize into the 8 standard buckets (High Level, Deprecations, Bug Fixes, Security, Bumps, Performance, Docs, Internal).
- **The Doc Rule:** Apply high-effort reasoning to documentation. If a change corrects a "Help" command or updates a tutorial to reflect actual code behavior, it is a **Bug Fix/Feature**, not just a doc update.

## 4. Assembly Line Architecture
Even with your large context window, process the delta in a **Sequential Assembly Line**:
- **Step 1:** Ingest the PR and its full diff.
- **Step 2:** Generate a "Raw Summary" and categorize.
- **Step 3:** Perform a "Self-Correction" pass: "Does this summary match the code change exactly?"
- **Step 4:** Export to the Markdown Workbook.

## 5. Markdown Workbook & Hidden Tags
- Generate `monthly_review.md` using the "Verification Section" layout.
- **Hidden IDs:** Every summary MUST include `` at the end of the line.
- **Audit Section:** Group the original PR titles at the bottom of each category so the user can "Trust but Verify" your 4.6 logic at a glance.

## 6. Resilience
- If Launchpad or Snap Store APIs return errors, fail gracefully. Do not attempt to "guess" the Stable SHA; notify the user to retry once the platform is back online.
Key 4.6 Adjustments I made:
Adaptive Reasoning: I’ve instructed the agent to use its "Extended Thinking" feature specifically to cross-reference the PR title against the code diff.

Self-Correction Pass: Since 4.6 is built for agents, I've added a "Step 3" to the assembly line where it explicitly audits its own work before presenting it to you.

Repo Awareness: I've told it to lean into its 1M context window to understand the "vibe" of the repo, which will help it write summaries that sound like a Canonical engineer wrote them.

With Sonnet 4.6 at the helm, you're in a great position. Do you want to try generating the Launchpad API bridge first, or shall we start with the Markdown Workbook generator?

Please help with development-roadmap.md: A step-by-step checklist of the "Design Tree" decisions we just made, serving as the "anchor" for the AI agent if it gets lost.

This development-roadmap.md is your mission control for the hackathon. It breaks the project into four logical phases, prioritizing the "Archaeology" (the hardest technical part) first to ensure you have a demo-able product by the afternoon.

Development Roadmap: K8s-Snap Patch Noticer
Phase 1: The Archaeology (Data Linkage)
Goal: Prove we can map a "Stable" channel revision to a specific GitHub SHA.

[ ] Initialize Environment: Create tools/patch-noticer/ and seed metadata/patch-metadata.json with a known "starting" SHA.

[ ] Snap Store Bridge: Implement a script to query the Snap Store API for the current revision in a given track (e.g., 1.30/stable).

[ ] Launchpad Bridge (HIGH RISK): Implement the logic to query Launchpad Build records for that revision to retrieve the commit_sha1.

[ ] The Delta Engine: Use the GitHub API to fetch all PRs and Commits between the patch-metadata.json SHA and the Launchpad SHA.

Phase 2: The Assembly Line (AI Triage)
Goal: Pass the delta through the Sonnet 4.6 "Truth Hierarchy."

[ ] Context Fetcher: For each PR in the delta, retrieve the Full File Diff, the PR Body, and the Title.

[ ] Prompt Implementation: Configure the "Assembly Line" to process PRs individually using the instructions in .copilot-instructions.md.

[ ] Classification: Ensure the AI correctly buckets PRs into the 8-category taxonomy (Features, Fixes, Bumps, etc.).

[ ] The "Value Shift" Test: Verify that Doc-only changes are correctly discarded unless they meet the "Instruction Update" criteria.

Phase 3: The Human-in-the-Loop (UX)
Goal: Generate the editable workbook and the finalization loop.

[ ] Workbook Generator: Create the logic to spit out monthly_review.md with:

## 📝 The Draft (Summaries + Hidden SHA tags).

## 🛑 The Cutting Room Floor (Justifications).

🔍 Verification tables for both.

[ ] The Finalize Command: Build the parser that:

Reads the edited monthly_review.md.

Identifies which SHAs were kept.

Updates patch-metadata.json with the newest "Included" SHA.

[ ] Export Engine: Generate the clean, tag-free Markdown snippet ready for a GitHub PR.

Phase 4: The Demo (Recording)
Goal: Demonstrate the 5-minute success criteria.

[ ] Identify the Delta: Show the tool finding the difference between state and Launchpad.

[ ] Verify Stable: Show the API check confirming the "Stable" revision.

[ ] Perform Triage: Open the monthly_review.md, "Rescue" one item from the Discarded list, and run the finalize command.

Success Checklist (Demo Targets)
Feature	Target	Status
Delta Discovery	Tool knows exactly what changed since the last run.	[ ]
Stable Reality	Tool doesn't guess; it asks Launchpad/Snap Store.	[ ]
Truth Hierarchy	AI ignores a "typo" in a PR title in favor of the Diff.	[ ]
State Update	patch-metadata.json is updated correctly after finalization.	[ ]
Note to AI Agent: If you hit a wall with the Launchpad API, refer to api-contracts.md to mock the response and move to Phase 2 to ensure we have a functional AI pipeline for the demo.

The formatting does not copy and paste well. Please provide the file in md format

Your Markdown file is ready
MD icon
 development-roadmap 
MD

I have consolidated the roadmap into this file so you can drop it directly into your tools/patch-noticer/ directory. This will act as the "Source of Truth" for your AI agent throughout the hackathon.

Pro-tip for the Demo: Use this roadmap as a checklist during your recording. Checking off the items in Phase 4 as you demonstrate them live is a very effective way to show the judges that you met your technical goals.

Good luck with the Launchpad integration! It’s the toughest nut to crack, but once you have that SHA, the rest of the AI pipeline will flow smoothly.





Your Canonical chats aren't used to improve our models. Gemini is AI and can make mistakes. Your privacy and GeminiOpens in a new window

# Development Roadmap: K8s-Snap Patch Noticer

## Phase 1: The Archaeology (Data Linkage)
**Goal:** Prove we can map a "Stable" channel revision to a specific GitHub SHA.
* [ ] **Initialize Environment:** Create `tools/patch-noticer/` and seed `metadata/patch-metadata.json` with a known "starting" SHA.
* [ ] **Snap Store Bridge:** Implement a script to query the Snap Store API for the current revision in a given track (e.g., `1.30/stable`).
* [ ] **Launchpad Bridge (HIGH RISK):** Implement the logic to query Launchpad Build records for that revision to retrieve the `commit_sha1`.
* [ ] **The Delta Engine:** Use the GitHub API to fetch all PRs and Commits between the `patch-metadata.json` SHA and the Launchpad SHA.

---

## Phase 2: The Assembly Line (AI Triage)
**Goal:** Pass the delta through the Sonnet 4.6 "Truth Hierarchy."
* [ ] **Context Fetcher:** For each PR in the delta, retrieve the **Full File Diff**, the PR Body, and the Title.
* [ ] **Prompt Implementation:** Configure the "Assembly Line" to process PRs individually using the instructions in `.copilot-instructions.md`.
* [ ] **Classification:** Ensure the AI correctly buckets PRs into the 8-category taxonomy (Features, Fixes, Bumps, etc.).
* [ ] **The "Value Shift" Test:** Verify that Doc-only changes are correctly discarded unless they meet the "Instruction Update" criteria.

---

## Phase 3: The Human-in-the-Loop (UX)
**Goal:** Generate the editable workbook and the finalization loop.
* [ ] **Workbook Generator:** Create the logic to spit out `monthly_review.md` with:
    * `## 📝 The Draft` (Summaries + Hidden SHA tags).
    * `## 🛑 The Cutting Room Floor` (Justifications).
    * `🔍 Verification` tables for both.
* [ ] **The Finalize Command:** Build the parser that:
    1.  Reads the edited `monthly_review.md`.
    2.  Identifies which SHAs were kept.
    3.  Updates `patch-metadata.json` with the newest "Included" SHA.
* [ ] **Export Engine:** Generate the clean, tag-free Markdown snippet ready for a GitHub PR.

---

## Phase 4: The Demo (Recording)
**Goal:** Demonstrate the 5-minute success criteria.
* [ ] **Identify the Delta:** Show the tool finding the difference between state and Launchpad.
* [ ] **Verify Stable:** Show the API check confirming the "Stable" revision.
* [ ] **Perform Triage:** Open the `monthly_review.md`, "Rescue" one item from the Discarded list, and run the `finalize` command.

---

## Success Checklist (Demo Targets)
| Feature | Target | Status |
| :--- | :--- | :--- |
| **Delta Discovery** | Tool knows exactly what changed since the last run. | [ ] |
| **Stable Reality** | Tool doesn't guess; it asks Launchpad/Snap Store. | [ ] |
| **Truth Hierarchy** | AI ignores a "typo" in a PR title in favor of the Diff. | [ ] |
| **State Update** | `patch-metadata.json` is updated correctly after finalization. | [ ] |

---
