import logging
from logging import Logger
from typing import Optional, Dict
from uuid import UUID

from okdmr.dmrlib.storage import ADDRESS_TYPE, ADDRESS_EMPTY
from okdmr.dmrlib.storage.repeater import Repeater


class RepeaterStorage:
    """
    OK-DMR Generic Repeater Storage
    """

    def __init__(self, logger: Logger = None):
        self.__repeaters: Dict[UUID, Repeater] = dict()
        self.__logger = logging.getLogger("StorageInterface") if not logger else logger

    def match_incoming(
        self,
        address: ADDRESS_TYPE,
        auto_create: bool = False,
        patch: Dict[str, any] = {},
    ) -> Optional[Repeater]:
        found = self.match_attr("address_in", address)

        if not found and auto_create:
            found = self.create_repeater(dmr_id=None, address_in=address)

        return self.save(rpt=found, patch=patch)

    def save(self, rpt: Repeater, patch: Dict[str, any] = {}) -> Repeater:
        """
        Will save modified Repeater in the storage, and return it right after

        Args:
            patch:
            rpt:

        Returns:

        """
        if len(patch):
            self.__repeaters.update({rpt.id: rpt.patch(patch=patch)})
        return rpt

    def match_attr(self, attr_name: str, match_value: any) -> Optional[Repeater]:
        """
        Will match any Repeater attribute (by attr_name) against match_value

        Args:
            attr_name:
            match_value:

        Returns:
            Repeater or None if matchin fails
        """
        found: Optional[Repeater] = None
        for repeater in self.__repeaters.values():
            if getattr(repeater, attr_name) == match_value:
                if not found:
                    found = repeater
                else:
                    self.__logger.critical(
                        f"match_attr({attr_name}) found duplicate for value {match_value}"
                    )
        return found

    def match_uuid(self, uuid: UUID) -> Optional[Repeater]:
        """
        Args:
            uuid:

        Returns:
            Repeater or None if matching fails
        """
        return self.match_attr("id", uuid)

    def create_repeater(
        self,
        dmr_id: int = None,
        address_in: ADDRESS_TYPE = ADDRESS_EMPTY,
        address_out: ADDRESS_TYPE = ADDRESS_EMPTY,
    ) -> Repeater:
        """
        Override this method if you need to extend Repeater object, you can create compatible instance instead here

        Args:
            dmr_id:
            address_in:
            address_out:
        """
        # create object, generating UUID
        rpt = Repeater(address_in=address_in, address_out=address_out, dmr_id=dmr_id)
        # save to storage
        self.__repeaters[rpt.id] = rpt
        return rpt

    def __len__(self):
        return len(self.__repeaters)
