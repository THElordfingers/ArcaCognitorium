╔═════════════════════════════════════════════════════════════════════════╗
║◤                                                                      ◥ ║
║                                                                         ║
║    ＰＲＡＥＳＩＤＩＵＭ — ＳＹＳＴＥＭＳ ＣＨＥＣＫ                     ║
║                                                                         ║
║◣                                                                      ◢ ║
╠═════════════════════════════════════════════════════════════════════════╣
║                                                                         ║
║    Application  ·  PRAESIDIUM                                           ║
║    Version      ·  1.4                                                  ║
║    Started      ·  04-01-2026                                           ║
║                                                                         ║
╚═════════════════════════════════════════════════════════════════════════╝
╔═════════════════════╗
║ Verification steps: ║
╚═════════════════════╝
☑  1. Canvas opens on secondary monitor without crash ☑    
☐  2. All widgets restore to correct positions from layout.json 
		- Some that are meant to do, but many iterations of many windows
		  appear, that are not supposed to.
☑  3. GitWidget shows current branch and repo status 
		
☑  4. ChatWidget — send a message, confirm streaming response
☑  5. TokenTracker updates within 1 second of chat completion
☐  6. Restart app — widget positions are identical on relaunch
		- see 2.
		
═════════════════════════════════════════════════════════════════════════
╔════════════╗
║ Checklist: ║
╚════════════╝
☐  layout.json exists at `~/.arca/layout.json` after launch
	- Exists, but empty
☐  Widget geometry survives app restart (no reset)
	- no. some do, tons of extra
☑  Git operations stream live — UI does not freeze
	-Can stage, commit, push
☑  ClaudeBox import resolves — no ImportError in console
	- chat works.
☑  Lock / unlock state persists across restart
	- yes
☐  `bus.on()` subscription pattern in ChatWidget (not `bus.once()`)
		- donno how to check that, no debug in terminal
═════════════════════════════════════════════════════════════════════════
╔════════════╗
║ Open Items ║
╚════════════╝
 
(INGENIUM pipeline widget + remaining dockables) — pending.
	
Stale layout entry accumulation — cleanup deferred.
	-this is important
Exocognii FastAPI service integration (build node status, drift flags)
	yes, as well as full control panel and systems status
not yet wired — ReferentiaAggregator degrades gracefully.
		?
