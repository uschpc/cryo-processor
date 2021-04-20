Below is a WIP graph representing the CryoEM workflow

```mermaid
graph TD
    A[Image processing initiated by user] -->|process first 20 images| B[Apply the motion correction with Motioncor2];
    subgraph Pegasus
        B -->|Apply motion correction and convert 20 images to jpeg| C[Present the images to the user<br> in a web gallery]
        C --> D{Do the sample<br> and images look good?}
        D -- Yes --> E[Apply motion correction the rest of the images]
        D -- No --> F[End]
        E --> G[Get the CTF estimations for the images]
        G --> H[Update the web gallery for the initial images with CTF estimates for these images]
        G -->|pass the CTF estimates to the endpoint| I[export data for interactive processing]
        B -->|pass Dose-Weighted images to the endpoint| I[export data for interactive processing]
    end
    subgraph Cryosparc
        I -->|import to Cryosparc| J(3D reconstruction in Cryosparc)
    end
    subgraph Relion
        I -->|import to Relion| AA(3D reconstruction in Relion)
    end
    subgraph Post-processing in Pegasus
        J --> S(Post-processing)
        AA --> S(Post-processing)
    end
    
    
    style A fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
    style B fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
    style C fill:#d4ffd8,stroke:#6dc293,stroke-width:2px,stroke-dasharray: 5 3
    style D fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
    style E fill:#d4ffd8,stroke:#6dc293,stroke-width:2px,stroke-dasharray: 5 3
    style F fill:red,stroke:#6dc293,stroke-width:2px
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
