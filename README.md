# Soccer Match Event Logs for Process Mining

This repository contains the event logs processed from a soccer match event dataset.
The logs have been processed for creating Event Knowledge Graphs (EKGs).

>  Reference Dataset and Literature: https://www.kaggle.com/datasets/aleespinosa/soccer-match-event-dataset/data & [[paper]](https://figshare.com/collections/Soccer_match_event_dataset/4415000/5).

>  More information about the processing steps can be found [here](/docs/data_processing.md).

## Object-Centric Event Log Information

### Event Attributes

- **eventId:** Unique identifier for each event.
- **activity:** Describes the type of event.
- **time:** The computed datetime of the event.
- **match:** Identifier of the corresponding match.
- **team:** Identifier of the team associated with the event.
- **player:** Identifier of the player involved in the event.
- **position_init:** Identifier of the event's position.

### Team Attributes

- **entityId:** Unique team identifier assigned by Wyscout (refer to Wyscout documentation at [https://apidocs.wyscout.com/](https://apidocs.wyscout.com/)).
- **name:** Official or commonly used team name.
- **city:** City where the team is based.
- **country:** Country code of the team’s location.

### Player Attributes

- **entityId:** Unique player identifier assigned by Wyscout (refer to Wyscout documentation at [https://apidocs.wyscout.com/](https://apidocs.wyscout.com/)).
- **name:** Short name of the player.
- **team:** Identifier of the player’s club team.
- **nationalTeam:** Identifier of the player’s national team, if applicable.
- **role:** Player’s role abbreviation: DEF (Defender), MID (Midfielder), FWD (Forward), GKP (Goalkeeper).
- **birthYear:** Player’s year of birth.

### Position Attributes

- **entityId:** Unique identifier for the field area.
- **area:** General

## Event Log Folder Structure

Each league is organized into its own folder. Within this folder, the `entities` subfolder holds all tables containing object attributes, while the `events.csv` file stores the event data, while `events_with_area.csv` contains the event data processed to record also the position entity.

```
    📁 {league}
    ├── 📁 entities
    │   ├── 📄 position.csv
    │   ├── 📄 matches.csv
    │   ├── 📄 players.csv
    │   └── 📄 teams.csv
    |   📄 events.csv
    └── 📄 events_with_position.csv
```
