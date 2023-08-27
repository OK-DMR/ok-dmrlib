from okdmr.dmrlib.storage.repeater_storage import RepeaterStorage


def test_storage_auto_create(caplog):
    rs: RepeaterStorage = RepeaterStorage()
    assert len(rs) == 0, f"Pre-defined repeaters?"

    addr1 = ("", 0)
    addr2 = ("", 500)
    addr3 = ("192.168.2.10", 500)

    rs.match_incoming(address=addr1, auto_create=True)
    assert len(rs) == 1
    rs.match_incoming(address=addr1, auto_create=True)
    assert len(rs) == 1
    rs.match_incoming(address=addr2, auto_create=True)
    assert len(rs) == 2
    rs.match_incoming(address=addr3, auto_create=True)
    assert len(rs) == 3

    rpt = rs.match_incoming(addr1)
    rpt = rs.save(rpt=rpt, patch={"callsign": "OK4DMR"})
    assert rpt.callsign == "OK4DMR"

    rpt = rs.match_incoming(addr2, auto_create=True)
    rpt = rs.save(rpt=rpt, patch={"callsign": "OK4DMR"})
    assert rpt.callsign == "OK4DMR"

    rs.match_attr("callsign", "OK4DMR")

    assert rs.match_uuid(rpt.id) == rpt
