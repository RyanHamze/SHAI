# SHAI Setup: before you apply

SHAI is software that configures an existing Ubuntu Desktop installation.
Ubuntu remains the operating system and continues to own its kernel, drivers,
firmware, terminal, repositories, package manager, and OS security updates.

Installing the SHAI DEB does not debloat or reconfigure Ubuntu. Changes begin
only after the normal desktop user launches `shai-setup`, reviews this scope,
selects an architecture, and approves the exact setup plan.

## What the debloat targets

Setup uses named package catalogs already exercised on the disposable Ubuntu
26.04 test VM. Depending on what is installed, it may remove selected:

- games, LibreOffice, Thunderbird, and unused media-player/photo applications;
- printer, scanner, and modem packages;
- domain-login and remote-desktop packages;
- reporting applications while retaining the intentionally preserved Whoopsie
  package in a disabled state;
- non-US dictionaries, help, extra themes, and selected personal utilities.

The authoritative APT simulation runs again immediately before each removal.
SHAI stops if a debloat step would install another package or remove a
protected Ubuntu component outside the reviewed exceptions.

## What it does not target

Setup does not scan or delete personal files, media libraries, documents,
downloads, browser profiles, SSH keys, mounted data drives, or arbitrary files
in the user's home directory. It does not format, partition, or mount disks.

It preserves the Ubuntu login and GNOME desktop, NetworkManager, Firefox,
Terminal, APT, Snap, PackageKit, accessibility packages, drivers, firmware
tools, bootloader packages, and kernels. OpenSSH package files are retained.

Removing `shai-installer` later does not automatically reinstall Ubuntu
applications removed with approval. Use a VM checkpoint, system backup, or a
reviewed package reinstall plan when complete rollback is required.

## Other setup changes

- Scheduled APT, Snap, and firmware refresh activity is changed to the existing
  SHAI manual-update policy. Manual Ubuntu updates remain available.
- Ubuntu location and technical-problem reporting controls are disabled.
- Existing Location portal grants are cleared, GeoClue is masked, and automatic
  device location remains off until the user deliberately changes the policy.
- Events and Tasks notifications, GNOME online-account providers, media sharing,
  and GNOME Wellbeing recording/reminders are disabled. Setup does not delete
  existing online-account credentials; SHAPP will later offer a separately
  simulated and approved component removal.
- Automatic date and time synchronization remains enabled so signed Ubuntu
  repository metadata and security operations use an accurate clock.
  Setup repeats this warning in the completed-system summary.
- The Web Offline toggle is installed. The user's Offline choice controls the
  mode left active after setup. Proxy-based Web Offline is not a host-wide
  firewall or air-gap and does not control software that ignores the desktop
  proxy.
- The reversible SHAI desktop theme applies its wallpaper, GTK colors, icon
  theme, GNOME dark mode, and green accent. GNOME Shell panel styling activates
  when Ubuntu's optional `gnome-shell-extension-user-theme` package is already
  installed. Setup reports that layer as pending instead of downloading it
  silently. Ubuntu identity and boot/login branding are unchanged.
- SHAI Home, SHAPP, SHAI Health, and Web Offline launchers are installed after
  successful setup. SHAI Appearance provides user-controlled switching between
  SHAI, Ubuntu defaults, and the appearance saved before SHAI. AIA is added
  only when Local AI is selected.
- Ptyxis and GNOME Terminal profiles already present receive a reversible-style
  SHAI palette with black background and `#33EE33` foreground. The palette file
  remains selectable from terminal preferences.
- The completion page and SHAI Home show local user roles plus the device name,
  hardware model, processor, memory, disk capacity, OS and architecture, GNOME,
  windowing system, kernel, and applied privacy defaults.

## Architecture choices

`Install compatible apps directly in Ubuntu` is the simple default. SHAPP will
offer only applications with a separately audited native Ubuntu installation
method. It will not silently substitute a container.

`One SHAI-managed Docker stack` is the advanced option. It means one future
Docker Engine and one SHAI-managed Compose project. Each service still runs in
its own container so it can be independently updated, stopped, backed up, or
removed. Docker and service images are not installed during base setup.

Smart-home, local-AI, and offline answers shape later recommendations. Local
apps and tools are selected later in SHAPP. Before any download, SHAPP must show
its source, size, resource impact, ports, storage, and network requirements.
