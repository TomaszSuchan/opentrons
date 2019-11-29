# Scripts for Opentrons robot

## General instructions

### Robot calibration

### Running programs
In general, I usually put only the racks/modules/tip boxes during the calibration step after the pipette moves to the location of the particular rack. This avoids hitting it in case something is not calibrated well.

## DNA purification with AMPure
The script is configured using `run_custom_protocol` function. For sample number equal or less than 4 single-channel pipettes are used and for more one multichannel and one single-channel pipette is used.

Reagents for <=4 samples:
- ethanol in 50 ml Falcon tube in well 1, slot 5
- AMPure beads in well 1, slot 4
- elution buffer in well 2, slot 4

Reagents for >4 samples:
- ethanol in Agilent 12-column reservoir, column 12, slot 4
- elution buffer in Agilent 12-column reservoir, column 1, slot 4
- AMPure beads in well 1, slot 5
