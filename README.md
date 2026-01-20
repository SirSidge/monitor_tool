# monitor_tool

# What is this project?
    As the name suggests, it is a monitoring app. This app will run in the background on Windows checking what apps are currently running in the foreground. A running state will be updated depending on whether the app is productive/unproductive or other. The time spent is recorded to show how much time is spent on each state. An alarm is setup to go off when I've spent too much time being unproductive. You can add apps dynamically, when displaying the current processes and adding them to the relevant state. Your stats are stored locally so that you can have a daily/weekly/monthly/yearly overview.
# Goal
    The goal is to help me be more productive with my time. The alarm and force-closure of apps will push me to stop/reduce my unproductive time by preventing those 4+h long gaming sessions. I love stats, being able to store them will be very interesting for me to go over.

# Bugs
    1: 

# Polish
    1: 

# To Do
    1: ----- Unproductive calculator ----- 
        1.1: Daily time limit of 2h
        1.2: Weekly time limit of 18h
        1.3: Reset and/or Sleep button for above timer.
        1.4: Auto-close unproductive apps once time limit is reached
        1.5: Warning 30min before time limit/s are reached.

    2: ----- Productivity calculator ----- 
        2.1: Measure productive time ✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓

    3: ----- Single monitoring app ----- 
        3.1: Check if app is already running, if so prevent second iteration.

    4: ----- Implement AI -----
        4.1: Include AI to detect if an app (for example a new game) should be allocated to unproductive or not.
        4.2: Automatically add app name to the relevant list.

    5: ----- Inactive -----
        5.1: When there has been no activity on the peripherals for more than 5min (?) then change status to idle. ✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓

    6: ----- Display processes -----
        6.1: Ability to copy app name from display processes window
        6.2: Create display processes window. Shows current running apps.
        6.3: Add selected app to any of the statuses
    
    7: ----- Local storage -----
        7.1: Store data locally.
        7.2: Save data every minute(?) in case of crashes, minimising loss of data.
        7.3: Save data as app is closed. (on exit)
    
    8: ----- Display Stats -----
        8.1: Create button that will open a browser page.
        8.2: Upload the local data to the browser page (as needed? Or maybe all of it at once, cached?)
        8.3: Design browser page to display stats clearly and be interactive. See PowerBi for examples (but you can do better)


    ----- Misc -----
        What does the JSON file need to store?
        - Running totals: daily, weekly, monthly, and total
        - Time in statuses: Productive, Unproductive, Idle
        - What date and time events occured