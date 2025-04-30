## Data Processing

### Processing Steps

1. **Datetime Assignment:** The original event table contains the match identifier, the match period (e.g., 1H for the first half, 2H for the second half, E1 for first extra time, E2 for second extra time, and P for penalty time), and the timestamp in seconds indicating when the event occurred. The match start time, recorded in the match table, is used to derive the event's absolute datetime by adding the event's seconds to the match start time.  
   Since the timer resets at the start of each period, the processing tracks the datetime of the last event and recalculates the datetime by adding the new period’s seconds.

2. **Event and Entity Table Cleaning:** The event and entity tables are cleaned and formatted as described in subsequent sections.

3. **Position Processing:** Position data is processed according to the details provided in [area processing](#area-processing) section.


### Area Processing
Position areas and zones are derived from the original dataset, which contains the initial and final positions of each event on the x and y axes. These positions are represented as integer pairs in the range [0, 100], indicating the percentage distance from the attacking team's left corner. The data processing method is illustrated in Figure 1.  
Notably, if x or y values correspond to 0 or 100, the area is set as *out of the field*.

![Soccer Field Area Processing](/docs/imgs/field-processing.png)
**Figure 1:** Soccer field area processing method based on x and y percentages.

