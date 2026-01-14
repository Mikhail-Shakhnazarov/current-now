# Auth (v2)

V2 does not implement authentication because v2 does not call provider APIs.

Provider and model selection exist in the UI and are carried through the engine protocol so that the assembled provider request payload can be inspected. The expectation is that API-key authentication is implemented first when provider calls are added.

Subscription login is an explicit product goal but remains an open design problem. Consumer account logins such as ChatGPT Plus and Claude Pro are not implemented in v2 and may require provider-specific login flows, secure token storage, and policy constraints.

The v2 architecture preserves a seam for later work by keeping the engine as a separate component. Provider auth can be implemented behind the engine boundary without changing the cockpit UI.
