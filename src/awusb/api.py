"""Pydantic models for client-server communication."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from .usbdevice import UsbDevice


class StrictBaseModel(BaseModel):
    """Base model with strict validation - no extra fields allowed."""

    model_config = ConfigDict(extra="forbid")


class ListRequest(StrictBaseModel):
    """Request to list available USB devices."""

    command: Literal["list"] = "list"


class DeviceRequest(StrictBaseModel):
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

    command: Literal["find"] = "find"


class AttachRequest(DeviceRequest):
    """Request to attach a USB device."""

    command: Literal["attach"] = "attach"


class DetachRequest(DeviceRequest):
    """Request to detach a USB device."""

    command: Literal["detach"] = "detach"


class ListResponse(StrictBaseModel):
    """Response containing list of USB devices."""

    status: Literal["success"]
    data: list[UsbDevice]


class DeviceResponse(StrictBaseModel):
    """Response to find/attach/detach requests."""

    status: Literal["success"]
    data: UsbDevice


class ErrorResponse(StrictBaseModel):
    """Error response."""

    status: Literal["error"]
    message: str
