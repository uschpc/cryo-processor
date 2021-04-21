Below is a WIP graph representing the CryoEM workflow

```mermaid
graph TD
    A[Data processing initiated by user] --> B[Start the data transfer from the microscope];
    subgraph Pegasus Workflow
        B --> K[Apply the motion correction to the first 20 images]
        K --> L[Convert the first 20 images to jpeg]
        L --> C[Present the jpg images to a user<br> in a web gallery]
        C --> D{Does the Cryo-EM sample<br>and images look good?}
        D -- Yes --> E[Apply motion correction the rest of the images]
        D -- No --> F[End the processing]
        E -->|Non Dose-Weighted images| G[Get the CTF estimations for the images]
        G -->|pass the CTF estimates to the endpoint| I[export data for interactive processing]
        E -->|pass Dose-Weighted images to the endpoint| I[export data and notify the user to start interactive processing]
    end
    subgraph Cryosparc
        I -->|User imports data to Cryosparc| J(3D reconstruction in Cryosparc)
    end
    subgraph Relion
        I -->|User imports data to Relion| AA(3D reconstruction in Relion)
    end
    subgraph Post-processing in Pegasus
        J --> S(Post-processing)
        AA --> S(Post-processing)
    end
    
    
    style A fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
    style B fill:#FFDCB0,stroke:#6dc293,stroke-width:2px
    style C fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
    style K fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
    style L fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
    style D fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
    style E fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
    style F fill:#FF6B6B,stroke:#6dc293,stroke-width:2px
    style G fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
    style I fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
    style J fill:#fff4dd,stroke:#ffc457,stroke-width:2px
    style S fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
