    ::INIT                                                                        
                                                                                  
    TIER: Build CAELESTIS        
    TARGET: [single component or task — e.g. "Build Dolium v2"]                   
    STATE: :THEORY::REVIEW ::BUILD                                     
                                                                                  
    FILES IN SCOPE:                                                               
    - [paste raw GitHub URLs, or "none"]                                          
    - *Fetch live init_urls.txt first, then pick relevant files*                  
                                                                                  
    CONTEXT:                                                                      
      A missing part of a set of existing "Machinae" scripts. It needs to be added in,
      and additional files for entities can be created at that time.                             
                                                                                  
    TASK:                                                                         
      1. Build CAELESTIS                                                              
      Full build from scratch. Follows same interface as other Machinae ( update() ,  
      triggers.poll() ,  to_json() ,  write() ,  summary() ). Writes to               
      ~/.arca/caelestis.json . Uses pyswisseph + Lahiri Ayanamsha.                    
                                                                                      
      2. Build Mundana State Bus                                                      
      Aggregation layer for all seven Machinae. Shared data bus feeding two output    
      tracks: cosmetic/UI and entity behaviour.                                       
                                                                                      
      3. Build Celestial Resolver                                                     
      Per-entity CelestialContext injection from State Bus. Each entity gets          
      affinities, resistances, vulnerabilities, and special alignment conditions.     
                                                                                      
      4. Write  celestial.yaml  for all 11 entities + integrate into ENTITEX          
      ENTITEX generates  celestial.yaml  as part of entity package. Claude infers     
      affinities from existing traits and lore. Dedicated session.                                                      
                                                                                  
    CONSTRAINTS:                                                                  
   		Don't touch the existing Machinae. Dont Touch any parts of entities existing 
   		file structure. 
                                                                                  
    KNOWN STATE:                                                                  
		Several exisiting Machinae. 
