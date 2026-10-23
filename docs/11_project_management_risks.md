# Project Management and Risks

## Purpose and current scope

This document describes how the SAR Flood Isolation Platform project is
organized, how work is tracked across YouTrack and GitHub, and how technical
and delivery risks are monitored. The project investigates SAR-based flood
mapping for the 2024 spring floods in Kazakhstan and the potential isolation
of settlements from the road network.

The repository is currently a planning and design scaffold. The `src/` and
`tests/` directories do not yet contain a runnable application or automated
test suite. The current phase focuses on research, requirements, architecture,
prototype evidence, and evaluation planning; implementation and operational
deployment are future work.

## Team and responsibilities

| Participant | YouTrack tasks | Responsibilities |
| --- | --- | --- |
| Nurdaulet | DIP-1–DIP-7 | Project proposal; literature and existing-system reviews; technology comparison; requirements; architecture and diagrams; verification and evaluation plan |
| Mansur | DIP-8–DIP-13 | Repository README and structure; relevance evidence; UX prototype; project coordination and risks; supervisor feedback; pre-defense tag and demo |
| Supervisor | Review and guidance | Review key deliverables, give feedback, and advise on academic direction and acceptance expectations |

The YouTrack assignee and issue state are the source of truth for current
ownership and progress. The project owner maintains the GitHub repository and
coordinates updates between the issue tracker and repository.

## Milestones and dependencies

The milestones are sequenced by their logical prerequisites. Calendar dates
are not specified because no approved schedule has been recorded.

| Milestone | Related issues | Deliverable and exit condition | Dependencies | Recorded progress |
| --- | --- | --- | --- | --- |
| 1. Define the project | DIP-1 | Proposal defines the problem, users, aim, objectives, scope, and expected outcomes | None | Done |
| 2. Establish the evidence base | DIP-2–DIP-4 | Literature review and evidence-backed comparisons of existing systems and technology options | Milestone 1 | Done |
| 3. Specify and design the solution | DIP-5–DIP-6 | Testable requirements and an aligned architecture package with editable diagrams | Milestones 1–2 | Done |
| 4. Plan verification | DIP-7 | Evaluation plan defines methods, metrics, conditions, and a comparison baseline | Milestones 2–3 | Done |
| 5. Prepare repository and user-facing evidence | DIP-8–DIP-10 | README and repository structure, relevance evidence, and UX prototype | Milestones 1–4 | DIP-8 Done; DIP-9–DIP-10 In Progress |
| 6. Coordinate and review | DIP-11–DIP-12 | Risks, responsibilities, and dependencies are tracked; supervisor feedback and responses are documented | Milestones 1–5 | To do |
| 7. Prepare pre-defense submission | DIP-13 | Accessible Git tag, repository link, summary of completed work, limitations, and outstanding tasks | Milestones 1–6 | To do |

A milestone is complete when its exit condition is met and the corresponding
YouTrack issue contains a concise result and a link to its evidence. If the
work order changes, update dependencies in YouTrack and record the reason.
Do not mark blocked or incomplete work as done.

## GitHub and YouTrack workflow

1. Keep work focused on the relevant YouTrack issue and use the issue ID in
   the branch name, for example `DIP-11-youtrack-risks`.
2. Include the issue ID in commit messages, for example
   `DIP-11 Document project risks and dependencies`.
3. Keep the task branch synchronized with the GitHub repository. Add relevant
   branches, commits, and pull requests to the corresponding YouTrack issue.
   The project VCS integration checks branch names for issue references.
4. After pushing work, update the issue with a short summary, artifact links,
   remaining work, and the next action. Update the issue state to reflect the
   actual state of the deliverable.
5. Keep credentials, service-account keys, private datasets, and other
   sensitive information out of Git. Use example configuration files and the
   repository `.gitignore`.
6. Before the pre-defense submission, verify that the final commit and tag
   are accessible to the supervisor and committee, and document known
   limitations.

## Risk assessment method

Likelihood and impact are qualitative: Low, Medium, or High. The risk owner
reviews the mitigation at milestone boundaries and when new evidence or a
dependency changes the likelihood or impact. If a risk materializes, record
the issue, response, and any schedule or scope change in YouTrack.

## Risk register

| ID | Risk | Likelihood | Impact | Mitigation and response | Owner |
| --- | --- | --- | --- | --- | --- |
| R1 | Google Earth Engine access, quota, or authentication issues delay SAR processing. | Medium | High | Validate access early; keep credentials local; run a bounded test; document an approved export or manual-analysis fallback. | Nurdaulet |
| R2 | Flood-mask results vary substantially with threshold choice or polarization, weakening conclusions. | High | High | Use consistent inputs across methods; perform the planned sensitivity analysis; report uncertainty and avoid claiming one threshold is universally correct. | Nurdaulet |
| R3 | Reference flood data are incomplete, delayed, or misaligned with the Sentinel-1 scene. | Medium | High | Verify dates, coverage, resolution, and coordinate reference before evaluation; document exclusions and limit claims to supported comparisons. | Nurdaulet |
| R4 | OpenStreetMap roads or settlements are incomplete or outdated in the study area. | Medium | High | Record extraction date and coverage; check the network; distinguish missing map data from actual isolation and state the limitation in results. | Nurdaulet |
| R5 | Road-graph processing or spatial joins are too expensive for the selected area. | Medium | Medium | Begin with a bounded area; profile processing; partition or simplify where justified and document scale limits. | Nurdaulet |
| R6 | The planned web stack is not runnable by the pre-defense deadline. | Medium | Medium | Keep the current deliverables focused on reproducible analysis plans, interface/API examples, and prototype evidence; explicitly label implementation as future work. | Mansur |
| R7 | Interviews cannot be arranged or user needs cannot be substantiated. | Medium | Medium | Where interviews are infeasible, use verifiable public reports and official statements; distinguish sourced findings from assumptions. | Mansur |
| R8 | GitHub branches, commits, and YouTrack issues drift out of sync. | Medium | Medium | Use issue IDs in branches and commits; update issue evidence after pushing; review open issues and dependencies at each milestone. | Mansur |
| R9 | Late supervisor feedback requires rework of completed deliverables. | Medium | Medium | Request feedback at milestone boundaries; record decisions and responses; allow time for revisions before the final tag. | Mansur |
| R10 | Credentials or restricted data are accidentally committed. | Low | High | Use `.gitignore` and placeholder configuration; review staged files before committing; revoke and rotate exposed credentials immediately. | All contributors |
| R11 | A team member becomes unavailable or responsibilities are unclear. | Medium | Medium | Keep ownership and next actions explicit in YouTrack; document handoff context and shared project artifacts; escalate unresolved ownership to the supervisor. | Mansur |
| R12 | The analysis scope expands beyond the available time or data. | Medium | High | Prioritize the agreed flood event, three threshold methods, road-network isolation, and planned evaluation; defer optional features through a documented scope decision. | Mansur |

## Review and reporting

- Review milestone progress, open dependencies, and high-impact risks whenever
  an issue changes state or new evidence changes the plan.
- Keep evidence traceable: link documents, diagrams, prototypes, decisions,
  and evaluation results from the related YouTrack issue.
- For blocked work, record the blocking condition, responsible person, and
  next action instead of marking the issue complete.
- At submission, report what is complete, what remains incomplete, known
  limitations, and the exact Git tag and commit.

## Immediate actions

1. Complete DIP-9 and DIP-10 and attach the resulting evidence to their issues.
2. Review the risk register and dependencies with the supervisor; record any
   changes under DIP-11 or DIP-12.
3. Confirm the evidence and tag format required for DIP-13.
4. Before submission, verify issue references, repository visibility, branch
   contents, and the final summary.
