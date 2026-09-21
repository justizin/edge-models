# Tier: iOS devices

Facts from `docs/research-2026-09-20.md` §3.

Three routes, cheapest first:

1. **App Store llama.cpp / MLX front-ends, no Mac needed.** PocketPal AI (llama.cpp, open source), Locally by LM Studio (MLX + Foundation Models), Enclave, Private LLM (mlc). Sweep every device: record chip, RAM, iOS version, largest model that loads, tok/s on a fixed prompt. Reference points (Q4, llama.cpp Metal): TinyLlama 1.1B A15 39 / A16 54 / A17 Pro 57 / A18 70 / A19 Pro 87 tok/s; iPhone 16 Pro Llama 3.2 3B 12–18; iPhone 14 Pro Gemma 3 1B 20–28. MLX beats llama.cpp by 1.3–1.6x on A19 Pro.
   Memory ceilings: ~1–1.5 GB usable on 4 GB phones, ~2–2.5 GB on 6 GB, ~4.7 GB on 8 GB with the increased-memory entitlement. That maps to: 4 GB → ≤1B Q4; 6 GB → 2B Q4; 8 GB → 4B Q4.
2. **Apple Foundation Models framework** (iOS 26+, A17 Pro / M1 and newer, 8 GB RAM floor). On-device ~3B model; iOS 27 (Sep 14 2026) adds AFM 3 Core and a 20B-sparse Core Advanced on iPhone 17 Pro/Air. Context 4096 (iOS 26) / 8192 (iOS 27). Apple positions it for classification, tagging, extraction (`@Generable` enums), explicitly not for code generation. So: run the **IDS triage task** through it with a `@Generable enum Verdict { benign, malicious }`; skip the coding task. Needs Xcode 26/27; free personal team sideload is believed to work (no entitlement documented for the base model) but unconfirmed. The KVM Mac under ~/Work/funtime could host Xcode if no real Mac is around.
3. **MLX Swift / MLC-LLM** custom apps if route 1's apps can't load a model we care about.

## Deliverable
Per-device rows in the README: device, chip, RAM, iOS, route, model, tok/s, IDS F1 where measured. `deploy/ios/` gets the Swift sample for route 2 once a Mac with Xcode is confirmed.
