# SHAI Setup Wave A

Date: 2026-10-31
Status: implementation specification

## Revision 0.2.1

- Removed the internal `Wave A` label from every user-visible Setup, terminal,
  handoff-shell, package-description, and Setup README string.
- Added the linked `Brought to you by Aabey LLC` header attribution.
- Split the debloat summary into `Things SHAI may remove` and `Things that
  stay`, with personal files and media in the preserved list.
- Changed the confirmation to explicitly approve debloating and repurposing
  Ubuntu as a smart-home and AI automation hub.
- Made audited direct-Ubuntu installation the simple default and one managed
  Docker stack the advanced option. The stack remains separate service
  containers under one managed project, not one giant container.
- Added an Offline-by-default choice to the signed setup plan and backend state.
- Reworded online behavior around approved files and later SHAPP downloads.
- Changed completion to open SHAI Home first, then close Home and open SHAPP
  from the final button.

## Objective

Wave A turns the existing inert SHAI installer package into a branded graphical
setup experience. Installing the DEB still changes no Ubuntu applications or
settings. The user launches `shai-setup`, reviews the plan, and explicitly
approves the conversion before the existing protected debloat engine runs.

## Ordered flow

1. Install the local `shai-installer` DEB.
2. Run `shai-setup` as the normal desktop user.
3. Read the debloat notice. It explains that SHAI removes only named Ubuntu
   applications/settings from the reviewed catalogs and does not target files
   in the user's home, media folders, or mounted data drives.
4. Choose `Review README` or confirm and continue. No is a normal exit path.
5. Choose one high-level architecture:
   - One managed Docker stack: one Docker Engine and one SHAI-managed project,
     with separate service containers selected later in SHAPP.
   - Direct Ubuntu installation: advanced mode for apps with an audited native
     installation path.
6. Answer whether the appliance is intended for smart-home automation and
   whether local AI should be available. These answers filter later SHAPP
   recommendations; they do not install Home Assistant, Zigbee, models, or
   other optional workloads during Wave A.
7. Review the exact Wave A plan.
8. Click Apply. SHAI opens a visible Ubuntu terminal, requests sudo there, runs
   the exact simulated/protected debloat waves, applies the SHAI Brand v2
   wallpaper and GNOME dark/green settings, installs core SHAI launchers, and
   records the architecture choices.
9. Run package, desktop, and service health checks.
10. Show completion, open the Wave A SHAI Home shell, and launch the SHAPP
    handoff by default. SHAPP clearly states that optional app deployment is
    the next wave.

## Safety boundaries

- Package installation alone remains inert.
- No online check, package download, Docker installation, image pull, or model
  download occurs in Wave A.
- No broad purge, broad autoremove, kernel removal, boot change, disk format,
  or personal-file deletion is permitted.
- The existing APT simulation and protected-package gates remain authoritative.
- SHAI uses Ubuntu's visible terminal and sudo authentication. Passwords are
  never stored.
- The managed-stack choice does not create one giant all-services container.
- Historical SHAIBUNTU code and paths are not installed.

## Branding boundary

The Setup application and SHAI-owned launchers use `branding/SHAI_Brand_v2`.
Wave A installs the v2 wallpaper, v2 lockup/wordmark, dark SHAI application
surfaces, green `#33EE33` accent, GNOME `prefer-dark`, and GNOME green accent.
Ubuntu OS identity, boot branding, login manager branding, and attribution are
unchanged.

## Wave A application shells

SHAI Home, SHAPP, SHAI Health, and AIA launchers are present only after setup.
They are explicitly labeled Wave A shells. They display saved architecture
state and the next implementation boundary; they do not claim that monitoring,
app deployment, or AI management exists yet. AIA is installed only when local
AI was selected.
