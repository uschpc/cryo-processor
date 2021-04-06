```mermaid
graph TD
    A[Movies] -->|MotionCor2| B[Motioncorrected movies]
    B --> C{split to web}
    C -->|gctf| D[ctf corrected]
    C -->|website| E[web gallery with motioncorrected]
    D --> F{split to web}
    F -->|image classification| G[good images]
    F -->|website| H[web gallery with ctf images]
    B --> I[image classification]
    G --> I[image classification]
    I -->|particle picking| J[2D image classification]
