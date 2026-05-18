#todo 

[[ADVISE LCA Platform]] #todo 

- [x] Stage Creation - Press enter to create
- [ ] When setting target process for an intermediate, the thing does not refresh.
- [ ] I/O intermediate qty editing bug.
- [ ] I/O create Final product - "Final" missing from label
- [ ] lcia tagging, scoping table should have sort by
- [ ] lcia tagging, only 3.9.1 showing up
- [ ] scoping - multi select editor dropdowns not working
- [ ] dashboard - process breakdown chart mouseover. "Stage null - XXX"


### For CW Resolution
- [ ] For UPR Exchange name, creation thru portal does not seem to use `get_or_create_exchange_name`  logic. 
	- emission_factor_service.py
		- insert_lcia() , after the else statement ... `upr_exchange_name` 
	- How to resolve? just match name and unit? want to match upr_exchange_name_cpc_id as well? 
	- Frontend need to offer a lookup and selection?