from opentrons import labware, instruments, modules
import math

metadata = {
    'protocolName': 'AMPure DNA Purification',
    'author': 'Tomasz Suchan',
    'source': 'Opentrons modified protocol'
}

if 'ab-microamp-96-PCR' not in labware.list():
    labware.create(
        'ab-microamp-96-PCR',    # name of your labware
        grid=(12, 8),            # number of (columns, rows)
        spacing=(9.025, 9.025),  # distances (mm) between each (column, row)
        diameter=5.494,          # diameter (mm) of each well
        depth=22.5,              # depth (mm) of each well
        volume=200)              # volume (µL) of each well

if 'brand-8-strip-standard' not in labware.list():
    labware.create(
        'brand-8-strip-standard',# name of your labware
        grid=(12, 8),            # number of (columns, rows)
        spacing=(9.025, 9.025),  # distances (mm) between each (column, row)
        diameter=5,              # diameter (mm) of each well
        depth=21,                # depth (mm) of each well
        volume=200)              # volume (µL) of each well

mag_deck = modules.load('magdeck', '1')
input_plate = labware.load('brand-8-strip-standard', '2')
output_plate = labware.load('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '3')
waste_container = labware.load('agilent_1_reservoir_290ml', '9')


def run_custom_protocol(
        sample_number: int = 8,
        plate_type: 'StringSelection...' = 'biorad',
        sample_volume: float = 25,
        bead_ratio: float = 1.4,
        elution_buffer_volume: float = 25,
        incubation_time: float = 5,
        settling_time: float = 5,
        drying_time: float = 5):

    if plate_type == 'biorad':
        mag_plate = labware.load(
            'biorad_96_wellplate_200ul_pcr', '1', share=True)
        magdeck_height = 18
    elif plate_type == 'microamp':
        mag_plate = labware.load('ab-microamp-96-PCR', '1', share=True)
        magdeck_height = 22
    elif plate_type == 'strip':
        mag_plate = labware.load('brand-8-strip-standard', '1', share=True)
        magdeck_height = 22

    # p300
    col_num = sample_number // 8 + (1 if sample_number % 8 > 0 else 0)
    tiprack_num = col_num // 12 + (1 if col_num % 12 > 0 else 0)
    tips_slots = ['7', '8', '10'][:tiprack_num]
    tipracks_p300 = [labware.load(
        'opentrons_96_filtertiprack_200ul', slot) for slot in tips_slots]
    pipette_p300 = instruments.P300_Multi(
        mount='right',
        tip_racks=tipracks_p300)

    # p50
    tipracks_p50 = [labware.load('opentrons_96_filtertiprack_200ul', '11')]
    pipette_p50 = instruments.P50_Single(
        mount='left',
        tip_racks=tipracks_p50)

    air_vol_p50 = pipette_p50.max_volume * 0.1
    air_vol_p300 = pipette_p300.max_volume * 0.1

    # Define reagents
    if sample_number <= 4:
        reagent_container = labware.load(
            'opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '4')
        etoh_container = labware.load(
            'opentrons_6_tuberack_nest_50ml_conical', '5')
        beads = reagent_container.wells(0)
        elution_buffer = reagent_container.wells(1)
        ethanol = etoh_container.wells(0)
        magplate = [well for well in mag_plate.wells()[:sample_number]]
    else:
        reagent_container = labware.load(
            'usascientific_12_reservoir_22ml', '4')
        reagent_container2 = labware.load(
            'opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '5')
        beads = reagent_container2.wells(0)
        elution_buffer = reagent_container.wells(0)
        ethanol = reagent_container.wells(11)
        magplate = [col for col in mag_plate.cols()[:col_num]]

    samples = [well for well in input_plate.wells()[:sample_number]]
    magplate_samples = [well for well in mag_plate.wells()[:sample_number]]

    liquid_waste = waste_container.wells('A1')

    output = [well for well in output_plate.wells()[:sample_number]]

    # Define bead and mix volume
    bead_volume = sample_volume * bead_ratio
    if bead_volume / 2 > 50:
        mix_vol = 50
    else:
        mix_vol = bead_volume / 2
    total_vol = bead_volume + sample_volume + 5

    # Dispense beads
    pipette_p50.set_flow_rate(dispense=50)
    pipette_p50.distribute(bead_volume,
                           beads, magplate_samples)

    # Mix beads and PCR samples
    for target, dest in zip(magplate, samples):
        pipette_p300.pick_up_tip()
        pipette_p300.transfer(sample_volume, dest, target,
                             new_tip='never', air_gap=air_vol_p50)
        pipette_p300.mix(10, mix_vol, target)
        pipette_p300.blow_out()
        pipette_p300.drop_tip()

    # Incubate beads and PCR product at RT for 5 minutes
    pipette_p300.delay(minutes=incubation_time)

    # Engagae MagDeck and incubate
    mag_deck.engage(height=magdeck_height)
    pipette_p300.delay(minutes=settling_time)

    # Remove supernatant from magnetic beads
    pipette_p300.set_flow_rate(aspirate=25, dispense=150)
    for target in magplate:
        pipette_p300.transfer(total_vol, target, liquid_waste,
                              air_gap=air_vol_p300, blow_out=True)

    # Wash beads twice with 70% ethanol
    pipette_p300.set_flow_rate(aspirate=25, dispense=25)
    for cycle in range(2):
        for target in magplate:
            pipette_p300.transfer(150, ethanol, target, new_tip='always')
        pipette_p300.delay(seconds=30)
        for target in magplate:
            pipette_p300.transfer(170, target, liquid_waste, new_tip='always')
    for target in magplate:
        pipette_p300.transfer(170, target, liquid_waste, new_tip='always')

    # Dry at RT
    pipette_p300.delay(minutes=drying_time)

    # Disengage MagDeck
    mag_deck.disengage()

    # Mix beads with elution buffer
    for i, target in enumerate(magplate):
        side = 0 if i%2 == 0 else math.pi
        move_loc = (target, target.from_center(r=0, h=-0.8, theta=side))
        disp_loc = (target, target.from_center(r=0.9, h=0, theta=side))

        pipette_p300.pick_up_tip()
        pipette_p300.aspirate(elution_buffer_volume, elution_buffer)
        pipette_p300.dispense(elution_buffer_volume, target)
        for n in range(5):
            pipette_p300.aspirate(mix_vol, target)
            pipette_p300.move_to(move_loc)
            pipette_p300.dispense(mix_vol, disp_loc)
        pipette_p300.mix(5, mix_vol, target)
        pipette_p300.drop_tip()

    # Incubate at RT for x minutes
    pipette_p300.delay(minutes=incubation_time)

    # Engagae MagDeck for x minutes and remain engaged for DNA elution
    mag_deck.engage(height=magdeck_height)
    pipette_p50.delay(minutes=settling_time)

    # Transfer clean PCR product to a new well
    for target, dest in zip(magplate_samples, output):
        pipette_p50.transfer(elution_buffer_volume, target,
                             dest, air_gap=air_vol_p50, blow_out=True)

    # Disengage MagDeck
    mag_deck.disengage()

run_custom_protocol(**{'sample_number': 8,     # up to 24 samples
                       'plate_type': 'biorad',  # 'biorad' or 'microamp' or 'strip'
                       'sample_volume': 25.0,
                       'bead_ratio': 1.4,
                       'elution_buffer_volume': 25.0,
                       'incubation_time': 5, # time before the magnet and after elution in minutes
                       'settling_time': 1,   # time on the magnet in minutes
                       'drying_time': 4})    # drying time in minutes
