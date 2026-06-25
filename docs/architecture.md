# contracts-analysis — Architecture

```mermaid
flowchart TB
    subgraph ext["External"]
        YF["yfinance<br/>option chains + live prices"]
        IRX["Yahoo Finance ^IRX<br/>risk-free rate"]
    end

    subgraph k3s["k3s Cluster — namespace: contracts-analysis"]
        subgraph app["App Pod — NodePort 30502"]
            DASH["dashboard.py<br/>Streamlit UI"]
            subgraph backend["Backend — wtf_options"]
                SVC["options_service.py<br/>analyze_income_options<br/>analyze_buy_options"]
                MKT["market_data.py<br/>get_live_or_close_price<br/>get_risk_free_rate<br/>calculate_greeks"]
                SVC --> MKT
            end
            DASH --> SVC
        end
        CFG[("ConfigMap<br/>config.yaml")]
    end

    USER["Browser<br/>localhost:30502"]

    MKT -->|"option chain fetch"| YF
    MKT -->|"^IRX rate"| IRX
    app --- CFG
    USER --> DASH

    classDef external fill:#f5f5f5,stroke:#888,color:#333
    classDef pod fill:#e3f2fd,stroke:#1565c0,color:#333
    classDef cfg fill:#fff8e1,stroke:#f9a825,color:#333
    classDef user fill:#fce4ec,stroke:#c62828,color:#333

    class YF,IRX external
    class DASH,SVC,MKT pod
    class CFG cfg
    class USER user
```

**Legend**
- Light grey — external data sources (yfinance, Treasury yield)
- Blue — application components (Streamlit UI + wtf\_options backend)
- Yellow — k8s config
- Pink — end-user entry point

**Data flow:** User selects tickers and strategy filters → Streamlit calls options\_service → market\_data fetches live/close prices and ^IRX rate from yfinance → py\_vollib computes Greeks → filtered contracts returned to dashboard.
