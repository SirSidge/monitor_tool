# monitor_tool

# Bugs
1: Once elapsed has reached 2h (7200), it will keep displaying that 2h was reached regardless of the state of POE.

# Polish
1: App lags heavily when you show it after a few hours. Probably a solution is to stop updating the displayed psutil window while it is minimised.

# Features
1: ----- Unproductive calculator ----- 
1.1: Daily time limit of 2h
1.2: Weekly time limit of 18h
1.3: Reset and/or Sleep button for above timer.
1.4: Auto-close unproductive apps
1.5: Ability to add app from the "display processes" window to any status.

2: ----- Productivity calculator ----- 
2.1: Measure productive time ✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓

3: ----- Find Apps ----- 
3.1: Search for all apps currently running
3.2: Add apps to 'productivity_status'

4: ----- Single monitoring app ----- 
4.1: Check if app is already running, if so prevent second iteration.

5: ----- Implement AI -----
5.1: Include AI to detect if an app (for example a new game) should be allocated to unproductive or not.

6: ----- Inactive -----
6.1: When there has been no activity on the peripherals for more than 5min (?) then change status to idle. ✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓


----- Misc -----
What does the JSON file need to store?
- Running totals: daily, weekly, monthly, and total
- Time in statuses: Productive, Unproductive, Idle
- What date and time events occured