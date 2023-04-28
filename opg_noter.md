---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.14.5
  kernelspec:
    display_name: base
    language: python
    name: python3
---

# opg_noter
## egen formuleringen af opgaven
- aflever i .txt  rum-tid positioner med usikkerhed i formatet `<time> <rebel> <x> <y> <z> <uncertainty>` for hver af nedenstående, og suppler med .py for modellen/algoritmen og evt. en fil med kommentarer/forklaringer:
    - rebel (ca 30)
    - tid (ca 1000)
    - hvor positioner er et sted i 1000 * 1000 * 1000
- rebeller rejser på unavngivne rumskibe med sine holdkammerater mellem stjerner og stjerneklustre. rebeller forlader ikke sit skib. rebeller udsender en af tre typer beskeder, som vi håber at bruge for at finde positionerne
    - NEA: næreste stjerne
    - COT: co-traveller
    - LOC: location
- bestræb nøjagtige og præcise svar, dvs. punkt estimater og err. 

## refleksioner
* For rebeller der ikke oplyser positionen, kan denne oplysning måske findes ved at se hvor deres rejsemakker befinder sig.
* Hvad fortæller næreste stjerne om lokationen?
* Hvis stjerner klumper sammen i clusters, hvad fortæller det så om rebellers missing position?
* Rebellernes rejser ikke er helt random, så kan vi estimere dem :)
* 
    * [](https://en.wikipedia.org/wiki/Training,_validation,_and_test_data_sets)

## baggrundsmateriale
1. start with `truth_plotter.ipynb` to get a feeling behind truth data by visualizing it.
2. `public_plotter.ipynb`: Parses the public rebel broadcasts and returns some dataframes you can use [I guess to create a model]. Also plots the location of the LOC ﬂavour of leaks for simple inspection as an example.
3. `grade_assignment.ipynb`: reads your solution, along with the truth file and provides a score. Very slow. If not using notebooks, you can also just call `grade_assignment()` directly in `rebel_decode.py`.
4. `rebel_decode.py`: The muscle power behind the notebooks. Feel free to extend or alter. 
5. eventually change dataframes layouts 

## hjælpe spørgsmål / delopgaver (may help in constructing your scored assignment)
- How many ships are there in the graded assignment?
- List all passengers of each ship in the graded assignment
- What type of leaks are most common?
- Are public message leak rates independent of time/position?
    - If not, can you determine the analytical function that govern the rates?
- We said rebel movements are not completely random. Is this true?

## noter
- opgavebeskrivelsen indeholder måske en fejl i linjen om `00??_public.txt` og `assignment_public.txt`
- public data synes at være træningsdata, imens truth/real data synes at være testdata
- opgaven kan givet vis laves i rebel decode
- `rebel_decode.py` indeholder grade_assignment, som kan være hurtigere og bedre
- `00??_truth.txt` indeholder 
    - WORLD LOG med forskellige antal
        - systemer (fx 4158) som hver har
            - location (0-1000 x 0-1000 x 0-1000)
            - nNeigh værdier (fx 28, 14)
            - navn (fx StarID_00017)
        - skibe (fx 4), som har forskellige værdier
            - shipID_00000
            - værdie
            - starID_
            - lokationer
            - værdi
        - rebeller (fx 33), som har forskellige værdier
            - RevelID_00000
            - navn
            - besked
            - ship_ID_
    - EVENT LOG, der beskriver
        - bevægelse / besked
        - ShipID_
        - RebelID_ og navn (hvis besked)
- `00_??public.txt` indeholder
    - tid (0-1000)
    - besked-type
    - navn
    - besked-indhold (navn/lokation/starID_)
- `sample_answer.txt` indeholder 1000 * rebelnavne i format `<time> <rebel> <x> <y> <z> <uncertainty>`
- `assignment_public.txt` indeholder ~ `00??_public.txt`
- brug evt. `make_dummy_answer` som returnerer `sample_answer.txt` til at lave et svar
- `REBS` er ikke df, men dict med nested dicts. 
