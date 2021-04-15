Below is a WIP graph representing the CryoEM workflow

```mermaid
graph TD
    subgraph Pegasus
        A[Movies] -->|MotionCor2| B(motion corrected movies)
        B -->|convert 20 images to jpeg| C(web gallery with<br> motioncorrected images)
        D -->|convert 20 images to jpeg| E(web gallery with<br> ctf images)
        D -->|image classification<br>discard bad images| F(good images)
        C -->|gctf on non-Dose Weighted images| D(ctf estimates)
        B -->|use Dose Weighted images| I[exposure curation]
        F --> I[exposure curation]
    end
    subgraph Cryosparc
        I -->|import to Cryosparc| J(manual particle picking)
        J --> K[2D particle classification]
        K --> L[select 2D classes]
        L --> M[Template-based auto particle picking]
        M --> N[Particle inspection]
        N --> O[Particle extraction]
        O --> P[2D particle classification]
        P --> Q[selection of best classes]
        Q --> R[3D reconstruction]
        Q -->|if 2D classes are better and <br>there is a need to improve the quality| M[Template-based <br>auto particle picking] 
    end
    subgraph Pegasus2
        R --> S(Post-processing)
    end
    
    
    style A fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
    style B fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
    style C fill:#d4ffd8,stroke:#6dc293,stroke-width:2px,stroke-dasharray: 5 3
    style D fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
    style E fill:#d4ffd8,stroke:#6dc293,stroke-width:2px,stroke-dasharray: 5 3
    style F fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
    style I fill:#d4ffd8,stroke:#6dc293,stroke-width:2px,stroke-dasharray: 5 5
    style J fill:#fff4dd,stroke:#ffc457,stroke-width:2px,stroke-dasharray: 5 3
    style K fill:#fff4dd,stroke:#ffc457,stroke-width:2px,stroke-dasharray: 5 3
    style L fill:#fff4dd,stroke:#ffc457,stroke-width:2px,stroke-dasharray: 5 3
    style M fill:#fff4dd,stroke:#ffc457,stroke-width:2px,stroke-dasharray: 5 3
    style N fill:#fff4dd,stroke:#ffc457,stroke-width:2px,stroke-dasharray: 5 3
    style O fill:#fff4dd,stroke:#ffc457,stroke-width:2px,stroke-dasharray: 5 3
    style P fill:#fff4dd,stroke:#ffc457,stroke-width:2px,stroke-dasharray: 5 3
    style Q fill:#fff4dd,stroke:#ffc457,stroke-width:2px,stroke-dasharray: 5 3
    style R fill:#fff4dd,stroke:#ffc457,stroke-width:2px,stroke-dasharray: 5 3
    style S fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
