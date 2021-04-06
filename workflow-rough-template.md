```mermaid
graph TD
    A[Movies] -->|MotionCor2| B[Motioncorrected movies]
    B --> C{split to web}
    C -->|gctf| D[ctf corrected]
    C -->|convert 10 images to jpeg| E[web gallery with motioncorrected images]
    D --> F{split to web}
    F -->|image classification| G[good images]
    F -->|convert 10 images to jpeg| H[web gallery with ctf images]
    B --> I[image classification]
    G --> I[image classification]
    I -->|particle picking| J[2D image classification]
