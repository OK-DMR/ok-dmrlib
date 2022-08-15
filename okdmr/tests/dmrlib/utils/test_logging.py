import logging

from okdmr.dmrlib.utils.logging_trait import LoggingTrait


class TestLogging(LoggingTrait):
    def test_logs(self, caplog) -> None:
        # setup
        caplog.set_level(logging.DEBUG)
        self.get_logger().setLevel(level=logging.DEBUG)

        self.log_info("info")
        self.log_debug("debug")
        self.log_error("error")
        self.log_warning("warning")
        self.log_exception("error")

        assert len(caplog.records) == 5

        for record in caplog.records:
            assert record.levelname.lower() == record.msg
