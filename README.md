# monitor_tool

# Bugs
1: Once elapsed has reached 2h (7200), it will keep displaying that 2h was reached regardless of the state of POE.

# Features
1: ----- Unproductive calculator ----- 
1.1: Daily time limit of 2h
1.2: Weekly time limit of 18h
1.3: Reset and/or Sleep button for above timer.
1.4: Auto-close unproductive apps

2: ----- Productivity calculator ----- 
2.1: Measure productive time

3: ----- Find Apps ----- 
3.1: Search for all apps currently running
3.2: Add apps to 'productivity_status'

4: ----- Single monitoring app ----- 
4.1: Check if app is already running, if so prevent second iteration.


----- Misc -----
What does the JSON file need to store?
- Running totals: daily, weekly, monthly, and total
- Time in statuses: Productive, Unproductive, Idle
- What date and time events occured


Can I have a C-code script running for my python app? I don't see how I can see what app is in the foreground using python, but maybe with C I can?