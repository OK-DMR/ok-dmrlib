from okdmr.dmrlib.tools.hrnp_client import HRNPClient, HRNPClientConfiguration


def test_hrnp_client():
    parsed = HRNPClient.args().parse_args(["192.168.22.10"])
    config = HRNPClientConfiguration(**vars(parsed))
    hc: HRNPClient = HRNPClient(config)
    assert not hc.is_running
    hc.stop()
    assert not hc.is_running
