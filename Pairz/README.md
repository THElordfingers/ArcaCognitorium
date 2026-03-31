88888888ba             88                                     88      ad888888b,  
88      "8b            ""                                   ,d88     d8"     "88  
88      ,8P                                               888888             a8P  
88aaaaaa8P' ,adPPYYba, 88 8b,dPPYba, 888888888    8b       d8 88          ,d8P"   
88""""""'   ""     `Y8 88 88P'   "Y8      a8P"    `8b     d8' 88        a8P"      
88          ,adPPPPP88 88 88           ,d8P'       `8b   d8'  88      a8P'        
88          88,    ,88 88 88         ,d8"           `8b,d8'   88 888 d8"          
88          `"8bbdP"Y8 88 88         888888888        "8"     88 888 88888888888  




 __                 __   |   __                       __            __         
|__)_ . __    /|     _)  |  |__)_ _ _ _ _ |_    _ |  /   _ | _  _  (_    .|_ _ 
|  (_||| /_    |.   /__  |  |  (-| (_(-|_)|_|_|(_||  \__(_)|(_)|   __)|_|||_(- 
                                       |

Pairz is a generative color tool designed for designers who want to master accessible,
perceptually uniform palettes. By utilizing the OKLAB color space, Pairz ensures that 
what looks good to the eye is backed by mathematical precision.


          __               
|_/ _    |__ _ |_    _ _ _ 
| \(-\/  |(-(_||_|_|| (-_) 
     /     


    Perceptual Averaging: Create "Bridge" (Tertiary) colors that are perfectly centered 
    between your Background and Foreground.

    Live Accessibility: Real-time WCAG 2.1 contrast checking and vision simulation.

    Dynamic UI: A responsive canvas that scales your palette visualization and 
    typography hierarchy (24/18/12) as you resize.

    Deep Stats: Eight distinct infographics including OKLAB Solar Systems, Luminance 
    Ladders, and Harmony Wheels.


 __                                   
|  \. _ _ _|_ _  _    |  . _|_. _  _  
|__/|| (-(_|_(_)| \/  |__|_)|_|| )(_) 
                  /               _/ 

Pairz/
├── main.py                 # Core Application & UI Shell
├── modules/
│   ├── generator.py        # OKLAB math & Generation Algorithms
│   ├── stats_engine.py     # Infographic drawing logic (8 Aspects)
│   ├── storage.py          # Pair & Preset saving/loading
│   └── sample_view.py      # Sample Text Renderer & Randomizer
├── exports/
│   ├── ColourPairs/        # Finalized .json and .txt pairs
│   └── SliderPresets/      # Saved generator configurations (.json)
├── assets/
│   └── fonts/              # Custom UI fonts (if applicable)
└── README.md               # Project Documentation


                        __                    
|_/ _  |_  _  _  _ _|  (_ |_  _  _|_ _   |_ _ 
| \(-\/|_)(_)(_|| (_|  __)| )(_)| |_(_|_||__) 
     /


Command					Action

Space					Generate New Pair
Shift + Space			Randomize Sample Text (in Sample View)
Tab						Cycle Main Pages (Generator/Sample/Stats)
Shift + Tab				Cycle Sidebar Configuration Tabs
Ctrl + Tab				Cycle Internal Sub-Tabs (Help/Stats)
Ctrl + Scroll			Scale Body Text size
Shift + Scroll			Scale Title Text size


