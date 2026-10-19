---
name: freecad-parametric
description: Builds and edits parametric FreeCAD models by Python script (PartDesign bodies, constrained sketches, VarSet parameters, STEP/STL export), checking and tracing each stage. Use when the user wants a part or fitted multi-part design in FreeCAD, a .FCStd file changed, or a printable enclosure, bracket, lid or mount modelled parametrically.
---

# FreeCAD parametric modelling

Goal: a model that the user changes with a few named parameters. Units: mm and degrees.

## Setup

1. Print `App.Version()`. Stable is 1.0 or 1.1. Development builds use year numbers (26.x). If a call fails, examine the installed API with `dir(obj)` or `obj.PropertiesList`. Correct the call one time. Do not guess a second time.
2. Run code with `FreeCADCmd script.py` or a FreeCAD MCP tool. If you cannot run FreeCAD, tell the user and give the scripts. Do not report a result that you did not see.
3. New model: copy `templates/base_part.py` and set `SKILL_DIR` to the folder of this skill. One script builds the full document. Edit the script and run it again. Do not change a live document.
4. Existing `.FCStd`: open it and list its tree and parameters. Make the smallest change.
5. `from fc import *` gives all helpers. Run them. Do not read their source. `help(name)` shows the arguments.

## Method

State the method in one sentence.

| Task | Method |
|---|---|
| One prismatic part | PartDesign Body: sketch on the Body's origin plane, Pad/Pocket, dress-ups last |
| Several parts that fit together | One VarSet + one master sketch; one Body per part in a Std Part; `Clearance` parameter |
| Moving parts | Script the parts; the user places Assembly joints in the GUI (no stable joint API) |
| Organic shape | Part module (`Part.make*`, booleans), or tell the user that PartDesign is a poor fit |

## Rules

- Put each dimension in one `App::VarSet` as a typed property (`App::PropertyLength`, `App::PropertyAngle`, `App::PropertyInteger`) with a one-line doc string. Drive geometry with expressions, not copied numbers.
- Mating size = nominal + `Clearance`. Ask for the printer. Start at 0.15–0.5 mm per side and recommend a fit test print.
- Get planes from the Body that you build (`body.Origin.OriginFeatures`, Role `XY_Plane`), not from `doc.XY_Plane`.
- Attach sketches only to origin planes or datum planes on them, not to generated faces or edges. A part refers to parameters and the master sketch, not to faces of other parts. Use SubShapeBinders on sketches only.
- A Body is one solid. Add fillets and chamfers last, on names from `faces()` or `edges()`, not a fixed `"Edge7"`.
- Sketch indices: geometry from 0; point 1 start, 2 end, 3 centre; root point `(-1, 1)`; axes `-1` (X) and `-2` (Y). Add Horizontal, Vertical, Equal and Symmetric before dimensions. Rename a constraint before you set its expression. Do not use unit names (`A`, `mol`) as constraint names.
- Symmetric pad: `SideType = "Symmetric"` if the property exists, else `Midplane = True`.
- Do not use `autoRemoveRedundants()`. It deletes constraints.

## Spatial: measure, do not imagine

Do not calculate orientation or position in your head. Measure it. Each check prints one line. A failed check makes `report` print `ISSUES`, and the stage stops.

1. **Frame.** In stage 1, record the frame with `decide`: Z up, origin at a named datum, front −Y, right +X, top +Z. After that, use axes and signed values, not "left" or "above".
2. **Orientation.** After you attach a sketch, `axes(sk)` prints its x, y and normal. Change `Reversed` or `SideType` only after `expect` shows the direction of growth.
3. **Prediction.** Before the run, write `expect(obj, size=(x,y,z), lo=..., volume=...)` from the parameters. Do not copy measured values into it. Tolerance: 0.01 mm on size, 0.1 % on volume.
4. **Relations.** `on_top(a, b)`, `centred(a, b, "xy")`, `fits(a, b, clearance)`, `solid_at(a, p)`, and `solid_at(a, p, solid=False)` for holes. For other relations, use `spec(name, condition, detail)`.
5. **Selection.** `faces(pad, normal="+Z", extreme="max")` and `edges(pad, direction="Z", where=lambda c: c.z > 5)` return `FaceN`/`EdgeN` names and print what they found. Examine that output before you use the names.
6. **Mating.** Put the origin of each part at its mating point. Position the part with one `Placement` from parameters.
7. **Joints.** Renders do not show sub-mm gaps. Accept a joint on `fits` and sections, not on the image.

## Trace

The script is the record. Do not write other documentation.

- Put each build step and its checks in `with step("S3", "Cut the cable hole in the rear wall.", "The cable exits at +Y."):`. The step prints one line: volume change, size and failures.
- Record each assumption or choice with `decide("D2", "Clearance is 0.2 mm per side.", "FDM printer.")`.
- `checkpoint` writes `TRACE.md` with the parameters, decisions and steps.

## Writing (ASD-STE100)

Use this style for comments, docstrings, step, decision and parameter text, and messages to the user.

- An instruction has 20 words or fewer. A description has 25 words or fewer. Write one instruction in each sentence. Use the active voice.
- Use one word for one thing: part, Body, feature, sketch, parameter, clearance, frame, stage, step.
- A comment gives a step ID or a reason that the code cannot show. It does not repeat the code.
- To the user: before a stage, write one sentence about the next action. After a stage, give the outputs and open questions only. Do not explain FreeCAD unless the user asks. Do not summarize code or output that the user can read. Do not use filler, praise or apology.

## Stages

1 requirements and method (sizes, fits, printer, what moves; ask only questions that change the design) → 2 master sketch → 3 one part at a time → 4 fit check → 5 dress-ups and export. Skip stages that do not apply. A single simple part uses stages 1, 3 and 5.

End each stage with `checkpoint(doc, N, pairs=[(a, b, clearance)], cuts=[("z", at)])`. It runs `report`, renders four views, cuts one section per joint, prints placements if there is more than one part, writes `TRACE.md` and saves `stageN.FCStd`. `report` must print `OK`. Examine the images yourself.

- **Interactive (default):** show the images, the `report`, step and placement lines, new decisions and open questions. Wait for approval. Users find wrong-side errors (a handle inside the cup) that checks miss.
- **Autonomous** (the user said go ahead, or nobody can answer): do all stages, record assumptions with `decide`, and report one time at the end.

Last stage: run `stress(doc, Params, ["Width", ...])` on the main dimensions. Then export with `shape.exportStep(path)` and `shape.exportStl(path, 0.05)`.

If a stage fails two times for the same reason, stop. Propose a different construction.
