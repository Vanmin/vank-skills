# Swift / Apple platform

Load this file for iOS, macOS, SwiftUI, AppKit, UIKit, or Swift backend
on Apple platforms. Multi-skill iOS delivery still belongs to
`vk-ios-agents`; this file is the `vk-work` gate when implementation
stays in `vk-work`.

Priority: security/compliance → correctness → performance → maintainability.

## Security / compliance

Review secrets, Keychain/storage, transport, sandbox/entitlements, privacy
permissions, and sensitive logging before calling the change complete.
If a design weakens ATS, sandbox, privacy scope, or secure storage, stop
and report.

## Performance

Review repeated rendering, redundant state propagation, expensive `body`
work, duplicate subscriptions, and main-thread blocking.
"Works locally" is not enough if the update model is obviously wasteful.

## Memory and lifecycle

Review retain cycles, timer/observer cleanup, task cancellation, and
long-lived ownership. Record a plausible leak path as a risk even without
Instruments.

## SwiftUI

Prefer stable identity, localized state, cheap `body`, and explicit
ownership for observable models. Avoid derived work in `body` and
accidental view-model recreation.

## Platform integration

Respect scene/window ownership, background/foreground, and user-triggered
permission boundaries. Do not broaden filesystem or device access.

## Extra verification

When this file loaded, the verification summary must include:

- security/compliance result
- repeated-render / redundant-compute result
- memory/lifecycle result
- targeted unit/UI tests and build when available
