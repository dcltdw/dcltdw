# Garmin Connect IQ store release

Shared release process for dcltdw's Garmin apps (watch faces / apps). Imported
into a Garmin repo via `@~/Github/dcltdw/claude/garmin-release.md`. Each repo's
CLAUDE.md adds a project supplement (signing-key path, device list, store-copy
location, …) below the import.

Don't cut a release unless asked. Uploading to the store is outward-facing and
done by the human, not by Claude.

## Pre-release checklist
1. **Confirm scope.** Diff `main` against the last release tag; ship only
   intended, reviewed work — no stray/diagnostic branches riding along.
2. **Compile-verify.** Clean `monkeyc` build (`BUILD SUCCESSFUL`) with the right
   SDK + `JAVA_HOME`. Monkey C is type-checked at compile, so this is the
   cheapest real check. Sweep the targets / do the `-e` export rather than one
   device. Behavior beyond "it compiles" needs a simulator/device check (there
   is typically no CI or test suite).
3. **Signing key — verify, don't assume.** The Connect IQ store binds an app to
   its first version's key pair and rejects any build signed with a different
   key. Use the project's key and **verify it by RSA-modulus match** against the
   already-published `.prg` before building:
   `openssl pkey -inform DER -in <key> -pubout | openssl rsa -pubin -modulus -noout`
   then grep the hex modulus in the published `.prg`.
4. **Build the store package.** `-e` export → the `.iq` with all products,
   signed with the verified key. Confirm the device count and size.
5. **Re-verify the artifact.** Modulus-match the actual `.iq` / `.prg`, not just
   the key you intended to use.
6. **Store documents.** Update the store description ("What's new in X.Y.Z" +
   move the prior version to history, keep under the 4000-char cap), the store
   README, and any changelog — accurate to the real changes.
7. **Secret scan** the diff and the built artifacts.
8. **Board + PR hygiene** per `AGENTS.md` (board moved, PR bodies complete,
   commits stamped).
9. **Tag** the release commit `vX.Y.Z`.
10. **Hand off.** The human uploads to the store. A release is **unconfirmed**
    until the wild says otherwise — for a fix, that's the error dashboard / a
    reporter, not the green build.

## Project supplement (put in each repo's CLAUDE.md, not here)
- Signing-key path + how it was verified.
- Target device list / primary test device.
- Where the store copy lives (description / changelog files).
- Any device- or app-specific release quirks.
