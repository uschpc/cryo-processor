Below is a WIP graph representing the CryoEM workflow if the sample inspection is more convenient in the ThermoFisher EPU software

```mermaid
graph TD
    A[Data Collection initiated by user on the microscope] --> B
    B[User inspects the sample in the EPU data collection software] -->C{Does the Cryo-EM sample<br>and images look good?}
    C -- No --> D[End the data collection]
    C -- Yes --> E[Initiate the data transfer to the central storage]
    E --> F[Initiate the workflow]
    subgraph Pegasus Workflow
        F --> G[Apply the motion correction to the dataset]
        G -->|Show the progress to the user| H[Convert the first 20 images to jpeg]
        H --> I[Present the jpg images to a user<br> in a web gallery]
        F -->|Non Dose-Weighted images| J[Get the CTF estimations for the images]
        F -->|pass Dose-Weighted images to the endpoint| K[export data and notify the user to start interactive processing]
        J -->|pass the CTF estimates to the endpoint| K[export data and notify the user to start interactive processing]
    end
    subgraph Cryosparc
        K -->|User imports data to Cryosparc| L(3D reconstruction in Cryosparc)
    end
    subgraph Relion
        K -->|User imports data to Relion| AA(3D reconstruction in Relion)
    end
    subgraph Post-processing in Pegasus
        L --> S(Post-processing)
        AA --> S(Post-processing)
    end
    
    
    style A fill:#b3e6ff,stroke:#66ccff,stroke-width:2px
    style B fill:#b3e6ff,stroke:#66ccff,stroke-width:2px
    style C fill:#b3e6ff,stroke:#66ccff,stroke-width:2px
    style D fill:#ffad99,stroke:#ffad99,stroke-width:2px
    style E fill:#FFDCB0,stroke:#6dc293,stroke-width:2px
    style F fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
    style G fill:#e6ffe6,stroke:#6dc293,stroke-width:2px
    style H fill:#e6ffe6,stroke:#6dc293,stroke-width:2px
    style I fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
    style K fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
    style L fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
    style S fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
    
