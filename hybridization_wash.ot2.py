from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'MyBaits v4 wash protocol',
    'author': 'Tomasz Suchan <t.suchan@botany.pl>',
    'description': 'Protocol for washing the DNA enriched with MyBaits v4',
    'apiLevel': '2.0'
}


def run(protocol: protocol_api.ProtocolContext):
    # modules
    module_pcr = protocol.load_module('thermocycler', 7)
    pcr = module_pcr.load_labware('biorad_96_wellplate_200ul_pcr')

    module_magnet = protocol.load_module('magdeck', 4)
    magnet = module_magnet.load_labware('biorad_96_wellplate_200ul_pcr')

    # labware
    tipracks = [protocol.load_labware(
        'opentrons_96_filtertiprack_200ul', slot) for slot in ['5','6']]
    trash = protocol.load_labware(
        'agilent_1_reservoir_290ml', 9)
    elution_plate = protocol.load_labware(
        'biorad_96_wellplate_200ul_pcr', 1)
    tubes_rack_l = protocol.load_labware(
        'opentrons_6_tuberack_falcon_50ml_conical', 2)
    tubes_rack_s = protocol.load_labware(
        'opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', 3)

    # pipettes
    pipette_multi = protocol.load_instrument(
        'p300_multi', 'left', tip_racks=tipracks)
    pipette_single = protocol.load_instrument(
        'p300_single', 'right', tip_racks=tipracks)

    # commands
    module_pcr.set_block_temperature(65)  # heat to 65 deg
    module_pcr.set_lid_temperature(85)
    module_pcr.open_lid()
    pipette_single.transfer(200, tubes_rack_l['A1'],
                              [pcr.columns_by_name()[column] for column in ['7', '8', '9', '10']])  # wash buffer
    pipette_single.transfer(100, tubes_rack_s['A1'],
                              pcr.columns_by_name()['11'])  # elution buffer
    protocol.pause('Load the samples')  # 30 uL hybridization vol + 70 uL beads

    def wash(step, elution_vol):
        module_pcr.close_lid()
        protocol.delay(minutes=5)
        module_pcr.open_lid()
        module_magnet.engage()
        pipette_multi.pick_up_tip()
        pipette_multi.transfer(180, pcr.columns()[step],
                               magnet.columns()[step],
                               new_tip='never')
        protocol.delay(seconds=30)
        pipette_multi.transfer(180, magnet.columns()[step],
                               trash.columns()[0],
                               new_tip='never')
        pipette_multi.drop_tip()
        module_magnet.disengage()
        pipette_multi.pick_up_tip()
        pipette_multi.transfer(180, pcr.columns()[step+6],
                               magnet.columns()[step],
                               new_tip='never')
        pipette_multi.mix(5, 100)
        pipette_multi.transfer(180, magnet.columns()[step],
                               pcr.columns()[step+1],
                               new_tip='never')
        pipette_multi.drop_tip()

    # wash steps 1-3
    for i in range(4):
        wash(step=i, elution_vol=180)
    # last wash and elute in final volume
    wash(step=4, elution_vol=30)

    # elution step - if using polymerase other than KAPA HiFi Hot Start
    module_pcr.set_block_temperature(95)
    module_pcr.set_lid_temperature(115)
    module_pcr.close_lid()
    protocol.delay(minutes=5)
    module_pcr.open_lid()
    module_magnet.engage()
    pipette_multi.transfer(30, pcr.columns_by_name()['4'],
                           magnet.columns_by_name()['4'])
    protocol.delay(minutes=1)
    pipette_multi.transfer(30, magnet.columns_by_name()['4'],
                           elution_plate.columns_by_name()['1'])

    module_pcr.deactivate()
