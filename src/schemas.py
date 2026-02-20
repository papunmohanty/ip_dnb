from __future__ import annotations

from pydantic import BaseModel


class Asn(BaseModel):
    asn: str
    route: str
    netname: str
    name: str
    country_code: str
    domain: str
    type: str
    rir: str


class Privacy(BaseModel):
    is_abuser: bool
    is_anonymous: bool
    is_bogon: bool
    is_hosting: bool
    is_icloud_relay: bool
    is_proxy: bool
    is_tor: bool
    is_vpn: bool


class Hosting(BaseModel):
    provider: str
    domain: str
    network: str


class Company(BaseModel):
    name: str
    domain: str
    country_code: str
    type: str


class Abuse(BaseModel):
    address: str
    country_code: str
    email: str
    name: str
    network: str
    phone: str


class Model(BaseModel):
    ip: str
    country: str
    country_code: str
    is_eu: bool
    city: str
    continent: str
    latitude: float
    longitude: float
    time_zone: str
    postal_code: str
    subdivision: str
    currency_code: str
    calling_code: str
    is_anycast: bool
    is_satellite: bool
    asn: Asn
    privacy: Privacy
    hosting: Hosting
    company: Company
    abuse: Abuse
