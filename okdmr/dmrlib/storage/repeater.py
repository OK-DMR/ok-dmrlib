import logging
import uuid
from logging import Logger
from typing import Dict
from uuid import UUID

import asyncio

from okdmr.dmrlib.hytera.snmp import (
    SNMP,
    KNOWN_SNMP_COMMUNITIES,
    DEFAULT_SNMP_COMMUNITY,
)
from okdmr.dmrlib.storage import ADDRESS_TYPE, ADDRESS_EMPTY


class Repeater:
    """ """

    def __init__(
        self,
        dmr_id: int = 0,
        callsign: str = "",
        serial: str = "",
        address_in: ADDRESS_TYPE = ADDRESS_EMPTY,
        address_out: ADDRESS_TYPE = ADDRESS_EMPTY,
        snmp_enabled: bool = True,
        nat_enabled: bool = False,
        logger: Logger = None,
    ) -> None:
        self.__attrs: Dict[str, any] = dict()
        self.id: UUID = uuid.uuid4()
        """ id is read-only field identifies the repeater regardless the params/attrs/configs """
        self.logger = logging.getLogger(f"[RPT {self.id}]") if not logger else logger
        self.address_in: ADDRESS_TYPE = address_in
        """ Address(IP+Port) from which the data come """
        self.address_out: ADDRESS_TYPE = address_out
        """ Address(IP+Port) for sending data to repeater """
        self.address_nat: ADDRESS_TYPE = ADDRESS_EMPTY
        """ Address(IP+Port) to which Repeater is sending data (NAT external IP + Forwarded Port) """
        self.snmp_enabled: bool = snmp_enabled
        self.nat_enabled: bool = nat_enabled
        self.dmr_id: int = dmr_id
        self.callsign: str = callsign
        self.serial: str = serial

    def attr(self, key: str, value: any = None) -> any:
        """
        Repeater should be generic, contains network-wise typed properties/members, but all the non-generic
        attributes shall be stored in private __attrs dict

        Args:
            key:
            value:

        Returns:
            Value set for key
        """
        if value is None:
            # read only
            return self.__attrs.get(key, None)

        else:
            # write and return the value written
            # allows for chain calls
            self.__attrs[key] = value
            return value

    def delete_attr(self, key: str) -> bool:
        """

        Args:
            key: attribute name to delete

        Returns:
            True if the attr was found and deleted, False if it was undefined
        """
        rtn: bool = key in self.__attrs.keys()
        del self.__attrs[key]
        return rtn

    def repeater_target_address(self) -> ADDRESS_TYPE:
        """
        Address to which the Repeater is configured to send data to
        If the repeater is in LAN (without NAT) this is the same IP
        If the repeater is behind NAT the IP/Port will be NAT-IP + some Port

        Returns:
            Address that Repeater should send data to
        """
        return self.address_nat if self.nat_enabled else self.address_in

    def patch(self, patch: Dict[str, any] = {}) -> "Repeater":
        """
        Will patch both instance members and dynamic attributes storage

        Args:
            patch: dictionary of attributes to patch (string keys, any kind of values)

        Returns:
            Repeater/self
        """

        for key, value in patch.items():
            if hasattr(self, key):
                setattr(self, key, value)
            elif value is not None:
                self.attr(key, value)
        return self

    def read_snmp_values(
        self,
        snmp_community: KNOWN_SNMP_COMMUNITIES = DEFAULT_SNMP_COMMUNITY,
        patch_self: bool = True,
    ) -> Dict[str, any]:
        """

        Returns:

        """
        if not self.snmp_enabled:
            return {}

        snmp_data = asyncio.run(
            SNMP().walk_ip(ip=self.address_out[0], snmp_community=snmp_community)
        )
        if patch_self:
            print(snmp_data)
            self.patch(snmp_data)
        return snmp_data
