# Architecture

Two diagrams. The first is what runs on stage. The second is the slide that answers
*"could this operate inside a regulated bank."* Show the second, run the first.

## What we built

Single Streamlit process. No network calls on the demo path, so nothing can fail live.

```mermaid
flowchart TB
    subgraph offline["Offline - runs before the demo, never during"]
        CSV[("Challenge data<br/>12 CSV + rm_notes.json")]
        VER["verify.py<br/>deterministic recompute"]
        SEED["seed/build_seed.py<br/>12 risk factors, 21 exposure edges"]
        AUTH["Authoring agent<br/>LLM, human-edited"]
        FACTS[("out/facts.json")]
        PLANS[("plans/PLAN-00x.json<br/>state DRAFTED")]
        CSV --> VER --> FACTS
        CSV --> SEED --> FACTS
        FACTS --> AUTH --> PLANS
    end

    subgraph app["Streamlit app - one process"]
        ENGINE["engine.py<br/>shock, revalue, LTV, trigger eval<br/>PURE ARITHMETIC"]
        STATE["store.py<br/>plan state machine<br/>st.session_state + append-only log"]
        UI["ui.py<br/>board, plan card, dial"]
        ENGINE --> UI
        STATE --> UI
        ENGINE --> STATE
    end

    FACTS --> ENGINE
    PLANS --> STATE
    UI --> RM(["Priscilla"])
    RM -->|"arm / dismiss / action"| STATE

    style ENGINE fill:#0b4f6c,color:#fff
    style STATE fill:#0b4f6c,color:#fff
    style AUTH fill:#7a4900,color:#fff
```

Dark blue is deterministic. Amber is the model, and it is **offline, upstream, and human-reviewed**.

## Production shape

The same boundary, drawn against bank infrastructure. Nothing here is built this weekend;
the point is that nothing here is unusual either.

```mermaid
flowchart TB
    subgraph src["Bank systems of record"]
        CUST[("Custody / positions")]
        CRED[("Credit and collateral")]
        CRM[("CRM - objectives, notes")]
        MKT[("Market data")]
    end

    subgraph plat["Wealth intelligence layer"]
        ING["Ingestion - snapshot-versioned<br/>every plan pins the snapshot it was computed on"]
        REF[("Look-through reference data<br/>maintained by Product Control<br/>NOT inferred at runtime")]
        ENG["Deterministic engine<br/>exposure, LTV, bands, liquidity, triggers"]
        WATCH["Trigger watcher<br/>durable workflow per plan"]
        LLM["Authoring service<br/>drafts prose, proposes edges<br/>never evaluates, never executes"]
        AUD[("Audit store - append-only<br/>signed arming records")]
    end

    subgraph ch["Channels"]
        WB["RM workbench"]
        EX["Execution / order mgmt"]
    end

    CUST --> ING
    CRED --> ING
    CRM --> ING
    MKT --> ING
    ING --> ENG
    REF --> ENG
    ENG --> LLM
    ENG --> WATCH
    LLM -->|"drafts"| WB
    WATCH -->|"fires"| WB
    WB -->|"arm - human interrupt 1"| AUD
    WB -->|"action - human interrupt 2"| EX
    WB --> AUD
    EX --> AUD

    style ENG fill:#0b4f6c,color:#fff
    style WATCH fill:#0b4f6c,color:#fff
    style LLM fill:#7a4900,color:#fff
    style AUD fill:#2d572c,color:#fff
```

## The boundary, stated

| Deterministic - no model | Model |
|---|---|
| Exposure aggregation across portfolios | Drafting plan prose from client context |
| Lending value, advance rates, LTV | Proposing exposure edges from `underlying_reference` free text, **for human review** |
| Trigger evaluation | Narrating the arithmetic into what the RM says out loud |
| Mandate band and concentration checks | Detecting where `rm_notes` contradict computed state |
| Liquidity coverage vs planned cash needs | Critiquing an action against mandate, profile and objectives |

> **A trigger is never evaluated by a model.**
> It is a schema constant: `trigger.evaluated_by == "deterministic"`. A plan claiming otherwise
> fails validation.

## Answers to the questions a bank asks

**Data protection.** Client data never reaches the model as identifiers; the authoring service
receives computed exposures and de-identified context. The look-through mapping is reference data
owned by Product Control, not something inferred at runtime from free text.

**Model risk.** The model's output is prose and proposals. Every number on screen is produced by
code with a unit test. Model failure degrades the wording of an insight, never its arithmetic and
never an execution.

**Auditability.** Append-only. The arming record is a signature over the plan body at arming time,
so what the RM approved cannot be silently rewritten, and the approval provably predates the
outcome. That is the artefact a post-hoc explanation can never produce.

**Scale.** 20 clients, 24 portfolios, 1,015 position rows. Exposure aggregation is a group-by; a
scenario is a vector multiply. The engine is milliseconds. The overnight scenario walk is
embarrassingly parallel by client.
