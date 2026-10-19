# User notes — BBQ10 phone/keyboard mount

Raw prompts, corrections, and measurements only. No design decisions or interpretations included.

## Initial issue list

- Column holes too small for the metal pin to go through
- New prototype keyboard didn't fit well, probably a bad print — needs a slit and support added
- Depth of the top keyboard column insert is good, but circumference needs to be bigger; the magnet holder insert needs to be smaller to go inside the metal pin
- Top magnets for kink mount should be next to the LED or switch line — a bit higher
- Kink magnet holes should be on the edge, not the bottom — only the center should be on the bottom
- Fix the phone corner dimensions
- "Kink" = the angle for landscape mode with magnet attachment
- Columns support the phone's positioning of the keyboard
- Keyboard reference: https://github.com/ZitaoTech/BBQ10_Keyboard_Pro
- Notes are rough, take with a grain of salt
- Want interface sketches between Pixel 10 Pro + Pixelsnap (MagSafe) case, portrait and landscape, mounting plate and columns
- Mounting columns house the magnet and a metal pin that inserts into the keyboard side for full support
- Magnets are on the screen/hardware keyboard only; pins are under the phone mount only
- 3 positions wanted: continuous with the screen, on the phone and the screen, and landscape/keyboard angled into the space between phone and columns
- Keyboard extending beyond the columns in some positions is OK
- Magnet array: 3x3, pattern NSN / NSN / NNN
- Should be powerful enough to hold in place

## Workspace instruction

- Use this folder and workspace to save changes. Do not use the old project folder.

## Pin/connector measurements and clarification

- Metal pin is inside the hole. The keyboard also has a circular pin with space inside. So it's 2 pins "docking" into each other. The metal pin lives inside another hole in the mount column, it's not exposed outside.
- Banana connector male plug outer diameter: 2mm or 3.5mm
- Only the male is used inside a circular housing. Female part is fully plastic and enters into the housing and accepts the banana plug inside.
- Correction: No press fit. We will assemble it. The pin goes into the column from the other side, and the magnet housing goes on top as a pin to hold it in place.
- The plug needs to fit inside the metal pin, give some tolerance into the pin.
- Confirmed: pin lives in the Column, socket is in the Post.

## Magnet measurements

- Neodymium magnets, 5mm x 2mm, circular
- Magnet caps needs to be 3x3 kinked array, not just a single magnet.
- It's the whole 3x3 array. We need 2 of these, one for each column. On top of the pin mounting.
- Same piece as the MagnetCap.
- Correction: Why are they circumferential? The magnets I have are cylinders with N and S on the circular top and bottom.

## Phone/case measurements

- Pixel 10 Pro with Pixelsnap case on, outer dimensions: 157 x 77 x 10mm
- Corner radius: 10mm

## Kink angle

- Calculated as 17.5°, but may need adjustment once mounting hardware is added — must be configurable.

## Printer/tolerance

- FDM printer, 0.2mm clearance per side.

## LED/button correction

- You measured LED holes wrong. Those are buttons. Try it on the Left Y axis.
- Bottom case holes for LEDs on the sides. Use that as reference. Corner radius is 10mm.
- Later: Forget about the LED. Clearly I said it wrong. Focus on the posts.

## Layout corrections

- ColL/ColR must be OUTSIDE the phone (can't be under the phone and still plug into something).
- PostL/PostR must also be outside the keyboard — these are additional parts attaching to each other.
- Keep posts/columns as close as possible to minimize footprint, while respecting size, tolerance, and strength.
- Confirmed pairing: PostL mates with ColL, PostR mates with ColR.
- "Phone looks OK, not ideal though." / "Keyboard is not ok" (before the post/column fixes). Later: "Phone looks OK now, keyboard posts can be closer."
