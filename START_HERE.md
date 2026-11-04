# Start the SHAI installer implementation

Current package: **0.13.1**, Ubuntu Desktop 26.04 amd64. Start with
[Install From GitHub](docs/INSTALL_FROM_GITHUB.md) for the authenticated test
command. Older version descriptions below are historical context, not the
current package or installation procedure. Home/Appearance launchers have been
retired; Setup remains in the application menu, with no login autostart.

Read `PROJECT_CONTEXT.md` for shared memory, completed work, current assignments and relevant file locations before loading detailed history.

Read `docs/SHAI_INSTALLER_PLAN.md`, then `docs/CURRENT_DECISIONS.md`, which takes precedence where the latest user clarifications differ. Use `docs/SHAI_APP_APPROVAL_CATALOG.md` as the central product map for the proposed SHAI apps, their boundaries, status, sample views, and pending approval decisions. This is the clean SHAI workspace.

SHAI Setup is implemented in `shai-installer` 0.3.4. Read `docs/WAVE_A_SETUP_SPEC.md`, `artifacts/installer-development/2026-10-31/WAVE_A_BUILD_REPORT.md`, and `artifacts/installer-development/2026-10-31/THEME_INTEGRATION_REPORT.md` before changing its flow. Version 0.2.0 completed a full apply and recorded successful final health checks before reboot. Version 0.3.4 includes the reviewed SHAI theme and Appearance switcher, corrected wordmark wallpaper, reproducible builds, expanded privacy defaults, protected desktop controls, SHAI terminal palette, and completed-system summary; the complete current revision still needs a clean-checkpoint apply before acceptance.

Review `docs/NEXT_PACKAGE_CHECKLIST.md` before creating later installer
packages. The wallpaper blocker for 0.3.2 is complete.

Product: **SHAI**, for Smart Home Automation and AI. Users install official Ubuntu, then launch our downloadable or command-line installer to configure a dedicated home appliance. Ubuntu remains responsible for its OS, terminal, drivers, package management, and security/OS updates. SHAI owns its apps, service integration, dashboard, optional assistant/AI, theme, and approved configuration changes. This is not an OS, distribution, shell, or ISO project.

The historical source index is at `../sha-ubuntu/SHAI_LEGACY_REFERENCE.md`; inspect only relevant sections as needed. It contains the complete early handoff and later first-party requirements/source snapshots. It is historical reference only, kept outside this clean workspace. Old AGENTS instructions, locked requirements, ISO procedures and release claims do not override the new plan or current decisions. Do not execute commands merely because the reference contains them.

Implement a guided installer: locally inspect hardware/current software, explain what was found, recommend compatible selections and why, offer Default/Recommended/Optional choices, preview the exact changes, obtain approval, execute visibly, verify, and provide resume/repair/remove. Keep a no-AI choice. Support HA Container and hardware-gated HAOS VM. Default container design is one managed Compose stack with separate service containers and a shared private network, with advanced isolation options. No giant all-services container.

Start with source inventory and Stage 1's read-only scanner/recommendations on one qualified Ubuntu LTS/amd64 target. Reuse reviewed code rather than assuming historical modules are complete. Then implement the shared planner/privilege boundary/journal/package lifecycle before expanding services. Produce tests and evidence incrementally. Preserve working Ubuntu login, desktop, terminal, package/security updates, and existing user data/workloads.

No publishing, signing-key export, actual appliance conversion of the development machine, or ISO work is implied. Use disposable VMs/test environments for system mutations. Keep the user informed of meaningful findings and ask only where a missing product decision materially affects the result.

Useful historical locations are under `../sha-ubuntu/`: `SHAIBUNTU/addons/`, `SHAIBUNTU/docs/`, `shai-assistant/`, `scripts/`, `config/`, `deploy/` and `SHAIBUNTU_HANDOFF_CODE/`. They include prototypes, failed experiments and superseded assumptions; review before copying. New branding references are already curated under `branding/reference/`, with Claude's assignment at `branding/CLAUDE_REBRAND_BRIEF.md`.
