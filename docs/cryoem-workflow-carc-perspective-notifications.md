Below is a WIP graph representing the CryoEM workflow if the sample inspection is more convenient in the ThermoFisher EPU software

```mermaid
graph TD
    A[Data Collection initiated by user on the microscope] --> B
    B[User inspects the sample in the EPU data collection software] -->C{Does the Cryo-EM sample<br>and images look good?}
    C -- No --> D[End the data collection]
    C -- Yes --> CA{Who is the owner of the dataset?}
    CA -- Amgen --> CB[Start the data transfer to the Amgen storage]
    CA -- USC --> CD[obtain user_id, group_id,session_id, dataset_name<br>Automatic start of the transfer to central storage]
    CD --> E[Show user the web interface<br>get the necessary data from the user]
    E --> F[Initiate the workflow on discovery1]
    E -->|Send notification to the users that the Slack channel was created| BB[Create a data collection slack channel<br> with the members of the group that collects the data]
    E -->|Send notification to the users via email| BBB[inform user where the website is and send url and/or login info]
    subgraph Pegasus Workflow
        F --> G[Apply the motion correction to the dataset]
        G -->|Show the progress to the user| H[Convert the motion corrected images to jpeg]
        G -->|Non Dose-Weighted images| J[Get the CTF estimations for the images]
        J --> I[Convert the ctf estimates to jpeg]
        G -->|pass Dose-Weighted images to the endpoint| K[export data and notify the user to start interactive processing]
        J -->|pass the CTF estimates to the endpoint| K[export data and notify the user to start interactive processing]
    end
    subgraph Slack notifications
        BB --> CC[Notify user that the process started]
        F ---|Send notification| CC
        CC --> DD[Notify user that the motion correction started]
        G ---|Send notification that the motion correction started| DD
        DD --> EE[Show thumbnails of motioncorrected images to the user]
        H ---|Send thumbnails to the channel| EE
        EE --> FF[Show thumbnails of ctf estimates to the user]
        I ---|Send thumbnails to the channel| FF
        FF --> GG[Notify the user that data is ready]
        K ---|Send notification| GG
    end
    subgraph Email notifications
        BBB --> GGG[Notify the user that data is ready]
        K ---|Send notification| GGG
    end
    subgraph User-interactive 3D reconstruction
        K -->|User imports data to Cryosparc| L(3D reconstruction in Cryosparc)
        K -->|User imports data to Relion| AA(3D reconstruction in Relion)
    end
    subgraph Post-processing in Pegasus
        L --> S(Post-processing)
        AA --> S(Post-processing)
    end
    
    
    style A fill:#b3e6ff,stroke:#66ccff,stroke-width:2px
    style B fill:#b3e6ff,stroke:#66ccff,stroke-width:2px
    style C fill:#b3e6ff,stroke:#66ccff,stroke-width:2px
    style CA fill:#b3e6ff,stroke:#66ccff,stroke-width:2px
    style CB fill:#b3e6ff,stroke:#66ccff,stroke-width:2px
    style D fill:#ffad99,stroke:#ffad99,stroke-width:2px
    style E fill:#FFDCB0,stroke:#6dc293,stroke-width:2px
    style F fill:#FFDCB0,stroke:#6dc293,stroke-width:2px
    style G fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
    style H fill:#e6ffe6,stroke:#6dc293,stroke-width:2px
    style I fill:#e6ffe6,stroke:#6dc293,stroke-width:2px
    style J fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
    style K fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
    style L fill:#e6e6ff,stroke:#6dc293,stroke-width:2px
    style AA fill:#e6e6ff,stroke:#6dc293,stroke-width:2px
    style S fill:#d4ffd8,stroke:#6dc293,stroke-width:2px
