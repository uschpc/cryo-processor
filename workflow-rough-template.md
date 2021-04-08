```mermaid
graph TD
    A[Movies] -->|MotionCor2| B{motion corrected movies}
    B -->|gctf| D{ctf estimates}
    B -->|convert 10 images to jpeg| C[web gallery with motioncorrected images]
    D -->|convert 10 images to jpeg| E[web gallery with ctf images]
    D -->|image classification| F[good images]
    B --> I[exposure curation]
    F --> I[exposure curation]
    I --> J(manual particle picking)
    J --> K[2D particle classification]
    K --> L[select 2D classes]
    L --> M[Template-based auto particle picking]
    M --> N[Particle inspection]
    N --> O[Particle extraction]
    O --> P[2D particle classification]
    P --> Q[selection of best classes]
    Q --> R[3D reconstruction]
    Q -->|if 2D classes are better and there is a need to improve the quality| M[Template-based auto particle picking]
    R --> S[Post-processing]
