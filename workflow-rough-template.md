```mermaid
graph TD
    A[Movies] -->|MotionCor2| B[Motioncorrected movies]
    B --> C{split to web}
    C -->|gctf| D[ctf corrected]
    C -->|convert 10 images to jpeg| E[web gallery with motioncorrected images]
    D --> F{split to web}
    F -->|image classification| G[good images]
    F -->|convert 10 images to jpeg| H[web gallery with ctf images]
    B --> I[exposure curation]
    G --> I[exposure curation]
    I --> J(manual particle picking)
    J --> K[2D particle classification]
    K --> L[select 2D classes]
    L --> M[Template-based auto particle picking]
    M --> N[Particle inspection]
    N --> O[Particle extraction]
    O --> P[2D particle classification]
    P --> Q[selection of best classes]
    P -->|if 2D classes are better and there is a need to improve the quality| M[Template-based auto particle picking]
    Q --> R[3D reconstruction]
    R --> S[Post-processing]
