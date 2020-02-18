# Scripts for Opentrons robot

## General instructions

### Testing programs
All scripts can be tested using `opentrons_simulate` program.

Install it using `pip`:

```
pip install opentrons
```

Test program:

```
opentrons_simulate <name_of_the_script>
```

This will list all the steps of the protocol, e.g.:

```
[...]
Engaging Magnetic Module
Picking up tip from A2 of Opentrons 96 Filter Tip Rack 200 µL on 5
Transferring 180.0 from A1 of Bio-Rad 96 Well Plate 200 µL PCR on Thermocycler Module on 7 to A1 of Bio-Rad 96 Well Plate 200 µL PCR on Magnetic Module on 4
	Aspirating 180.0 uL from A1 of Bio-Rad 96 Well Plate 200 µL PCR on Thermocycler Module on 7 at 1.0 speed
	Dispensing 180.0 uL into A1 of Bio-Rad 96 Well Plate 200 µL PCR on Magnetic Module on 4 at 1.0 speed
Delaying for 0 minutes and 30 seconds
Transferring 180.0 from A1 of Bio-Rad 96 Well Plate 200 µL PCR on Magnetic Module on 4 to A1 of Agilent 1 Well Reservoir 290 mL on 9
	Aspirating 180.0 uL from A1 of Bio-Rad 96 Well Plate 200 µL PCR on Magnetic Module on 4 at 1.0 speed
	Dispensing 180.0 uL into A1 of Agilent 1 Well Reservoir 290 mL on 9 at 1.0 speed
Dropping tip into A1 of Opentrons Fixed Trash on 12
Disengaging Magnetic Module
[...]
```

### Robot calibration

### Running programs
In general, I usually put only the racks/modules/tip boxes during the calibration step after the pipette moves to the location of the particular rack. This avoids hitting it in case something is not calibrated well.

## Protocols

### DNA purification with AMPure
Protocol requires megnetic modile. The script is configured using `run_custom_protocol` function. For sample number equal or less than 4 single-channel pipettes are used and for more one multichannel and one single-channel pipette is used.

Reagents for <=4 samples:
- ethanol in 50 ml Falcon tube: well 1, slot 5
- AMPure beads:  well 1, slot 4
- elution buffer: well 2, slot 4

Reagents for >4 samples:
- ethanol in Agilent 12-column reservoir: column 12, slot 4
- elution buffer in Agilent 12-column reservoir: column 1, slot 4
- AMPure beads: well 1, slot 5

TO DO:
- rewrite for Opentrons API 2.0

### Hybridization wash protocol for MyBaits v4

This protocol requires magnetic module and PCR module. Maximum 8 samples can be processed at once, and this is advisable number as an 8-channel pipette is used for speed.

Reagents:
- sample after hybridization with streptavidine beads added: column 1 in PCR machine
- hybidization wash buffer (6 ml for 8 samples, in 50 ml Falcon tube): well 1, slot 2
- elution buffer (300 ul for 8 samples in 1.5 ml Eppendorf tube) : well 1, slot 3

TO DO:
- make sample number more flexible?
