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
| KbCornerR | 12.35 mm | Measured: case bottom corner radius in plan. |
| KbDepth | 50.58 mm | Measured: case depth from the top wall face to the bottom edge. |
| KbFloorZ | 1.20 mm | Measured: top wall openings start above this height. |
| KbH | 7.00 mm | Measured: BBQ10 bottom case height. |
| KbLen | 92.78 mm | Derived. Keyboard end-to-end length. |
| KbScrewHeadD | 4.20 mm | Measured: bottom screw countersink diameter. |
| KbScrewX | 31.05 mm | Measured: bottom screw hole distance from the centre line. |
| KbScrewY | -42.38 mm | Measured: bottom screw hole Y. |
| KbTabY | 1.00 mm | Measured: top-edge tabs protrude this far past the wall. |
| KbTabZ | 2.00 mm | Measured: tab bottom above the case floor face. |
| KbW | 71.81 mm | Measured: BBQ10 bottom case width. |
| KinkAngle | 8.22 ° | Derived. Position 3: right triangle of keyboard length and column height. |
| KinkRowY | -7.26 mm | Derived. Kink magnet row Y: under the pad edge row in position 3. |
| KinkY | -3.20 mm | Derived. Kink line Y on the cap. |
| LipH | 3.00 mm | Corner lip height above the plate. |
| LipLen | 15.00 mm | Corner lip length along each phone edge from the corner. |
| LipT | 2.00 mm | Corner lip wall thickness. |
| LobeR | 0.50 mm | Radius of each lobe rib. |
| MagD | 5.00 mm | Magnet diameter. |
| MagEdge | 1.40 mm | Wall between a magnet pocket and the cap side. |
| MagT | 2.00 mm | Magnet thickness. |
| MagWeb | 1.00 mm | Wall between two magnet pockets. |
| MouthChamfer | 0.80 mm | Chamfer at the socket mouth. |
| PadT | 2.80 mm | Derived. Magnet pad thickness. |
| PadY | -40.08 mm | Derived. Magnet pad centre Y. |
| PhoneL | 157.00 mm | Phone in Pixelsnap case, length. |
| PhoneR | 10.00 mm | Phone corner radius in plan. |
| PhoneT | 10.00 mm | Phone in Pixelsnap case, thickness. |
| PhoneTopY | -12.70 mm | Derived. Y of the phone edge near the columns. |
| PhoneW | 77.00 mm | Phone in Pixelsnap case, width. |
| PinBoreD | 3.90 mm | Derived. Column pin bore. The spring passes it freely. |
| PinD | 2.00 mm | Metal pin nominal diameter (2 mm banana). The post bore grips it. |
| PinHeadD | 5.00 mm | Assumed: metal pin base diameter. |
| PinHeadL | 1.50 mm | Assumed: metal pin base length. |
| PinShankL | 6.00 mm | Assumed: metal pin contact length below the base. |
| PinSpringD | 3.50 mm | Metal pin spring diameter at rest, in the middle of the contact. |
| Pitch | 6.40 mm | Derived. Magnet pitch. |
| PlateCornerR | 3.00 mm | Plate corner radius at the column end. |
| PlateT | 4.40 mm | Mount plate thickness. |
| PlateW | 81.40 mm | Derived. Plate width. |
| PocketD | 5.40 mm | Derived. Magnet pocket diameter. |
| PocketDepth | 2.20 mm | Derived. Magnet pocket depth. |
| PostBoreD | 3.60 mm | Measured from the fitted test post: bore for the banana plug. |
| PostChamfer | 0.40 mm | Chamfer at the post tip. |
| PostFillet | 0.60 mm | Fillet radius at the post base. |
| PostL | 5.70 mm | Derived. Post length above the ear. |
| PostLobeD | 3.28 mm | Measured from the fitted test post: diameter across the 3 lobes. |
| PostLobeL | 2.00 mm | Measured from the fitted test post: lobe length at the bore mouth. |
| PostOD | 8.00 mm | Keyboard post outer diameter. |
| PostReliefD | 4.14 mm | Measured from the fitted test post: relief between the lobes. |
| PostTipGap | 0.30 mm | Gap between the post tip and the socket ceiling. |
| PostX | 25.41 mm | Derived. Column and post axis distance from the centre line. |
| RingDepth | 1.00 mm | Ring recess depth in the plate top. |
| RingID | 46.00 mm | MagSafe steel ring inner diameter. |
| RingOD | 54.00 mm | MagSafe steel ring outer diameter. |
| RingOffset | 0.00 mm | Ring centre offset from the phone centre along +Y. |
| RingY | -91.20 mm | Derived. Y of the ring centre. |
| ScreenGap | 0.50 mm | Cap top above the screen surface. |
| ScrewHoleD | 4.60 mm | Derived. Screw access hole through the pad. |
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
| D7 | Metal pin: 2 mm banana male. Its spring is 3.5 mm at rest, in the middle of the contact. The base is not measured: PinHeadD, PinHeadL and PinShankL are assumptions. | User: 2 mm plug, 3.5 mm where it flexes, base not in the measurement. |
| D8 | Cap and column are 21.00 mm square. | This is the smallest square that holds the 3x3 magnet array. |
| D9 | Assembly: slide 8 magnets into the cap side slots past the lips. Put the centre magnet in from the bottom. Push each metal pin into its column from the top. Glue each cap on its column; the cap closes the centre pocket and holds the pin. | User: open pockets let magnets jump out. Slots hold each magnet apart under a skin. |
| D10 | Magnet poles on the cap top, rows from +Y to -Y: N S N, N S N, N N N. The N N N row is on the kink bevel. Put each pad magnet to attract the cap magnet below it in position 2. | User pattern NSN/NSN/NNN. A pad has 6 magnets: the screw hole and the case corner take two places, the centre has no free side. |
| D11 | Print all three parts as modelled with no supports: slots bridge 5.4 mm under a skin. | The bar and the cap stand on flat bottoms. Posts and columns are vertical. |
| D14 | Keyboard side: a full-height dock bar with 3 mm cheeks on both side walls and a tongue under the plate. No thin neck. | User: the phone hangs on this joint in position 1, so the torque is large. |
| D15 | In position 1 the plate bears on the bar and tongue. The banana plugs hold the posts in the sockets. | User: the banana plug is good enough for position 1. |
| D12 | Position 2: the keyboard lies keys up on the phone, top edge toward the phone top. Its corner pads rest on the caps; the floor is 3.3 mm above the screen. | User: the keys must be usable on the phone. |
| D13 | Position 3: KinkAngle = 8.22 deg from the right triangle of the keyboard length (92.8 mm) and the column height (10.5 mm). The pad edge row lands on the kink row. | User: the angle comes from this triangle. |
| D16 | The post bore copies the fitted test post: 3.6 mm bore, 3 lobes at 3.28 mm over the last 2 mm, 4.14 mm relief. The post OD stays 8 mm for strength. | User: the test post fits the banana plug with its flex spaces and sizes. |

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
| S8 | Cut the pin bores and collar counterbores from the column top. | The pin goes in from the top. Bore = PinSpringD + 2 x Clearance. | PhoneMount vol -111.3 mm3, size 81.40x142.40x9.10 |
| S9L | Pad the MagnetCapL block. | The cap covers the column top. | MagnetCapL vol +2537.9 mm3, size 21.00x21.00x5.80 |
| S10L | Cut the kink bevel on the -Y side of MagnetCapL. | The keyboard rests on the bevel at KinkAngle in the landscape position. | MagnetCapL vol -79.2 mm3, size 21.00x21.00x5.80 |
| S11L | Cut eight magnet slots and the centre pocket in MagnetCapL. | Each magnet slides in from the nearest side, under a skin. The kink row exits at -Y. | MagnetCapL vol -609.8 mm3, size 21.00x21.00x5.80 |
| S9R | Pad the MagnetCapR block. | The cap covers the column top. | MagnetCapR vol +2537.9 mm3, size 21.00x21.00x5.80 |
| S10R | Cut the kink bevel on the -Y side of MagnetCapR. | The keyboard rests on the bevel at KinkAngle in the landscape position. | MagnetCapR vol -79.2 mm3, size 21.00x21.00x5.80 |
| S11R | Cut eight magnet slots and the centre pocket in MagnetCapR. | Each magnet slides in from the nearest side, under a skin. The kink row exits at -Y. | MagnetCapR vol -609.8 mm3, size 21.00x21.00x5.80 |
| S12 | Load the BBQ10 bottom case into the keyboard frame KB. | KB: floor face at z = 0, keys at +z, top wall face at y = 0, centred on x. | Keyboard vol +6147.3 mm3, size 71.81x51.58x7.00 |
| S13 | Pad the base slab, then the dock bar with cheeks and tongue. | Phone torque goes through a full-height bar into both case side walls. | Keyboard vol +16621.4 mm3, size 77.81x92.78x7.00 |
| S15 | Pad the posts and cut the pin bore through post and ear. | Bore sizes copy the test post that fits the banana plug. | Keyboard vol +305.0 mm3, size 77.81x92.78x12.70 |
| S16 | Cut two slits across each post. | The slits let the post flex to fit the socket. | Keyboard vol -31.5 mm3, size 77.81x92.78x12.70 |
| S17 | Pad two magnet pads under the bottom corners and cut the screw access holes. | Pads meet the caps in position 2 and the kink row in position 3. | Keyboard vol +2193.2 mm3, size 77.81x92.78x15.50 |
| S18a | Cut six magnet slots in each pad, under a skin on the pad bottom. | Each magnet slides in from a pad side and snaps past the lip. | Keyboard vol -866.3 mm3, size 77.81x92.78x15.50 |
| S18 | Place the keyboard in position 1 and add the reference bodies. | Phone and metal pins are bought parts, for fit checks only. | Keyboard vol -0.0 mm3, size 77.81x92.78x15.50; Phone vol +120031.6 mm3, size 77.00x157.00x10.00; MetalPinL vol +48.3 mm3, size 5.00x5.00x7.50; MetalPinR vol +48.3 mm3, size 5.00x5.00x7.50 |
| S19 | Check the fits in position 1. | Each joint keeps Clearance or touches by design. | no geometry change |
| S20 | Chamfer the socket mouths. | A lead-in guides the post into the socket. | PhoneMount vol -18.0 mm3, size 81.40x142.40x9.10 |
| S21 | Fillet the post bases and chamfer the post tips. | The fillet is the post support. The chamfer is a lead-in. | Keyboard vol +0.4 mm3, size 77.81x92.78x15.50 |
| S22 | Export the printed parts in their own frames. | Print MagnetCap twice. | no geometry change |
