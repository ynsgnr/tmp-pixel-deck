# stage5

FreeCAD 1.0.2. Units: mm, degrees. Rebuild: `FreeCADCmd build_dock.py`.

## Parameters

| Name | Value | Use |
|---|---|---|
| BarY | 1.20 mm | Derived. Dock bar face near the case. |
| BaseIn | 0.60 mm | Base slab overlap under the top wall. |
| CapH | 5.80 mm | Magnet cap height on the flat part. |
| CapW | 21.00 mm | Derived. Square size of cap, column and ear. |
| CheekIn | 0.30 mm | Cheek overlap into the side wall. |
| CheekL | 20.00 mm | Cheek length down each case side wall. |
| CheekT | 3.00 mm | Dock bar cheek thickness outside each case side wall. |
| Clearance | 0.20 mm | Gap per side between mating printed parts. |
| ColTop | 4.70 mm | Derived. Column top above the plate top. |
| EarT | 7.00 mm | Derived. Dock bar height, equal to the case height. |
| EarY | 11.70 mm | Derived. Post axis distance from the keyboard top wall. |
| EdgeR | 2.00 mm | Corner radius of columns, caps and ears in plan. |
| HeadBoreD | 5.40 mm | Derived. Collar counterbore diameter. |
| HeadBoreDepth | 1.70 mm | Derived. Collar counterbore depth. |
| KbFloorZ | 1.20 mm | Measured: top wall openings start above this height. |
| KbH | 7.00 mm | Measured: BBQ10 bottom case height. |
| KbTabY | 1.00 mm | Measured: top-edge tabs protrude this far past the wall. |
| KbTabZ | 2.00 mm | Measured: tab bottom above the case floor face. |
| KbW | 71.81 mm | Measured: BBQ10 bottom case width. |
| KinkAngle | 17.50 ° | Kink bevel angle for the landscape position. |
| KinkRowY | -7.06 mm | Derived. Kink magnet row Y on the cap. |
| KinkY | -3.20 mm | Derived. Kink line Y on the cap. |
| LipH | 3.00 mm | Corner lip height above the plate. |
| LipLen | 15.00 mm | Corner lip length along each phone edge from the corner. |
| LipT | 2.00 mm | Corner lip wall thickness. |
| MagD | 5.00 mm | Magnet diameter. |
| MagEdge | 1.40 mm | Wall between a magnet pocket and the cap side. |
| MagT | 2.00 mm | Magnet thickness. |
| MagWeb | 1.00 mm | Wall between two magnet pockets. |
| MouthChamfer | 0.80 mm | Chamfer at the socket mouth. |
| PhoneL | 157.00 mm | Phone in Pixelsnap case, length. |
| PhoneR | 10.00 mm | Phone corner radius in plan. |
| PhoneT | 10.00 mm | Phone in Pixelsnap case, thickness. |
| PhoneTopY | -12.70 mm | Derived. Y of the phone edge near the columns. |
| PhoneW | 77.00 mm | Phone in Pixelsnap case, width. |
| PinBoreD | 3.90 mm | Derived. Pin bore in the column and the post. |
| PinD | 3.50 mm | Metal pin (banana male) contact diameter. |
| PinHeadD | 5.00 mm | Metal pin collar diameter. |
| PinHeadL | 1.50 mm | Metal pin collar length. |
| PinShankL | 6.00 mm | Metal pin length below the collar. |
| Pitch | 6.40 mm | Derived. Magnet pitch. |
| PlateCornerR | 3.00 mm | Plate corner radius at the column end. |
| PlateT | 4.40 mm | Mount plate thickness. |
| PlateW | 81.40 mm | Derived. Plate width. |
| PocketD | 5.40 mm | Derived. Magnet pocket diameter. |
| PocketDepth | 2.20 mm | Derived. Magnet pocket depth. |
| PostChamfer | 0.40 mm | Chamfer at the post tip. |
| PostFillet | 0.60 mm | Fillet radius at the post base. |
| PostL | 5.70 mm | Derived. Post length above the ear. |
| PostOD | 8.00 mm | Keyboard post outer diameter. |
| PostTipGap | 0.30 mm | Gap between the post tip and the socket ceiling. |
| PostX | 25.41 mm | Derived. Column and post axis distance from the centre line. |
| RingDepth | 1.00 mm | Ring recess depth in the plate top. |
| RingID | 46.00 mm | MagSafe steel ring inner diameter. |
| RingOD | 54.00 mm | MagSafe steel ring outer diameter. |
| RingOffset | 0.00 mm | Ring centre offset from the phone centre along +Y. |
| RingY | -91.20 mm | Derived. Y of the ring centre. |
| ScreenGap | 0.50 mm | Cap top above the screen surface. |
| SkinT | 0.60 mm | Skin between a magnet and the mating face. |
| SlitBottom | 1.00 mm | Uncut post length above the ear. |
| SlitW | 0.80 mm | Width of the two slits in each post. |
| SlotLip | 0.30 mm | Slot entry is this much narrower per side; the magnet snaps past it. |
| SlotLipL | 1.00 mm | Length of the narrow slot entry. |
| SocketD | 8.40 mm | Derived. Socket diameter. |
| SocketDepth | 6.00 mm | Column socket depth from the plate bottom. |
| TongueL | 20.00 mm | Tongue length past the ears. It bears on the plate bottom in position 1. |

## Decisions

| ID | Decision | Reason |
|---|---|---|
| D1 | Z is up and normal to the screen. Origin: X on the phone centre line, Y on the line through the ColL and ColR axes, Z on the plate top face. | The column axes are the mating datum for the keyboard posts. |
| D2 | The phone extends to -Y. In position 1 the keyboard extends to +Y. | Position 1 is the keyboard continuous with the screen. |
| D3 | Clearance is 0.2 mm per side. No press fits. | User: FDM printer, 0.2 mm per side, parts are assembled. |
| D4 | Method: one VarSet, one Body per part in one Std Part. No master sketch. | All interfaces are Params expressions, so a master sketch adds no data. |
| D5 | The keyboard Body starts from the BBQ10 bottom case STEP (MIT licence). | The user STL is not a closed solid. The STEP is the same case without the old posts. |
| D6 | Magnets are 5 mm diameter x 2 mm, poles on the flat faces, in a 3x3 array. | User measurements. Magnet size drives the cap, column and ear size. |
| D7 | Metal pin: banana male 3.5 mm, with an assumed 5 mm x 1.5 mm collar. Change PinHeadD, PinHeadL and PinShankL to the real part. | Only the 3.5 mm diameter is known. |
| D8 | Cap and column are 21.00 mm square. | This is the smallest square that holds the 3x3 magnet array. |
| D9 | Assembly: slide 8 magnets into the cap side slots past the lips. Put the centre magnet in from the bottom. Push each metal pin into its column from the top. Glue each cap on its column; the cap closes the centre pocket and holds the pin. | User: open pockets let magnets jump out. Slots hold each magnet apart under a skin. |
| D10 | Magnet poles on the cap top, rows from +Y to -Y: N S N, N S N, N N N. The N N N row is on the kink bevel. Put each ear magnet to attract the cap magnet below it. | User pattern NSN/NSN/NNN. An ear has 5 magnets: the bar blocks the other slot exits. |
| D11 | Print all three parts as modelled with no supports: slots bridge 5.4 mm under a skin. | The bar and the cap stand on flat bottoms. Posts and columns are vertical. |
| D14 | Keyboard side: a full-height dock bar with 3 mm cheeks on both side walls and a tongue under the plate. No thin neck. | User: the phone hangs on this joint in position 1, so the torque is large. |
| D15 | In position 1 the plate bears on the bar and tongue. Posts take the pull-out force; only the banana plugs and slits hold them in the socket. | Open question: add magnets or a latch between plate bottom and tongue if the posts pull out. |
| D12 | Position 2: the keyboard floor rests on the cap tops at Z = 10.50, 0.50 mm above the screen. The ears are at +Y, so the keys are turned 180 deg from position 1. | Open question: confirm the keyboard direction in position 2. |
| D13 | Position 3: the keyboard edge rests on the plate 36.5 mm from the column axes. The kink row is 30.9 mm up the keyboard floor. The case has no magnets there. | Open question: magnets in the keyboard for position 3 (user: focus on the posts first). |

## Steps

| ID | Action | Reason | Result |
|---|---|---|---|
| S1 | Make the parameters. | All dimensions come from Params. | no geometry change |
| S2 | Check the interface stack from the parameters. | Wall and engagement sizes must be printable before modelling. | no geometry change |
| S3 | Pad the plate down from Z = 0. | The phone back rests on Z = 0. | PhoneMount vol +47856.7 mm3, size 81.40x142.40x4.40 |
| S4 | Pad ColL and ColR up from the plate. | Columns stand outside the phone, at +Y. | PhoneMount vol +4113.1 mm3, size 81.40x142.40x9.10 |
| S5 | Pad the two corner lips. | The lips locate the phone corners (R = PhoneR). | PhoneMount vol +331.1 mm3, size 81.40x142.40x9.10 |
| S6 | Cut the ring recess in the plate top. | A stick-on MagSafe ring holds the phone. | PhoneMount vol -691.2 mm3, size 81.40x142.40x9.10 |
| S7 | Cut the post sockets up from the plate bottom. | Posts enter from below the mount. | PhoneMount vol -665.0 mm3, size 81.40x142.40x9.10 |
| S8 | Cut the pin bores and collar counterbores from the column top. | The pin goes in from the top. Bore = PinD + 2 x Clearance. | PhoneMount vol -111.3 mm3, size 81.40x142.40x9.10 |
| S9L | Pad the MagnetCapL block. | The cap covers the column top. | MagnetCapL vol +2537.9 mm3, size 21.00x21.00x5.80 |
| S10L | Cut the kink bevel on the -Y side of MagnetCapL. | The keyboard rests on the bevel at KinkAngle in the landscape position. | MagnetCapL vol -172.7 mm3, size 21.00x21.00x5.80 |
| S11L | Cut eight magnet slots and the centre pocket in MagnetCapL. | Each magnet slides in from the nearest side, under a skin. The kink row exits at -Y. | MagnetCapL vol -631.1 mm3, size 21.00x21.00x5.80 |
| S9R | Pad the MagnetCapR block. | The cap covers the column top. | MagnetCapR vol +2537.9 mm3, size 21.00x21.00x5.80 |
| S10R | Cut the kink bevel on the -Y side of MagnetCapR. | The keyboard rests on the bevel at KinkAngle in the landscape position. | MagnetCapR vol -172.7 mm3, size 21.00x21.00x5.80 |
| S11R | Cut eight magnet slots and the centre pocket in MagnetCapR. | Each magnet slides in from the nearest side, under a skin. The kink row exits at -Y. | MagnetCapR vol -631.1 mm3, size 21.00x21.00x5.80 |
| S12 | Load the BBQ10 bottom case into the keyboard frame KB. | KB: floor face at z = 0, keys at +z, top wall face at y = 0, centred on x. | Keyboard vol +6147.3 mm3, size 71.81x51.58x7.00 |
| S13 | Pad the base slab, then the dock bar with cheeks and tongue. | Phone torque goes through a full-height bar into both case side walls. | Keyboard vol +16621.4 mm3, size 77.81x92.78x7.00 |
| S15 | Pad the posts and cut the pin bore through post and ear. | Bore = PinD + 2 x Clearance. | Keyboard vol +269.6 mm3, size 77.81x92.78x12.70 |
| S16 | Cut two slits across each post. | The slits let the post flex to fit the socket. | Keyboard vol -30.9 mm3, size 77.81x92.78x12.70 |
| S17 | Cut five magnet slots in each ear, under a skin on the bar bottom. | The +y row exits at +y, the outer column at the side. Bar and tongue block the rest. | Keyboard vol -868.4 mm3, size 77.81x92.78x12.70 |
| S18 | Place the keyboard in position 1 and add the reference bodies. | Phone and metal pins are bought parts, for fit checks only. | Keyboard vol -0.0 mm3, size 77.81x92.78x12.70; Phone vol +120031.6 mm3, size 77.00x157.00x10.00; MetalPinL vol +87.2 mm3, size 5.00x5.00x7.50; MetalPinR vol +87.2 mm3, size 5.00x5.00x7.50 |
| S19 | Check the fits in position 1. | Each joint keeps Clearance or touches by design. | no geometry change |
| S20 | Chamfer the socket mouths. | A lead-in guides the post into the socket. | PhoneMount vol -18.0 mm3, size 81.40x142.40x9.10 |
| S21 | Fillet the post bases and chamfer the post tips. | The fillet is the post support. The chamfer is a lead-in. | Keyboard vol +0.4 mm3, size 77.81x92.78x12.70 |
| S22 | Export the printed parts in their own frames. | Print MagnetCap twice. | no geometry change |
