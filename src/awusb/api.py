"""Pydantic models for client-server communication."""

from typing import Literal

from pydantic import BaseModel

from .usbdevice import UsbDevice


class ListRequest(BaseModel):
    """Request to list available USB devices."""

    command: Literal["list"] = "list"


class DeviceRequest(BaseModel):
    """
    A base class for all device-related requests.
    Includes search criteria used to identify a device.
    """

    id: str | None = None
    bus: str | None = None
    serial: str | None = None
    desc: str | None = None
    first: bool = False


class FindRequest(DeviceRequest):
    """Request to find a USB device."""


class AttachRequest(DeviceRequest):
    """Request to attach a USB device."""


class DetachRequest(DeviceRequest):
    """Request to detach a USB device."""


class ListResponse(BaseModel):
    """Response containing list of USB devices."""

    status: Literal["success"]
    data: list[UsbDevice]


class DeviceResponse(BaseModel):
    """Response to find/attach/detach requests."""

    status: Literal["success"]
    data: UsbDevice


class ErrorResponse(BaseModel):
    """Error response."""

    status: Literal["error"]
    message: str
